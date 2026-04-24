//╔═════════════════════════════╗                       
//║  Link: t.me/FrontendVSCode                       ║                         
//║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║    
//║  lang: C                                         ║                     
//║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║                      
//║  build:3.10.15                                   ║
//║  files: process_info.c                           ║    
//╚═════════════════════════════╝



#include "../include/process_info.h"
#include "../include/safe_read.h"
#include "../include/common.h"
#include <sys/sysinfo.h>
#include <dirent.h>
#include <ctype.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>

// ==================== ЗАЩИТА ОТ ПОВТОРНОГО ВКЛЮЧЕНИЯ ====================
#ifdef PROCESS_INFO_C
#error "process_info.c включен дважды!"
#endif
#define PROCESS_INFO_C

// ==================== КОНСТАНТЫ ====================
#define PROC_PATH "/proc"
#define MAX_PROC_SCAN 1024
#define HERTZ_PER_SECOND 100
#define MIN_CPU_DELTA 0.1f

// ==================== СТАТИЧЕСКИЕ ПЕРЕМЕННЫЕ ====================
typedef struct {
    unsigned long long total_jiffies;
    struct timespec last_update;
    int initialized;
} ProcStats;

static struct {
    unsigned long long* prev_cpu_jiffies;
    int count;
    struct timespec last_time;
} process_cache = {NULL, 0, {0, 0}};

static ProcStats proc_stats = {0};

// ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

/**
 * Инициализация статистики процессов
 */
static void ensure_proc_stats_initialized(void) {
    if (!proc_stats.initialized) {
        proc_stats.total_jiffies = 0;
        clock_gettime(CLOCK_MONOTONIC, &proc_stats.last_update);
        proc_stats.initialized = 1;
    }
}

/**
 * Получение общего количества jiffies системы
 */
static unsigned long long get_total_jiffies(void) {
    FILE* fp = fopen("/proc/stat", "r");
    if (fp == NULL) return 0;
    
    char line[256];
    unsigned long long user, nice, system, idle, iowait, irq, softirq, steal;
    
    if (fgets(line, sizeof(line), fp) != NULL) {
        if (sscanf(line, "cpu %llu %llu %llu %llu %llu %llu %llu %llu",
                   &user, &nice, &system, &idle, &iowait, &irq, &softirq, &steal) == 8) {
            fclose(fp);
            return user + nice + system + idle + iowait + irq + softirq + steal;
        }
    }
    
    fclose(fp);
    return 0;
}

/**
 * Безопасное получение времени CPU процесса
 */
static unsigned long long get_process_cpu_safe(int pid) {
    char path[MAX_PATH];
    snprintf(path, sizeof(path), "/proc/%d/stat", pid);
    
    size_t dummy = 0;
    char* stat = safe_read_file(path, &dummy);
    if (stat == NULL) return 0;
    
    unsigned long long utime = 0, stime = 0;
    int fields = sscanf(stat,
        "%*d %*s %*c %*d %*d %*d %*d %*d %*u %*u %*u %*u %*u %llu %llu",
        &utime, &stime);
    
    free(stat);
    
    return (fields == 2) ? (utime + stime) : 0;
}

/**
 * Получение имени процесса
 */
static char* get_process_name_safe(int pid) {
    char path[MAX_PATH];
    char* name = NULL;
    size_t dummy = 0;
    
    // Сначала пробуем cmdline (полная командная строка)
    snprintf(path, sizeof(path), "/proc/%d/cmdline", pid);
    name = safe_read_file(path, &dummy);
    
    // Если cmdline пустой, пробуем comm (имя процесса)
    if (name == NULL || name[0] == '\0') {
        if (name != NULL) {
            free(name);
            name = NULL;
        }
        
        snprintf(path, sizeof(path), "/proc/%d/comm", pid);
        name = safe_read_file(path, &dummy);
    }
    
    // Если всё равно пусто, создаём имя из PID
    if (name == NULL || name[0] == '\0') {
        if (name != NULL) free(name);
        name = malloc(32);
        if (name != NULL) {
            snprintf(name, 32, "[%d]", pid);
        }
        return name;
    }
    
    // Обработка имени
    if (name != NULL) {
        // Убираем путь, оставляем только имя файла
        char* last_slash = strrchr(name, '/');
        if (last_slash != NULL && *(last_slash + 1) != '\0') {
            char* tmp = strdup(last_slash + 1);
            if (tmp != NULL) {
                free(name);
                name = tmp;
            }
        }
        
        // Убираем переводы строк
        char* nl = strchr(name, '\n');
        if (nl != NULL) *nl = '\0';
        
        char* cr = strchr(name, '\r');
        if (cr != NULL) *cr = '\0';
    }
    
    return name;
}

/**
 * Получение памяти процесса
 */
static unsigned long get_process_mem_safe(int pid) {
    char path[MAX_PATH];
    snprintf(path, sizeof(path), "/proc/%d/statm", pid);
    
    long pages = safe_read_long(path);
    if (pages > 0) {
        return (unsigned long)pages * sysconf(_SC_PAGESIZE);
    }
    return 0;
}

/**
 * Получение состояния процесса
 */
static char get_process_state_safe(int pid) {
    char path[MAX_PATH];
    snprintf(path, sizeof(path), "/proc/%d/stat", pid);
    
    size_t dummy = 0;
    char* stat = safe_read_file(path, &dummy);
    if (stat == NULL) return '?';
    
    char state = '?';
    // Формат: pid (comm) state ...
    char* first_space = strchr(stat, ' ');
    if (first_space != NULL) {
        char* second_space = strchr(first_space + 1, ' ');
        if (second_space != NULL) {
            char* third_space = strchr(second_space + 1, ' ');
            if (third_space != NULL) {
                state = *(second_space + 1);
            }
        }
    }
    
    free(stat);
    return state;
}

/**
 * Получение приоритета процесса
 */
static int get_process_priority_safe(int pid) {
    char path[MAX_PATH];
    snprintf(path, sizeof(path), "/proc/%d/stat", pid);
    
    size_t dummy = 0;
    char* stat = safe_read_file(path, &dummy);
    if (stat == NULL) return 0;
    
    int priority = 0;
    // Парсим 18-е поле (priority)
    int field = 0;
    char* token = strtok(stat, " ");
    while (token != NULL && field < 18) {
        if (field == 17) { // priority - 18-е поле (0-based)
            priority = atoi(token);
            break;
        }
        token = strtok(NULL, " ");
        field++;
    }
    
    free(stat);
    return priority;
}

/**
 * Получение времени запуска процесса
 */
static unsigned long long get_process_start_time_safe(int pid) {
    char path[MAX_PATH];
    snprintf(path, sizeof(path), "/proc/%d/stat", pid);
    
    size_t dummy = 0;
    char* stat = safe_read_file(path, &dummy);
    if (stat == NULL) return 0;
    
    unsigned long long start_time = 0;
    // Парсим 22-е поле (starttime)
    int field = 0;
    char* token = strtok(stat, " ");
    while (token != NULL && field < 22) {
        if (field == 21) { // starttime - 22-е поле (0-based)
            start_time = strtoull(token, NULL, 10);
            break;
        }
        token = strtok(NULL, " ");
        field++;
    }
    
    free(stat);
    return start_time;
}

/**
 * Функция сравнения процессов по CPU
 */
static int compare_processes_by_cpu(const void* a, const void* b) {
    const ProcessInfo* pa = (const ProcessInfo*)a;
    const ProcessInfo* pb = (const ProcessInfo*)b;
    
    if (pb->cpu > pa->cpu) return 1;
    if (pb->cpu < pa->cpu) return -1;
    return 0;
}

/**
 * Функция сравнения процессов по памяти
 */
static int compare_processes_by_mem(const void* a, const void* b) {
    const ProcessInfo* pa = (const ProcessInfo*)a;
    const ProcessInfo* pb = (const ProcessInfo*)b;
    
    if (pb->mem > pa->mem) return 1;
    if (pb->mem < pa->mem) return -1;
    return 0;
}

/**
 * Проверка, является ли имя директории PID-ом
 */
static int is_valid_pid(const char* name) {
    if (name == NULL || name[0] == '\0') return 0;
    
    for (const char* p = name; *p; p++) {
        if (!isdigit((unsigned char)*p)) return 0;
    }
    return 1;
}

// ==================== ОСНОВНЫЕ ФУНКЦИИ ====================

int get_top_processes(ProcessInfo* procs, int max_count) {
    if (procs == NULL || max_count <= 0) return 0;
    
    ensure_proc_stats_initialized();
    
    // Получаем общее количество jiffies для расчёта процентов
    unsigned long long total_jiffies = get_total_jiffies();
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);
    
    // Временный массив для сбора процессов
    ProcessInfo* temp_procs = NULL;
    int temp_count = 0;
    int max_temp = max_count * 3;  // Сканируем больше, чтобы отсортировать
    
    temp_procs = (ProcessInfo*)calloc(max_temp, sizeof(ProcessInfo));
    if (temp_procs == NULL) return 0;
    
    DIR* dir = opendir(PROC_PATH);
    if (dir == NULL) {
        free(temp_procs);
        return 0;
    }
    
    struct dirent* entry;
    
    // Сбор информации о процессах
    while ((entry = readdir(dir)) != NULL && temp_count < max_temp) {
        if (!is_valid_pid(entry->d_name)) continue;
        
        int pid = atoi(entry->d_name);
        if (pid <= 0) continue;
        
        ProcessInfo* p = &temp_procs[temp_count];
        memset(p, 0, sizeof(ProcessInfo));
        
        p->pid = pid;
        
        // Имя процесса
        char* name = get_process_name_safe(pid);
        if (name != NULL) {
            strncpy(p->name, name, sizeof(p->name) - 1);
            p->name[sizeof(p->name) - 1] = '\0';
            free(name);
        } else {
            snprintf(p->name, sizeof(p->name), "[%d]", pid);
        }
        
        // CPU (будет обновлено позже с дельтой)
        p->cpu = 0.0f;
        
        // Память
        p->mem = get_process_mem_safe(pid);
        
        // Состояние
        p->state = get_process_state_safe(pid);
        
        // Приоритет
        p->priority = get_process_priority_safe(pid);
        
        // Время запуска
        p->start_time = get_process_start_time_safe(pid);
        
        temp_count++;
    }
    
    closedir(dir);
    
    // Если есть кеш предыдущих значений, вычисляем CPU usage
    if (process_cache.count > 0 && process_cache.prev_cpu_jiffies != NULL &&
        process_cache.last_time.tv_sec > 0) {
        
        double time_diff = (now.tv_sec - process_cache.last_time.tv_sec) +
                          (now.tv_nsec - process_cache.last_time.tv_nsec) / 1e9;
        
        if (time_diff > 0.1) {  // Минимум 100ms для точности
            unsigned long long total_diff = total_jiffies - proc_stats.total_jiffies;
            
            for (int i = 0; i < temp_count; i++) {
                unsigned long long current = get_process_cpu_safe(temp_procs[i].pid);
                if (current > process_cache.prev_cpu_jiffies[i] && total_diff > 0) {
                    float cpu_percent = (current - process_cache.prev_cpu_jiffies[i]) * 100.0f / total_diff;
                    if (cpu_percent >= MIN_CPU_DELTA) {
                        temp_procs[i].cpu = cpu_percent;
                    }
                }
            }
        }
    }
    
    // Обновляем кеш
    if (process_cache.prev_cpu_jiffies != NULL) {
        free(process_cache.prev_cpu_jiffies);
    }
    
    process_cache.prev_cpu_jiffies = (unsigned long long*)malloc(temp_count * sizeof(unsigned long long));
    if (process_cache.prev_cpu_jiffies != NULL) {
        for (int i = 0; i < temp_count; i++) {
            process_cache.prev_cpu_jiffies[i] = get_process_cpu_safe(temp_procs[i].pid);
        }
        process_cache.count = temp_count;
        process_cache.last_time = now;
    }
    
    proc_stats.total_jiffies = total_jiffies;
    
    // Сортируем по CPU
    if (temp_count > 0) {
        qsort(temp_procs, temp_count, sizeof(ProcessInfo), compare_processes_by_cpu);
    }
    
    // Копируем нужное количество результатов
    int result_count = (temp_count < max_count) ? temp_count : max_count;
    for (int i = 0; i < result_count; i++) {
        memcpy(&procs[i], &temp_procs[i], sizeof(ProcessInfo));
    }
    
    free(temp_procs);
    return result_count;
}

int get_top_processes_by_mem(ProcessInfo* procs, int max_count) {
    if (procs == NULL || max_count <= 0) return 0;
    
    ProcessInfo* temp_procs = NULL;
    int temp_count = 0;
    int max_temp = max_count * 3;
    
    temp_procs = (ProcessInfo*)calloc(max_temp, sizeof(ProcessInfo));
    if (temp_procs == NULL) return 0;
    
    DIR* dir = opendir(PROC_PATH);
    if (dir == NULL) {
        free(temp_procs);
        return 0;
    }
    
    struct dirent* entry;
    
    while ((entry = readdir(dir)) != NULL && temp_count < max_temp) {
        if (!is_valid_pid(entry->d_name)) continue;
        
        int pid = atoi(entry->d_name);
        if (pid <= 0) continue;
        
        ProcessInfo* p = &temp_procs[temp_count];
        memset(p, 0, sizeof(ProcessInfo));
        
        p->pid = pid;
        
        char* name = get_process_name_safe(pid);
        if (name != NULL) {
            strncpy(p->name, name, sizeof(p->name) - 1);
            p->name[sizeof(p->name) - 1] = '\0';
            free(name);
        } else {
            snprintf(p->name, sizeof(p->name), "[%d]", pid);
        }
        
        p->mem = get_process_mem_safe(pid);
        p->state = get_process_state_safe(pid);
        
        temp_count++;
    }
    
    closedir(dir);
    
    if (temp_count > 0) {
        qsort(temp_procs, temp_count, sizeof(ProcessInfo), compare_processes_by_mem);
    }
    
    int result_count = (temp_count < max_count) ? temp_count : max_count;
    for (int i = 0; i < result_count; i++) {
        memcpy(&procs[i], &temp_procs[i], sizeof(ProcessInfo));
    }
    
    free(temp_procs);
    return result_count;
}

int get_process_info(int pid, ProcessInfo* info) {
    if (info == NULL || pid <= 0) return 0;
    
    memset(info, 0, sizeof(ProcessInfo));
    info->pid = pid;
    
    char* name = get_process_name_safe(pid);
    if (name != NULL) {
        strncpy(info->name, name, sizeof(info->name) - 1);
        info->name[sizeof(info->name) - 1] = '\0';
        free(name);
    } else {
        snprintf(info->name, sizeof(info->name), "[%d]", pid);
    }
    
    info->cpu = get_process_cpu_safe(pid) / 100.0f;  // Приблизительно
    info->mem = get_process_mem_safe(pid);
    info->state = get_process_state_safe(pid);
    info->priority = get_process_priority_safe(pid);
    info->start_time = get_process_start_time_safe(pid);
    info->threads = 1;  // TODO: получить реальное количество
    
    // Получаем количество потоков
    char path[MAX_PATH];
    snprintf(path, sizeof(path), "/proc/%d/task", pid);
    DIR* task_dir = opendir(path);
    if (task_dir != NULL) {
        int thread_count = 0;
        struct dirent* task_entry;
        while ((task_entry = readdir(task_dir)) != NULL) {
            if (is_valid_pid(task_entry->d_name)) {
                thread_count++;
            }
        }
        info->threads = thread_count;
        closedir(task_dir);
    }
    
    return 1;
}

int process_exists(int pid) {
    if (pid <= 0) return 0;
    
    char path[MAX_PATH];
    snprintf(path, sizeof(path), "/proc/%d", pid);
    
    return safe_file_exists(path);
}

int get_total_process_count(void) {
    int count = 0;
    DIR* dir = opendir(PROC_PATH);
    
    if (dir != NULL) {
        struct dirent* entry;
        while ((entry = readdir(dir)) != NULL) {
            if (is_valid_pid(entry->d_name)) {
                count++;
            }
        }
        closedir(dir);
    }
    
    return count;
}

int kill_process(int pid, int signal) {
    if (pid <= 0) return -1;
    return kill(pid, signal);
}

float get_process_cpu_percent(int pid) {
    static unsigned long long prev_cpu = 0;
    static unsigned long long prev_total = 0;
    static struct timespec prev_time = {0, 0};
    
    unsigned long long current_cpu = get_process_cpu_safe(pid);
    unsigned long long current_total = get_total_jiffies();
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);
    
    if (prev_cpu == 0 || prev_total == 0 || prev_time.tv_sec == 0) {
        prev_cpu = current_cpu;
        prev_total = current_total;
        prev_time = now;
        return 0;
    }
    
    double time_diff = (now.tv_sec - prev_time.tv_sec) +
                      (now.tv_nsec - prev_time.tv_nsec) / 1e9;
    
    if (time_diff < 0.1) return 0;
    
    unsigned long long cpu_diff = current_cpu - prev_cpu;
    unsigned long long total_diff = current_total - prev_total;
    
    prev_cpu = current_cpu;
    prev_total = current_total;
    prev_time = now;
    
    if (total_diff == 0) return 0;
    
    return (int)(cpu_diff * 100 / total_diff);
}

void format_basic_process(const ProcessInfo* info, char* buffer, size_t buffer_size) {
    if (info == NULL || buffer == NULL || buffer_size == 0) return;
    
    char mem_str[32];
    if (info->mem < 1024) {
        snprintf(mem_str, sizeof(mem_str), "%lu B", info->mem);
    } else if (info->mem < 1024 * 1024) {
        snprintf(mem_str, sizeof(mem_str), "%.2f KB", info->mem / 1024.0);
    } else if (info->mem < 1024 * 1024 * 1024) {
        snprintf(mem_str, sizeof(mem_str), "%.2f MB", info->mem / (1024.0 * 1024.0));
    } else {
        snprintf(mem_str, sizeof(mem_str), "%.2f GB", info->mem / (1024.0 * 1024.0 * 1024.0));
    }
    
    char state_char[2] = {info->state, '\0'};
    
    snprintf(buffer, buffer_size,
             "PID: %-6d | %c | %-16s | CPU: %5.1f%% | MEM: %8s",
             info->pid, info->state, info->name, info->cpu, mem_str);
}

void format_process_detailed(const ProcessInfo* info, char* buffer, size_t buffer_size) {
    if (info == NULL || buffer == NULL || buffer_size == 0) return;
    
    char mem_str[32];
    format_bytes(mem_str, sizeof(mem_str), info->mem);
    
    const char* state_str;
    switch (info->state) {
        case 'R': state_str = "Running"; break;
        case 'S': state_str = "Sleeping"; break;
        case 'D': state_str = "Disk Sleep"; break;
        case 'Z': state_str = "Zombie"; break;
        case 'T': state_str = "Stopped"; break;
        case 't': state_str = "Tracing"; break;
        case 'X': state_str = "Dead"; break;
        case 'x': state_str = "Dead"; break;
        case 'K': state_str = "Wakekill"; break;
        case 'W': state_str = "Waking"; break;
        case 'P': state_str = "Parked"; break;
        default: state_str = "Unknown"; break;
    }
    
    snprintf(buffer, buffer_size,
             "📊 Процесс: %s (PID: %d)\n"
             "   Состояние: %s (%c)\n"
             "   CPU: %.1f%%\n"
             "   Память: %s\n"
             "   Приоритет: %d\n"
             "   Потоков: %d\n"
             "   Время запуска: %ld",
             info->name, info->pid,
             state_str, info->state,
             info->cpu,
             mem_str,
             info->priority,
             info->threads,
             info->start_time);
}

// ==================== КОНЕЦ ФАЙЛА ====================
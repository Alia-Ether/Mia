//╔═════════════════════════════╗                       
//║  Link: t.me/FrontendVSCode                       ║                         
//║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║    
//║  lang: C                                         ║                     
//║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║                      
//║  build:3.10.15                                   ║
//║  files: hardware_info.c                          ║    
//╚═════════════════════════════╝

#include "../include/hardware_info.h"
#include "../include/safe_read.h"
#include "../include/common.h"
#include <math.h>
#include <sys/utsname.h>
#include <sys/statvfs.h>
#include <sys/sysinfo.h>
#include <errno.h>
#include <time.h>

// ==================== ЗАЩИТА ОТ ПОВТОРНОГО ВКЛЮЧЕНИЯ ====================
#ifdef HARDWARE_INFO_C
#error "hardware_info.c включен дважды!"
#endif
#define HARDWARE_INFO_C

// ==================== ГЛОБАЛЬНЫЕ СТАТИСТИКИ CPU ====================
static struct {
    unsigned long long total;
    unsigned long long idle;
    unsigned long long per_cpu[MAX_CPUS];
    unsigned long long idle_per_cpu[MAX_CPUS];
    int initialized;
} cpu_stats = {0};

// ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

/**
 * Безопасное чтение с значением по умолчанию
 */
static long safe_read_with_default(const char* path, long default_value) {
    long value = safe_read_long(path);
    return (value > 0) ? value : default_value;
}

/**
 * Инициализация статистики CPU
 */
static void ensure_cpu_stats_initialized(void) {
    if (!cpu_stats.initialized) {
        memset(&cpu_stats, 0, sizeof(cpu_stats));
        cpu_stats.initialized = 1;
    }
}

// ==================== CPU INFO ====================

CPUInfo get_cpu_info(void) {
    CPUInfo info;
    memset(&info, 0, sizeof(info));
    ensure_cpu_stats_initialized();
    
    // Количество ядер
    info.cores_total = sysconf(_SC_NPROCESSORS_CONF);
    info.cores_online = sysconf(_SC_NPROCESSORS_ONLN);
    
    if (info.cores_total <= 0) info.cores_total = 1;
    if (info.cores_online <= 0) info.cores_online = 1;
    
    // Частоты ядер
    for (int i = 0; i < info.cores_total && i < MAX_CPUS; i++) {
        char path[MAX_PATH];
        long freq = 0;
        
        snprintf(path, sizeof(path),
                 "/sys/devices/system/cpu/cpu%d/cpufreq/scaling_cur_freq", i);
        freq = safe_read_long(path);
        
        if (freq <= 0) {
            snprintf(path, sizeof(path),
                     "/sys/devices/system/cpu/cpu%d/cpufreq/cpuinfo_cur_freq", i);
            freq = safe_read_long(path);
        }
        
        info.freq_cur[i] = (freq > 0) ? (float)freq / 1000.0f : 0.0f;
    }
    
    // Температура
    info.temperature = 0.0f;
    const char* temp_paths[] = {
        "/sys/class/thermal/thermal_zone0/temp",
        "/sys/class/thermal/thermal_zone1/temp",
        "/sys/class/thermal/thermal_zone2/temp",
        "/sys/class/thermal/thermal_zone3/temp",
        "/sys/class/thermal/thermal_zone4/temp",
        "/sys/class/thermal/thermal_zone5/temp",
        "/sys/devices/virtual/thermal/thermal_zone0/temp",
        NULL
    };
    
    for (int i = 0; temp_paths[i] != NULL; i++) {
        long temp = safe_read_long(temp_paths[i]);
        if (temp > 0) {
            info.temperature = (float)temp / 1000.0f;
            break;
        }
    }
    
    // Модель CPU
    strcpy(info.model, "Unknown");
    size_t dummy_size = 0;
    char* cpuinfo = safe_read_file("/proc/cpuinfo", &dummy_size);
    if (cpuinfo != NULL) {
        char* model = strstr(cpuinfo, "Processor");
        if (model == NULL) model = strstr(cpuinfo, "model name");
        if (model == NULL) model = strstr(cpuinfo, "Hardware");
        
        if (model != NULL) {
            char* colon = strchr(model, ':');
            if (colon != NULL) {
                colon++;
                while (*colon == ' ') colon++;
                
                char* nl = strchr(colon, '\n');
                if (nl != NULL) *nl = '\0';
                
                strncpy(info.model, colon, sizeof(info.model) - 1);
                info.model[sizeof(info.model) - 1] = '\0';
            }
        }
        free(cpuinfo);
    }
    
    // Архитектура
    struct utsname uts;
    if (uname(&uts) == 0) {
        strncpy(info.arch, uts.machine, sizeof(info.arch) - 1);
        info.arch[sizeof(info.arch) - 1] = '\0';
    } else {
        strcpy(info.arch, "unknown");
    }
    
    // Статистика использования CPU
    FILE* stat = fopen("/proc/stat", "r");
    if (stat != NULL) {
        char line[256];
        int cpu_idx = 0;
        
        // Общая статистика
        if (fgets(line, sizeof(line), stat) != NULL) {
            unsigned long long user, nice, system, idle, iowait, irq, softirq, steal;
            
            if (sscanf(line, "cpu %llu %llu %llu %llu %llu %llu %llu %llu",
                       &user, &nice, &system, &idle, &iowait, &irq, &softirq, &steal) == 8) {
                
                unsigned long long idle_all = idle + iowait;
                unsigned long long total = user + nice + system + idle_all + irq + softirq + steal;
                
                if (cpu_stats.total > 0 && total > cpu_stats.total) {
                    unsigned long long total_diff = total - cpu_stats.total;
                    unsigned long long idle_diff = idle_all - cpu_stats.idle;
                    
                    if (total_diff > 0) {
                        info.total_usage = (int)((total_diff - idle_diff) * 100.0 / total_diff);
                        if (info.total_usage < 0) info.total_usage = 0;
                        if (info.total_usage > 100) info.total_usage = 100;
                    }
                }
                
                cpu_stats.total = total;
                cpu_stats.idle = idle_all;
            }
        }
        
        // Статистика по ядрам
        while (fgets(line, sizeof(line), stat) != NULL && cpu_idx < info.cores_total) {
            if (strncmp(line, "cpu", 3) == 0 && line[3] >= '0' && line[3] <= '9') {
                unsigned long long user, nice, system, idle, iowait, irq, softirq, steal;
                int core_num;
                
                if (sscanf(line, "cpu%d %llu %llu %llu %llu %llu %llu %llu %llu",
                           &core_num, &user, &nice, &system, &idle, &iowait,
                           &irq, &softirq, &steal) == 9 && core_num < MAX_CPUS) {
                    
                    unsigned long long idle_all = idle + iowait;
                    unsigned long long total = user + nice + system + idle_all + irq + softirq + steal;
                    
                    if (cpu_stats.per_cpu[core_num] > 0 && total > cpu_stats.per_cpu[core_num]) {
                        unsigned long long total_diff = total - cpu_stats.per_cpu[core_num];
                        unsigned long long idle_diff = idle_all - cpu_stats.idle_per_cpu[core_num];
                        
                        if (total_diff > 0) {
                            int usage = (int)((total_diff - idle_diff) * 100.0 / total_diff);
                            if (usage < 0) usage = 0;
                            if (usage > 100) usage = 100;
                            info.cpu_usage[core_num] = usage;
                        }
                    }
                    
                    cpu_stats.per_cpu[core_num] = total;
                    cpu_stats.idle_per_cpu[core_num] = idle_all;
                    cpu_idx++;
                }
            }
        }
        fclose(stat);
    } else {
        if (errno == EACCES || errno == EPERM) {
            info.total_usage = -1; // Признак того, что нужны права su
        }
    }
    
    // Если не удалось получить загрузку, ставим значение по умолчанию
    if (info.total_usage == 0) {
        info.total_usage = 1;
    }
    
    return info;
}

// ==================== MEMORY INFO ====================

MemoryInfo get_memory_info(void) {
    MemoryInfo info;
    memset(&info, 0, sizeof(info));
    
    struct sysinfo si;
    if (sysinfo(&si) == 0) {
        info.total = (unsigned long long)si.totalram * si.mem_unit;
        info.free = (unsigned long long)si.freeram * si.mem_unit;
        info.used = info.total - info.free;
        
        if (info.total > 0) {
            info.percent = (int)((info.used * 100) / info.total);
        }
        
        info.swap_total = (unsigned long long)si.totalswap * si.mem_unit;
        info.swap_free = (unsigned long long)si.freeswap * si.mem_unit;
        
        if (info.swap_total > 0) {
            info.swap_used = info.swap_total - info.swap_free;
            info.swap_percent = (int)((info.swap_used * 100) / info.swap_total);
        }
    }
    
    size_t dummy_size = 0;
    char* meminfo = safe_read_file("/proc/meminfo", &dummy_size);
    if (meminfo != NULL) {
        char* line = meminfo;
        char* nl;
        
        while ((nl = strchr(line, '\n')) != NULL) {
            *nl = '\0';
            
            if (strncmp(line, "MemAvailable:", 13) == 0) {
                unsigned long long kb;
                if (sscanf(line + 13, "%llu", &kb) == 1) {
                    info.available = kb * 1024;
                }
            } else if (strncmp(line, "Cached:", 7) == 0) {
                unsigned long long kb;
                if (sscanf(line + 7, "%llu", &kb) == 1) {
                    info.cached = kb * 1024;
                }
            } else if (strncmp(line, "Buffers:", 8) == 0) {
                unsigned long long kb;
                if (sscanf(line + 8, "%llu", &kb) == 1) {
                    info.buffers = kb * 1024;
                }
            }
            
            line = nl + 1;
        }
        free(meminfo);
    }
    
    return info;
}

// ==================== DISK INFO ====================

DiskInfo* get_disk_info(int* count) {
    static DiskInfo disks[MAX_DISKS];
    *count = 0;
    
    if (count == NULL) return disks;
    
    FILE* mounts = fopen("/proc/mounts", "r");
    if (mounts == NULL) return disks;
    
    char line[512];
    while (fgets(line, sizeof(line), mounts) != NULL && *count < MAX_DISKS) {
        char device[256], mount[256], fs[32];
        
        if (sscanf(line, "%255s %255s %31s", device, mount, fs) == 3) {
            // Фильтруем только реальные диски и общие точки монтирования
            // Добавляем /data, /storage, /mnt, /proc/mounts может иметь разные пути
            if (strstr(device, "/dev/block") != NULL || 
                strstr(mount, "/storage") != NULL || 
                strstr(mount, "/sdcard") != NULL ||
                strstr(mount, "/data") != NULL || // Добавлено /data
                strstr(mount, "/mnt") != NULL ||  // Добавлено /mnt
                strstr(device, "/dev/mmcblk") != NULL ||
                strstr(device, "/dev/sd") != NULL ||
                strcmp(mount, "/") == 0) { // Всегда включаем корневую файловую систему
                
                DiskInfo* d = &disks[*count];
                memset(d, 0, sizeof(DiskInfo));
                
                strncpy(d->mount_point, mount, sizeof(d->mount_point) - 1);
                d->mount_point[sizeof(d->mount_point) - 1] = '\0';
                
                strncpy(d->filesystem, fs, sizeof(d->filesystem) - 1);
                d->filesystem[sizeof(d->filesystem) - 1] = '\0';
                
                struct statvfs vfs;
                if (statvfs(mount, &vfs) == 0) {
                    unsigned long long block_size = vfs.f_frsize;
                    d->total = (unsigned long long)vfs.f_blocks * block_size;
                    d->free = (unsigned long long)vfs.f_bavail * block_size;
                    d->used = d->total - d->free;
                    
                    if (d->total > 0) {
                        d->percent = (int)((d->used * 100) / d->total);
                    }
                } else {
                    // Если statvfs не удалось, ставим значения по умолчанию
                    d->total = 0;
                    d->free = 0;
                    d->used = 0;
                    d->percent = 0;
                }
                
                (*count)++;
            }
        }
    }
    fclose(mounts);
    
    // Если после всего не нашли ни одного диска, возвращаем 0
    if (*count == 0) {
        // Возможно, стоит добавить сюда заглушку или сообщение об ошибке,
        // если /proc/mounts пуст или не содержит ожидаемых данных.
        // Но для начала, просто вернем 0.
    }
    
    return disks;
}

// ==================== BATTERY INFO ====================

/**
 * Преобразование строки статуса в enum BatteryStatus
 */
static BatteryStatus status_string_to_enum(const char* status_str) {
    if (status_str == NULL) return BATTERY_STATUS_UNKNOWN;
    
    if (strstr(status_str, "Charging") != NULL) {
        return BATTERY_STATUS_CHARGING;
    } else if (strstr(status_str, "Discharging") != NULL) {
        return BATTERY_STATUS_DISCHARGING;
    } else if (strstr(status_str, "Full") != NULL) {
        return BATTERY_STATUS_FULL;
    } else if (strstr(status_str, "Empty") != NULL) {
        return BATTERY_STATUS_EMPTY;
    } else if (strstr(status_str, "Not charging") != NULL) {
        return BATTERY_STATUS_NOT_CHARGING;
    } else if (strstr(status_str, "Good") != NULL) {
        return BATTERY_STATUS_HEALTH_GOOD;
    } else if (strstr(status_str, "Warning") != NULL) {
        return BATTERY_STATUS_HEALTH_WARN;
    } else if (strstr(status_str, "Bad") != NULL) {
        return BATTERY_STATUS_HEALTH_BAD;
    }
    
    return BATTERY_STATUS_UNKNOWN;
}

/**
 * Преобразование enum BatteryStatus в строку
 */
static const char* status_enum_to_string(BatteryStatus status) {
    switch (status) {
        case BATTERY_STATUS_CHARGING: return "Charging";
        case BATTERY_STATUS_DISCHARGING: return "Discharging";
        case BATTERY_STATUS_FULL: return "Full";
        case BATTERY_STATUS_EMPTY: return "Empty";
        case BATTERY_STATUS_NOT_CHARGING: return "Not charging";
        case BATTERY_STATUS_HEALTH_GOOD: return "Good";
        case BATTERY_STATUS_HEALTH_WARN: return "Warning";
        case BATTERY_STATUS_HEALTH_BAD: return "Bad";
        default: return "Unknown";
    }
}

BatteryInfo get_battery_info(void) {
    BatteryInfo info;
    memset(&info, 0, sizeof(info));
    
    const char* battery_path = "/sys/class/power_supply/battery";
    const char* alt_battery_path = "/sys/class/power_supply/BAT0";
    char path[MAX_PATH];
    
    if (!safe_file_exists("/sys/class/power_supply/battery") &&
        !safe_file_exists("/sys/class/power_supply/BAT0")) {
        return info;
    }
    
    // Уровень заряда
    snprintf(path, sizeof(path), "%s/capacity", battery_path);
    info.level = safe_read_long(path);
    
    if (info.level <= 0) {
        snprintf(path, sizeof(path), "%s/capacity", alt_battery_path);
        info.level = safe_read_long(path);
        if (info.level > 0) {
            battery_path = alt_battery_path;
        }
    }
    
    // Напряжение
    snprintf(path, sizeof(path), "%s/voltage_now", battery_path);
    long voltage = safe_read_long(path);
    info.voltage = (voltage > 0) ? voltage / 1000 : 0;
    
    // Ток
    snprintf(path, sizeof(path), "%s/current_now", battery_path);
    long current = safe_read_long(path);
    info.current = (current != 0) ? current / 1000 : 0;
    
    // Температура
    snprintf(path, sizeof(path), "%s/temp", battery_path);
    long temp = safe_read_long(path);
    info.temperature = (temp > 0) ? temp / 10 : 0;
    
    // Технология
    snprintf(path, sizeof(path), "%s/technology", battery_path);
    size_t dummy_size = 0;
    char* tech = safe_read_file(path, &dummy_size);
    if (tech != NULL) {
        strncpy(info.technology, tech, sizeof(info.technology) - 1);
        info.technology[sizeof(info.technology) - 1] = '\0';
        free(tech);
    } else {
        strcpy(info.technology, "Unknown");
    }
    
    // Здоровье
    snprintf(path, sizeof(path), "%s/health", battery_path);
    char* health = safe_read_file(path, &dummy_size);
    if (health != NULL) {
        strncpy(info.health, health, sizeof(info.health) - 1);
        info.health[sizeof(info.health) - 1] = '\0';
        free(health);
    } else {
        strcpy(info.health, "Unknown");
    }
    
    // Статус (как строка и как enum)
    snprintf(path, sizeof(path), "%s/status", battery_path);
    char* status_str = safe_read_file(path, &dummy_size);
    
    if (status_str != NULL) {
        // Сохраняем enum статуса
        info.status = status_string_to_enum(status_str);
        free(status_str);
    } else {
        info.status = BATTERY_STATUS_UNKNOWN;
    }
    
    // Ёмкость
    snprintf(path, sizeof(path), "%s/charge_full", battery_path);
    long charge_full = safe_read_long(path);
    info.capacity = (charge_full > 0) ? charge_full / 1000 : 0;
    
    // Оставшееся время (используем enum для проверки)
    if (info.current != 0 && info.capacity > 0 && info.level > 0) {
        int remaining_mah = info.capacity * info.level / 100;
        
        if (info.status == BATTERY_STATUS_CHARGING) {
            info.time_remaining = (info.capacity - remaining_mah) * 3600 / abs(info.current);
        } else if (info.status == BATTERY_STATUS_DISCHARGING) {
            info.time_remaining = remaining_mah * 3600 / abs(info.current);
        }
        
        if (info.time_remaining < 0) info.time_remaining = 0;
    }
    
    return info;
}

/**
 * Получение строки статуса батареи (для совместимости с main.c)
 */
const char* get_battery_status_string(BatteryStatus status) {
    return status_enum_to_string(status);
}

// ==================== ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ ====================

int get_battery_level(void) {
    BatteryInfo info = get_battery_info();
    return info.level;
}

int is_battery_charging(void) {
    BatteryInfo info = get_battery_info();
    return (info.status == BATTERY_STATUS_CHARGING);
}

int is_battery_present(void) {
    return (safe_file_exists("/sys/class/power_supply/battery") ||
            safe_file_exists("/sys/class/power_supply/BAT0"));
}

float get_battery_temperature(void) {
    BatteryInfo info = get_battery_info();
    return (float)info.temperature;
}

int get_cpu_count(void) {
    return sysconf(_SC_NPROCESSORS_CONF);
}

int get_online_cpu_count(void) {
    return sysconf(_SC_NPROCESSORS_ONLN);
}

unsigned long long get_total_ram(void) {
    struct sysinfo si;
    if (sysinfo(&si) == 0) {
        return (unsigned long long)si.totalram * si.mem_unit;
    }
    return 0;
}

unsigned long long get_free_ram(void) {
    struct sysinfo si;
    if (sysinfo(&si) == 0) {
        return (unsigned long long)si.freeram * si.mem_unit;
    }
    return 0;
}

// ==================== КОНЕЦ ФАЙЛА ====================
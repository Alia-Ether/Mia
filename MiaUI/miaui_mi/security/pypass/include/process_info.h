//╔═════════════════════════════╗                       
//║  Link: t.me/FrontendVSCode                       ║                         
//║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║    
//║  lang: C                                         ║                     
//║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║                      
//║  build:3.10.15                                   ║
//║  files: process_info.h                           ║    
//╚═════════════════════════════╝



#ifndef PROCESS_INFO_H
#define PROCESS_INFO_H

// ==================== ЗАЩИТА ОТ ПОВТОРНОГО ВКЛЮЧЕНИЯ ====================
#ifdef PROCESS_INFO_H_INCLUDED
#error "process_info.h включен дважды!"
#endif
#define PROCESS_INFO_H_INCLUDED

// ==================== СТАНДАРТНЫЕ БИБЛИОТЕКИ ====================
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <ctype.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/sysinfo.h>
#include <sys/resource.h>
#include <sys/time.h>
#include <time.h>
#include <pwd.h>
#include <grp.h>
#include <signal.h>
#include <errno.h>

// ==================== ОБЩИЕ ОПРЕДЕЛЕНИЯ ====================
#ifndef MAX_PROCESSES
#define MAX_PROCESSES 128
#endif

#ifndef MAX_NAME
#define MAX_NAME 64
#endif

#ifndef MAX_PATH
#define MAX_PATH 256
#endif

#ifndef MAX_FILES
#define MAX_FILES 256
#endif

#ifndef MAX_ENV
#define MAX_ENV 128
#endif

#ifndef MAX_ARGS
#define MAX_ARGS 64
#endif

// ==================== СТРУКТУРА ДЛЯ main.c ====================
typedef struct {
    int pid;                                // ID процесса
    char name[MAX_NAME];                    // имя процесса
    float cpu;                              // CPU процент
    unsigned long mem;                      // память (bytes)
    char state;                             // состояние (R, S, D, Z, T)
    int priority;                           // приоритет
    int threads;                            // количество потоков
    time_t start_time;                       // время запуска
} ProcessInfo;

// ==================== ОСТАЛЬНЫЕ СТРУКТУРЫ (ДЛЯ РАСШИРЕННОЙ ИНФОРМАЦИИ) ====================

// Состояния процесса
typedef enum {
    PROC_STATE_UNKNOWN = 0,
    PROC_STATE_RUNNING = 'R',
    PROC_STATE_SLEEPING = 'S',
    PROC_STATE_DISK_SLEEP = 'D',
    PROC_STATE_STOPPED = 'T',
    PROC_STATE_TRACING = 't',
    PROC_STATE_ZOMBIE = 'Z',
    PROC_STATE_DEAD = 'X',
    PROC_STATE_WAKE_KILL = 'K',
    PROC_STATE_WAKING = 'W',
    PROC_STATE_PARKED = 'P'
} ProcessState;

// Приоритеты процесса
typedef struct {
    int priority;                           // приоритет
    int nice;                               // nice значение
    int rt_priority;                        // realtime приоритет
    int policy;                             // политика планирования
    char policy_str[32];                     // строковое представление
} ProcessPriority;

// Временные характеристики
typedef struct {
    unsigned long long utime;                // время в user mode
    unsigned long long stime;                // время в kernel mode
    unsigned long long cutime;               // время детей в user mode
    unsigned long long cstime;               // время детей в kernel mode
    unsigned long long starttime;            // время старта (в тиках)
    unsigned long long total_time;           // общее время CPU
    float cpu_usage_percent;                 // процент CPU
    float cpu_time_seconds;                  // время CPU в секундах
    float cpu_time_total;                     // общее время с детьми
} ProcessTime;

// Память процесса
typedef struct {
    unsigned long size;                      // размер виртуальной памяти
    unsigned long resident;                   // размер физической памяти
    unsigned long shared;                     // разделяемая память
    unsigned long text;                       // код
    unsigned long data;                        // данные
    unsigned long library;                     // библиотеки
    unsigned long dirty;                       // грязные страницы
    unsigned long rss;                         // resident set size
    unsigned long vsize;                       // virtual size
    unsigned long swap;                        // swap
    unsigned long rss_anon;                    // анонимная память
    unsigned long rss_file;                    // файловая память
    unsigned long rss_shmem;                   // разделяемая память
    unsigned long vmlck;                       // заблокированная память
    float mem_percent;                         // процент от общей памяти
} ProcessMemory;

// Дисковая активность
typedef struct {
    unsigned long long read_bytes;             // байт прочитано
    unsigned long long write_bytes;            // байт записано
    unsigned long long cancelled_write_bytes;  // отменённая запись
    unsigned long long read_chars;             // символов прочитано
    unsigned long long write_chars;            // символов записано
    unsigned long long read_syscalls;          // системных вызовов на чтение
    unsigned long long write_syscalls;         // системных вызовов на запись
    float read_speed;                          // скорость чтения (KB/s)
    float write_speed;                         // скорость записи (KB/s)
} ProcessIO;

// Сетевая активность
typedef struct {
    int inodes[MAX_PROCESSES];                 // inode сокетов
    int socket_count;                          // количество сокетов
    unsigned long long rx_bytes;               // байт принято
    unsigned long long tx_bytes;               // байт отправлено
    unsigned long long rx_packets;              // пакетов принято
    unsigned long long tx_packets;              // пакетов отправлено
    int tcp_connections;                        // TCP соединений
    int udp_sockets;                            // UDP сокетов
    int unix_sockets;                           // Unix сокетов
    int listening_ports;                         // слушающих портов
    char connections[32][64];                    // список соединений
} ProcessNetwork;

// Детальная информация о процессе
typedef struct {
    int pid;                                    // PID
    int ppid;                                   // родительский PID
    int pgid;                                   // группа процессов
    int sid;                                    // сессия
    int tgid;                                   // thread group ID
    char name[MAX_NAME];                        // имя процесса
    char comm[MAX_NAME];                        // командная строка (short)
    char cmdline[MAX_PATH];                     // полная командная строка
    char exe_path[MAX_PATH];                    // путь к исполняемому файлу
    char cwd[MAX_PATH];                         // текущая рабочая директория
    char root[MAX_PATH];                         // корневая директория
    
    uid_t uid;                                  // пользователь ID
    gid_t gid;                                   // группа ID
    char user[MAX_NAME];                         // имя пользователя
    char group[MAX_NAME];                        // имя группы
    
    ProcessState state;                          // состояние
    char state_char;                             // символ состояния
    ProcessPriority priority;                    // приоритет
    int processor;                                // процессор
    ProcessTime time;                             // время
    ProcessMemory memory;                         // память
    ProcessIO io;                                 // дисковая активность
    ProcessNetwork net;                           // сетевая активность
    
    int fd_count;                                 // количество открытых файлов
    char open_files[MAX_FILES][MAX_PATH];         // открытые файлы
    
    int thread_count;                             // количество потоков
    int thread_pids[MAX_PROCESSES];                // PID потоков
    
    unsigned long long minflt;                     // minor faults
    unsigned long long majflt;                     // major faults
    unsigned long long nvcsw;                      // voluntary context switches
    unsigned long long nivcsw;                     // non-voluntary context switches
    unsigned long long voluntary_ctxt_switches;    // добровольные переключения
    unsigned long long nonvoluntary_ctxt_switches; // недобровольные переключения
    
    time_t start_time;                             // время запуска (сек)
    time_t uptime;                                 // время работы (сек)
    char start_time_str[32];                       // строка времени запуска
    char uptime_str[32];                            // строка времени работы
    
    // Дополнительно
    int tty;                                       // терминал
    int tty_pgrp;                                  // группа терминала
    int flags;                                     // флаги
    int exit_signal;                               // сигнал завершения
    int nice;                                      // nice значение
    int rtprio;                                    // реального времени приоритет
    int policy;                                    // политика планирования
    
    char env[MAX_ENV][MAX_PATH];                   // переменные окружения
    int env_count;                                  // количество переменных
} ProcessDetailedInfo;

// Процесс для топа (расширенный)
typedef struct {
    int pid;                                       // PID
    char name[MAX_NAME];                           // имя
    float cpu;                                     // CPU %
    float mem;                                      // MEM %
    unsigned long mem_bytes;                        // память в байтах
    int mem_percent;                                // процент памяти
    int threads;                                    // потоки
    ProcessState state;                             // состояние
    char state_char;                                // символ состояния
    char user[MAX_NAME];                            // пользователь
    float uptime;                                   // время работы (часы)
    float cpu_time;                                 // время CPU
    int priority;                                   // приоритет
    int nice;                                       // nice
    long rss;                                       // RSS
    long vsz;                                       // VSZ
    unsigned long long read_bytes;                  // прочитано байт
    unsigned long long write_bytes;                 // записано байт
} ProcessTopInfo;

// Статистика системы
typedef struct {
    int total_processes;                            // всего процессов
    int running_processes;                          // запущенных
    int sleeping_processes;                         // спящих
    int stopped_processes;                          // остановленных
    int zombie_processes;                           // зомби
    int dead_processes;                             // мёртвых
    int parked_processes;                           // припаркованных
    
    int total_threads;                              // всего потоков
    int kernel_threads;                             // потоков ядра
    
    float load_average_1min;                        // нагрузка 1 мин
    float load_average_5min;                        // нагрузка 5 мин
    float load_average_15min;                       // нагрузка 15 мин
    
    unsigned long long total_cpu_time;               // всего CPU времени
    unsigned long long total_memory;                 // всего памяти
    unsigned long long used_memory;                   // использовано памяти
    unsigned long long free_memory;                   // свободно памяти
    int memory_percent;                               // процент использования памяти
    
    unsigned long long total_swap;                    // всего swap
    unsigned long long used_swap;                     // использовано swap
    int swap_percent;                                 // процент swap
    
    int last_pid;                                     // последний PID
    time_t boot_time;                                 // время загрузки
    time_t current_time;                              // текущее время
} ProcessSystemStats;

// ==================== ПРОТОТИПЫ ФУНКЦИЙ ====================

#ifdef __cplusplus
extern "C" {
#endif

// ===== ОСНОВНЫЕ ФУНКЦИИ (то что нужно main.c) =====
int get_top_processes(ProcessInfo* procs, int max_count);
int get_top_processes_by_cpu(ProcessInfo* procs, int max_count);
int get_top_processes_by_mem(ProcessInfo* procs, int max_count);
int get_process_info(int pid, ProcessInfo* info);
int get_process_list(int* pids, int max_count);

// ===== Детальная информация =====
int get_process_detailed(int pid, ProcessDetailedInfo* info);
int get_process_cmdline(int pid, char* buffer, size_t size);
int get_process_exe_path(int pid, char* buffer, size_t size);
int get_process_cwd(int pid, char* buffer, size_t size);
int get_process_root(int pid, char* buffer, size_t size);
int get_process_env(int pid, char** env, int max_count);
int get_process_open_files(int pid, char** files, int max_count);
int get_process_threads(int pid, int* threads, int max_count);
int get_process_connections(int pid, char connections[][64], int max_count);

// ===== Статистика =====
ProcessSystemStats get_system_stats(void);
int get_process_count(void);
int get_thread_count(void);
float get_load_average(void);
float get_load_average_1(void);
float get_load_average_5(void);
float get_load_average_15(void);
int get_process_count_by_state(ProcessState state);
int get_running_process_count(void);
int get_zombie_process_count(void);

// ===== Проверки =====
int process_exists(int pid);
int is_process_running(int pid);
int is_process_zombie(int pid);
int is_process_stopped(int pid);
int is_process_sleeping(int pid);
int get_process_state(int pid, ProcessState* state);
char get_process_state_char(int pid);

// ===== Владелец =====
int get_process_owner(int pid, char* user, size_t size);
int get_process_group(int pid, char* group, size_t size);
int get_process_uid(int pid, uid_t* uid);
int get_process_gid(int pid, gid_t* gid);
int get_process_priority(int pid, int* priority);
int get_process_nice(int pid, int* nice);

// ===== Поиск =====
int find_process_by_name(const char* name, int* pids, int max_count);
int find_process_by_user(const char* user, int* pids, int max_count);
int find_process_by_uid(uid_t uid, int* pids, int max_count);
int find_process_by_state(ProcessState state, int* pids, int max_count);
int find_process_by_exe(const char* exe_path, int* pids, int max_count);
int find_process_by_port(int port, int* pids, int max_count);
int find_process_by_connection(const char* remote_ip, int port, int* pids, int max_count);

// ===== Управление =====
int kill_process(int pid, int signal);
int pause_process(int pid);
int resume_process(int pid);
int set_process_priority(int pid, int priority);
int set_process_nice(int pid, int nice);
int set_process_affinity(int pid, int cpu_mask);
int set_process_name(int pid, const char* name);

// ===== Мониторинг =====
int watch_process(int pid, ProcessDetailedInfo* info, int interval_ms);
int watch_top_processes(ProcessTopInfo* procs, int max_count, int interval_ms);
int watch_process_cpu(int pid, float* cpu_usage, int interval_ms);
int watch_process_mem(int pid, unsigned long* mem_usage, int interval_ms);
int watch_process_io(int pid, ProcessIO* io, int interval_ms);

// ===== Форматирование =====
const char* process_state_string(ProcessState state);
const char* process_state_char_string(char state);
const char* process_priority_policy_string(int policy);
void format_process_info(const ProcessDetailedInfo* info, char* buffer, size_t size);
void format_process_top(const ProcessTopInfo* info, char* buffer, size_t size);
void format_system_stats(const ProcessSystemStats* stats, char* buffer, size_t size);
void format_basic_process(const ProcessInfo* info, char* buffer, size_t size);
void format_process_memory(const ProcessMemory* mem, char* buffer, size_t size);
void format_process_io(const ProcessIO* io, char* buffer, size_t size);
void format_process_time(const ProcessTime* time, char* buffer, size_t size);

// ===== Утилиты =====
int get_process_tree(int pid, int* pids, int max_count);
int get_process_children(int pid, int* pids, int max_count);
int get_process_parent(int pid, int* ppid);
int get_process_stats_snapshot(ProcessTopInfo* procs, int max_count);
void sort_processes_by_cpu(ProcessTopInfo* procs, int count);
void sort_processes_by_mem(ProcessTopInfo* procs, int count);
void sort_processes_by_pid(ProcessTopInfo* procs, int count);

// ===== CPU функции =====
float get_process_cpu_percent(int pid);
float get_process_cpu_time(int pid);
int get_process_cpu_affinity(int pid, unsigned long* mask);
int get_process_last_cpu(int pid);

// ===== Память функции =====
unsigned long get_process_memory_rss(int pid);
unsigned long get_process_memory_vsz(int pid);
float get_process_memory_percent(int pid);
int get_process_memory_maps(int pid, char** maps, int max_count);

// ===== Диск функции =====
int get_process_io_stats(int pid, ProcessIO* io);
int get_process_io_counters(int pid, unsigned long long* rchar, 
                           unsigned long long* wchar, unsigned long long* syscr,
                           unsigned long long* syscw, unsigned long long* read_bytes,
                           unsigned long long* write_bytes);

// ===== Сеть функции =====
int get_process_sockets(int pid, int* sockets, int max_count);
int get_process_ports(int pid, int* ports, int max_count);
int get_process_connections_detailed(int pid, char connections[][128], int max_count);

#ifdef __cplusplus
}
#endif

#endif // PROCESS_INFO_H
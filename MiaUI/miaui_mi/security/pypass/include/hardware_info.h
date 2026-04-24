//╔═════════════════════════════╗                       
//║  Link: t.me/FrontendVSCode                       ║                         
//║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║    
//║  lang: C                                         ║                     
//║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║                      
//║  build:3.10.15                                   ║
//║  files: hardware_info.h                          ║    
//╚═════════════════════════════╝


#ifndef HARDWARE_INFO_H
#define HARDWARE_INFO_H

// ==================== ЗАЩИТА ОТ ПОВТОРНОГО ВКЛЮЧЕНИЯ ====================
#ifdef HARDWARE_INFO_H_INCLUDED
#error "hardware_info.h включен дважды!"
#endif
#define HARDWARE_INFO_H_INCLUDED

// ==================== СТАНДАРТНЫЕ БИБЛИОТЕКИ ====================
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/sysinfo.h>
#include <sys/utsname.h>
#include <sys/statvfs.h>
#include <dirent.h>
#include <time.h>
#include <stdint.h>
#include <limits.h>
#include <math.h>

// ==================== ОБЩИЕ ОПРЕДЕЛЕНИЯ ====================
#ifndef MAX_CPUS
#define MAX_CPUS 32
#endif

#ifndef MAX_NAME
#define MAX_NAME 128
#endif

#ifndef MAX_PATH
#define MAX_PATH 256
#endif

#ifndef MAX_PROCESSES
#define MAX_PROCESSES 64
#endif

#ifndef MAX_DISKS
#define MAX_DISKS 16
#endif

#ifndef MAX_GOVERNORS
#define MAX_GOVERNORS 8
#endif

// ==================== ТИПЫ ПРОЦЕССОРОВ ====================
typedef enum {
    CPU_UNKNOWN = 0,
    CPU_ARM,
    CPU_ARM64,
    CPU_X86,
    CPU_X86_64,
    CPU_MIPS,
    CPU_RISCV,
    CPU_PPC,
    CPU_SPARC,
    CPU_ALPHA,
    CPU_IA64
} CPUArch;

// ==================== ТИПЫ БАТАРЕЙ ====================
typedef enum {
    BATTERY_UNKNOWN = 0,
    BATTERY_LIION,
    BATTERY_LIPOLY,
    BATTERY_NIMH,
    BATTERY_NICD,
    BATTERY_LIFEPO4,
    BATTERY_LEAD_ACID,
    BATTERY_SILVER_OXIDE,
    BATTERY_ZINC_CARBON,
    BATTERY_ALKALINE
} BatteryType;

// ==================== СОСТОЯНИЯ БАТАРЕИ ====================
typedef enum {
    BATTERY_STATUS_UNKNOWN = 0,
    BATTERY_STATUS_CHARGING,
    BATTERY_STATUS_DISCHARGING,
    BATTERY_STATUS_FULL,
    BATTERY_STATUS_EMPTY,
    BATTERY_STATUS_NOT_CHARGING,
    BATTERY_STATUS_HEALTH_GOOD,
    BATTERY_STATUS_HEALTH_WARN,
    BATTERY_STATUS_HEALTH_BAD
} BatteryStatus;

// ==================== ИСТОЧНИКИ ПИТАНИЯ ====================
typedef enum {
    POWER_SOURCE_UNKNOWN = 0,
    POWER_SOURCE_BATTERY,
    POWER_SOURCE_AC,
    POWER_SOURCE_USB,
    POWER_SOURCE_WIRELESS
} PowerSource;

// ==================== ИНФОРМАЦИЯ О CPU ====================
typedef struct {
    int cores_total;
    int cores_online;
    int cores_present;
    int cores_offline;
    float freq_cur[MAX_CPUS];
    float freq_min[MAX_CPUS];
    float freq_max[MAX_CPUS];
    int cpu_usage[MAX_CPUS];
    int total_usage;
    float temperature;
    float temp_min;
    float temp_max;
    float temp_crit;
    char model[MAX_NAME];
    char hardware[MAX_NAME];
    char arch[MAX_NAME];
    CPUArch arch_type;
    char features[512];
    int has_neon;
    int has_sse;
    int has_sse2;
    int has_sse3;
    int has_sse4;
    int has_avx;
    int has_avx2;
    int has_vfp;
    int has_vfpv3;
    int has_vfpv4;
    int has_fp;
    int has_asimd;
    char governor[MAX_NAME];
    char available_governors[MAX_GOVERNORS][MAX_NAME];
    int governor_count;
    unsigned long long bogo_mips;
    unsigned long long cpu_mhz;
    unsigned long long cpu_mhz_max;
    unsigned long long cpu_mhz_min;
    int cpu_family;
    int cpu_model;
    int cpu_stepping;
    char cpu_revision[32];
    int cache_size_l1d;
    int cache_size_l1i;
    int cache_size_l2;
    int cache_size_l3;
} CPUInfo;

// ==================== ИНФОРМАЦИЯ О ПАМЯТИ ====================
typedef struct {
    unsigned long long total;
    unsigned long long free;
    unsigned long long available;
    unsigned long long used;
    unsigned long long cached;
    unsigned long long buffers;
    unsigned long long active;
    unsigned long long inactive;
    unsigned long long dirty;
    unsigned long long mapped;
    unsigned long long slab;
    unsigned long long kernel_stack;
    unsigned long long page_tables;
    unsigned long long shmem;
    unsigned long long sreclaimable;
    unsigned long long sunreclaim;
    unsigned long long anon_pages;
    unsigned long long file_pages;
    int percent;
    
    unsigned long long swap_total;
    unsigned long long swap_free;
    unsigned long long swap_used;
    unsigned long long swap_cached;
    unsigned long long swap_anon;
    int swap_percent;
    
    unsigned long long huge_pages_total;
    unsigned long long huge_pages_free;
    unsigned long long huge_pages_size;
    unsigned long long huge_pages_rsvd;
    unsigned long long huge_pages_surp;
    
    unsigned long long low_total;
    unsigned long long low_free;
    unsigned long long high_total;
    unsigned long long high_free;
} MemoryInfo;

// ==================== ИНФОРМАЦИЯ О ДИСКЕ ====================
typedef struct {
    char mount_point[MAX_PATH];
    char device[MAX_PATH];
    char filesystem[32];
    char mount_options[256];
    unsigned long long total;
    unsigned long long free;
    unsigned long long used;
    unsigned long long avail;
    unsigned long long used_by_system;
    int percent;
    unsigned long long total_inodes;
    unsigned long long free_inodes;
    unsigned long long used_inodes;
    int inode_percent;
    unsigned long long block_size;
    unsigned long long total_blocks;
    unsigned long long free_blocks;
    unsigned long long used_blocks;
    int is_readonly;
    int is_removable;
    int is_loop;
    int is_root;
    char uuid[64];
    char label[128];
    char model[64];
    char vendor[64];
    char type[32];
} DiskInfo;

// ==================== ИНФОРМАЦИЯ О БАТАРЕЕ ====================
typedef struct {
    int level;
    int voltage;
    int voltage_min;
    int voltage_max;
    int voltage_now;
    int current;
    int current_avg;
    int current_now;
    int power;
    int power_now;
    int temperature;
    int capacity;
    int capacity_full;
    int capacity_design;
    int capacity_level;
    char technology[32];
    BatteryType tech_type;
    BatteryStatus status;
    char health[32];
    char manufacturer[64];
    char model_name[64];
    char serial[64];
    int time_remaining;
    int time_full;
    int time_empty;
    int cycle_count;
    int temp;
    int charge_now;
    int charge_full;
    int charge_full_design;
    int energy_now;
    int energy_full;
    int energy_full_design;
    int power_avg;
    int present;
    int charging_source;
    int charge_type;
    int charge_current;
    int charge_voltage;
    int charge_control_limit;
    int charge_control_limit_max;
    int status_int;
} BatteryInfo;

// ==================== ИНФОРМАЦИЯ О ПИТАНИИ ====================
typedef struct {
    int usb_present;
    int ac_present;
    int wireless_present;
    PowerSource charging_source;
    int charge_type;
    int charge_current;
    int charge_current_max;
    int charge_voltage;
    int charge_voltage_max;
    int input_current;
    int input_voltage;
    int power_supply_count;
    int power_supply_online;
    int mains_present;
    int battery_present;
    int ups_present;
} PowerInfo;

// ==================== ИНФОРМАЦИЯ О ТЕМПЕРАТУРЕ ====================
typedef struct {
    float cpu_temp;
    float gpu_temp;
    float battery_temp;
    float ambient_temp;
    float skin_temp;
    float soc_temp;
    float pmic_temp;
    int thermal_zones;
    float zone_temps[16];
    char zone_names[16][32];
} ThermalInfo;

// ==================== ИНФОРМАЦИЯ О ЧАСТОТЕ ====================
typedef struct {
    float cpu_freq;
    float gpu_freq;
    float ddr_freq;
    float bus_freq;
    int cpu_scaling;
    int gpu_scaling;
} FrequencyInfo;

// ==================== ПРОТОТИПЫ ФУНКЦИЙ ====================

#ifdef __cplusplus
extern "C" {
#endif

// ===== Основные функции =====
CPUInfo get_cpu_info(void);
MemoryInfo get_memory_info(void);
DiskInfo* get_disk_info(int* count);
BatteryInfo get_battery_info(void);
PowerInfo get_power_info(void);
ThermalInfo get_thermal_info(void);
FrequencyInfo get_frequency_info(void);

// ===== Детальные функции =====
int get_cpu_usage_per_core(int* usage, int max_cores);
int get_cpu_frequencies(float* freqs, int max_cores);
int get_cpu_temperature(float* temp, int* zone_count);
int get_disk_io_stats(unsigned long long* read_bytes, unsigned long long* write_bytes);

// ===== Преобразования =====
const char* get_cpu_arch_string(CPUArch arch);
const char* get_battery_type_string(BatteryType type);
const char* get_battery_status_string(BatteryStatus status);
const char* get_power_source_string(PowerSource source);
CPUArch get_cpu_arch_from_string(const char* arch_str);

// ===== Форматирование =====
void format_cpu_info(const CPUInfo* cpu, char* buffer, size_t buffer_size);
void format_cpu_detailed(const CPUInfo* cpu, char* buffer, size_t buffer_size);
void format_memory_info(const MemoryInfo* mem, char* buffer, size_t buffer_size);
void format_disk_info(const DiskInfo* disk, char* buffer, size_t buffer_size);
void format_battery_info(const BatteryInfo* bat, char* buffer, size_t buffer_size);
void format_power_info(const PowerInfo* power, char* buffer, size_t buffer_size);
void format_thermal_info(const ThermalInfo* thermal, char* buffer, size_t buffer_size);

// ===== Получение простых значений =====
int get_cpu_count(void);
int get_online_cpu_count(void);
int get_cpu_usage_total(void);
unsigned long long get_total_ram(void);
unsigned long long get_free_ram(void);
unsigned long long get_available_ram(void);
int get_battery_level(void);
int is_battery_charging(void);
int is_battery_present(void);
float get_cpu_temperature_avg(void);
float get_battery_temperature(void);

// ===== Управление мониторингом =====
void init_hardware_monitor(void);
void update_hardware_stats(void);
void reset_hardware_stats(void);
void start_hardware_monitoring(int interval_ms);
void stop_hardware_monitoring(void);

// ===== Статистика =====
int get_disk_count(void);
unsigned long long get_total_disk_space(void);
unsigned long long get_free_disk_space(void);
int get_swap_percent(void);
float get_average_cpu_freq(void);

// ===== Проверки =====
int has_battery(void);
int has_thermal_sensors(void);
int has_frequency_scaling(void);
int has_governor(const char* governor);

#ifdef __cplusplus
}
#endif

#endif // HARDWARE_INFO_H
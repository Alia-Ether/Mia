//╔═════════════════════════════╗                       
//║  Link: t.me/FrontendVSCode                       ║                         
//║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║    
//║  lang: C                                         ║                     
//║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║                      
//║  build:3.10.15                                   ║
//║  files: system_info.h                            ║    
//╚═════════════════════════════╝

#ifndef SYSTEM_INFO_H
#define SYSTEM_INFO_H

// ==================== СТАНДАРТНЫЕ БИБЛИОТЕКИ ====================
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <sys/utsname.h>
#include <sys/sysinfo.h>
#include <pwd.h>
#include <grp.h>

// ==================== ПОДКЛЮЧАЕМ ОБЩИЕ ОПРЕДЕЛЕНИЯ ====================
#include "common.h"

// ==================== ТИПЫ СБОРОК ====================
typedef enum {
    BUILD_TYPE_UNKNOWN = 0,
    BUILD_TYPE_USER,
    BUILD_TYPE_USERDEBUG,
    BUILD_TYPE_ENG,
    BUILD_TYPE_TEST,
    BUILD_TYPE_DEV,
    BUILD_TYPE_SHIP,
    BUILD_TYPE_OTA
} BuildType;

// ==================== СОСТОЯНИЯ БЕЗОПАСНОСТИ ====================
typedef enum {
    SEC_STATE_UNKNOWN = 0,
    SEC_STATE_LOCKED,
    SEC_STATE_UNLOCKED,
    SEC_STATE_ENGINEERING,
    SEC_STATE_VERIFIED,
    SEC_STATE_ORANGE,
    SEC_STATE_YELLOW,
    SEC_STATE_GREEN,
    SEC_STATE_RED
} SecurityState;

// ⚠️ DeviceType УЖЕ ОПРЕДЕЛЁН В common.h, НЕ ДУБЛИРУЕМ!

// ==================== СОСТОЯНИЯ ROOT ====================
typedef enum {
    ROOT_UNKNOWN = 0,
    ROOT_NONE,
    ROOT_MAGISK,
    ROOT_SUPERSU,
    ROOT_KERNELSU,
    ROOT_OTHER
} RootType;

// ==================== РАСШИРЕННАЯ ИНФОРМАЦИЯ ОБ УСТРОЙСТВЕ ====================
typedef struct {
    // Основная информация
    char manufacturer[MAX_STR];
    char brand[MAX_STR];
    char model[MAX_STR];
    char name[MAX_STR];
    char device[MAX_STR];
    char product[MAX_STR];
    char hardware[MAX_STR];
    char platform[MAX_STR];
    char board[MAX_STR];
    char bootloader[MAX_STR];
    char radio[MAX_STR];
    
    // Версии
    char android_version[MAX_STR];
    char android_release[MAX_STR];
    int sdk;
    int sdk_int;
    int preview_sdk;
    int security_patch_day;
    int security_patch_month;
    int security_patch_year;
    char security_patch[MAX_STR];
    char baseband[MAX_STR];
    char kernel_version[MAX_STR];
    char kernel_release[MAX_STR];
    char kernel_arch[MAX_STR];
    
    // Сборка
    char build_id[MAX_STR];
    char build_date[MAX_STR];
    char build_time[MAX_STR];
    char build_type[MAX_STR];
    BuildType build_type_enum;
    char build_tags[MAX_STR];
    char build_user[MAX_STR];
    char build_host[MAX_STR];
    char build_version_sdk[MAX_STR];
    char build_version_codename[MAX_STR];
    char build_version_incremental[MAX_STR];
    char build_version_release[MAX_STR];
    char build_version_release_or_codename[MAX_STR];
    char build_fingerprint[MAX_STR];
    char build_fingerprint_full[MAX_STR];
    char build_description[MAX_STR];
    char build_display_id[MAX_STR];
    char build_characteristics[MAX_STR];
    
    // Идентификаторы
    char serial[MAX_STR];
    char serialno[MAX_STR];
    char codename[MAX_STR];
    char incremental[MAX_STR];
    char description[MAX_STR];
    char display_id[MAX_STR];
    char unique_id[MAX_STR];
    char secure_id[MAX_STR];
    
    // Временные метки
    time_t build_timestamp;
    time_t build_date_utc;
    time_t first_boot;
    time_t last_boot;
    time_t current_time;
    
    // Безопасность
    SecurityState bootloader_state;
    SecurityState vbmeta_state;
    SecurityState verified_boot_state;
    int verified_boot;
    int dm_verity;
    int force_encrypted;
    int file_based_encryption;
    int full_disk_encryption;
    
    // Root
    int has_root;
    RootType root_type;
    char root_method[MAX_STR];
    char root_path[MAX_PATH];
    
    // SELinux
    int selinux_enabled;
    int selinux_enforced;
    char selinux_mode[32];
    char selinux_policy[MAX_STR];
    
    // Дополнительно
    char ab_update[MAX_STR];
    char dynamic_partitions[MAX_STR];
    char treble_enabled[MAX_STR];
    char vndk_version[MAX_STR];
    char apex_version[MAX_STR];
    char cpu_abi[MAX_STR];
    char cpu_abi2[MAX_STR];
    char cpu_abilist[MAX_STR];
    char cpu_abilist32[MAX_STR];
    char cpu_abilist64[MAX_STR];
    char zygote[MAX_STR];
    int is_64bit;
    int is_32bit;
    
    // Производитель
    char manufacturer_name[MAX_STR];
    char manufacturer_country[MAX_STR];
    char manufacturer_city[MAX_STR];
    char manufacturer_web[MAX_STR];
    
    // Тип устройства (используем DeviceType из common.h)
    DeviceType device_type;
    char device_type_str[MAX_STR];
    int is_phone;
    int is_tablet;
    int is_tv;
    int is_wearable;
    int is_automotive;
    
    // Информация о батарее
    int battery_present;
    int battery_capacity;
    char battery_technology[MAX_STR];
    
    // Сенсоры
    int has_fingerprint;
    int has_face_unlock;
    int has_iris_scanner;
    int has_heart_rate;
    int has_spo2;
    int has_barometer;
    int has_gyroscope;
    int has_accelerometer;
    int has_magnetometer;
    int has_light_sensor;
    int has_proximity;
    
    // Сеть
    int has_nfc;
    int has_5g;
    int has_wifi_6;
    int has_wifi_6e;
    int has_wifi_7;
    int has_bluetooth_5;
    int has_ble;
    int has_esim;
    int has_dual_sim;
    int has_ir_blaster;
    
    // Другое
    int has_notch;
    int has_punch_hole;
    int has_popup_camera;
    int has_under_display_camera;
    int has_under_display_fingerprint;
    int has_side_fingerprint;
    int has_face_id;
    int has_touch_id;
    int has_stereo_speakers;
    int has_headphone_jack;
    int has_sd_card;
    int has_wireless_charging;
    int has_fast_charging;
    int has_waterproof;
    int water_proof_rating;
} SystemInfo;

// ==================== РАСШИРЕННАЯ ИНФОРМАЦИЯ О ДИСПЛЕЕ ====================
typedef struct {
    // Разрешение
    int width;
    int height;
    int width_physical;
    int height_physical;
    float size_inches;
    float aspect_ratio;
    float pixel_count;
    
    // Плотность
    int dpi;
    int density_dpi;
    float scaled_density;
    float xdpi;
    float ydpi;
    float ppi;
    
    // Частота
    float refresh_rate;
    float min_refresh_rate;
    float max_refresh_rate;
    float touch_sampling_rate;
    
    // Яркость
    int brightness;
    int min_brightness;
    int max_brightness;
    int brightness_mode;
    int auto_brightness;
    int hbm_mode;
    int nits;
    
    // Производитель
    char manufacturer[MAX_STR];
    char model[MAX_STR];
    char panel_type[MAX_STR];
    char driver[MAX_STR];
    
    // HDR
    int hdr;
    int hdr_max_luminance;
    float hdr_max_average_luminance;
    float hdr_min_luminance;
    int hdr_formats;
    
    // Цвет
    float color_gamut[3];
    char color_profile[MAX_STR];
    int color_depth;
    int wide_color;
    int dci_p3;
    int srgb;
    int adobe_rgb;
    int display_p3;
    
    // Поворот
    int rotation;
    int orientation;
    int default_orientation;
    int can_rotate;
    
    // Касания
    int touch_support;
    int multitouch;
    int max_touch_points;
    int stylus_support;
    int pressure_sensitivity;
    int hover_support;
    
    // Особенности
    int always_on;
    int always_on_display;
    int cutout;
    float cutout_width;
    float cutout_height;
    float cutout_x;
    float cutout_y;
    int has_notch;
    int has_punch_hole;
    int has_under_display_camera;
    int has_curved_edges;
    int hole_in_display;
    
    // Режимы
    int night_mode;
    int reading_mode;
    int eye_care_mode;
    int dc_dimming;
    int pwm_frequency;
    
    // Дополнительно
    int hw_composer;
    int vsync_period;
    int vsync_offset;
    int display_id;
    int is_primary;
    int is_external;
    int is_virtual;
    char edid[MAX_STR];
    char serial[MAX_STR];
} DisplayInfo;

// ==================== ИНФОРМАЦИЯ О СЕТИ ====================
typedef struct {
    char device_id[MAX_STR];
    char advertising_id[MAX_STR];
    char android_id[MAX_STR];
    char gsf_id[MAX_STR];
    char google_id[MAX_STR];
    char firebase_id[MAX_STR];
    char huawei_id[MAX_STR];
    char samsung_id[MAX_STR];
    char xiaomi_id[MAX_STR];
    char mi_id[MAX_STR];
    char oaid[MAX_STR];
    char vaid[MAX_STR];
    char aaid[MAX_STR];
    char idfa[MAX_STR];
    char idfv[MAX_STR];
    char mac_wifi[MAX_STR];
    char mac_bt[MAX_STR];
    char mac_eth[MAX_STR];
    char imei[MAX_STR];
    char imei2[MAX_STR];
    char meid[MAX_STR];
    char meid2[MAX_STR];
    char iccid[MAX_STR];
    char iccid2[MAX_STR];
    char imsi[MAX_STR];
    char imsi2[MAX_STR];
    char phone_number[MAX_STR];
    char phone_number2[MAX_STR];
} NetworkIdentity;

// ==================== ИНФОРМАЦИЯ О ПРОШИВКЕ ====================
typedef struct {
    char firmware_version[MAX_STR];
    char vendor_firmware[MAX_STR];
    char oem_unlock[MAX_STR];
    char warranty_bit[MAX_STR];
    char warranty_void[MAX_STR];
    char knox_version[MAX_STR];
    char knox_status[MAX_STR];
    char safetynet_status[MAX_STR];
    char play_protect_status[MAX_STR];
    char verified_boot_state[MAX_STR];
    char verity_mode[MAX_STR];
    char vbmeta_digest[MAX_STR];
    char vbmeta_state[MAX_STR];
    char mia_version[MAX_STR];
    char mia_state[MAX_STR];
    char dm_verity_mode[MAX_STR];
    char encryption_state[MAX_STR];
    char encryption_type[MAX_STR];
    char fs_encryption[MAX_STR];
    char block_encryption[MAX_STR];
    char file_encryption[MAX_STR];
    char metadata_encryption[MAX_STR];
    char keymaster_version[MAX_STR];
    char gatekeeper_version[MAX_STR];
    char weaver_version[MAX_STR];
    char widevine_level[MAX_STR];
    char playready_level[MAX_STR];
    char clearkey_level[MAX_STR];
} FirmwareInfo;

// ==================== ИНФОРМАЦИЯ О ЯДРЕ ====================
typedef struct {
    char version[MAX_STR];
    char release[MAX_STR];
    char machine[MAX_STR];
    char sysname[MAX_STR];
    char nodename[MAX_STR];
    char domainname[MAX_STR];
    char build_date[MAX_STR];
    char build_user[MAX_STR];
    char build_host[MAX_STR];
    char compiler[MAX_STR];
    char compiler_version[MAX_STR];
    int page_size;
    int physical_pages;
    int available_pages;
    int swap_pages;
    int swap_free_pages;
    int uptime_seconds;
    int load_1;
    int load_5;
    int load_15;
    int processes;
    int procs_running;
    int procs_blocked;
    int ctxt_switches;
    int btime;
} KernelInfo;

// ==================== ИНФОРМАЦИЯ О ПАМЯТИ ====================
typedef struct {
    unsigned long long total_ram;
    unsigned long long free_ram;
    unsigned long long available_ram;
    unsigned long long cached;
    unsigned long long buffers;
    unsigned long long swap_total;
    unsigned long long swap_free;
    unsigned long long swap_cached;
    unsigned long long active;
    unsigned long long inactive;
    unsigned long long dirty;
    unsigned long long writeback;
    unsigned long long anon_pages;
    unsigned long long mapped;
    unsigned long long slab;
    unsigned long long sreclaimable;
    unsigned long long sunreclaim;
    unsigned long long page_tables;
    unsigned long long kernel_stack;
    unsigned long long hardware_corrupted;
    unsigned long long huge_pages_total;
    unsigned long long huge_pages_free;
    unsigned long long huge_page_size;
} MemoryInfoDetailed;

// ==================== ИНФОРМАЦИЯ О ПРОЦЕССАХ ====================
typedef struct {
    int total_processes;
    int running;
    int sleeping;
    int stopped;
    int zombie;
    int dead;
    int kernel_threads;
    int user_threads;
    int total_threads;
    int max_pid;
    int last_pid;
} ProcessInfoDetailed;

// ==================== ПРОТОТИПЫ ФУНКЦИЙ ====================

#ifdef __cplusplus
extern "C" {
#endif

// Основные функции
SystemInfo get_system_info(void);
DisplayInfo get_display_info(void);
NetworkIdentity get_network_identity(void);
FirmwareInfo get_firmware_info(void);
KernelInfo get_kernel_info(void);
MemoryInfoDetailed get_memory_info_detailed(void);
ProcessInfoDetailed get_process_info_detailed(void);

// Детекторы
int is_emulator(void);
int is_rooted(void);
int is_secure(void);
int has_gapps(void);
int has_huawei_services(void);
int has_samsung_services(void);
int has_xiaomi_services(void);
int has_magisk(void);
int has_supersu(void);
int has_kernelsu(void);
int has_xposed(void);
int has_edxposed(void);
int has_lsposed(void);

// Региональные
const char* get_country_code(void);
const char* get_language_code(void);
const char* get_timezone(void);
const char* get_locale(void);
const char* get_region(void);

// Версии
const char* get_os_version(void);
const char* get_api_level_string(void);
const char* get_security_patch_level(void);
const char* get_build_date_string(void);
const char* get_build_time_string(void);
const char* get_build_utc_string(void);

// Форматирование
void format_system_info(const SystemInfo* sys, char* buffer, size_t buffer_size);
void format_system_info_detailed(const SystemInfo* sys, char* buffer, size_t buffer_size);
void format_display_info(const DisplayInfo* disp, char* buffer, size_t buffer_size);
void format_display_info_detailed(const DisplayInfo* disp, char* buffer, size_t buffer_size);
void format_kernel_info(const KernelInfo* kernel, char* buffer, size_t buffer_size);
// ⚠️ ЭТИ ФУНКЦИИ УЖЕ ЕСТЬ В ДРУГИХ ФАЙЛАХ, НЕ ДУБЛИРУЕМ!
// void format_mem_det_detailed(...); // Есть в hardware_info.h
// void format_proc_det_detailed(...); // Есть в process_info.h
void format_device_summary(char* buffer, size_t buffer_size);
void format_device_summary_detailed(char* buffer, size_t buffer_size);

// Получение отдельных значений
const char* get_device_codename(void);
const char* get_device_serial(void);
const char* get_build_fingerprint(void);
const char* get_kernel_version(void);
const char* get_bootloader_version(void);
const char* get_baseband_version(void);
const char* get_hardware(void);
const char* get_platform(void);
const char* get_board(void);
const char* get_manufacturer(void);
const char* get_brand(void);
const char* get_model(void);
const char* get_product(void);
const char* get_device(void);

// Время
time_t get_boot_time(void);
time_t get_uptime(void);
const char* get_uptime_string(void);
const char* get_boot_time_string(void);
const char* get_current_time_string(void);

// Безопасность
const char* get_selinux_mode(void);
int is_selinux_enforcing(void);
int is_selinux_permissive(void);
int is_verified_boot(void);
int is_dm_verity_enabled(void);
int is_force_encrypted(void);
int is_file_encrypted(void);
int is_full_disk_encrypted(void);

// Тип устройства
DeviceType get_device_type(void);
const char* get_device_type_string(void);
int is_phone_device(void);
int is_tablet_device(void);
int is_tv_device(void);
int is_wearable_device(void);
int is_automotive_device(void);

// Характеристики
int has_fingerprint_sensor(void);
int has_face_unlock(void);
int has_iris_scanner(void);
int has_nfc(void);
int has_ir_blaster(void);
int has_notch_display(void);
int has_punch_hole_display(void);
int has_under_display_fingerprint(void);
int has_stereo_speakers(void);
int has_headphone_jack(void);
int has_sd_card_slot(void);
int has_wireless_charging(void);
int has_fast_charging(void);
int has_waterproof(void);

// Сравнение
int compare_system_info(const SystemInfo* a, const SystemInfo* b);
int compare_display_info(const DisplayInfo* a, const DisplayInfo* b);

#ifdef __cplusplus
}
#endif

#endif // SYSTEM_INFO_H

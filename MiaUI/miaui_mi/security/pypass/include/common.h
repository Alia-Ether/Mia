//╔═════════════════════════════╗                       
//║  Link: t.me/FrontendVSCode                       ║                         
//║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║    
//║  lang: C                                         ║                     
//║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║                      
//║  build:3.10.15                                   ║
//║  files: common.h                                 ║    
//╚═════════════════════════════╝


#ifndef COMMON_H
#define COMMON_H

// ==================== ЗАЩИТА ОТ ПОВТОРНОГО ВКЛЮЧЕНИЯ ====================
#ifdef COMMON_H_INCLUDED
#error "common.h включен дважды!"
#endif
#define COMMON_H_INCLUDED

// ==================== СТАНДАРТНЫЕ БИБЛИОТЕКИ ====================
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>
#include <sys/types.h>

// ==================== ЕДИНЫЕ РАЗМЕРЫ (БАЗОВЫЕ) ====================
#ifndef MAX_STR
#define MAX_STR         256     // максимальная длина строки
#endif

#ifndef MAX_NAME
#define MAX_NAME        128     // максимальная длина имени
#endif

#ifndef MAX_PATH
#define MAX_PATH        512     // максимальная длина пути
#endif

#ifndef MAX_BUFFER
#define MAX_BUFFER      1024    // размер буфера по умолчанию
#endif

// ==================== ЕДИНЫЕ РАЗМЕРЫ (СПЕЦИАЛИЗИРОВАННЫЕ) ====================
#ifndef MAX_CPUS
#define MAX_CPUS        32      // максимум ядер CPU
#endif

#ifndef MAX_SENSORS
#define MAX_SENSORS     64      // максимум датчиков
#endif

#ifndef MAX_CAMERAS
#define MAX_CAMERAS     8       // максимум камер
#endif

#ifndef MAX_DISKS
#define MAX_DISKS       16      // максимум дисков
#endif

#ifndef MAX_INTERFACES
#define MAX_INTERFACES  16      // максимум сетевых интерфейсов
#endif

#ifndef MAX_PROCESSES
#define MAX_PROCESSES   128     // максимум процессов для отображения
#endif

#ifndef MAX_RESOLUTIONS
#define MAX_RESOLUTIONS 16      // максимум разрешений для камеры
#endif

#ifndef MAX_FPS
#define MAX_FPS         32      // максимум FPS режимов
#endif

#ifndef MAX_HISTORY
#define MAX_HISTORY     60      // размер истории для графиков
#endif

// ==================== ЛИМИТЫ БЕЗОПАСНОСТИ ====================
#ifndef SAFE_MAX_SIZE
#define SAFE_MAX_SIZE   (1024 * 1024)        // 1MB - макс размер файла
#endif

#ifndef SAFE_TIMEOUT
#define SAFE_TIMEOUT    5                    // таймаут в секундах
#endif

#ifndef SAFE_RETRY
#define SAFE_RETRY      3                    // количество попыток
#endif

// ==================== ВЕРСИИ ====================
#ifndef VERSION_MAJOR
#define VERSION_MAJOR   2
#endif

#ifndef VERSION_MINOR
#define VERSION_MINOR   1
#endif

#ifndef VERSION_PATCH
#define VERSION_PATCH   2026
#endif

#define VERSION_STRING  "2.1.2026"

// ==================== ТИПЫ ДАННЫХ ====================
typedef uint8_t  u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;

typedef int8_t   i8;
typedef int16_t  i16;
typedef int32_t  i32;
typedef int64_t  i64;

typedef float    f32;
typedef double   f64;

// ==================== СТАТУСЫ ВЫПОЛНЕНИЯ ====================
typedef enum {
    STATUS_OK = 0,
    STATUS_ERROR = -1,
    STATUS_TIMEOUT = -2,
    STATUS_NOT_FOUND = -3,
    STATUS_PERMISSION_DENIED = -4,
    STATUS_INVALID_PARAM = -5,
    STATUS_OUT_OF_MEMORY = -6,
    STATUS_NOT_IMPLEMENTED = -7,
    STATUS_BUSY = -8,
    STATUS_AGAIN = -9,
    STATUS_EOF = -10,
    STATUS_EMPTY = -11,
    STATUS_EXISTS = -12
} StatusCode;

// ==================== УРОВНИ ВАЖНОСТИ ====================
typedef enum {
    LOG_LEVEL_DEBUG = 0,
    LOG_LEVEL_INFO,
    LOG_LEVEL_WARNING,
    LOG_LEVEL_ERROR,
    LOG_LEVEL_CRITICAL,
    LOG_LEVEL_SILENT
} LogLevel;

// ==================== ТИПЫ УСТРОЙСТВ ====================
typedef enum {
    DEVICE_UNKNOWN = 0,
    DEVICE_PHONE,
    DEVICE_TABLET,
    DEVICE_TV,
    DEVICE_WATCH,
    DEVICE_AUTO,
    DEVICE_AUTOMOTIVE,      // добавлено
    DEVICE_WEARABLE,        // добавлено
    DEVICE_LAPTOP,
    DEVICE_DESKTOP,
    DEVICE_SERVER,
    DEVICE_EMBEDDED,
    DEVICE_VIRTUAL,
    DEVICE_OTHER            // добавлено
} DeviceType;

// ==================== ЕДИНИЦЫ ИЗМЕРЕНИЯ ====================
typedef enum {
    UNIT_UNKNOWN = 0,
    UNIT_BYTES,
    UNIT_KILOBYTES,
    UNIT_MEGABYTES,
    UNIT_GIGABYTES,
    UNIT_TERABYTES,
    UNIT_CELSIUS,
    UNIT_FAHRENHEIT,
    UNIT_VOLT,
    UNIT_AMPERE,
    UNIT_WATT,
    UNIT_PERCENT,
    UNIT_HERTZ,
    UNIT_KILOHERTZ,
    UNIT_MEGAHERTZ,
    UNIT_GIGAHERTZ,
    UNIT_SECONDS,
    UNIT_MINUTES,
    UNIT_HOURS,
    UNIT_DAYS,
    UNIT_METERS,
    UNIT_CENTIMETERS,
    UNIT_KILOMETERS
} UnitType;

// ==================== ПРИОРИТЕТЫ ====================
typedef enum {
    PRIORITY_LOW = 0,
    PRIORITY_NORMAL,
    PRIORITY_HIGH,
    PRIORITY_CRITICAL
} Priority;

// ==================== БУЛЕВЫ ЗНАЧЕНИЯ ====================
typedef enum {
    FALSE = 0,
    TRUE = 1
} Bool;

// ==================== МАКРОСЫ БЕЗОПАСНОСТИ ====================

// Безопасное освобождение памяти
#define SAFE_FREE(ptr) do { \
    if (ptr) { free(ptr); ptr = NULL; } \
} while(0)

// Безопасное закрытие файла
#define SAFE_CLOSE(fp) do { \
    if (fp) { fclose(fp); fp = NULL; } \
} while(0)

// Проверка на валидность указателя
#define IS_VALID_PTR(ptr) ((ptr) != NULL)

// Проверка на валидность индекса
#define IS_VALID_INDEX(idx, max) ((idx) >= 0 && (idx) < (max))

// Минимум и максимум
#define MIN(a,b) (((a) < (b)) ? (a) : (b))
#define MAX(a,b) (((a) > (b)) ? (a) : (b))

// Ограничение значения
#define CLAMP(x, min, max) MIN(MAX((x), (min)), (max))

// Безопасное приведение типов
#define SAFE_CAST(type, value) ((value) ? (type)(value) : 0)

// Получение размера массива
#define ARRAY_SIZE(arr) (sizeof(arr) / sizeof((arr)[0]))

// Проверка битовых флагов
#define IS_FLAG_SET(value, flag) (((value) & (flag)) == (flag))

// Установка битового флага
#define SET_FLAG(value, flag) ((value) |= (flag))

// Сброс битового флага
#define CLEAR_FLAG(value, flag) ((value) &= ~(flag))

// ==================== МАКРОСЫ ДЛЯ ОТЛАДКИ ====================

#ifdef DEBUG
#define DEBUG_PRINT(fmt, ...) \
    fprintf(stderr, "[DEBUG] %s:%d: " fmt "\n", __FILE__, __LINE__, ##__VA_ARGS__)
#else
#define DEBUG_PRINT(fmt, ...) do {} while(0)
#endif

#define ERROR_PRINT(fmt, ...) \
    fprintf(stderr, "[ERROR] %s:%d: " fmt "\n", __FILE__, __LINE__, ##__VA_ARGS__)

#define WARN_PRINT(fmt, ...) \
    fprintf(stderr, "[WARN] %s:%d: " fmt "\n", __FILE__, __LINE__, ##__VA_ARGS__)

#define INFO_PRINT(fmt, ...) \
    fprintf(stderr, "[INFO] %s:%d: " fmt "\n", __FILE__, __LINE__, ##__VA_ARGS__)

// ==================== КОНВЕРТАЦИЯ ЕДИНИЦ ====================

// Конвертация байт в килобайты
#define BYTES_TO_KB(bytes) ((bytes) / 1024.0)

// Конвертация байт в мегабайты
#define BYTES_TO_MB(bytes) ((bytes) / (1024.0 * 1024.0))

// Конвертация байт в гигабайты
#define BYTES_TO_GB(bytes) ((bytes) / (1024.0 * 1024.0 * 1024.0))

// Конвертация байт в терабайты
#define BYTES_TO_TB(bytes) ((bytes) / (1024.0 * 1024.0 * 1024.0 * 1024.0))

// Конвертация герц в килогерцы
#define HZ_TO_KHZ(hz) ((hz) / 1000.0)

// Конвертация герц в мегагерцы
#define HZ_TO_MHZ(hz) ((hz) / 1000000.0)

// Конвертация герц в гигагерцы
#define HZ_TO_GHZ(hz) ((hz) / 1000000000.0)

// Конвертация мегагерц в герцы
#define MHZ_TO_HZ(mhz) ((mhz) * 1000000.0)

// Конвертация секунд в минуты
#define SEC_TO_MIN(sec) ((sec) / 60.0)

// Конвертация секунд в часы
#define SEC_TO_HOUR(sec) ((sec) / 3600.0)

// Конвертация секунд в дни
#define SEC_TO_DAY(sec) ((sec) / 86400.0)

// ==================== ФУНКЦИИ-ПОМОЩНИКИ ====================

/**
 * Безопасное копирование строки
 */
static inline char* safe_strdup(const char* str) {
    if (str == NULL) return NULL;
    size_t len = strlen(str) + 1;
    char* copy = (char*)malloc(len);
    if (copy) memcpy(copy, str, len);
    return copy;
}

/**
 * Безопасное копирование строки с ограничением длины
 */
static inline char* safe_strndup(const char* str, size_t n) {
    if (str == NULL) return NULL;
    size_t len = strnlen(str, n);
    char* copy = (char*)malloc(len + 1);
    if (copy) {
        memcpy(copy, str, len);
        copy[len] = '\0';
    }
    return copy;
}

/**
 * Получение строки версии
 */
static inline const char* get_version_string(void) {
    return VERSION_STRING;
}

/**
 * Получение версии как числа
 */
static inline int get_version_number(void) {
    return (VERSION_MAJOR * 10000 + VERSION_MINOR * 100 + VERSION_PATCH);
}

/**
 * Получение текстового описания статуса
 */
static inline const char* status_string(StatusCode code) {
    switch (code) {
        case STATUS_OK: return "OK";
        case STATUS_ERROR: return "Error";
        case STATUS_TIMEOUT: return "Timeout";
        case STATUS_NOT_FOUND: return "Not found";
        case STATUS_PERMISSION_DENIED: return "Permission denied";
        case STATUS_INVALID_PARAM: return "Invalid parameter";
        case STATUS_OUT_OF_MEMORY: return "Out of memory";
        case STATUS_NOT_IMPLEMENTED: return "Not implemented";
        case STATUS_BUSY: return "Busy";
        case STATUS_AGAIN: return "Try again";
        case STATUS_EOF: return "End of file";
        case STATUS_EMPTY: return "Empty";
        case STATUS_EXISTS: return "Already exists";
        default: return "Unknown";
    }
}

/**
 * Получение названия устройства
 */
static inline const char* device_type_string(DeviceType type) {
    switch (type) {
        case DEVICE_PHONE: return "Phone";
        case DEVICE_TABLET: return "Tablet";
        case DEVICE_TV: return "TV";
        case DEVICE_WATCH: return "Watch";
        case DEVICE_AUTO: return "Auto";
        case DEVICE_AUTOMOTIVE: return "Automotive";
        case DEVICE_WEARABLE: return "Wearable";
        case DEVICE_LAPTOP: return "Laptop";
        case DEVICE_DESKTOP: return "Desktop";
        case DEVICE_SERVER: return "Server";
        case DEVICE_EMBEDDED: return "Embedded";
        case DEVICE_VIRTUAL: return "Virtual";
        case DEVICE_OTHER: return "Other";
        default: return "Unknown";
    }
}

/**
 * Получение названия единицы измерения
 */
static inline const char* unit_string(UnitType unit) {
    switch (unit) {
        case UNIT_BYTES: return "B";
        case UNIT_KILOBYTES: return "KB";
        case UNIT_MEGABYTES: return "MB";
        case UNIT_GIGABYTES: return "GB";
        case UNIT_TERABYTES: return "TB";
        case UNIT_CELSIUS: return "°C";
        case UNIT_FAHRENHEIT: return "°F";
        case UNIT_VOLT: return "V";
        case UNIT_AMPERE: return "A";
        case UNIT_WATT: return "W";
        case UNIT_PERCENT: return "%";
        case UNIT_HERTZ: return "Hz";
        case UNIT_KILOHERTZ: return "kHz";
        case UNIT_MEGAHERTZ: return "MHz";
        case UNIT_GIGAHERTZ: return "GHz";
        case UNIT_SECONDS: return "s";
        case UNIT_MINUTES: return "min";
        case UNIT_HOURS: return "h";
        case UNIT_DAYS: return "d";
        case UNIT_METERS: return "m";
        case UNIT_CENTIMETERS: return "cm";
        case UNIT_KILOMETERS: return "km";
        default: return "";
    }
}

/**
 * Получение названия приоритета
 */
static inline const char* priority_string(Priority prio) {
    switch (prio) {
        case PRIORITY_LOW: return "Low";
        case PRIORITY_NORMAL: return "Normal";
        case PRIORITY_HIGH: return "High";
        case PRIORITY_CRITICAL: return "Critical";
        default: return "Unknown";
    }
}

/**
 * Получение названия уровня логирования
 */
static inline const char* log_level_string(LogLevel level) {
    switch (level) {
        case LOG_LEVEL_DEBUG: return "DEBUG";
        case LOG_LEVEL_INFO: return "INFO";
        case LOG_LEVEL_WARNING: return "WARN";
        case LOG_LEVEL_ERROR: return "ERROR";
        case LOG_LEVEL_CRITICAL: return "CRITICAL";
        case LOG_LEVEL_SILENT: return "SILENT";
        default: return "UNKNOWN";
    }
}

/**
 * Форматирование байт в человекочитаемый вид
 */
static inline void format_bytes(char* buf, size_t buf_size, unsigned long long bytes) {
    if (buf == NULL || buf_size == 0) return;
    
    const char* units[] = {"B", "KB", "MB", "GB", "TB", "PB"};
    int unit = 0;
    double value = bytes;
    
    while (value >= 1024.0 && unit < 5) {
        value /= 1024.0;
        unit++;
    }
    
    if (unit == 0) {
        snprintf(buf, buf_size, "%llu %s", bytes, units[unit]);
    } else {
        snprintf(buf, buf_size, "%.2f %s", value, units[unit]);
    }
}

/**
 * Форматирование времени в человекочитаемый вид
 */
static inline void format_time(char* buf, size_t buf_size, time_t seconds) {
    if (buf == NULL || buf_size == 0) return;
    
    int days = seconds / 86400;
    int hours = (seconds % 86400) / 3600;
    int mins = (seconds % 3600) / 60;
    int secs = seconds % 60;
    
    if (days > 0) {
        snprintf(buf, buf_size, "%dд %dч %dм", days, hours, mins);
    } else if (hours > 0) {
        snprintf(buf, buf_size, "%dч %dм %dс", hours, mins, secs);
    } else if (mins > 0) {
        snprintf(buf, buf_size, "%dм %dс", mins, secs);
    } else {
        snprintf(buf, buf_size, "%dс", secs);
    }
}

#endif // COMMON_H
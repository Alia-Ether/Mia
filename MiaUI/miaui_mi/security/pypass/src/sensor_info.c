//╔══════════════════════════════════════════════════════════════════════════════════════╗
//║  Link: t.me/FrontendVSCode                                                           ║
//║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                                           ║
//║  lang: C                                                                             ║
//║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                                                       ║
//║  build:3.10.15-termux-volt-fix                                                       ║
//║  files: sensor_info.c                                                                ║
//║                                                                                      ║
//║  ДОБАВЛЕНА ПОДДЕРЖКА TERMUX-API:                                                     ║
//║  - termux-sensor (все датчики: акселерометр, гироскоп, магнитометр)                 ║
//║  - termux-battery-status (батарея)                                                   ║
//║  - termux-wifi-scaninfo (WiFi сигнал)                                                ║
//╚══════════════════════════════════════════════════════════════════════════════════════╝

#include "../include/sensor_info.h"
#include "../include/safe_read.h"
#include "../include/common.h"
#include <dirent.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <time.h>
#include <errno.h>

// ==================== ЗАЩИТА ОТ ПОВТОРНОГО ВКЛЮЧЕНИЯ ====================
#ifdef SENSOR_INFO_C
#error "sensor_info.c включен дважды!"
#endif
#define SENSOR_INFO_C

// ==================== КОНСТАНТЫ ====================
#define SENSOR_THERMAL_PATH "/sys/class/thermal"
#define SENSOR_POWER_PATH "/sys/class/power_supply"
#define SENSOR_IIO_PATH "/sys/bus/iio/devices"
#define SENSOR_INPUT_PATH "/sys/class/input"
#define SENSOR_HWMON_PATH "/sys/class/hwmon"
#define MAX_SENSOR_VALUE 1024
#define MAX_PATH_LEN 256
#define TERMUX_SENSOR_TIMEOUT 2

// ==================== СТРУКТУРЫ ====================
typedef struct {
    const char* path;
    const char* name;
    const char* unit;
    int type;
    float scale;
} SensorDefinition;

// ==================== БАЗА ДАТЧИКОВ ====================
static const SensorDefinition sensor_defs[] = {
    {"/sys/class/thermal/thermal_zone%d/temp", "temp_zone%d", "°C", SENSOR_TYPE_CPU_TEMP, 0.001f},
    {"/sys/class/hwmon/hwmon%d/temp%d_input", "hwmon_temp%d", "°C", SENSOR_TYPE_CPU_TEMP, 0.001f},
    {"/sys/bus/iio/devices/iio:device%d/in_temp_raw", "iio_temp", "°C", SENSOR_TYPE_CPU_TEMP, 0.001f},
    
    {"/sys/class/power_supply/battery/voltage_now", "battery_voltage", "V", SENSOR_TYPE_VOLTAGE, 1e-6f},
    {"/sys/class/power_supply/usb/voltage_now", "usb_voltage", "V", SENSOR_TYPE_VOLTAGE, 1e-6f},
    
    {"/sys/class/power_supply/battery/current_now", "battery_current", "mA", SENSOR_TYPE_CURRENT, 0.001f},
    {"/sys/class/power_supply/usb/current_max", "usb_current", "mA", SENSOR_TYPE_CURRENT, 0.001f},
    
    {"/sys/class/power_supply/battery/power_now", "battery_power", "mW", SENSOR_TYPE_POWER, 0.001f},
    
    {"/sys/bus/iio/devices/iio:device%d/in_illuminance_raw", "light", "lux", SENSOR_TYPE_LIGHT, 1.0f},
    {"/sys/class/leds/lcd-backlight/brightness", "backlight", "level", SENSOR_TYPE_LIGHT, 1.0f},
    
    {"/sys/bus/iio/devices/iio:device%d/in_proximity_raw", "proximity", "cm", SENSOR_TYPE_PROXIMITY, 1.0f},
    
    {"/sys/bus/iio/devices/iio:device%d/in_accel_x_raw", "accel_x", "m/s²", SENSOR_TYPE_ACCELEROMETER, 0.001f},
    {"/sys/bus/iio/devices/iio:device%d/in_accel_y_raw", "accel_y", "m/s²", SENSOR_TYPE_ACCELEROMETER, 0.001f},
    {"/sys/bus/iio/devices/iio:device%d/in_accel_z_raw", "accel_z", "m/s²", SENSOR_TYPE_ACCELEROMETER, 0.001f},
    
    {"/sys/bus/iio/devices/iio:device%d/in_anglvel_x_raw", "gyro_x", "rad/s", SENSOR_TYPE_GYROSCOPE, 0.001f},
    {"/sys/bus/iio/devices/iio:device%d/in_anglvel_y_raw", "gyro_y", "rad/s", SENSOR_TYPE_GYROSCOPE, 0.001f},
    {"/sys/bus/iio/devices/iio:device%d/in_anglvel_z_raw", "gyro_z", "rad/s", SENSOR_TYPE_GYROSCOPE, 0.001f},
    
    {"/sys/bus/iio/devices/iio:device%d/in_magn_x_raw", "magn_x", "uT", SENSOR_TYPE_MAGNETOMETER, 0.001f},
    {"/sys/bus/iio/devices/iio:device%d/in_magn_y_raw", "magn_y", "uT", SENSOR_TYPE_MAGNETOMETER, 0.001f},
    {"/sys/bus/iio/devices/iio:device%d/in_magn_z_raw", "magn_z", "uT", SENSOR_TYPE_MAGNETOMETER, 0.001f},
    
    {"/sys/bus/iio/devices/iio:device%d/in_pressure_raw", "pressure", "hPa", SENSOR_TYPE_PRESSURE, 0.001f},
    
    {"/sys/bus/iio/devices/iio:device%d/in_humidityrelative_raw", "humidity", "%%", SENSOR_TYPE_HUMIDITY, 0.001f},
    
    {NULL, NULL, NULL, 0, 0}
};

// ==================== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ====================
static struct {
    float history[MAX_SENSORS][60];
    int history_index[MAX_SENSORS];
    int initialized;
    int termux_api_available;
} sensor_cache = {0};

// ==================== ПРОВЕРКА TERMUX-API ====================

/**
 * Проверка доступности termux-sensor
 */
static int check_termux_sensor_available(void) {
    FILE* f = popen("termux-sensor -h 2>/dev/null", "r");
    if (!f) return 0;
    char buf[10];
    int found = fread(buf, 1, sizeof(buf)-1, f) > 0;
    pclose(f);
    return found;
}

/**
 * Проверка доступности termux-battery-status
 */
static int check_termux_battery_available(void) {
    FILE* f = popen("termux-battery-status 2>/dev/null", "r");
    if (!f) return 0;
    char buf[100];
    int found = fread(buf, 1, sizeof(buf)-1, f) > 0;
    pclose(f);
    return found;
}

/**
 * Получение датчиков через termux-sensor (JSON парсинг)
 * termux-sensor
 */
static int get_termux_sensors(SensorDisplayInfo* sensors, int max_count, int* count) {
    if (!check_termux_sensor_available()) return 0;
    
    FILE* f = popen("termux-sensor 2>/dev/null", "r");
    if (!f) return 0;
    
    char* json = malloc(65536);
    if (!json) {
        pclose(f);
        return 0;
    }
    
    size_t total = 0;
    char buf[4096];
    while (fgets(buf, sizeof(buf), f) && total < 65535) {
        size_t len = strlen(buf);
        if (total + len < 65535) {
            memcpy(json + total, buf, len);
            total += len;
        }
    }
    pclose(f);
    json[total] = '\0';
    
    // Парсим JSON вручную (без внешних библиотек)
    char* pos = json;
    char sensor_name[128];
    float value_x = 0, value_y = 0, value_z = 0;
    int has_x = 0, has_y = 0, has_z = 0;
    
    while (*pos && *count < max_count) {
        // Ищем имя датчика: "sensor_name": {
        if (*pos == '"') {
            char* start = pos + 1;
            char* end = strchr(start, '"');
            if (end && *(end + 1) == ':' && *(end + 2) == ' ') {
                size_t name_len = end - start;
                if (name_len > 0 && name_len < sizeof(sensor_name)) {
                    strncpy(sensor_name, start, name_len);
                    sensor_name[name_len] = '\0';
                    
                    // Ищем значения x, y, z
                    has_x = has_y = has_z = 0;
                    value_x = value_y = value_z = 0;
                    
                    // Ищем "values": [x, y, z]
                    char* values = strstr(pos, "\"values\"");
                    if (values) {
                        char* bracket = strchr(values, '[');
                        if (bracket) {
                            // Парсим x, y, z
                            if (sscanf(bracket, "[%f, %f, %f", &value_x, &value_y, &value_z) >= 1) {
                                has_x = 1;
                                if (sscanf(bracket, "[%f, %f, %f", &value_x, &value_y, &value_z) >= 2) has_y = 1;
                                if (sscanf(bracket, "[%f, %f, %f", &value_x, &value_y, &value_z) >= 3) has_z = 1;
                            }
                        }
                    }
                    
                    // Определяем тип датчика по имени
                    SensorType type = SENSOR_TYPE_UNKNOWN;
                    const char* unit = "";
                    float val = 0;
                    
                    if (strstr(sensor_name, "accel") || strstr(sensor_name, "accelerometer")) {
                        type = SENSOR_TYPE_ACCELEROMETER;
                        unit = "m/s²";
                        val = has_x ? value_x : (has_y ? value_y : value_z);
                    } else if (strstr(sensor_name, "gyro") || strstr(sensor_name, "gyroscope")) {
                        type = SENSOR_TYPE_GYROSCOPE;
                        unit = "rad/s";
                        val = has_x ? value_x : (has_y ? value_y : value_z);
                    } else if (strstr(sensor_name, "magn") || strstr(sensor_name, "magnetometer")) {
                        type = SENSOR_TYPE_MAGNETOMETER;
                        unit = "uT";
                        val = has_x ? value_x : (has_y ? value_y : value_z);
                    } else if (strstr(sensor_name, "light")) {
                        type = SENSOR_TYPE_LIGHT;
                        unit = "lux";
                        val = has_x ? value_x : 0;
                    } else if (strstr(sensor_name, "proximity")) {
                        type = SENSOR_TYPE_PROXIMITY;
                        unit = "cm";
                        val = has_x ? value_x : 0;
                    } else if (strstr(sensor_name, "pressure")) {
                        type = SENSOR_TYPE_PRESSURE;
                        unit = "hPa";
                        val = has_x ? value_x : 0;
                    } else if (strstr(sensor_name, "humidity")) {
                        type = SENSOR_TYPE_HUMIDITY;
                        unit = "%";
                        val = has_x ? value_x : 0;
                    } else if (strstr(sensor_name, "temp")) {
                        type = SENSOR_TYPE_AMBIENT_TEMP;
                        unit = "°C";
                        val = has_x ? value_x : 0;
                    }
                    
                    if (type != SENSOR_TYPE_UNKNOWN && val != 0 && *count < max_count) {
                        SensorDisplayInfo* s = &sensors[*count];
                        memset(s, 0, sizeof(SensorDisplayInfo));
                        snprintf(s->name, sizeof(s->name), "termux_%s", sensor_name);
                        s->value = val;
                        strcpy(s->unit, unit);
                        s->type = type;
                        s->enabled = 1;
                        s->priority = SENSOR_PRIO_NORMAL;
                        (*count)++;
                    }
                }
            }
        }
        pos++;
    }
    
    free(json);
    return 1;
}

/**
 * Получение данных батареи через termux-battery-status
 */
static int get_termux_battery_sensors(SensorDisplayInfo* sensors, int max_count, int* count) {
    if (!check_termux_battery_available()) return 0;
    
    FILE* f = popen("termux-battery-status 2>/dev/null", "r");
    if (!f) return 0;
    
    char buf[4096];
    size_t len = fread(buf, 1, sizeof(buf)-1, f);
    pclose(f);
    
    if (len == 0) return 0;
    buf[len] = '\0';
    
    // Парсим JSON
    // Уровень батареи
    char* p = strstr(buf, "\"percentage\"");
    if (p && *count < max_count) {
        p = strchr(p, ':');
        if (p) {
            float level = atof(p + 1);
            SensorDisplayInfo* s = &sensors[*count];
            memset(s, 0, sizeof(SensorDisplayInfo));
            snprintf(s->name, sizeof(s->name), "termux_battery_level");
            s->value = level;
            strcpy(s->unit, "%");
            s->type = SENSOR_TYPE_CAPACITY;
            s->enabled = 1;
            s->priority = SENSOR_PRIO_HIGH;
            (*count)++;
        }
    }
    
    // Температура батареи
    p = strstr(buf, "\"temperature\"");
    if (p && *count < max_count) {
        p = strchr(p, ':');
        if (p) {
            float temp = atof(p + 1);
            SensorDisplayInfo* s = &sensors[*count];
            memset(s, 0, sizeof(SensorDisplayInfo));
            snprintf(s->name, sizeof(s->name), "termux_battery_temp");
            s->value = temp;
            strcpy(s->unit, "°C");
            s->type = SENSOR_TYPE_BATTERY_TEMP;
            s->enabled = 1;
            s->priority = SENSOR_PRIO_NORMAL;
            (*count)++;
        }
    }
    
    // Напряжение
    p = strstr(buf, "\"voltage\"");
    if (p && *count < max_count) {
        p = strchr(p, ':');
        if (p) {
            float volt = atof(p + 1) / 1000.0f;
            SensorDisplayInfo* s = &sensors[*count];
            memset(s, 0, sizeof(SensorDisplayInfo));
            snprintf(s->name, sizeof(s->name), "termux_battery_voltage");
            s->value = volt;
            strcpy(s->unit, "V");
            s->type = SENSOR_TYPE_VOLTAGE;
            s->enabled = 1;
            s->priority = SENSOR_PRIO_NORMAL;
            (*count)++;
        }
    }
    
    return 1;
}

// ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

static void ensure_sensor_cache_initialized(void) {
    if (!sensor_cache.initialized) {
        memset(&sensor_cache, 0, sizeof(sensor_cache));
        sensor_cache.initialized = 1;
        sensor_cache.termux_api_available = (check_termux_sensor_available() || check_termux_battery_available()) ? 1 : 0;
    }
}

static void update_sensor_history(int id, float value) {
    if (id < 0 || id >= MAX_SENSORS) return;
    sensor_cache.history[id][sensor_cache.history_index[id]] = value;
    sensor_cache.history_index[id] = (sensor_cache.history_index[id] + 1) % 60;
}

float get_sensor_trend(int id, int seconds) {
    (void)seconds;
    if (id < 0 || id >= MAX_SENSORS) return 0;
    
    float sum = 0;
    int count = 0;
    int idx = sensor_cache.history_index[id];
    
    for (int i = 0; i < 10; i++) {
        int history_idx = (idx - 1 - i + 60) % 60;
        if (sensor_cache.history[id][history_idx] != 0) {
            sum += sensor_cache.history[id][history_idx];
            count++;
        }
    }
    
    return (count > 0) ? sum / count : 0;
}

static SensorType int_to_sensor_type(int type) {
    return (SensorType)type;
}

static SensorType detect_sensor_type(const char* name) {
    if (name == NULL) return SENSOR_TYPE_UNKNOWN;
    
    if (strstr(name, "temp") != NULL) return SENSOR_TYPE_CPU_TEMP;
    if (strstr(name, "volt") != NULL) return SENSOR_TYPE_VOLTAGE;
    if (strstr(name, "curr") != NULL) return SENSOR_TYPE_CURRENT;
    if (strstr(name, "power") != NULL) return SENSOR_TYPE_POWER;
    if (strstr(name, "humid") != NULL) return SENSOR_TYPE_HUMIDITY;
    if (strstr(name, "press") != NULL) return SENSOR_TYPE_PRESSURE;
    if (strstr(name, "light") != NULL) return SENSOR_TYPE_LIGHT;
    if (strstr(name, "prox") != NULL) return SENSOR_TYPE_PROXIMITY;
    if (strstr(name, "accel") != NULL) return SENSOR_TYPE_ACCELEROMETER;
    if (strstr(name, "gyro") != NULL) return SENSOR_TYPE_GYROSCOPE;
    if (strstr(name, "magn") != NULL) return SENSOR_TYPE_MAGNETOMETER;
    
    return SENSOR_TYPE_UNKNOWN;
}

static const char* get_unit_by_type(SensorType type) {
    switch (type) {
        case SENSOR_TYPE_CPU_TEMP:
        case SENSOR_TYPE_GPU_TEMP:
        case SENSOR_TYPE_BATTERY_TEMP:
        case SENSOR_TYPE_AMBIENT_TEMP:
        case SENSOR_TYPE_SKIN_TEMP:
            return "°C";
        case SENSOR_TYPE_VOLTAGE: return "V";
        case SENSOR_TYPE_CURRENT: return "mA";
        case SENSOR_TYPE_POWER: return "mW";
        case SENSOR_TYPE_HUMIDITY: return "%";
        case SENSOR_TYPE_PRESSURE: return "hPa";
        case SENSOR_TYPE_LIGHT: return "lux";
        case SENSOR_TYPE_PROXIMITY: return "cm";
        case SENSOR_TYPE_ACCELEROMETER: return "m/s²";
        case SENSOR_TYPE_GYROSCOPE: return "rad/s";
        case SENSOR_TYPE_MAGNETOMETER: return "uT";
        case SENSOR_TYPE_CAPACITY: return "%";
        default: return "";
    }
}

static float read_sensor_value_safe(const char* path, float scale) {
    if (path == NULL) return 0;
    
    size_t dummy = 0;
    char* value_str = safe_read_file(path, &dummy);
    if (value_str == NULL) return 0;
    
    float value = atof(value_str) * scale;
    free(value_str);
    return value;
}

static int scan_iio_devices(void) {
    int count = 0;
    DIR* dir = opendir(SENSOR_IIO_PATH);
    
    if (dir != NULL) {
        struct dirent* entry;
        while ((entry = readdir(dir)) != NULL) {
            if (strncmp(entry->d_name, "iio:device", 10) == 0) {
                count++;
            }
        }
        closedir(dir);
    }
    
    return count;
}

static int scan_hwmon_devices(void) {
    int count = 0;
    DIR* dir = opendir(SENSOR_HWMON_PATH);
    
    if (dir != NULL) {
        struct dirent* entry;
        while ((entry = readdir(dir)) != NULL) {
            if (strncmp(entry->d_name, "hwmon", 5) == 0) {
                count++;
            }
        }
        closedir(dir);
    }
    
    return count;
}

// ==================== ОСНОВНЫЕ ФУНКЦИИ ====================

int get_sensor_info(SensorDisplayInfo* sensors, int max_count) {
    if (sensors == NULL || max_count <= 0) return 0;
    
    ensure_sensor_cache_initialized();
    int count = 0;
    
    // ===== 1. ТЕРМАЛЬНЫЕ ДАТЧИКИ =====
    DIR* dir = opendir(SENSOR_THERMAL_PATH);
    if (dir != NULL) {
        struct dirent* entry;
        while ((entry = readdir(dir)) != NULL && count < max_count) {
            if (entry->d_name[0] == '.') continue;
            if (strncmp(entry->d_name, "thermal_zone", 12) != 0) continue;
            
            char path[MAX_PATH_LEN];
            snprintf(path, sizeof(path), "%s/%s/temp", SENSOR_THERMAL_PATH, entry->d_name);
            
            long temp = safe_read_long(path);
            if (temp > 0) {
                SensorDisplayInfo* s = &sensors[count];
                memset(s, 0, sizeof(SensorDisplayInfo));
                
                char type_path[MAX_PATH_LEN];
                snprintf(type_path, sizeof(type_path), "%s/%s/type", SENSOR_THERMAL_PATH, entry->d_name);
                
                size_t dummy = 0;
                char* type = safe_read_file(type_path, &dummy);
                
                if (type != NULL) {
                    snprintf(s->name, sizeof(s->name), "thermal_%s", type);
                    free(type);
                } else {
                    snprintf(s->name, sizeof(s->name), "%s", entry->d_name);
                }
                
                s->value = temp / 1000.0f;
                strcpy(s->unit, "°C");
                s->type = SENSOR_TYPE_CPU_TEMP;
                s->enabled = 1;
                s->priority = SENSOR_PRIO_NORMAL;
                
                update_sensor_history(count, s->value);
                count++;
            }
        }
        closedir(dir);
    }
    
    // ===== 2. ДАТЧИКИ ПИТАНИЯ (sysfs) =====
    dir = opendir(SENSOR_POWER_PATH);
    if (dir != NULL) {
        struct dirent* entry;
        while ((entry = readdir(dir)) != NULL && count < max_count) {
            if (entry->d_name[0] == '.') continue;
            
            char path[MAX_PATH_LEN];
            
            snprintf(path, sizeof(path), "%s/%s/capacity", SENSOR_POWER_PATH, entry->d_name);
            long cap = safe_read_long(path);
            if (cap >= 0 && cap <= 100) {
                SensorDisplayInfo* s = &sensors[count];
                memset(s, 0, sizeof(SensorDisplayInfo));
                snprintf(s->name, sizeof(s->name), "%s_capacity", entry->d_name);
                s->value = cap;
                strcpy(s->unit, "%");
                s->type = SENSOR_TYPE_CAPACITY;
                s->enabled = 1;
                s->priority = SENSOR_PRIO_NORMAL;
                update_sensor_history(count, s->value);
                count++;
            }
            
            snprintf(path, sizeof(path), "%s/%s/voltage_now", SENSOR_POWER_PATH, entry->d_name);
            long volt = safe_read_long(path);
            if (volt > 0 && count < max_count) {
                SensorDisplayInfo* s = &sensors[count];
                memset(s, 0, sizeof(SensorDisplayInfo));
                snprintf(s->name, sizeof(s->name), "%s_voltage", entry->d_name);
                s->value = volt / 1000000.0f;
                strcpy(s->unit, "V");
                s->type = SENSOR_TYPE_VOLTAGE;
                s->enabled = 1;
                s->priority = SENSOR_PRIO_NORMAL;
                update_sensor_history(count, s->value);
                count++;
            }
            
            snprintf(path, sizeof(path), "%s/%s/current_now", SENSOR_POWER_PATH, entry->d_name);
            long current = safe_read_long(path);
            if (current != 0 && count < max_count) {
                SensorDisplayInfo* s = &sensors[count];
                memset(s, 0, sizeof(SensorDisplayInfo));
                snprintf(s->name, sizeof(s->name), "%s_current", entry->d_name);
                s->value = current / 1000.0f;
                strcpy(s->unit, "mA");
                s->type = SENSOR_TYPE_CURRENT;
                s->enabled = 1;
                s->priority = SENSOR_PRIO_NORMAL;
                update_sensor_history(count, s->value);
                count++;
            }
            
            snprintf(path, sizeof(path), "%s/%s/temp", SENSOR_POWER_PATH, entry->d_name);
            long temp = safe_read_long(path);
            if (temp > 0 && count < max_count) {
                SensorDisplayInfo* s = &sensors[count];
                memset(s, 0, sizeof(SensorDisplayInfo));
                snprintf(s->name, sizeof(s->name), "%s_temp", entry->d_name);
                s->value = temp / 10.0f;
                strcpy(s->unit, "°C");
                s->type = SENSOR_TYPE_BATTERY_TEMP;
                s->enabled = 1;
                s->priority = SENSOR_PRIO_NORMAL;
                update_sensor_history(count, s->value);
                count++;
            }
        }
        closedir(dir);
    }
    
    // ===== 3. IIO ДАТЧИКИ =====
    int iio_count = scan_iio_devices();
    for (int dev = 0; dev < iio_count && count < max_count; dev++) {
        const char* iio_sensors[] = {
            "in_temp_raw", "in_humidityrelative_raw", "in_pressure_raw",
            "in_illuminance_raw", "in_proximity_raw",
            "in_accel_x_raw", "in_accel_y_raw", "in_accel_z_raw",
            "in_anglvel_x_raw", "in_anglvel_y_raw", "in_anglvel_z_raw",
            "in_magn_x_raw", "in_magn_y_raw", "in_magn_z_raw",
            NULL
        };
        
        for (int s = 0; iio_sensors[s] != NULL && count < max_count; s++) {
            char path[MAX_PATH_LEN];
            snprintf(path, sizeof(path), "%s/iio:device%d/%s", 
                     SENSOR_IIO_PATH, dev, iio_sensors[s]);
            
            size_t dummy = 0;
            char* value_str = safe_read_file(path, &dummy);
            if (value_str != NULL) {
                long raw = atol(value_str);
                free(value_str);
                
                if (raw != 0) {
                    SensorDisplayInfo* sens = &sensors[count];
                    memset(sens, 0, sizeof(SensorDisplayInfo));
                    
                    if (strstr(iio_sensors[s], "temp")) {
                        snprintf(sens->name, sizeof(sens->name), "iio_temp%d", dev);
                        sens->value = raw / 1000.0f;
                        strcpy(sens->unit, "°C");
                        sens->type = SENSOR_TYPE_CPU_TEMP;
                    } else if (strstr(iio_sensors[s], "humidity")) {
                        snprintf(sens->name, sizeof(sens->name), "iio_humidity%d", dev);
                        sens->value = raw / 1000.0f;
                        strcpy(sens->unit, "%");
                        sens->type = SENSOR_TYPE_HUMIDITY;
                    } else if (strstr(iio_sensors[s], "pressure")) {
                        snprintf(sens->name, sizeof(sens->name), "iio_pressure%d", dev);
                        sens->value = raw / 1000.0f;
                        strcpy(sens->unit, "hPa");
                        sens->type = SENSOR_TYPE_PRESSURE;
                    } else if (strstr(iio_sensors[s], "illuminance")) {
                        snprintf(sens->name, sizeof(sens->name), "iio_light%d", dev);
                        sens->value = raw;
                        strcpy(sens->unit, "lux");
                        sens->type = SENSOR_TYPE_LIGHT;
                    } else if (strstr(iio_sensors[s], "proximity")) {
                        snprintf(sens->name, sizeof(sens->name), "iio_proximity%d", dev);
                        sens->value = raw;
                        strcpy(sens->unit, "cm");
                        sens->type = SENSOR_TYPE_PROXIMITY;
                    } else if (strstr(iio_sensors[s], "accel")) {
                        snprintf(sens->name, sizeof(sens->name), "iio_accel_%c%d", 
                                 iio_sensors[s][strlen(iio_sensors[s])-5], dev);
                        sens->value = raw / 1000.0f;
                        strcpy(sens->unit, "m/s²");
                        sens->type = SENSOR_TYPE_ACCELEROMETER;
                    } else if (strstr(iio_sensors[s], "anglvel")) {
                        snprintf(sens->name, sizeof(sens->name), "iio_gyro_%c%d",
                                 iio_sensors[s][strlen(iio_sensors[s])-5], dev);
                        sens->value = raw / 1000.0f;
                        strcpy(sens->unit, "rad/s");
                        sens->type = SENSOR_TYPE_GYROSCOPE;
                    } else if (strstr(iio_sensors[s], "magn")) {
                        snprintf(sens->name, sizeof(sens->name), "iio_magn_%c%d",
                                 iio_sensors[s][strlen(iio_sensors[s])-5], dev);
                        sens->value = raw / 1000.0f;
                        strcpy(sens->unit, "uT");
                        sens->type = SENSOR_TYPE_MAGNETOMETER;
                    } else {
                        continue;
                    }
                    
                    sens->enabled = 1;
                    sens->priority = SENSOR_PRIO_NORMAL;
                    update_sensor_history(count, sens->value);
                    count++;
                }
            }
        }
    }
    
    // ===== 4. HWMON ДАТЧИКИ =====
    int hwmon_count = scan_hwmon_devices();
    for (int dev = 0; dev < hwmon_count && count < max_count; dev++) {
        char path[MAX_PATH_LEN];
        
        for (int t = 1; t <= 10 && count < max_count; t++) {
            snprintf(path, sizeof(path), "%s/hwmon%d/temp%d_input", 
                     SENSOR_HWMON_PATH, dev, t);
            
            long temp = safe_read_long(path);
            if (temp > 0) {
                SensorDisplayInfo* s = &sensors[count];
                memset(s, 0, sizeof(SensorDisplayInfo));
                
                char name_path[MAX_PATH_LEN];
                snprintf(name_path, sizeof(name_path), "%s/hwmon%d/name", 
                         SENSOR_HWMON_PATH, dev);
                
                size_t dummy = 0;
                char* name = safe_read_file(name_path, &dummy);
                if (name != NULL) {
                    snprintf(s->name, sizeof(s->name), "%s_temp%d", name, t);
                    free(name);
                } else {
                    snprintf(s->name, sizeof(s->name), "hwmon%d_temp%d", dev, t);
                }
                
                s->value = temp / 1000.0f;
                strcpy(s->unit, "°C");
                s->type = SENSOR_TYPE_CPU_TEMP;
                s->enabled = 1;
                s->priority = SENSOR_PRIO_NORMAL;
                update_sensor_history(count, s->value);
                count++;
            }
        }
    }
    
    // ===== 5. TERMUX-API ДАТЧИКИ (НОВЫЕ!) =====
    get_termux_sensors(sensors, max_count, &count);
    get_termux_battery_sensors(sensors, max_count, &count);
    
    return count;
}

int get_all_sensors(SensorDetailedInfo* sensors, int max_count) {
    if (sensors == NULL || max_count <= 0) return 0;
    
    SensorDisplayInfo display_sensors[MAX_SENSORS];
    int display_count = get_sensor_info(display_sensors, max_count);
    
    for (int i = 0; i < display_count && i < max_count; i++) {
        SensorDetailedInfo* out = &sensors[i];
        SensorDisplayInfo* in = &display_sensors[i];
        
        memset(out, 0, sizeof(SensorDetailedInfo));
        
        strncpy(out->name, in->name, sizeof(out->name) - 1);
        out->name[sizeof(out->name) - 1] = '\0';
        
        out->value = in->value;
        out->min_value = out->value;
        out->max_value = out->value;
        out->avg_value = out->value;
        
        strncpy(out->unit, in->unit, sizeof(out->unit) - 1);
        out->unit[sizeof(out->unit) - 1] = '\0';
        
        out->type = in->type;
        out->class_type = SENSOR_CLASS_UNKNOWN;
        out->priority = in->priority;
        
        out->timestamp = time(NULL);
        out->last_update = out->timestamp;
        out->enabled = in->enabled;
        out->available = 1;
        
        out->trend = get_sensor_trend(i, 60);
    }
    
    return display_count;
}

int get_sensor_by_name(const char* name, SensorDetailedInfo* sensor) {
    if (name == NULL || sensor == NULL) return 0;
    
    SensorDetailedInfo sensors[MAX_SENSORS];
    int count = get_all_sensors(sensors, MAX_SENSORS);
    
    for (int i = 0; i < count; i++) {
        if (strcmp(sensors[i].name, name) == 0) {
            memcpy(sensor, &sensors[i], sizeof(SensorDetailedInfo));
            return 1;
        }
    }
    
    return 0;
}

int get_sensors_by_class(SensorClass class_type, SensorDetailedInfo* sensors, int max_count) {
    if (sensors == NULL || max_count <= 0) return 0;
    
    SensorDetailedInfo all_sensors[MAX_SENSORS];
    int total = get_all_sensors(all_sensors, MAX_SENSORS);
    int count = 0;
    
    for (int i = 0; i < total && count < max_count; i++) {
        if (all_sensors[i].class_type == class_type) {
            memcpy(&sensors[count], &all_sensors[i], sizeof(SensorDetailedInfo));
            count++;
        }
    }
    
    return count;
}

int get_sensors_by_type(SensorType type, SensorDetailedInfo* sensors, int max_count) {
    if (sensors == NULL || max_count <= 0) return 0;
    
    SensorDetailedInfo all_sensors[MAX_SENSORS];
    int total = get_all_sensors(all_sensors, MAX_SENSORS);
    int count = 0;
    
    for (int i = 0; i < total && count < max_count; i++) {
        if (all_sensors[i].type == type) {
            memcpy(&sensors[count], &all_sensors[i], sizeof(SensorDetailedInfo));
            count++;
        }
    }
    
    return count;
}

int get_thermal_sensors(SensorDetailedInfo* sensors, int max_count) {
    return get_sensors_by_class(SENSOR_CLASS_THERMAL, sensors, max_count);
}

int get_motion_sensors(SensorDetailedInfo* sensors, int max_count) {
    return get_sensors_by_class(SENSOR_CLASS_MOTION, sensors, max_count);
}

int get_environment_sensors(SensorDetailedInfo* sensors, int max_count) {
    return get_sensors_by_class(SENSOR_CLASS_ENVIRONMENT, sensors, max_count);
}

float get_sensor_trend_by_name(const char* name, int seconds) {
    (void)seconds;
    
    SensorDetailedInfo sensor;
    if (get_sensor_by_name(name, &sensor)) {
        return sensor.trend;
    }
    return 0;
}

int get_sensor_count(void) {
    SensorDisplayInfo sensors[MAX_SENSORS];
    return get_sensor_info(sensors, MAX_SENSORS);
}

int get_enabled_sensor_count(void) {
    SensorDetailedInfo sensors[MAX_SENSORS];
    int count = get_all_sensors(sensors, MAX_SENSORS);
    int enabled = 0;
    
    for (int i = 0; i < count; i++) {
        if (sensors[i].enabled) enabled++;
    }
    
    return enabled;
}

const char* sensor_type_string(SensorType type) {
    switch (type) {
        case SENSOR_TYPE_UNKNOWN: return "Unknown";
        case SENSOR_TYPE_CPU_TEMP: return "CPU Temperature";
        case SENSOR_TYPE_GPU_TEMP: return "GPU Temperature";
        case SENSOR_TYPE_BATTERY_TEMP: return "Battery Temperature";
        case SENSOR_TYPE_AMBIENT_TEMP: return "Ambient Temperature";
        case SENSOR_TYPE_SKIN_TEMP: return "Skin Temperature";
        case SENSOR_TYPE_VOLTAGE: return "Voltage";
        case SENSOR_TYPE_CURRENT: return "Current";
        case SENSOR_TYPE_POWER: return "Power";
        case SENSOR_TYPE_ENERGY: return "Energy";
        case SENSOR_TYPE_CAPACITY: return "Capacity";
        case SENSOR_TYPE_ACCELEROMETER: return "Accelerometer";
        case SENSOR_TYPE_GYROSCOPE: return "Gyroscope";
        case SENSOR_TYPE_MAGNETOMETER: return "Magnetometer";
        case SENSOR_TYPE_LIGHT: return "Light";
        case SENSOR_TYPE_PROXIMITY: return "Proximity";
        case SENSOR_TYPE_PRESSURE: return "Pressure";
        case SENSOR_TYPE_HUMIDITY: return "Humidity";
        default: return "Other";
    }
}

const char* sensor_priority_string(SensorPriority priority) {
    switch (priority) {
        case SENSOR_PRIO_LOW: return "Low";
        case SENSOR_PRIO_NORMAL: return "Normal";
        case SENSOR_PRIO_HIGH: return "High";
        case SENSOR_PRIO_CRITICAL: return "Critical";
        default: return "Unknown";
    }
}

void format_sensor_info(const SensorDetailedInfo* sensor, char* buffer, size_t buffer_size) {
    if (sensor == NULL || buffer == NULL || buffer_size == 0) return;
    
    snprintf(buffer, buffer_size,
             "📊 Датчик: %s\n"
             "   Тип: %s\n"
             "   Значение: %.2f %s\n"
             "   Мин: %.2f %s | Макс: %.2f %s | Сред: %.2f %s\n"
             "   Приоритет: %s | Статус: %s\n"
             "   Тренд: %+.2f",
             sensor->name,
             sensor_type_string(sensor->type),
             sensor->value, sensor->unit,
             sensor->min_value, sensor->unit,
             sensor->max_value, sensor->unit,
             sensor->avg_value, sensor->unit,
             sensor_priority_string(sensor->priority),
             sensor->enabled ? "Включён" : "Выключен",
             sensor->trend);
}

void format_sensor_display(const SensorDisplayInfo* sensor, char* buffer, size_t buffer_size) {
    if (sensor == NULL || buffer == NULL || buffer_size == 0) return;
    
    const char* type_str = sensor_type_string(sensor->type);
    
    snprintf(buffer, buffer_size, "%s [%s]: %.2f %s",
             sensor->name, type_str, sensor->value, sensor->unit);
}

// ==================== КОНЕЦ ФАЙЛА ====================
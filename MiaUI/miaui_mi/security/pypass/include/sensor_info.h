//╔═════════════════════════════╗                       
//║  Link: t.me/FrontendVSCode                       ║                         
//║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║    
//║  lang: C                                         ║                     
//║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║                      
//║  build:3.10.15                                   ║
//║  files: sensor_info.h                            ║    
//╚═════════════════════════════╝



#ifndef SENSOR_INFO_H
#define SENSOR_INFO_H

// ==================== ЗАЩИТА ОТ ПОВТОРНОГО ВКЛЮЧЕНИЯ ====================
#ifdef SENSOR_INFO_H_INCLUDED
#error "sensor_info.h включен дважды!"
#endif
#define SENSOR_INFO_H_INCLUDED

// ==================== СТАНДАРТНЫЕ БИБЛИОТЕКИ ====================
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <math.h>
#include <time.h>
#include <errno.h>

// ==================== ОБЩИЕ ОПРЕДЕЛЕНИЯ ====================
#ifndef MAX_SENSORS
#define MAX_SENSORS 64
#endif

#ifndef MAX_NAME
#define MAX_NAME 64
#endif

#ifndef MAX_PATH
#define MAX_PATH 256
#endif

#ifndef MAX_HISTORY
#define MAX_HISTORY 60
#endif

#ifndef MAX_TYPES
#define MAX_TYPES 16
#endif

// ==================== ТИПЫ ДАТЧИКОВ ====================
typedef enum {
    SENSOR_TYPE_UNKNOWN = 0,
    
    // Температура
    SENSOR_TYPE_CPU_TEMP,           // температура CPU
    SENSOR_TYPE_GPU_TEMP,           // температура GPU
    SENSOR_TYPE_BATTERY_TEMP,       // температура батареи
    SENSOR_TYPE_AMBIENT_TEMP,       // температура окружающей среды
    SENSOR_TYPE_SKIN_TEMP,          // температура корпуса
    SENSOR_TYPE_PMIC_TEMP,          // температура PMIC
    SENSOR_TYPE_DDR_TEMP,           // температура памяти
    SENSOR_TYPE_WIFI_TEMP,          // температура Wi-Fi
    SENSOR_TYPE_CHARGER_TEMP,       // температура зарядки
    
    // Электричество
    SENSOR_TYPE_VOLTAGE,            // напряжение
    SENSOR_TYPE_CURRENT,            // ток
    SENSOR_TYPE_POWER,              // мощность
    SENSOR_TYPE_ENERGY,             // энергия
    SENSOR_TYPE_CAPACITY,           // ёмкость
    SENSOR_TYPE_RESISTANCE,         // сопротивление
    SENSOR_TYPE_FREQUENCY_ELEC,     // частота электрическая
    
    // Движение и положение
    SENSOR_TYPE_ACCELEROMETER,      // акселерометр
    SENSOR_TYPE_GYROSCOPE,          // гироскоп
    SENSOR_TYPE_MAGNETOMETER,       // магнитометр
    SENSOR_TYPE_GRAVITY,            // гравитация
    SENSOR_TYPE_LINEAR_ACCEL,       // линейное ускорение
    SENSOR_TYPE_ROTATION_VECTOR,    // вектор вращения
    SENSOR_TYPE_ORIENTATION,        // ориентация
    SENSOR_TYPE_STEP_COUNTER,       // счётчик шагов
    SENSOR_TYPE_STEP_DETECTOR,      // детектор шагов
    SENSOR_TYPE_SIGNIFICANT_MOTION, // значительное движение
    
    // Окружение
    SENSOR_TYPE_LIGHT,              // освещение
    SENSOR_TYPE_PROXIMITY,          // приближение
    SENSOR_TYPE_PRESSURE,           // давление
    SENSOR_TYPE_HUMIDITY,           // влажность
    SENSOR_TYPE_GAS,                // газ
    SENSOR_TYPE_PM1,                // частицы 1μm
    SENSOR_TYPE_PM2_5,              // частицы 2.5μm
    SENSOR_TYPE_PM10,               // частицы 10μm
    SENSOR_TYPE_CO2,                // CO2
    SENSOR_TYPE_TVOC,               // летучие органические соединения
    SENSOR_TYPE_OZONE,              // озон
    SENSOR_TYPE_DUST,               // пыль
    SENSOR_TYPE_UV,                 // ультрафиолет
    SENSOR_TYPE_IR,                 // инфракрасное излучение
    
    // Здоровье
    SENSOR_TYPE_HEART_RATE,         // пульс
    SENSOR_TYPE_SPO2,               // насыщение кислородом
    SENSOR_TYPE_BLOOD_PRESSURE,     // давление крови
    SENSOR_TYPE_BLOOD_GLUCOSE,      // уровень сахара
    SENSOR_TYPE_ECG,                // ЭКГ
    SENSOR_TYPE_EEG,                // ЭЭГ
    SENSOR_TYPE_EMG,                // ЭМГ
    SENSOR_TYPE_BREATH_RATE,        // частота дыхания
    
    // Положение
    SENSOR_TYPE_GPS_LAT,            // широта GPS
    SENSOR_TYPE_GPS_LON,            // долгота GPS
    SENSOR_TYPE_GPS_ALT,            // высота GPS
    SENSOR_TYPE_GPS_SPEED,          // скорость GPS
    SENSOR_TYPE_GPS_ACCURACY,       // точность GPS
    SENSOR_TYPE_GPS_BEARING,        // направление GPS
    
    // Частота
    SENSOR_TYPE_FREQUENCY,          // частота
    SENSOR_TYPE_RPM,                // обороты в минуту
    SENSOR_TYPE_PULSE,              // пульсации
    SENSOR_TYPE_VIBRATION,          // вибрация
    
    // Другое
    SENSOR_TYPE_ANGLE,              // угол
    SENSOR_TYPE_DISTANCE,           // расстояние
    SENSOR_TYPE_VELOCITY,           // скорость
    SENSOR_TYPE_ACCELERATION,       // ускорение
    SENSOR_TYPE_FORCE,              // сила
    SENSOR_TYPE_TORQUE,             // крутящий момент
    SENSOR_TYPE_FLOW,               // поток
    SENSOR_TYPE_LEVEL,              // уровень
    SENSOR_TYPE_COUNT               // счётчик
} SensorType;

// ==================== КЛАССЫ ДАТЧИКОВ ====================
typedef enum {
    SENSOR_CLASS_UNKNOWN = 0,
    SENSOR_CLASS_THERMAL,           // термические
    SENSOR_CLASS_ELECTRICAL,        // электрические
    SENSOR_CLASS_MOTION,            // движения
    SENSOR_CLASS_POSITION,          // положения
    SENSOR_CLASS_ENVIRONMENT,       // окружающей среды
    SENSOR_CLASS_HEALTH,            // здоровья
    SENSOR_CLASS_LOCATION,          // местоположения
    SENSOR_CLASS_FREQUENCY,         // частоты
    SENSOR_CLASS_OPTICAL,           // оптические
    SENSOR_CLASS_ACOUSTIC,          // акустические
    SENSOR_CLASS_BIOMETRIC,         // биометрические
    SENSOR_CLASS_CHEMICAL,          // химические
    SENSOR_CLASS_MECHANICAL,        // механические
    SENSOR_CLASS_RADIATION,         // радиация
    SENSOR_CLASS_OTHER              // другие
} SensorClass;

// ==================== ПРИОРИТЕТЫ ДАТЧИКОВ ====================
typedef enum {
    SENSOR_PRIO_LOW = 0,
    SENSOR_PRIO_NORMAL,
    SENSOR_PRIO_HIGH,
    SENSOR_PRIO_CRITICAL,
    SENSOR_PRIO_EMERGENCY
} SensorPriority;

// ==================== РЕЖИМЫ РАБОТЫ ====================
typedef enum {
    SENSOR_MODE_UNKNOWN = 0,
    SENSOR_MODE_ONE_SHOT,
    SENSOR_MODE_ON_CHANGE,
    SENSOR_MODE_CONTINUOUS,
    SENSOR_MODE_FIFO
} SensorMode;

// ==================== ИСТОЧНИКИ ДАННЫХ ====================
typedef enum {
    SENSOR_SOURCE_UNKNOWN = 0,
    SENSOR_SOURCE_SYSFS,
    SENSOR_SOURCE_IIO,
    SENSOR_SOURCE_HWMON,
    SENSOR_SOURCE_THERMAL,
    SENSOR_SOURCE_POWER_SUPPLY,
    SENSOR_SOURCE_INPUT,
    SENSOR_SOURCE_HID,
    SENSOR_SOURCE_ANDROID_SENSOR
} SensorSource;

// ==================== ИНФОРМАЦИЯ О ДАТЧИКЕ ====================
typedef struct {
    // Основная информация
    int id;                                     // ID датчика
    char name[MAX_NAME];                        // название датчика
    char path[MAX_PATH];                        // путь в sysfs
    SensorType type;                            // тип датчика
    SensorClass class_type;                      // класс датчика
    SensorPriority priority;                     // приоритет
    SensorSource source;                         // источник данных
    SensorMode mode;                             // режим работы
    
    // Текущее значение
    float value;                                // текущее значение
    float min_value;                            // минимальное значение
    float max_value;                            // максимальное значение
    float avg_value;                            // среднее значение
    float raw_value;                            // сырое значение
    
    // Единицы измерения
    char unit[MAX_NAME];                        // единица измерения
    char unit_symbol[8];                        // символ единицы
    
    // Точность
    float accuracy;                             // точность
    float resolution;                           // разрешение
    float offset;                               // смещение
    float scale;                                // масштаб
    
    // Время
    time_t timestamp;                           // временная метка
    time_t last_update;                         // последнее обновление
    int update_rate;                            // частота обновления (ms)
    int min_delay;                              // минимальная задержка (us)
    int max_delay;                              // максимальная задержка (us)
    
    // Статус
    int enabled;                                // включён
    int available;                              // доступен
    int faulty;                                 // ошибка
    int calibrated;                             // откалиброван
    char status[32];                            // статус
    
    // Дополнительно
    char vendor[MAX_NAME];                      // производитель
    char model[MAX_NAME];                       // модель
    char version[MAX_NAME];                     // версия
    char serial[MAX_NAME];                      // серийный номер
    int channel;                                // канал
    int index;                                  // индекс
    int batch_count;                            // количество в пакете
    
    // История
    float history[MAX_HISTORY];                  // история значений
    int history_index;                           // индекс в истории
    int history_size;                            // размер истории
    float trend;                                 // тренд (рост/падение)
    float min_trend;                             // минимальный тренд
    float max_trend;                             // максимальный тренд
    
    // Пороги
    float warning_min;                           // порог предупреждения мин
    float warning_max;                           // порог предупреждения макс
    float critical_min;                          // критический порог мин
    float critical_max;                          // критический порог макс
    int threshold_exceeded;                       // превышение порога
    
    // Статистика
    float avg_1min;                              // среднее за 1 минуту
    float avg_5min;                              // среднее за 5 минут
    float avg_15min;                             // среднее за 15 минут
    float min_recorded;                          // минимум за всё время
    float max_recorded;                          // максимум за всё время
    time_t min_time;                              // время минимума
    time_t max_time;                              // время максимума
    int sample_count;                             // количество измерений
} SensorDetailedInfo;

// ==================== ДАТЧИК ДЛЯ ОТОБРАЖЕНИЯ ====================
typedef struct {
    int id;                                      // ID датчика
    char name[MAX_NAME];                         // название
    float value;                                 // значение
    char unit[MAX_NAME];                         // единица
    SensorType type;                             // тип
    int enabled;                                 // включён
    SensorPriority priority;                      // приоритет
    int has_warning;                              // есть предупреждение
    int has_critical;                             // есть критическое
    char status_char;                             // символ статуса
} SensorDisplayInfo;

// ==================== СТАТИСТИКА ДАТЧИКОВ ====================
typedef struct {
    int total_sensors;                           // всего датчиков
    int enabled_sensors;                          // включённых
    int faulty_sensors;                           // ошибочных
    int warning_sensors;                           // с предупреждениями
    int critical_sensors;                          // с критическими
    
    int thermal_sensors;                           // температурных
    int electrical_sensors;                        // электрических
    int motion_sensors;                            // движения
    int position_sensors;                          // положения
    int environment_sensors;                       // окружения
    int health_sensors;                            // здоровья
    int location_sensors;                          // местоположения
    
    float avg_temperature;                         // средняя температура
    float max_temperature;                          // максимальная
    float min_temperature;                          // минимальная
    char hottest_sensor[MAX_NAME];                  // самый горячий датчик
    char coldest_sensor[MAX_NAME];                  // самый холодный датчик
    
    float total_power_consumption;                  // общее потребление
    float total_energy;                              // общая энергия
    float battery_capacity;                          // ёмкость батареи
} SensorStatistics;

// ==================== СОБЫТИЕ ДАТЧИКА ====================
typedef struct {
    int sensor_id;                                 // ID датчика
    SensorType type;                               // тип
    float value;                                   // значение
    float threshold;                               // порог
    time_t timestamp;                              // время
    char description[128];                         // описание
} SensorEvent;

// ==================== ПРОТОТИПЫ ФУНКЦИЙ ====================

#ifdef __cplusplus
extern "C" {
#endif

// ===== Основные функции =====
int get_sensor_info(SensorDisplayInfo* sensors, int max_count);
int get_all_sensors(SensorDetailedInfo* sensors, int max_count);
int get_sensor_by_id(int id, SensorDetailedInfo* sensor);
int get_sensor_by_name(const char* name, SensorDetailedInfo* sensor);
int get_sensor_by_path(const char* path, SensorDetailedInfo* sensor);

// ===== По классам и типам =====
int get_sensors_by_class(SensorClass class_type, SensorDetailedInfo* sensors, int max_count);
int get_sensors_by_type(SensorType type, SensorDetailedInfo* sensors, int max_count);
int get_sensors_by_source(SensorSource source, SensorDetailedInfo* sensors, int max_count);
int get_thermal_sensors(SensorDetailedInfo* sensors, int max_count);
int get_motion_sensors(SensorDetailedInfo* sensors, int max_count);
int get_environment_sensors(SensorDetailedInfo* sensors, int max_count);
int get_health_sensors(SensorDetailedInfo* sensors, int max_count);
int get_location_sensors(SensorDetailedInfo* sensors, int max_count);

// ===== Управление =====
int enable_sensor(int id);
int disable_sensor(int id);
int enable_sensor_by_name(const char* name);
int disable_sensor_by_name(const char* name);
int calibrate_sensor(int id, float offset, float scale);
int reset_sensor(int id);
int set_sensor_threshold(int id, float warning_min, float warning_max, 
                        float critical_min, float critical_max);
int set_sensor_update_rate(int id, int rate_ms);

// ===== Мониторинг =====
int watch_sensor(int id, SensorDetailedInfo* info, int interval_ms);
int watch_all_sensors(SensorDetailedInfo* sensors, int max_count, int interval_ms);
int get_sensor_events(SensorEvent* events, int max_count);
float get_sensor_trend(int id, int seconds);
float get_sensor_trend_by_name(const char* name, int seconds);
int sensor_is_stable(int id, float variance_percent, int seconds);

// ===== Статистика =====
SensorStatistics get_sensor_statistics(void);
int get_sensor_count(void);
int get_enabled_sensor_count(void);
int get_faulty_sensor_count(void);
float get_average_temperature(void);
float get_total_power(void);
float get_battery_capacity(void);

// ===== Поиск =====
int find_sensor_by_type(SensorType type, SensorDetailedInfo* sensors, int max_count);
int find_sensor_by_value_range(float min, float max, SensorDetailedInfo* sensors, int max_count);
int find_sensors_with_warning(SensorDetailedInfo* sensors, int max_count);
int find_sensors_with_critical(SensorDetailedInfo* sensors, int max_count);
int find_sensors_by_name_pattern(const char* pattern, SensorDetailedInfo* sensors, int max_count);

// ===== Форматирование =====
const char* sensor_type_string(SensorType type);
const char* sensor_class_string(SensorClass class_type);
const char* sensor_priority_string(SensorPriority priority);
const char* sensor_source_string(SensorSource source);
const char* sensor_mode_string(SensorMode mode);
const char* sensor_status_string(const SensorDetailedInfo* sensor);
char sensor_status_char(const SensorDetailedInfo* sensor);
void format_sensor_info(const SensorDetailedInfo* sensor, char* buffer, size_t size);
void format_sensor_display(const SensorDisplayInfo* sensor, char* buffer, size_t size);
void format_sensor_event(const SensorEvent* event, char* buffer, size_t size);
void format_sensor_value(char* buffer, size_t size, float value, const char* unit);

// ===== Утилиты =====
int sensor_is_critical(const SensorDetailedInfo* sensor);
int sensor_needs_attention(const SensorDetailedInfo* sensor);
int sensor_has_warning(const SensorDetailedInfo* sensor);
float convert_sensor_value(float value, const char* from_unit, const char* to_unit);
int compare_sensors_by_priority(const void* a, const void* b);
int compare_sensors_by_value(const void* a, const void* b);
int compare_sensors_by_name(const void* a, const void* b);

// ===== Чтение значений =====
float read_sensor_value(int id);
int read_sensor_raw(int id, long* raw);
int read_sensor_batch(int* ids, float* values, int count);

// ===== События =====
int register_sensor_callback(int id, void (*callback)(SensorEvent*));
int unregister_sensor_callback(int id);
int wait_for_sensor_event(int id, SensorEvent* event, int timeout_ms);

// ===== Энергопотребление =====
float get_sensor_power_consumption(int id);
float get_total_sensor_power(void);
int set_sensor_power_mode(int id, int low_power);

#ifdef __cplusplus
}
#endif

#endif // SENSOR_INFO_H
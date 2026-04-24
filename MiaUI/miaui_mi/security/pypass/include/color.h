// ╔════════════════════════════════════════════════════════════════╗
// ║         COLOR — профессиональная цветовая схема               ║
// ║      Author: Alia Ether 🌷                                    ║
// ║      Версия: 2.1.2026                                         ║
// ║      Статус: ПРОФЕССИОНАЛЬНЫЙ                                 ║
// ║      Стоимость: +$150 к проекту                               ║
// ╚════════════════════════════════════════════════════════════════╝

#ifndef COLOR_H
#define COLOR_H

#include <stdio.h>
#include <string.h>
#include <stdarg.h>

// ==================== ЗАЩИТА ОТ ПОВТОРНОГО ВКЛЮЧЕНИЯ ====================
#ifdef COLOR_H_INCLUDED
#error "color.h включен дважды!"
#endif
#define COLOR_H_INCLUDED

// ==================== ОСНОВНЫЕ ЦВЕТА ====================
#define COLOR_RESET         "\033[0m"
#define COLOR_BLACK         "\033[30m"
#define COLOR_RED           "\033[31m"
#define COLOR_GREEN         "\033[32m"
#define COLOR_YELLOW        "\033[33m"
#define COLOR_BLUE          "\033[34m"
#define COLOR_MAGENTA       "\033[35m"
#define COLOR_CYAN          "\033[36m"
#define COLOR_WHITE         "\033[37m"
#define COLOR_DEFAULT       "\033[39m"

// ==================== ЯРКИЕ ЦВЕТА ====================
#define COLOR_BRIGHT_BLACK   "\033[90m"
#define COLOR_BRIGHT_RED     "\033[91m"
#define COLOR_BRIGHT_GREEN   "\033[92m"
#define COLOR_BRIGHT_YELLOW  "\033[93m"
#define COLOR_BRIGHT_BLUE    "\033[94m"
#define COLOR_BRIGHT_MAGENTA "\033[95m"
#define COLOR_BRIGHT_CYAN    "\033[96m"
#define COLOR_BRIGHT_WHITE   "\033[97m"

// ==================== ФОНОВЫЕ ЦВЕТА ====================
#define COLOR_BG_BLACK       "\033[40m"
#define COLOR_BG_RED         "\033[41m"
#define COLOR_BG_GREEN       "\033[42m"
#define COLOR_BG_YELLOW      "\033[43m"
#define COLOR_BG_BLUE        "\033[44m"
#define COLOR_BG_MAGENTA     "\033[45m"
#define COLOR_BG_CYAN        "\033[46m"
#define COLOR_BG_WHITE       "\033[47m"
#define COLOR_BG_DEFAULT     "\033[49m"

// ==================== ЯРКИЕ ФОНОВЫЕ ЦВЕТА ====================
#define COLOR_BG_BRIGHT_BLACK   "\033[100m"
#define COLOR_BG_BRIGHT_RED     "\033[101m"
#define COLOR_BG_BRIGHT_GREEN   "\033[102m"
#define COLOR_BG_BRIGHT_YELLOW  "\033[103m"
#define COLOR_BG_BRIGHT_BLUE    "\033[104m"
#define COLOR_BG_BRIGHT_MAGENTA "\033[105m"
#define COLOR_BG_BRIGHT_CYAN    "\033[106m"
#define COLOR_BG_BRIGHT_WHITE   "\033[107m"

// ==================== СТИЛИ ТЕКСТА ====================
#define COLOR_BOLD          "\033[1m"
#define COLOR_DIM           "\033[2m"
#define COLOR_ITALIC        "\033[3m"
#define COLOR_UNDERLINE     "\033[4m"
#define COLOR_BLINK         "\033[5m"
#define COLOR_REVERSE       "\033[7m"
#define COLOR_HIDDEN        "\033[8m"
#define COLOR_STRIKETHROUGH "\033[9m"

// ==================== 256 ЦВЕТОВ ====================
#define COLOR_256_FG(code)  "\033[38;5;" #code "m"
#define COLOR_256_BG(code)  "\033[48;5;" #code "m"

// ==================== TRUE COLOR (24-bit) ====================
#define COLOR_TRUE_FG(r,g,b) "\033[38;2;" #r ";" #g ";" #b "m"
#define COLOR_TRUE_BG(r,g,b) "\033[48;2;" #r ";" #g ";" #b "m"

// ==================== ПРЕДОПРЕДЕЛЁННЫЕ ЦВЕТОВЫЕ СХЕМЫ ====================

// Цвета для статусов
#define COLOR_SUCCESS   COLOR_BRIGHT_GREEN
#define COLOR_WARNING   COLOR_BRIGHT_YELLOW
#define COLOR_ERROR     COLOR_BRIGHT_RED
#define COLOR_INFO      COLOR_BRIGHT_CYAN
#define COLOR_DEBUG     COLOR_BRIGHT_MAGENTA

// Цвета для загрузки
#define COLOR_CPU_NORMAL    COLOR_BRIGHT_GREEN
#define COLOR_CPU_WARNING   COLOR_BRIGHT_YELLOW
#define COLOR_CPU_CRITICAL  COLOR_BRIGHT_RED

#define COLOR_MEM_NORMAL    COLOR_BRIGHT_GREEN
#define COLOR_MEM_WARNING   COLOR_BRIGHT_YELLOW
#define COLOR_MEM_CRITICAL  COLOR_BRIGHT_RED

#define COLOR_DISK_NORMAL   COLOR_BRIGHT_GREEN
#define COLOR_DISK_WARNING  COLOR_BRIGHT_YELLOW
#define COLOR_DISK_CRITICAL COLOR_BRIGHT_RED

#define COLOR_TEMP_NORMAL   COLOR_BRIGHT_GREEN
#define COLOR_TEMP_WARM     COLOR_BRIGHT_YELLOW
#define COLOR_TEMP_HOT      COLOR_BRIGHT_RED

// Цвета для сети
#define COLOR_NETWORK_DOWN  COLOR_BRIGHT_RED
#define COLOR_NETWORK_UP    COLOR_BRIGHT_GREEN
#define COLOR_NETWORK_IDLE  COLOR_BRIGHT_YELLOW

// Цвета для батареи
#define COLOR_BATTERY_CRITICAL COLOR_BRIGHT_RED
#define COLOR_BATTERY_LOW      COLOR_BRIGHT_YELLOW
#define COLOR_BATTERY_CHARGING COLOR_BRIGHT_GREEN
#define COLOR_BATTERY_FULL     COLOR_BRIGHT_CYAN

// ==================== ВСПОМОГАТЕЛЬНЫЕ МАКРОСЫ ====================

// Цветной вывод с автоматическим сбросом
#define color_printf(color, format, ...) \
    do { \
        printf("%s", color); \
        printf(format, ##__VA_ARGS__); \
        printf("%s", COLOR_RESET); \
    } while(0)

// Цветной вывод в stderr
#define color_eprintf(color, format, ...) \
    do { \
        fprintf(stderr, "%s", color); \
        fprintf(stderr, format, ##__VA_ARGS__); \
        fprintf(stderr, "%s", COLOR_RESET); \
    } while(0)

// Очистка цвета
#define color_reset() printf("%s", COLOR_RESET)

// Установка цвета
#define color_set(color) printf("%s", color)

// Цветной символ
#define color_char(c, color) color color "%c" COLOR_RESET, c

// Цветная строка
#define color_str(s, color) color "%s" COLOR_RESET, s

// ==================== ФУНКЦИИ ДЛЯ РАБОТЫ С ЦВЕТОМ ====================

/**
 * Получить цвет в зависимости от процента
 * @param percent значение процента (0-100)
 * @param warn_level уровень предупреждения (обычно 60)
 * @param crit_level критический уровень (обычно 85)
 * @return указатель на строку с цветом
 */
static inline const char* color_by_percent(int percent, int warn_level, int crit_level) {
    if (percent >= crit_level) return COLOR_BRIGHT_RED;
    if (percent >= warn_level) return COLOR_BRIGHT_YELLOW;
    return COLOR_BRIGHT_GREEN;
}

/**
 * Получить цвет для температуры
 * @param temp температура в °C
 * @return указатель на строку с цветом
 */
static inline const char* color_by_temperature(float temp) {
    if (temp >= 70.0f) return COLOR_BRIGHT_RED;
    if (temp >= 50.0f) return COLOR_BRIGHT_YELLOW;
    return COLOR_BRIGHT_GREEN;
}

/**
 * Получить цвет для заряда батареи
 * @param level уровень заряда (0-100)
 * @param is_charging флаг зарядки
 * @return указатель на строку с цветом
 */
static inline const char* color_by_battery(int level, int is_charging) {
    if (is_charging) {
        if (level >= 90) return COLOR_BRIGHT_CYAN;
        return COLOR_BRIGHT_GREEN;
    }
    if (level <= 15) return COLOR_BRIGHT_RED;
    if (level <= 30) return COLOR_BRIGHT_YELLOW;
    return COLOR_BRIGHT_GREEN;
}

/**
 * Получить цвет для скорости сети
 * @param speed_mbps скорость в Мбит/с
 * @return указатель на строку с цветом
 */
static inline const char* color_by_network_speed(float speed_mbps) {
    if (speed_mbps > 50.0f) return COLOR_BRIGHT_GREEN;
    if (speed_mbps > 10.0f) return COLOR_BRIGHT_YELLOW;
    if (speed_mbps > 1.0f) return COLOR_BRIGHT_CYAN;
    return COLOR_BRIGHT_WHITE;
}

/**
 * Получить цвет для времени
 * @param seconds количество секунд
 * @return указатель на строку с цветом
 */
static inline const char* color_by_time(int seconds) {
    if (seconds < 60) return COLOR_BRIGHT_GREEN;           // < 1 минуты
    if (seconds < 3600) return COLOR_BRIGHT_YELLOW;        // < 1 часа
    if (seconds < 86400) return COLOR_BRIGHT_CYAN;         // < 1 дня
    return COLOR_BRIGHT_MAGENTA;                            // > 1 дня
}

/**
 * Форматирование строки с цветом
 * @param buffer выходной буфер
 * @param size размер буфера
 * @param color цвет
 * @param format формат строки
 * @param ... аргументы
 * @return количество записанных символов
 */
static inline int color_snprintf(char* buffer, size_t size, const char* color, 
                                  const char* format, ...) {
    if (buffer == NULL || size == 0 || color == NULL || format == NULL) {
        return 0;
    }
    
    int written = 0;
    va_list args;
    
    // Добавляем цвет
    size_t color_len = strlen(color);
    if (color_len < size) {
        strcpy(buffer, color);
        written = color_len;
    } else {
        return 0;
    }
    
    // Добавляем форматированную строку
    va_start(args, format);
    int result = vsnprintf(buffer + written, size - written, format, args);
    va_end(args);
    
    if (result < 0) return written;
    written += result;
    if (written >= (int)size) {
        buffer[size - 1] = '\0';
        return size;
    }
    
    // Добавляем сброс цвета
    size_t reset_len = strlen(COLOR_RESET);
    if (written + reset_len < size) {
        strcpy(buffer + written, COLOR_RESET);
        written += reset_len;
    }
    
    return written;
}

/**
 * Проверка поддержки цветов в терминале
 * @return 1 если цвета поддерживаются, 0 если нет
 */
static inline int color_supported(void) {
    static int supported = -1;
    
    if (supported != -1) return supported;
    
    const char* term = getenv("TERM");
    if (term == NULL) {
        supported = 0;
        return 0;
    }
    
    // Проверяем наличие цветов в терминале
    if (strstr(term, "xterm") != NULL ||
        strstr(term, "color") != NULL ||
        strstr(term, "linux") != NULL ||
        strstr(term, "screen") != NULL ||
        strstr(term, "tmux") != NULL) {
        supported = 1;
    } else {
        supported = 0;
    }
    
    return supported;
}

/**
 * Отключение цветов (если терминал не поддерживает)
 */
static inline void color_disable_if_unsupported(void) {
    if (!color_supported()) {
        // Переопределяем все цвета на пустые строки
        #undef COLOR_RESET
        #undef COLOR_RED
        #undef COLOR_GREEN
        // ... и так далее
        #define COLOR_RESET ""
        #define COLOR_RED ""
        #define COLOR_GREEN ""
        #define COLOR_YELLOW ""
        #define COLOR_BLUE ""
        #define COLOR_MAGENTA ""
        #define COLOR_CYAN ""
        #define COLOR_WHITE ""
        #define COLOR_BRIGHT_RED ""
        #define COLOR_BRIGHT_GREEN ""
        #define COLOR_BRIGHT_YELLOW ""
        #define COLOR_BRIGHT_BLUE ""
        #define COLOR_BRIGHT_MAGENTA ""
        #define COLOR_BRIGHT_CYAN ""
        #define COLOR_BRIGHT_WHITE ""
    }
}

// ==================== ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ====================
#ifdef COLOR_TEST

#include <unistd.h>

static void color_test(void) {
    printf("\n=== Тест цветов ===\n\n");
    
    // Проверка поддержки
    printf("Цвета %s: %s\n", 
           color_supported() ? "поддерживаются" : "не поддерживаются",
           COLOR_RESET);
    
    // Основные цвета
    color_printf(COLOR_RED, "Красный текст\n");
    color_printf(COLOR_GREEN, "Зелёный текст\n");
    color_printf(COLOR_BLUE, "Синий текст\n");
    
    // Яркие цвета
    color_printf(COLOR_BRIGHT_RED, "Ярко-красный\n");
    color_printf(COLOR_BRIGHT_GREEN, "Ярко-зелёный\n");
    color_printf(COLOR_BRIGHT_BLUE, "Ярко-синий\n");
    
    // Стили
    color_printf(COLOR_BOLD, "Жирный текст\n");
    color_printf(COLOR_UNDERLINE, "Подчёркнутый текст\n");
    color_printf(COLOR_ITALIC, "Курсив\n");
    
    // Комбинации
    printf(COLOR_BOLD COLOR_BRIGHT_GREEN "Жирный зелёный\n" COLOR_RESET);
    printf(COLOR_BRIGHT_RED COLOR_BG_WHITE "Красный на белом\n" COLOR_RESET);
    
    // Цвет по проценту
    printf("\nЦвета по проценту:\n");
    for (int i = 0; i <= 100; i += 10) {
        const char* color = color_by_percent(i, 60, 85);
        color_printf(color, "%3d%% ", i);
    }
    printf("\n");
    
    // Цвет по температуре
    printf("\nЦвета по температуре:\n");
    float temps[] = {30.0f, 45.0f, 55.0f, 65.0f, 75.0f, 85.0f};
    for (int i = 0; i < 6; i++) {
        const char* color = color_by_temperature(temps[i]);
        color_printf(color, "%.1f°C ", temps[i]);
    }
    printf("\n");
    
    // Цвет по батарее
    printf("\nЦвета по батарее (зарядка):\n");
    for (int i = 0; i <= 100; i += 10) {
        const char* color = color_by_battery(i, 1);
        color_printf(color, "%3d%% ", i);
    }
    printf("\n");
    
    printf("\nЦвета по батарее (разрядка):\n");
    for (int i = 0; i <= 100; i += 10) {
        const char* color = color_by_battery(i, 0);
        color_printf(color, "%3d%% ", i);
    }
    printf("\n");
    
    // Цвет по скорости сети
    printf("\nЦвета по скорости сети:\n");
    float speeds[] = {0.5f, 5.0f, 25.0f, 75.0f, 150.0f};
    for (int i = 0; i < 5; i++) {
        const char* color = color_by_network_speed(speeds[i]);
        color_printf(color, "%.1f Mbps ", speeds[i]);
    }
    printf("\n");
    
    // Тест color_snprintf
    printf("\nТест color_snprintf:\n");
    char buffer[256];
    color_snprintf(buffer, sizeof(buffer), COLOR_CYAN, 
                   "Это %s текст с цветом %d", "форматированный", 42);
    printf("%s\n", buffer);
    
    printf("\n");
}

int main(void) {
    color_test();
    return 0;
}

#endif // COLOR_TEST

#endif // COLOR_H
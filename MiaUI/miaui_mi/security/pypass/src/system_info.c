#include <math.h>
//╔═════════════════════════════╗                       
//║  Link: t.me/FrontendVSCode                       ║                         
//║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║    
//║  lang: C                                         ║                     
//║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║                      
//║  build:3.10.15                                   ║
//║  files: system_info.c                            ║    
//╚═════════════════════════════╝



#include "../include/system_info.h"
#include "../include/safe_read.h"
#include "../include/common.h"
#include <sys/stat.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <ctype.h>
#include <time.h>
#include <unistd.h>

// ==================== ЗАЩИТА ОТ ПОВТОРНОГО ВКЛЮЧЕНИЯ ====================
#ifdef SYSTEM_INFO_C
#error "system_info.c включен дважды!"
#endif
#define SYSTEM_INFO_C

// ==================== КОНСТАНТЫ ====================
#define BUILD_PROP_PATH "/system/build.prop"
#define BUILD_PROP_ALT_PATH "/vendor/build.prop"
#define BUILD_PROP_ALT2_PATH "/product/build.prop"
#define MAX_LINE_LEN 512
#define MAX_PROP_VALUE 256
#define MAX_CMD_OUTPUT 1024

// ==================== СТАТИЧЕСКИЕ ФУНКЦИИ ====================

/**
 * Проверка существования файла build.prop и выбор первого доступного
 */
static const char* get_build_prop_path(void) {
    static const char* paths[] = {
        BUILD_PROP_PATH,
        BUILD_PROP_ALT_PATH,
        BUILD_PROP_ALT2_PATH,
        "/system/system/build.prop",
        "/vendor/build.prop",
        "/product/build.prop",
        "/odm/build.prop",
        NULL
    };
    
    for (int i = 0; paths[i] != NULL; i++) {
        if (safe_file_exists(paths[i])) {
            return paths[i];
        }
    }
    
    return BUILD_PROP_PATH; // Возвращаем стандартный путь, даже если не существует
}

/**
 * Безопасное чтение свойства из build.prop
 * @param key ключ свойства (например "ro.product.manufacturer")
 * @return указатель на статический буфер со значением или пустую строку
 */
static const char* read_build_prop_safe(const char* key) {
    static char value[MAX_PROP_VALUE];
    value[0] = '\0';
    
    // Проверка входных параметров
    if (key == NULL || key[0] == '\0') {
        return value;
    }
    
    const char* prop_path = get_build_prop_path();
    
    // Проверяем существование файла
    if (!safe_file_exists(prop_path)) {
        return value;
    }
    
    FILE* fp = fopen(prop_path, "r");
    if (fp == NULL) {
        return value;
    }
    
    char line[MAX_LINE_LEN];
    size_t key_len = strlen(key);
    
    while (fgets(line, sizeof(line), fp) != NULL) {
        // Пропускаем комментарии
        if (line[0] == '#') continue;
        
        // Проверяем начало строки
        if (strncmp(line, key, key_len) == 0 && line[key_len] == '=') {
            char* val_start = line + key_len + 1;
            
            // Убираем пробелы в начале
            while (*val_start == ' ' || *val_start == '\t') val_start++;
            
            // Убираем перевод строки в конце
            char* newline = strchr(val_start, '\n');
            if (newline != NULL) *newline = '\0';
            
            // Убираем пробелы в конце
            char* end = val_start + strlen(val_start) - 1;
            while (end > val_start && (*end == ' ' || *end == '\t' || *end == '\r')) {
                *end = '\0';
                end--;
            }
            
            // Копируем в буфер с проверкой размера
            strncpy(value, val_start, sizeof(value) - 1);
            value[sizeof(value) - 1] = '\0';
            break;
        }
    }
    
    fclose(fp);
    return value;
}

/**
 * Безопасное преобразование строки в число
 */
static int safe_atoi(const char* str) {
    if (str == NULL || str[0] == '\0') return 0;
    
    // Пропускаем пробелы
    while (*str == ' ' || *str == '\t') str++;
    
    // Проверяем, что строка содержит только цифры (и возможно минус)
    const char* p = str;
    if (*p == '-') p++;
    while (*p) {
        if (!isdigit((unsigned char)*p)) return 0;
        p++;
    }
    
    return atoi(str);
}

/**
 * Безопасное выполнение shell команды с чтением вывода
 */
static char* execute_shell_command(const char* cmd) {
    if (cmd == NULL) return NULL;
    
    FILE* fp = popen(cmd, "r");
    if (fp == NULL) return NULL;
    
    char* result = malloc(MAX_CMD_OUTPUT);
    if (result == NULL) {
        pclose(fp);
        return NULL;
    }
    
    size_t total_read = 0;
    while (fgets(result + total_read, MAX_CMD_OUTPUT - total_read, fp) != NULL) {
        total_read = strlen(result);
        if (total_read >= MAX_CMD_OUTPUT - 1) break;
    }
    
    // Убираем перевод строки в конце
    if (total_read > 0 && result[total_read - 1] == '\n') {
        result[total_read - 1] = '\0';
    }
    
    pclose(fp);
    return result;
}

/**
 * Получение информации через getprop (быстрее чем чтение build.prop)
 */
static const char* get_prop_via_getprop(const char* key) {
    static char value[MAX_PROP_VALUE];
    value[0] = '\0';
    
    char cmd[128];
    snprintf(cmd, sizeof(cmd), "getprop %s", key);
    
    char* result = execute_shell_command(cmd);
    if (result != NULL && result[0] != '\0') {
        strncpy(value, result, sizeof(value) - 1);
        value[sizeof(value) - 1] = '\0';
        free(result);
    }
    
    return value;
}

/**
 * Определение типа сборки по строке
 */
static BuildType parse_build_type(const char* type_str) {
    if (type_str == NULL) return BUILD_TYPE_UNKNOWN;
    
    if (strcmp(type_str, "user") == 0) return BUILD_TYPE_USER;
    if (strcmp(type_str, "userdebug") == 0) return BUILD_TYPE_USERDEBUG;
    if (strcmp(type_str, "eng") == 0) return BUILD_TYPE_ENG;
    if (strcmp(type_str, "test") == 0) return BUILD_TYPE_TEST;
    
    return BUILD_TYPE_UNKNOWN;
}

/**
 * Определение состояния безопасности
 */
static SecurityState parse_security_state(const char* state_str) {
    if (state_str == NULL) return SEC_STATE_UNKNOWN;
    
    if (strstr(state_str, "locked") != NULL) return SEC_STATE_LOCKED;
    if (strstr(state_str, "unlocked") != NULL) return SEC_STATE_UNLOCKED;
    if (strstr(state_str, "engineering") != NULL) return SEC_STATE_ENGINEERING;
    
    return SEC_STATE_UNKNOWN;
}

/**
 * Получение времени сборки из строки
 */
static time_t parse_build_date(const char* date_str) {
    if (date_str == NULL || date_str[0] == '\0') return 0;
    
    // Пробуем разные форматы
    struct tm tm = {0};
    
    // Формат: "Wed Jul 11 22:46:09 UTC 2025"
    if (strptime(date_str, "%a %b %d %H:%M:%S %Z %Y", &tm) != NULL) {
        return mktime(&tm);
    }
    
    // Формат: "2025-07-11"
    if (strptime(date_str, "%Y-%m-%d", &tm) != NULL) {
        return mktime(&tm);
    }
    
    return 0;
}

// ==================== ОСНОВНЫЕ ФУНКЦИИ ====================

SystemInfo get_system_info(void) {
    SystemInfo info;
    memset(&info, 0, sizeof(info));
    
    // Пробуем getprop (быстрее)
    const char* (*prop_reader)(const char*) = get_prop_via_getprop;
    
    // Если getprop не работает, используем чтение build.prop
    char* test = execute_shell_command("getprop ro.product.manufacturer");
    if (test == NULL || test[0] == '\0') {
        prop_reader = read_build_prop_safe;
    }
    if (test != NULL) free(test);
    
    // ===== ПРОИЗВОДИТЕЛЬ И МОДЕЛЬ =====
    strncpy(info.manufacturer, prop_reader("ro.product.manufacturer"), 
            sizeof(info.manufacturer) - 1);
    strncpy(info.brand, prop_reader("ro.product.brand"), 
            sizeof(info.brand) - 1);
    strncpy(info.model, prop_reader("ro.product.model"), 
            sizeof(info.model) - 1);
    strncpy(info.name, prop_reader("ro.product.name"), 
            sizeof(info.name) - 1);
    strncpy(info.codename, prop_reader("ro.product.device"), 
            sizeof(info.codename) - 1);
    
    // Если модель пустая, пробуем альтернативные ключи
    if (info.model[0] == '\0') {
        strncpy(info.model, prop_reader("ro.product.device"), 
                sizeof(info.model) - 1);
    }
    if (info.model[0] == '\0') {
        strncpy(info.model, prop_reader("ro.product.name"), 
                sizeof(info.model) - 1);
    }
    
    // ===== ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ =====
    strncpy(info.device, prop_reader("ro.product.device"), 
            sizeof(info.device) - 1);
    strncpy(info.product, prop_reader("ro.product.name"), 
            sizeof(info.product) - 1);
    strncpy(info.hardware, prop_reader("ro.hardware"), 
            sizeof(info.hardware) - 1);
    strncpy(info.platform, prop_reader("ro.board.platform"), 
            sizeof(info.platform) - 1);
    strncpy(info.board, prop_reader("ro.product.board"), 
            sizeof(info.board) - 1);
    strncpy(info.bootloader, prop_reader("ro.bootloader"), 
            sizeof(info.bootloader) - 1);
    strncpy(info.radio, prop_reader("gsm.version.baseband"), 
            sizeof(info.radio) - 1);
    
    // ===== ВЕРСИЯ ANDROID =====
    strncpy(info.android_version, prop_reader("ro.build.version.release"), 
            sizeof(info.android_version) - 1);
    strncpy(info.android_release, info.android_version, 
            sizeof(info.android_release) - 1);
    
    const char* sdk_str = prop_reader("ro.build.version.sdk");
    info.sdk = safe_atoi(sdk_str);
    info.sdk_int = info.sdk;
    
    // ===== ИНФОРМАЦИЯ О СБОРКЕ =====
    strncpy(info.build_id, prop_reader("ro.build.id"), 
            sizeof(info.build_id) - 1);
    strncpy(info.build_date, prop_reader("ro.build.date"), 
            sizeof(info.build_date) - 1);
    strncpy(info.build_time, prop_reader("ro.build.date.utc"), 
            sizeof(info.build_time) - 1);
    strncpy(info.build_type, prop_reader("ro.build.type"), 
            sizeof(info.build_type) - 1);
    strncpy(info.build_tags, prop_reader("ro.build.tags"), 
            sizeof(info.build_tags) - 1);
    strncpy(info.build_user, prop_reader("ro.build.user"), 
            sizeof(info.build_user) - 1);
    strncpy(info.build_host, prop_reader("ro.build.host"), 64);
//             sizeof(info.build_host) - 1);
//     strncpy(info.fingerprint, prop_reader("ro.build.fingerprint"), 
//             sizeof(info.fingerprint) - 1);
//     strncpy(info.fingerprint_full, info.fingerprint, 
//             sizeof(info.fingerprint_full) - 1);
    strncpy(info.security_patch, prop_reader("ro.build.version.security_patch"), 
            sizeof(info.security_patch) - 1);
    strncpy(info.incremental, prop_reader("ro.build.version.incremental"), 
            sizeof(info.incremental) - 1);
    strncpy(info.description, prop_reader("ro.build.description"), 
            sizeof(info.description) - 1);
    strncpy(info.display_id, prop_reader("ro.build.display.id"), 
            sizeof(info.display_id) - 1);
    
    // ===== СЕРИЙНЫЙ НОМЕР =====
    strncpy(info.serial, prop_reader("ro.serialno"), 
            sizeof(info.serial) - 1);
    if (info.serial[0] == '\0') {
        char* serial = execute_shell_command("getprop ro.boot.serialno");
        if (serial != NULL) {
            strncpy(info.serial, serial, sizeof(info.serial) - 1);
            free(serial);
        }
    }
    
    // ===== ЯДРО =====
    char* kernel = execute_shell_command("uname -r");
    if (kernel != NULL) {
        strncpy(info.kernel_version, kernel, sizeof(info.kernel_version) - 1);
        strncpy(info.kernel_release, kernel, sizeof(info.kernel_release) - 1);
        free(kernel);
    }
    
    // ===== ПАРСИНГ ТИПОВ =====
    info.build_type_enum = parse_build_type(info.build_type);
    
    const char* boot_state = prop_reader("ro.boot.verifiedbootstate");
    info.bootloader_state = parse_security_state(boot_state);
    
    const char* vbmeta_state = prop_reader("ro.boot.vbmeta.device_state");
    info.vbmeta_state = parse_security_state(vbmeta_state);
    
    const char* verity_mode = prop_reader("ro.boot.veritymode");
    info.dm_verity = (verity_mode != NULL && strcmp(verity_mode, "enforcing") == 0) ? 1 : 0;
    
    // ===== ВРЕМЕННЫЕ МЕТКИ =====
    info.build_timestamp = parse_build_date(info.build_date);
    
    // Время последней загрузки
    struct sysinfo si;
    if (sysinfo(&si) == 0) {
        info.last_boot = time(NULL) - si.uptime;
    }
    
    // Первая загрузка (приблизительно)
    info.first_boot = info.last_boot - (7 * 24 * 3600); // Неделю назад
    
    // ===== SELINUX =====
    char* selinux = execute_shell_command("getenforce 2>/dev/null");
    if (selinux != NULL) {
        info.selinux_enabled = (strstr(selinux, "Enforcing") != NULL) ? 1 : 0;
        strncpy(info.selinux_mode, selinux, sizeof(info.selinux_mode) - 1);
        free(selinux);
    }
    
    // ===== ROOT =====
    info.has_root = (access("/system/bin/su", F_OK) == 0 ||
                     access("/system/xbin/su", F_OK) == 0 ||
                     access("/sbin/su", F_OK) == 0) ? 1 : 0;
    
    info.verified_boot = (info.bootloader_state == SEC_STATE_LOCKED) ? 1 : 0;
    
    return info;
}

DisplayInfo get_display_info(void) {
    DisplayInfo info;
    memset(&info, 0, sizeof(info));
    
    // ===== РАЗРЕШЕНИЕ ЭКРАНА =====
    char* display_info = execute_shell_command(
        "dumpsys display 2>/dev/null | grep -E 'mBaseDisplayInfo|displayWidth|displayHeight' | head -2"
    );
    
    if (display_info != NULL) {
        // Пробуем разные форматы вывода
        if (sscanf(display_info, "%*[^0-9]%d x %d", &info.width, &info.height) != 2) {
            // Пробуем альтернативный формат
            char* width_cmd = execute_shell_command(
                "dumpsys display 2>/dev/null | grep -E 'displayWidth' | head -1 | grep -o '[0-9]\\+'"
            );
            char* height_cmd = execute_shell_command(
                "dumpsys display 2>/dev/null | grep -E 'displayHeight' | head -1 | grep -o '[0-9]\\+'"
            );
            
            if (width_cmd != NULL) info.width = atoi(width_cmd);
            if (height_cmd != NULL) info.height = atoi(height_cmd);
            
            free(width_cmd);
            free(height_cmd);
        }
        free(display_info);
    }
    
    // Если не получили через dumpsys, пробуем системные файлы
    if (info.width == 0 || info.height == 0) {
        size_t file_size = 0;
        char* width_file = safe_read_file("/sys/class/graphics/fb0/virtual_size", &file_size);
        if (width_file != NULL) {
            if (sscanf(width_file, "%d,%d", &info.width, &info.height) != 2) {
                sscanf(width_file, "%d %d", &info.width, &info.height);
            }
            free(width_file);
        }
    }
    
    // ===== ФИЗИЧЕСКИЙ РАЗМЕР =====
    size_t file_size = 0;
    char* width_mm = safe_read_file("/sys/class/graphics/fb0/width", &file_size);
    char* height_mm = safe_read_file("/sys/class/graphics/fb0/height", &file_size);
    
    if (width_mm != NULL) {
        info.width_physical = atoi(width_mm);
        free(width_mm);
    }
    if (height_mm != NULL) {
        info.height_physical = atoi(height_mm);
        free(height_mm);
    }
    
    // ===== РАЗМЕР В ДЮЙМАХ =====
    if (info.width_physical > 0 && info.height_physical > 0) {
        float diagonal_mm = sqrt(info.width_physical * info.width_physical + 
                                 info.height_physical * info.height_physical);
        info.size_inches = diagonal_mm / 25.4f;
    }
    
    // ===== ПЛОТНОСТЬ ПИКСЕЛЕЙ =====
    const char* density_str = read_build_prop_safe("ro.sf.lcd_density");
    info.dpi = safe_atoi(density_str);
    info.density_dpi = info.dpi;
    
    if (info.dpi == 0) {
        // Пробуем через wm density
        char* density_cmd = execute_shell_command("wm density 2>/dev/null | grep -o '[0-9]\\+'");
        if (density_cmd != NULL) {
            info.dpi = atoi(density_cmd);
            info.density_dpi = info.dpi;
            free(density_cmd);
        }
    }
    
    // ===== ПЛОТНОСТЬ X/Y =====
    if (info.width > 0 && info.width_physical > 0) {
        info.xdpi = info.width * 25.4f / info.width_physical;
    }
    if (info.height > 0 && info.height_physical > 0) {
        info.ydpi = info.height * 25.4f / info.height_physical;
    }
    
    // ===== ЧАСТОТА ОБНОВЛЕНИЯ =====
    char* refresh_cmd = execute_shell_command(
        "dumpsys display 2>/dev/null | grep -E 'refreshRate' | head -1 | grep -o '[0-9.]\\+'"
    );
    if (refresh_cmd != NULL) {
        info.refresh_rate = atof(refresh_cmd);
        info.max_refresh_rate = info.refresh_rate;
        info.min_refresh_rate = info.refresh_rate;
        free(refresh_cmd);
    }
    
    // ===== ЯРКОСТЬ =====
    const char* brightness_paths[] = {
        "/sys/class/backlight/panel0-backlight/brightness",
        "/sys/class/backlight/backlight/brightness",
        "/sys/class/leds/lcd-backlight/brightness",
        "/sys/devices/platform/backlight/backlight/panel/brightness",
        "/sys/class/backlight/backlight/actual_brightness",
        NULL
    };
    
    for (int i = 0; brightness_paths[i] != NULL; i++) {
        long brightness = safe_read_long(brightness_paths[i]);
        if (brightness >= 0) {
            info.brightness = (int)brightness;
            
            // Пробуем получить максимальную яркость
            char max_path[MAX_PATH];
            strncpy(max_path, brightness_paths[i], sizeof(max_path) - 1);
            max_path[sizeof(max_path) - 1] = '\0';
            
            // Пробуем разные варианты имени файла для максимума
            const char* max_suffixes[] = {"_max", "_max_brightness", "/max_brightness", "/max", NULL};
            
            for (int j = 0; max_suffixes[j] != NULL; j++) {
                char test_path[MAX_PATH];
                snprintf(test_path, sizeof(test_path), "%s%s", 
                         brightness_paths[i], max_suffixes[j]);
                
                long max_bright = safe_read_long(test_path);
                if (max_bright > 0) {
                    info.max_brightness = (int)max_bright;
                    break;
                }
            }
            break;
        }
    }
    
    // ===== МИНИМАЛЬНАЯ ЯРКОСТЬ =====
    info.min_brightness = 0;
    info.auto_brightness = (access("/sys/class/backlight/backlight/auto_brightness", F_OK) == 0);
    
    // ===== ПРОИЗВОДИТЕЛЬ ДИСПЛЕЯ =====
    char* panel_info = execute_shell_command(
        "dumpsys display 2>/dev/null | grep -E 'mDisplayInfo|DeviceProductInfo' | head -5"
    );
    
    if (panel_info != NULL) {
        // Ищем производителя в скобках
        char* start = strchr(panel_info, '(');
        char* end = strchr(panel_info, ')');
        
        if (start != NULL && end != NULL && end > start) {
            int len = end - start - 1;
            if (len > 0 && len < (int)sizeof(info.manufacturer) - 1) {
                strncpy(info.manufacturer, start + 1, len);
                info.manufacturer[len] = '\0';
            }
        }
        free(panel_info);
    }
    
    // ===== ТИП ПАНЕЛИ =====
    char* panel_type = execute_shell_command(
        "getprop ro.boot.panel_type 2>/dev/null"
    );
    if (panel_type != NULL && panel_type[0] != '\0') {
        strncpy(info.panel_type, panel_type, sizeof(info.panel_type) - 1);
        free(panel_type);
    }
    
    // ===== ПОДДЕРЖКА HDR =====
    char* hdr_check = execute_shell_command(
        "dumpsys display 2>/dev/null | grep -i hdr | head -1"
    );
    
    if (hdr_check != NULL) {
        info.hdr = (strlen(hdr_check) > 0);
        
        // Пробуем получить HDR характеристики
        char* hdr_max = execute_shell_command(
            "dumpsys display 2>/dev/null | grep -i 'max.*luminance' | grep -o '[0-9.]\\+'"
        );
        if (hdr_max != NULL) {
            info.hdr_max_luminance = atoi(hdr_max);
            free(hdr_max);
        }
        
        free(hdr_check);
    }
    
    // ===== ГЛУБИНА ЦВЕТА =====
    char* color_depth = execute_shell_command(
        "getprop ro.sf.bits_per_pixel 2>/dev/null"
    );
    if (color_depth != NULL) {
        info.color_depth = atoi(color_depth);
        free(color_depth);
    } else {
        info.color_depth = 32; // По умолчанию
    }
    
    // ===== WIDE COLOR =====
    char* wide_color = execute_shell_command(
        "getprop ro.sf.has_wide_color 2>/dev/null"
    );
    if (wide_color != NULL) {
        info.wide_color = (strcmp(wide_color, "true") == 0) ? 1 : 0;
        free(wide_color);
    }
    
    // ===== ПОДДЕРЖКА КАСАНИЙ =====
    info.touch_support = (access("/dev/input/event0", F_OK) == 0);
    info.multitouch = info.touch_support; // Предполагаем
    
    // ===== ПОДДЕРЖКА СТИЛУСА =====
    info.stylus_support = (access("/dev/input/event2", F_OK) == 0);
    
    // ===== ALWAYS-ON DISPLAY =====
    info.always_on = (access("/sys/class/drm/card0/crtc-0/always_on", F_OK) == 0);
    
    // ===== ВЫРЕЗ (NOTCH/CUTOUT) =====
    info.cutout = 0; // По умолчанию нет выреза
    
    // Если не определили модель, используем build.prop
    if (info.manufacturer[0] == '\0') {
        strncpy(info.manufacturer, read_build_prop_safe("ro.product.manufacturer"),
                sizeof(info.manufacturer) - 1);
    }
    
    return info;
}

NetworkIdentity get_network_identity(void) {
    NetworkIdentity info;
    memset(&info, 0, sizeof(info));
    
    // Android ID
    char* android_id = execute_shell_command(
        "settings get secure android_id 2>/dev/null"
    );
    if (android_id != NULL) {
        strncpy(info.android_id, android_id, sizeof(info.android_id) - 1);
        free(android_id);
    }
    
    // GSF ID (Google Services Framework)
    char* gsf_id = execute_shell_command(
        "sqlite3 /data/data/com.google.android.gsf/databases/gservices.db "
        "'select value from main where name=\"android_id\"' 2>/dev/null"
    );
    if (gsf_id != NULL) {
        strncpy(info.gsf_id, gsf_id, sizeof(info.gsf_id) - 1);
        free(gsf_id);
    }
    
    // Advertising ID (через гугл сервисы)
    char* advertising_id = execute_shell_command(
        "cat /data/data/com.google.android.gms/shared_prefs/adid.xml 2>/dev/null | "
        "grep -o 'adid_key>.*<' | cut -d'>' -f2 | cut -d'<' -f1"
    );
    if (advertising_id != NULL) {
        strncpy(info.advertising_id, advertising_id, sizeof(info.advertising_id) - 1);
        free(advertising_id);
    }
    
    // Device ID (IMEI, но нужны root права)
    char* device_id = execute_shell_command(
        "service call iphonesubinfo 1 | grep -o '[0-9a-f]\\{8\\}' 2>/dev/null"
    );
    if (device_id != NULL) {
        strncpy(info.device_id, device_id, sizeof(info.device_id) - 1);
        free(device_id);
    }
    
    return info;
}

FirmwareInfo get_firmware_info(void) {
    FirmwareInfo info;
    memset(&info, 0, sizeof(info));
    
    const char* (*prop_reader)(const char*) = read_build_prop_safe;
    
    strncpy(info.firmware_version, prop_reader("ro.build.version.release"),
            sizeof(info.firmware_version) - 1);
    strncpy(info.vendor_firmware, prop_reader("ro.vendor.build.version.release"),
            sizeof(info.vendor_firmware) - 1);
    strncpy(info.oem_unlock, prop_reader("ro.oem_unlock_supported"),
            sizeof(info.oem_unlock) - 1);
    strncpy(info.warranty_bit, prop_reader("ro.warranty_bit"),
            sizeof(info.warranty_bit) - 1);
    
    return info;
}

int is_emulator(void) {
    const char* (*prop_reader)(const char*) = read_build_prop_safe;
    
    const char* hw = prop_reader("ro.hardware");
    if (hw != NULL && (strstr(hw, "goldfish") != NULL || 
                       strstr(hw, "ranchu") != NULL ||
                       strstr(hw, "qemu") != NULL)) {
        return 1;
    }
    
    const char* product = prop_reader("ro.product.device");
    if (product != NULL && (strstr(product, "generic") != NULL ||
                            strstr(product, "emulator") != NULL)) {
        return 1;
    }
    
    return 0;
}

int is_rooted(void) {
    return (access("/system/bin/su", F_OK) == 0 ||
            access("/system/xbin/su", F_OK) == 0 ||
            access("/sbin/su", F_OK) == 0 ||
            access("/magisk", F_OK) == 0 ||
            access("/data/local/tmp/magisk", F_OK) == 0);
}

int is_secure(void) {
    const char* verity = read_build_prop_safe("ro.boot.veritymode");
    return (verity != NULL && strcmp(verity, "enforcing") == 0);
}

int has_gapps(void) {
    return (access("/system/priv-app/GoogleServicesFramework", F_OK) == 0 ||
            access("/system/app/GoogleServicesFramework", F_OK) == 0);
}

int has_huawei_services(void) {
    return (access("/system/priv-app/HwServiceFramework", F_OK) == 0);
}

int has_samsung_services(void) {
    return (access("/system/priv-app/SamsungBilling", F_OK) == 0);
}

int has_xiaomi_services(void) {
    return (access("/system/priv-app/MiuiFramework", F_OK) == 0);
}

const char* get_country_code(void) {
    static char country[8] = "";
    
    char* code = execute_shell_command("getprop gsm.sim.operator.iso-country 2>/dev/null");
    if (code != NULL && code[0] != '\0') {
        strncpy(country, code, sizeof(country) - 1);
        free(code);
    } else {
        code = execute_shell_command("getprop ro.product.locale 2>/dev/null | cut -d'-' -f2");
        if (code != NULL) {
            strncpy(country, code, sizeof(country) - 1);
            free(code);
        }
    }
    
    return country;
}

const char* get_language_code(void) {
    static char lang[8] = "";
    
    char* code = execute_shell_command("getprop gsm.sim.operator.iso-country 2>/dev/null");
    if (code != NULL && code[0] != '\0') {
        strncpy(lang, code, sizeof(lang) - 1);
        free(code);
    } else {
        code = execute_shell_command("getprop ro.product.locale 2>/dev/null | cut -d'-' -f1");
        if (code != NULL) {
            strncpy(lang, code, sizeof(lang) - 1);
            free(code);
        }
    }
    
    return lang;
}

const char* get_timezone(void) {
    static char tz[32] = "";
    
    char* zone = execute_shell_command("getprop persist.sys.timezone 2>/dev/null");
    if (zone != NULL) {
        strncpy(tz, zone, sizeof(tz) - 1);
        free(zone);
    }
    
    return tz;
}

const char* get_os_version(void) {
    static char os[16] = "";
    
    const char* ver = read_build_prop_safe("ro.build.version.release");
    if (ver != NULL) {
        strncpy(os, ver, sizeof(os) - 1);
    }
    
    return os;
}

const char* get_api_level_string(void) {
    static char api[8] = "";
    
    const char* sdk = read_build_prop_safe("ro.build.version.sdk");
    if (sdk != NULL) {
        strncpy(api, sdk, sizeof(api) - 1);
    }
    
    return api;
}

const char* get_security_patch_level(void) {
    static char patch[16] = "";
    
    const char* sp = read_build_prop_safe("ro.build.version.security_patch");
    if (sp != NULL) {
        strncpy(patch, sp, sizeof(patch) - 1);
    }
    
    return patch;
}

void format_system_info(const SystemInfo* sys, char* buffer, size_t buffer_size) {
    if (sys == NULL || buffer == NULL || buffer_size == 0) return;
    
    char build_time[32];
    struct tm* tm = localtime(&sys->build_timestamp);
    if (tm != NULL) {
        strftime(build_time, sizeof(build_time), "%Y-%m-%d %H:%M", tm);
    } else {
        strcpy(build_time, "Unknown");
    }
    
    snprintf(buffer, buffer_size,
             "📱 УСТРОЙСТВО\n"
             "   Производитель: %s\n"
             "   Бренд: %s\n"
             "   Модель: %s\n"
             "   Кодовое имя: %s\n"
             "   Устройство: %s\n\n"
             
             "🤖 ANDROID\n"
             "   Версия: %s (API %d)\n"
             "   Сборка: %s\n"
             "   Тип: %s\n"
             "   Дата сборки: %s\n"
             "   Патч безопасности: %s\n\n"
             
             "🔧 АППАРАТУРА\n"
             "   Платформа: %s\n"
             "   Hardware: %s\n"
             "   Bootloader: %s\n"
             "   Baseband: %s\n\n"
             
             "🔒 БЕЗОПАСНОСТЬ\n"
             "   Root: %s\n"
             "   SELinux: %s\n"
             "   Verified Boot: %s\n"
             "   DM-Verity: %s\n"
             "   Bootloader: %s\n"
             "   VBMeta: %s",
             
             sys->manufacturer,
             sys->brand,
             sys->model,
             sys->codename,
             sys->device,
             
             sys->android_version,
             sys->sdk,
             sys->build_id,
             sys->build_type,
             build_time,
             sys->security_patch,
             
             sys->platform,
             sys->hardware,
             sys->bootloader,
             sys->radio,
             
             sys->has_root ? "Да" : "Нет",
             sys->selinux_enabled ? "Enforcing" : "Permissive",
             sys->verified_boot ? "Да" : "Нет",
             sys->dm_verity ? "Да" : "Нет",
             sys->bootloader_state == SEC_STATE_LOCKED ? "Locked" :
             sys->bootloader_state == SEC_STATE_UNLOCKED ? "Unlocked" : "Unknown",
             sys->vbmeta_state == SEC_STATE_LOCKED ? "Locked" :
             sys->vbmeta_state == SEC_STATE_UNLOCKED ? "Unlocked" : "Unknown");
}

void format_display_info(const DisplayInfo* info, char* buffer, size_t buffer_size) {
    if (info == NULL || buffer == NULL || buffer_size == 0) return;
    
    snprintf(buffer, buffer_size,
             "🖥️ ДИСПЛЕЙ\n"
             "   Разрешение: %dx%d\n"
             "   Плотность: %d dpi\n"
             "   Частота: %.1f Hz\n"
             "   Размер: %.1f дюймов\n"
             "   Яркость: %d/%d\n"
             "   HDR: %s\n"
             "   Панель: %s\n"
             "   Производитель: %s",
             info->width, info->height,
             info->dpi,
             info->refresh_rate,
             info->size_inches,
             info->brightness, info->max_brightness,
             info->hdr ? "Да" : "Нет",
             info->panel_type[0] ? info->panel_type : "Неизвестно",
             info->manufacturer[0] ? info->manufacturer : "Неизвестно");
}

void format_device_summary(char* buffer, size_t buffer_size) {
    if (buffer == NULL || buffer_size == 0) return;
    
    SystemInfo sys = get_system_info();
    DisplayInfo disp = get_display_info();
    
    snprintf(buffer, buffer_size,
             "%s %s | Android %s | %dx%d | %.1f Hz",
             sys.manufacturer,
             sys.model,
             sys.android_version,
             disp.width, disp.height,
             disp.refresh_rate);
}

const char* get_device_codename(void) {
    static char codename[64] = "";
    
    const char* code = read_build_prop_safe("ro.product.device");
    if (code != NULL) {
        strncpy(codename, code, sizeof(codename) - 1);
    }
    
    return codename;
}

const char* get_device_serial(void) {
    static char serial[64] = "";
    
    char* ser = execute_shell_command("getprop ro.serialno 2>/dev/null");
    if (ser != NULL) {
        strncpy(serial, ser, sizeof(serial) - 1);
        free(ser);
    }
    
    return serial;
}

const char* get_build_fingerprint(void) {
    static char fp[256] = "";
    
    const char* fprint = read_build_prop_safe("ro.build.fingerprint");
    if (fprint != NULL) {
        strncpy(fp, fprint, sizeof(fp) - 1);
    }
    
    return fp;
}

const char* get_kernel_version(void) {
    static char kernel[128] = "";
    
    char* ver = execute_shell_command("uname -r 2>/dev/null");
    if (ver != NULL) {
        strncpy(kernel, ver, sizeof(kernel) - 1);
        free(ver);
    }
    
    return kernel;
}

const char* get_bootloader_version(void) {
    static char bl[64] = "";
    
    const char* boot = read_build_prop_safe("ro.bootloader");
    if (boot != NULL) {
        strncpy(bl, boot, sizeof(bl) - 1);
    }
    
    return bl;
}

const char* get_baseband_version(void) {
    static char bb[64] = "";
    
    const char* base = read_build_prop_safe("gsm.version.baseband");
    if (base != NULL) {
        strncpy(bb, base, sizeof(bb) - 1);
    }
    
    return bb;
}

time_t get_boot_time(void) {
    struct sysinfo si;
    if (sysinfo(&si) == 0) {
        return time(NULL) - si.uptime;
    }
    return 0;
}

time_t get_uptime(void) {
    struct sysinfo si;
    if (sysinfo(&si) == 0) {
        return si.uptime;
    }
    return 0;
}

const char* get_uptime_string(void) {
    static char uptime_str[64];
    time_t uptime = get_uptime();
    
    int days = uptime / 86400;
    int hours = (uptime % 86400) / 3600;
    int mins = (uptime % 3600) / 60;
    int secs = uptime % 60;
    
    if (days > 0) {
        snprintf(uptime_str, sizeof(uptime_str), "%dд %dч %dм", days, hours, mins);
    } else if (hours > 0) {
        snprintf(uptime_str, sizeof(uptime_str), "%dч %dм %dс", hours, mins, secs);
    } else if (mins > 0) {
        snprintf(uptime_str, sizeof(uptime_str), "%dм %dс", mins, secs);
    } else {
        snprintf(uptime_str, sizeof(uptime_str), "%dс", secs);
    }
    
    return uptime_str;
}

// ==================== КОНЕЦ ФАЙЛА ====================
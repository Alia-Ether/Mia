//╔═════════════════════════════╗                       
//║  Link: t.me/FrontendVSCode                       ║                         
//║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║    
//║  lang: C                                         ║                     
//║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║                      
//║  build:3.10.15                                   ║
//║  files: camera_info.c                            ║    
//╚═════════════════════════════╝

#include "../include/camera_info.h"
#include "../include/safe_read.h"
#include "../include/common.h"
#include <dirent.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <regex.h>
#include <errno.h>
#include <time.h>

// ==================== ЗАЩИТА ОТ ПОВТОРНОГО ВКЛЮЧЕНИЯ ====================
#ifdef CAMERA_INFO_C
#error "camera_info.c включен дважды!"
#endif
#define CAMERA_INFO_C

// ==================== КОНСТАНТЫ ====================
#define CAMERA_SYSFS_PATH "/sys/devices/platform"
#define CAMERA_V4L_PATH "/sys/class/video4linux"
#define CAMERA_MSM_PATH "/sys/devices/platform/msm_camera"
#define MAX_CAMERA_NAME 64
#define MAX_CAMERA_MODEL 64
#define MAX_BUFFER 1024
#define MAX_CAMERAS 8

// ==================== СТРУКТУРЫ ДЛЯ ПАРСИНГА ====================
typedef struct {
    int id;
    char name[MAX_CAMERA_NAME];
    char model[MAX_CAMERA_MODEL];
    int facing;
    int orientation;
    int max_width;
    int max_height;
    float aperture;
    float focal_length;
    int has_flash;
    int has_autofocus;
    int has_eis;
    int has_ois;
    int has_hdr;
    int fps_min;
    int fps_max;
    char supported_modes[256];
} CameraInfoInternal;

// ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

/**
 * Безопасное выполнение команды с чтением вывода
 */
static char* execute_command_safe(const char* cmd) {
    if (cmd == NULL) return NULL;
    
    FILE* fp = popen(cmd, "r");
    if (fp == NULL) return NULL;
    
    char* result = malloc(MAX_BUFFER);
    if (result == NULL) {
        pclose(fp);
        return NULL;
    }
    
    result[0] = '\0';
    size_t total_read = 0;
    
    while (fgets(result + total_read, MAX_BUFFER - total_read, fp) != NULL) {
        total_read = strlen(result);
        if (total_read >= MAX_BUFFER - 1) break;
    }
    
    pclose(fp);
    return result;
}

/**
 * Удаление пробелов в начале и конце строки
 */
static void trim_string(char* str) {
    if (str == NULL) return;
    
    char* start = str;
    while (*start && isspace((unsigned char)*start)) start++;
    
    if (start != str) {
        memmove(str, start, strlen(start) + 1);
    }
    
    char* end = str + strlen(str) - 1;
    while (end >= str && isspace((unsigned char)*end)) {
        *end = '\0';
        end--;
    }
}

/**
 * Извлечение числа из строки по регулярному выражению
 */
static int extract_number(const char* str, const char* pattern) {
    if (str == NULL || pattern == NULL) return 0;
    
    regex_t regex;
    regmatch_t matches[2];
    int result = 0;
    
    if (regcomp(&regex, pattern, REG_EXTENDED) != 0) return 0;
    
    if (regexec(&regex, str, 2, matches, 0) == 0 && matches[1].rm_so != -1) {
        int len = matches[1].rm_eo - matches[1].rm_so;
        if (len > 0 && len < 32) {
            char num_str[32];
            snprintf(num_str, sizeof(num_str), "%.*s", len, str + matches[1].rm_so);
            result = atoi(num_str);
        }
    }
    
    regfree(&regex);
    return result;
}

/**
 * Извлечение числа с плавающей точкой из строки по регулярному выражению
 */
static float extract_float(const char* str, const char* pattern) {
    if (str == NULL || pattern == NULL) return 0;
    
    regex_t regex;
    regmatch_t matches[2];
    float result = 0;
    
    if (regcomp(&regex, pattern, REG_EXTENDED) != 0) return 0;
    
    if (regexec(&regex, str, 2, matches, 0) == 0 && matches[1].rm_so != -1) {
        int len = matches[1].rm_eo - matches[1].rm_so;
        if (len > 0 && len < 32) {
            char num_str[32];
            snprintf(num_str, sizeof(num_str), "%.*s", len, str + matches[1].rm_so);
            result = atof(num_str);
        }
    }
    
    regfree(&regex);
    return result;
}

// ==================== ПАРСИНГ DUMPSYS ====================

/**
 * Парсинг вывода dumpsys media.camera
 */
static int parse_dumpsys_camera(CameraInfoInternal* cameras, int max_count) {
    if (cameras == NULL || max_count <= 0) return 0;
    
    int count = 0;
    
    char* output = execute_command_safe(
        "dumpsys media.camera 2>/dev/null | grep -A 15 -E 'Camera [0-9]+'"
    );

    if (output == NULL || output[0] == '\0') {
        // Проверяем, была ли ошибка доступа или команда не найдена
        // execute_command_safe возвращает NULL, если команда не найдена или произошла ошибка выполнения

        // Проверяем, существует ли команда dumpsys
        if (access("/system/bin/dumpsys", F_OK) == -1) {
             // Команда dumpsys не найдена
             free(output);
             return -2; // Код ошибки: команда не найдена
        } else if (errno == EACCES || errno == EPERM) {
             // Ошибка доступа, требуются su права
             free(output);
             return -3; // Код ошибки: права доступа
        }

        free(output);
        return 0; // Камеры не найдены или пустой вывод
    }
    
    char* line = output;
    char* saveptr = NULL;
    int current_cam = -1;
    
    line = strtok_r(line, "\n", &saveptr);
    while (line != NULL && count < max_count) {
        // Убираем пробелы
        char* trimmed = line;
        while (*trimmed == ' ' || *trimmed == '\t') trimmed++;
        
        if (strstr(trimmed, "Camera ID") != NULL || 
            (strstr(trimmed, "Camera") != NULL && strchr(trimmed, ':') == NULL)) {
            
            current_cam = count;
            CameraInfoInternal* cam = &cameras[count];
            memset(cam, 0, sizeof(CameraInfoInternal));
            
            cam->id = extract_number(trimmed, ".*?([0-9]+).*");
            cam->facing = -1;
            cam->has_flash = -1;
            count++;
            
        } else if (current_cam >= 0 && current_cam < count) {
            CameraInfoInternal* cam = &cameras[current_cam];
            
            if (strstr(trimmed, "facing") != NULL) {
                if (strstr(trimmed, "BACK") != NULL || strstr(trimmed, "back") != NULL) {
                    cam->facing = 0;
                } else if (strstr(trimmed, "FRONT") != NULL || strstr(trimmed, "front") != NULL) {
                    cam->facing = 1;
                }
            }
            else if (strstr(trimmed, "width") != NULL) {
                int w = extract_number(trimmed, ".*?([0-9]+).*");
                if (w > cam->max_width) cam->max_width = w;
            }
            else if (strstr(trimmed, "height") != NULL) {
                int h = extract_number(trimmed, ".*?([0-9]+).*");
                if (h > cam->max_height) cam->max_height = h;
            }
            else if (strstr(trimmed, "aperture") != NULL) {
                float a = extract_float(trimmed, ".*?([0-9.]+).*");
                if (a > 0) cam->aperture = a;
            }
            else if (strstr(trimmed, "focal") != NULL || strstr(trimmed, "focalLength") != NULL) {
                float f = extract_float(trimmed, ".*?([0-9.]+).*");
                if (f > 0) cam->focal_length = f;
            }
            else if (strstr(trimmed, "flash") != NULL) {
                cam->has_flash = 1;
            }
            else if (strstr(trimmed, "autofocus") != NULL || strstr(trimmed, "af") != NULL) {
                cam->has_autofocus = 1;
            }
            else if (strstr(trimmed, "eis") != NULL || strstr(trimmed, "electronic") != NULL) {
                cam->has_eis = 1;
            }
            else if (strstr(trimmed, "ois") != NULL || strstr(trimmed, "optical") != NULL) {
                cam->has_ois = 1;
            }
            else if (strstr(trimmed, "hdr") != NULL) {
                cam->has_hdr = 1;
            }
            else if (strstr(trimmed, "fps") != NULL || strstr(trimmed, "frame rate") != NULL) {
                int fps = extract_number(trimmed, ".*?([0-9]+).*");
                if (fps > 0) {
                    if (cam->fps_min == 0 || fps < cam->fps_min) cam->fps_min = fps;
                    if (fps > cam->fps_max) cam->fps_max = fps;
                }
            }
            else if (strstr(trimmed, "name") != NULL || strstr(trimmed, "model") != NULL) {
                char* colon = strchr(trimmed, ':');
                if (colon != NULL) {
                    colon++;
                    while (*colon == ' ') colon++;
                    strncpy(cam->name, colon, sizeof(cam->name) - 1);
                    cam->name[sizeof(cam->name) - 1] = '\0';
                }
            }
        }
        
        line = strtok_r(NULL, "\n", &saveptr);
    }
    
    free(output);
    return count;
}

// ==================== ПОИСК В SYSFS ====================

/**
 * Сканирование sysfs для поиска камер
 */
static int scan_sysfs_cameras(CameraInfoInternal* cameras, int max_count) {
    if (cameras == NULL || max_count <= 0) return 0;
    
    int count = 0;
    
    const char* search_paths[] = {
        CAMERA_SYSFS_PATH,
        CAMERA_V4L_PATH,
        CAMERA_MSM_PATH,
        "/sys/devices/virtual/camera",
        "/sys/class/camera",
        "/sys/class/video4linux",
        NULL
    };
    
    for (int p = 0; search_paths[p] != NULL && count < max_count; p++) {
        DIR* dir = opendir(search_paths[p]);
        if (dir == NULL) continue;
        
        struct dirent* entry;
        while ((entry = readdir(dir)) != NULL && count < max_count) {
            if (entry->d_name[0] == '.') continue;
            
            if (strstr(entry->d_name, "camera") != NULL ||
                strstr(entry->d_name, "cam") != NULL ||
                strstr(entry->d_name, "video") != NULL) {
                
                CameraInfoInternal* cam = &cameras[count];
                memset(cam, 0, sizeof(CameraInfoInternal));
                
                cam->id = count;
                strncpy(cam->name, entry->d_name, sizeof(cam->name) - 1);
                cam->name[sizeof(cam->name) - 1] = '\0';
                
                if (strstr(entry->d_name, "front") != NULL) {
                    cam->facing = 1;
                } else if (strstr(entry->d_name, "back") != NULL) {
                    cam->facing = 0;
                }
                
                char path[256];
                snprintf(path, sizeof(path), "%s/%s/device/width", search_paths[p], entry->d_name);
                cam->max_width = safe_read_long(path);
                
                snprintf(path, sizeof(path), "%s/%s/device/height", search_paths[p], entry->d_name);
                cam->max_height = safe_read_long(path);
                
                count++;
            }
        }
        closedir(dir);
    }
    
    return count;
}

// ==================== ПАРСИНГ ЧЕРЕЗ CAMERA2 ====================

/**
 * Получение информации через Camera2 API
 */
static int get_camera2_info(CameraInfoInternal* cameras, int max_count) {
    if (cameras == NULL || max_count <= 0) return 0;
    
    int count = 0;
    
    char* output = execute_command_safe(
        "dumpsys media.camera | grep -A 15 -E 'Camera [0-9]+'"
    );
    
    if (output == NULL || output[0] == '\0') {
        free(output);
        return 0;
    }
    
    char* line = output;
    char* saveptr = NULL;
    int current_cam = -1;
    
    line = strtok_r(line, "\n", &saveptr);
    while (line != NULL && count < max_count) {
        char* trimmed = line;
        while (*trimmed == ' ' || *trimmed == '\t') trimmed++;
        
        if (strstr(trimmed, "Camera ") != NULL && strchr(trimmed, ':') == NULL) {
            current_cam = extract_number(trimmed, ".*?([0-9]+).*");
            if (current_cam >= 0 && current_cam < max_count) {
                if (current_cam >= count) count = current_cam + 1;
                memset(&cameras[current_cam], 0, sizeof(CameraInfoInternal));
                cameras[current_cam].id = current_cam;
                snprintf(cameras[current_cam].name, sizeof(cameras[current_cam].name), 
                        "Camera %d", current_cam);
            }
        } else if (current_cam >= 0 && current_cam < max_count) {
            CameraInfoInternal* cam = &cameras[current_cam];
            
            if (strstr(trimmed, "LENS_FACING") != NULL) {
                if (strstr(trimmed, "BACK") != NULL) cam->facing = 0;
                else if (strstr(trimmed, "FRONT") != NULL) cam->facing = 1;
            }
            else if (strstr(trimmed, "SENSOR_INFO_PIXEL_ARRAY_SIZE") != NULL) {
                cam->max_width = extract_number(trimmed, ".*?([0-9]+)x([0-9]+).*");
                cam->max_height = extract_number(trimmed, ".*?[0-9]+x([0-9]+).*");
            }
            else if (strstr(trimmed, "LENS_INFO_AVAILABLE_APERTURES") != NULL) {
                float a = extract_float(trimmed, ".*?([0-9.]+).*");
                if (a > 0) cam->aperture = a;
            }
            else if (strstr(trimmed, "LENS_INFO_AVAILABLE_FOCAL_LENGTHS") != NULL) {
                float f = extract_float(trimmed, ".*?([0-9.]+).*");
                if (f > 0) cam->focal_length = f;
            }
            else if (strstr(trimmed, "FLASH_INFO_AVAILABLE") != NULL) {
                cam->has_flash = (strstr(trimmed, "true") != NULL) ? 1 : 0;
            }
            else if (strstr(trimmed, "CONTROL_AF_AVAILABLE_MODES") != NULL) {
                cam->has_autofocus = (strstr(trimmed, "OFF") == NULL) ? 1 : 0;
            }
            else if (strstr(trimmed, "CONTROL_AE_AVAILABLE_MODES") != NULL) {
                if (strstr(trimmed, "ON") != NULL) cam->has_hdr = 1;
            }
        }
        
        line = strtok_r(NULL, "\n", &saveptr);
    }
    
    free(output);
    return count;
}

// ==================== ОСНОВНАЯ ФУНКЦИЯ ====================

/**
 * Получение информации о камерах
 */
int get_camera_info(CameraDisplayInfo* cameras, int max_count) {
    if (cameras == NULL || max_count <= 0) return 0;
    
    // Временный массив для внутреннего хранения
    CameraInfoInternal internal_cameras[MAX_CAMERAS];
    memset(internal_cameras, 0, sizeof(internal_cameras));
    
    int count = 0;
    
    // Пробуем разные методы получения информации
    count = parse_dumpsys_camera(internal_cameras, max_count);
    
    if (count == 0) {
        count = get_camera2_info(internal_cameras, max_count);
    }
    
    if (count == 0) {
        count = scan_sysfs_cameras(internal_cameras, max_count);
    }
    
    // Если ничего не нашли, добавляем заглушки
    if (count == 0) {
        for (int i = 0; i < 2 && i < max_count; i++) {
            internal_cameras[i].id = i;
            internal_cameras[i].facing = i; // 0 - back, 1 - front
            internal_cameras[i].max_width = 1920;
            internal_cameras[i].max_height = 1080;
            internal_cameras[i].aperture = 1.8f;
            internal_cameras[i].has_flash = (i == 0) ? 1 : 0;
            internal_cameras[i].has_autofocus = 1;
            count++;
        }
    }
    
    // Конвертируем во внешний формат
    for (int i = 0; i < count && i < max_count; i++) {
        CameraDisplayInfo* out = &cameras[i];
        CameraInfoInternal* in = &internal_cameras[i];
        
        out->id = in->id;
        out->facing = in->facing;
        out->max_width = in->max_width;
        out->max_height = in->max_height;
        out->aperture = in->aperture > 0 ? in->aperture : 2.4f;
        out->has_flash = in->has_flash;
        out->has_autofocus = in->has_autofocus;
        out->has_ois = in->has_ois;
        
        // Вычисляем мегапиксели
        if (out->max_width > 0 && out->max_height > 0) {
            out->megapixels = (out->max_width * out->max_height) / 1000000.0f;
        } else {
            out->megapixels = 12.0f; // Значение по умолчанию
        }
        
        // Проверка поддержки 4K
        out->can_record_4k = (out->max_width >= 3840 && out->max_height >= 2160);
        
        // Формируем имя
        if (in->name[0] != '\0' && strcmp(in->name, "unknown") != 0) {
            strncpy(out->name, in->name, sizeof(out->name) - 1);
        } else {
            snprintf(out->name, sizeof(out->name), "Camera %d", in->id);
        }
        out->name[sizeof(out->name) - 1] = '\0';
        
        // Добавляем информацию о расположении
        if (in->facing == 0) {
            strncat(out->name, " (Back)", sizeof(out->name) - strlen(out->name) - 1);
        } else if (in->facing == 1) {
            strncat(out->name, " (Front)", sizeof(out->name) - strlen(out->name) - 1);
        }
    }
    
    return count;
}

/**
 * Получение детальной информации о камере
 */
int get_camera_details(int camera_id, CameraDetailedInfo* info) {
    if (info == NULL) return 0;
    
    CameraDisplayInfo cameras[MAX_CAMERAS];
    int count = get_camera_info(cameras, MAX_CAMERAS);
    
    for (int i = 0; i < count; i++) {
        if (cameras[i].id == camera_id) {
            // Заполняем детальную информацию
            memset(info, 0, sizeof(CameraDetailedInfo));
            info->id = cameras[i].id;
            strncpy(info->name, cameras[i].name, sizeof(info->name) - 1);
            info->facing = cameras[i].facing;
            info->max_width = cameras[i].max_width;
            info->max_height = cameras[i].max_height;
            info->megapixels = cameras[i].megapixels;
            info->aperture = cameras[i].aperture;
            info->has_flash = cameras[i].has_flash;
            info->has_autofocus = cameras[i].has_autofocus;
            info->has_ois = cameras[i].has_ois;
            info->can_record_4k = cameras[i].can_record_4k;
            info->available = 1;
            return 1;
        }
    }
    
    return 0;
}

/**
 * Форматирование информации о камере для отображения
 */
void format_camera_display(const CameraDisplayInfo* cam, char* buffer, size_t buffer_size) {
    if (cam == NULL || buffer == NULL || buffer_size == 0) return;
    
    const char* facing_str;
    if (cam->facing == 0) facing_str = "Back";
    else if (cam->facing == 1) facing_str = "Front";
    else facing_str = "Unknown";
    
    char features[128] = "";
    if (cam->has_flash) strcat(features, "Flash ");
    if (cam->has_autofocus) strcat(features, "AF ");
    if (cam->has_ois) strcat(features, "OIS ");
    if (cam->can_record_4k) strcat(features, "4K");
    
    if (features[0] == '\0') strcpy(features, "Basic");
    
    snprintf(buffer, buffer_size,
             "📸 %s\n"
             "   ID: %d | Type: %s\n"
             "   Resolution: %dx%d (%.1f MP)\n"
             "   Aperture: f/%.1f\n"
             "   Features: %s",
             cam->name,
             cam->id, facing_str,
             cam->max_width, cam->max_height, cam->megapixels,
             cam->aperture,
             features);
}

// ==================== КОНЕЦ ФАЙЛА ====================
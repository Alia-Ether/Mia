//╔═════════════════════════════╗                       
//║  Link: t.me/FrontendVSCode                       ║                         
//║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║    
//║  lang: C                                         ║                     
//║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║                      
//║  build:3.10.15                                   ║
//║  files: camera_info.h                            ║    
//╚═════════════════════════════╝

#ifndef CAMERA_INFO_H
#define CAMERA_INFO_H

// ==================== СТАНДАРТНЫЕ БИБЛИОТЕКИ ====================
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <math.h>
#include <time.h>
#include <stdint.h>

// ==================== ОБЩИЕ ОПРЕДЕЛЕНИЯ ====================
#ifndef MAX_CAMERAS
#define MAX_CAMERAS 8
#endif

#ifndef MAX_NAME
#define MAX_NAME 128
#endif

#ifndef MAX_RESOLUTIONS
#define MAX_RESOLUTIONS 16
#endif

#ifndef MAX_FPS
#define MAX_FPS 32
#endif

// ==================== ОРИЕНТАЦИЯ КАМЕРЫ ====================
typedef enum {
    CAMERA_FACING_UNKNOWN = -1,
    CAMERA_FACING_BACK = 0,          // задняя
    CAMERA_FACING_FRONT = 1,          // фронтальная
    CAMERA_FACING_EXTERNAL = 2,       // внешняя (USB)
    CAMERA_FACING_AUX = 3,            // вспомогательная (глубины)
    CAMERA_FACING_MACRO = 4,          // макро
    CAMERA_FACING_TELEPHOTO = 5,      // телефото
    CAMERA_FACING_ULTRAWIDE = 6,      // ультраширокоугольная
    CAMERA_FACING_TOF = 7,            // Time of Flight
    CAMERA_FACING_THERMAL = 8         // тепловизор
} CameraFacing;

// ==================== ТИПЫ КАМЕР ====================
typedef enum {
    CAMERA_TYPE_UNKNOWN = 0,
    CAMERA_TYPE_STANDARD,              // стандартная
    CAMERA_TYPE_WIDE,                  // широкоугольная
    CAMERA_TYPE_ULTRAWIDE,              // ультраширокоугольная
    CAMERA_TYPE_TELEPHOTO,              // телефото
    CAMERA_TYPE_PERISCOPE,              // перископ
    CAMERA_TYPE_MACRO,                  // макро
    CAMERA_TYPE_DEPTH,                  // глубины
    CAMERA_TYPE_TOF,                     // ToF
    CAMERA_TYPE_IR,                       // инфракрасная
    CAMERA_TYPE_THERMAL,                  // тепловизор
    CAMERA_TYPE_MULTISPECTRAL              // мультиспектральная
} CameraType;

// ==================== ФОРМАТЫ ИЗОБРАЖЕНИЯ ====================
typedef enum {
    FORMAT_UNKNOWN = 0,
    FORMAT_JPEG,
    FORMAT_PNG,
    FORMAT_RAW,
    FORMAT_YUV,
    FORMAT_NV21,
    FORMAT_NV12,
    FORMAT_YUYV,
    FORMAT_MJPEG,
    FORMAT_H264,
    FORMAT_HEVC
} ImageFormat;

// ==================== РАЗРЕШЕНИЕ ====================
typedef struct {
    int width;                           // ширина
    int height;                          // высота
    float megapixels;                     // мегапиксели
    int is_video;                         // для видео
    float max_fps;                         // макс FPS
    ImageFormat format;                     // формат
} CameraResolution;

// ==================== ВИДЕО РЕЖИМЫ ====================
typedef struct {
    int width;                             // ширина
    int height;                            // высота
    int fps_min;                            // мин FPS
    int fps_max;                            // макс FPS
    int hdr;                                 // HDR поддержка
    int stabilization;                       // стабилизация
    char codec[32];                          // кодек
} CameraVideoMode;

// ==================== СТРУКТУРА ДЛЯ ОТОБРАЖЕНИЯ ====================
typedef struct {
    int id;                    // ID камеры
    char name[128];            // название
    int facing;                // 0-back, 1-front
    int max_width;             // макс ширина
    int max_height;            // макс высота
    float megapixels;          // мегапиксели
    float aperture;            // диафрагма
    int has_flash;             // есть вспышка
    int has_autofocus;         // автофокус
    int has_ois;               // оптическая стабилизация
    int can_record_4k;         // поддержка 4K
} CameraDisplayInfo;

// ==================== ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О КАМЕРЕ ====================
typedef struct {
    int id;
    char name[MAX_NAME];
    char model[MAX_NAME];
    char vendor[MAX_NAME];
    CameraFacing facing;
    CameraType type;
    CameraResolution resolutions[MAX_RESOLUTIONS];
    int resolution_count;
    int max_width;
    int max_height;
    float megapixels;
    float focal_length;
    float focal_length_35mm;
    float aperture;
    float min_aperture;
    float max_aperture;
    float focal_ratio;
    float field_of_view;
    float optical_zoom;
    float digital_zoom;
    int has_autofocus;
    int has_continuous_af;
    int has_touch_af;
    int has_macro;
    float min_focus_distance;
    int has_ois;
    int has_eis;
    int stabilization_modes;
    int has_flash;
    int flash_modes;
    int flash_power;
    int has_hdr;
    int hdr_modes;
    int hdr_plus;
    CameraVideoMode video_modes[MAX_FPS];
    int video_mode_count;
    int max_video_fps;
    int can_record_4k;
    int can_record_8k;
    int can_record_slowmotion;
    int can_record_hdr;
    int has_night_mode;
    int has_portrait_mode;
    int has_panorama;
    int has_burst;
    int has_timelapse;
    int has_raw;
    int has_manual_controls;
    int has_face_detection;
    int has_smile_detection;
    int has_blur_detection;
    int has_scene_detection;
    char sensor_name[MAX_NAME];
    char sensor_model[MAX_NAME];
    float sensor_size;
    float pixel_size;
    int pixel_binning;
    int iso_min;
    int iso_max;
    float shutter_speed_min;
    float shutter_speed_max;
    int available;
    int in_use;
    int exclusive;
    char status[32];
} CameraDetailedInfo;

// ==================== ПРОТОТИПЫ ФУНКЦИЙ ====================

#ifdef __cplusplus
extern "C" {
#endif

int get_camera_info(CameraDisplayInfo* cameras, int max_count);
int get_camera_detailed(int camera_id, CameraDetailedInfo* info);
void format_camera_display(const CameraDisplayInfo* cam, char* buffer, size_t buffer_size);

#ifdef __cplusplus
}
#endif

#endif // CAMERA_INFO_H
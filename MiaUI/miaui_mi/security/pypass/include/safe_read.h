//╔═════════════════════════════╗                       
//║  Link: t.me/FrontendVSCode                       ║                         
//║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║    
//║  lang: C                                         ║                     
//║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║                      
//║  build:3.10.15                                   ║
//║  files: safe_read.h                              ║    
//╚═════════════════════════════╝



#ifndef SAFE_READ_H
#define SAFE_READ_H

// ==================== ЗАЩИТА ОТ ПОВТОРНОГО ВКЛЮЧЕНИЯ ====================
#ifdef SAFE_READ_H_INCLUDED
#error "safe_read.h включен дважды!"
#endif
#define SAFE_READ_H_INCLUDED

// ==================== СТАНДАРТНЫЕ БИБЛИОТЕКИ ====================
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <limits.h>
#include <ctype.h>
#include <time.h>

// ==================== КОНСТАНТЫ БЕЗОПАСНОСТИ ====================
#define SAFE_READ_MAX_SIZE (1024 * 1024)      // максимальный размер файла (1MB)
#define SAFE_READ_MAX_PATH 4096                // максимальная длина пути
#define SAFE_READ_TIMEOUT 5                     // таймаут на чтение (сек)
#define SAFE_READ_RETRY_COUNT 3                  // количество попыток

// ==================== СТАТУСЫ ВЫПОЛНЕНИЯ ====================
typedef enum {
    SAFE_OK = 0,
    SAFE_ERROR_FILE_NOT_FOUND = -1,
    SAFE_ERROR_FILE_TOO_LARGE = -2,
    SAFE_ERROR_PERMISSION_DENIED = -3,
    SAFE_ERROR_OUT_OF_MEMORY = -4,
    SAFE_ERROR_READ_FAILED = -5,
    SAFE_ERROR_INVALID_PATH = -6,
    SAFE_ERROR_TIMEOUT = -7,
    SAFE_ERROR_NOT_A_FILE = -8,
    SAFE_ERROR_IS_DIRECTORY = -9,
    SAFE_ERROR_UNKNOWN = -99
} SafeReadError;

// ==================== ИНФОРМАЦИЯ О ФАЙЛЕ ====================
typedef struct {
    char path[SAFE_READ_MAX_PATH];             // полный путь
    char filename[256];                          // имя файла
    char extension[64];                          // расширение
    off_t size;                                   // размер
    mode_t mode;                                  // права доступа
    uid_t uid;                                    // владелец
    gid_t gid;                                    // группа
    time_t mtime;                                 // время модификации
    time_t ctime;                                 // время создания
    time_t atime;                                 // время доступа
    int is_file;                                  // это файл
    int is_dir;                                   // это директория
    int is_link;                                  // это ссылка
    int is_readable;                               // читаемый
    int is_writable;                               // записываемый
    int is_executable;                             // исполняемый
} SafeFileInfo;

// ==================== ОСНОВНЫЕ ФУНКЦИИ ====================

/**
 * Безопасное чтение файла с проверками
 */
static inline char* safe_read_file(const char* path, size_t* size) {
    if (path == NULL) {
        errno = EINVAL;
        return NULL;
    }
    
    size_t path_len = strlen(path);
    if (path_len >= SAFE_READ_MAX_PATH) {
        errno = ENAMETOOLONG;
        return NULL;
    }
    
    struct stat st;
    if (stat(path, &st) != 0) {
        return NULL;
    }
    
    if (!S_ISREG(st.st_mode)) {
        errno = (S_ISDIR(st.st_mode)) ? EISDIR : EINVAL;
        return NULL;
    }
    
    if (st.st_size > SAFE_READ_MAX_SIZE) {
        errno = EFBIG;
        return NULL;
    }
    
    if (st.st_size == 0) {
        if (size) *size = 0;
        char* empty = (char*)malloc(1);
        if (empty) empty[0] = '\0';
        return empty;
    }
    
    FILE* f = fopen(path, "r");
    if (f == NULL) return NULL;
    
    char* buffer = (char*)malloc(st.st_size + 1);
    if (buffer == NULL) {
        fclose(f);
        errno = ENOMEM;
        return NULL;
    }
    
    size_t read = fread(buffer, 1, st.st_size, f);
    int error = ferror(f);
    fclose(f);
    
    if (error || read != (size_t)st.st_size) {
        free(buffer);
        errno = EIO;
        return NULL;
    }
    
    buffer[read] = '\0';
    if (size) *size = read;
    return buffer;
}

/**
 * Безопасное чтение файла (простая версия)
 */
static inline char* safe_read_file_simple(const char* path) {
    return safe_read_file(path, NULL);
}

/**
 * Безопасное чтение числа из файла
 */
static inline long safe_read_long(const char* path) {
    char* content = safe_read_file_simple(path);
    if (content == NULL) return -1;
    
    char* p = content;
    while (*p && isspace((unsigned char)*p)) p++;
    
    long value = (*p) ? atol(p) : -1;
    free(content);
    return value;
}

/**
 * Безопасное чтение числа с плавающей точкой
 */
static inline double safe_read_double(const char* path) {
    char* content = safe_read_file_simple(path);
    if (content == NULL) return -1.0;
    
    char* p = content;
    while (*p && isspace((unsigned char)*p)) p++;
    
    double value = (*p) ? atof(p) : -1.0;
    free(content);
    return value;
}

/**
 * Безопасное чтение строки (первая строка)
 */
static inline char* safe_read_string(const char* path) {
    char* content = safe_read_file_simple(path);
    if (content == NULL) return NULL;
    
    char* nl = strchr(content, '\n');
    if (nl) *nl = '\0';
    
    char* cr = strchr(content, '\r');
    if (cr) *cr = '\0';
    
    size_t len = strlen(content);
    while (len > 0 && isspace((unsigned char)content[len - 1])) {
        content[--len] = '\0';
    }
    
    return content;
}

/**
 * Чтение всех строк файла в массив
 */
static inline char** safe_read_lines(const char* path, int* line_count) {
    if (line_count) *line_count = 0;
    
    char* content = safe_read_file_simple(path);
    if (content == NULL) return NULL;
    
    int count = 0;
    for (char* p = content; *p; p++) {
        if (*p == '\n') count++;
    }
    if (count > 0 || content[0]) count++;
    
    char** lines = (char**)malloc((count + 1) * sizeof(char*));
    if (lines == NULL) {
        free(content);
        return NULL;
    }
    
    int index = 0;
    char* line = content;
    char* next;
    
    while ((next = strchr(line, '\n')) != NULL) {
        *next = '\0';
        lines[index] = strdup(line);
        if (lines[index] == NULL) {
            for (int i = 0; i < index; i++) free(lines[i]);
            free(lines);
            free(content);
            return NULL;
        }
        index++;
        line = next + 1;
    }
    
    if (*line) {
        lines[index] = strdup(line);
        if (lines[index] == NULL) {
            for (int i = 0; i < index; i++) free(lines[i]);
            free(lines);
            free(content);
            return NULL;
        }
        index++;
    }
    
    lines[index] = NULL;
    free(content);
    
    if (line_count) *line_count = index;
    return lines;
}

/**
 * Освобождение массива строк
 */
static inline void safe_free_lines(char** lines) {
    if (lines == NULL) return;
    for (int i = 0; lines[i] != NULL; i++) {
        free(lines[i]);
    }
    free(lines);
}

// ==================== ФУНКЦИИ ПРОВЕРКИ ====================

static inline int safe_file_exists(const char* path) {
    if (path == NULL) return 0;
    struct stat st;
    return (stat(path, &st) == 0);
}

static inline int safe_is_regular_file(const char* path) {
    if (path == NULL) return 0;
    struct stat st;
    if (stat(path, &st) != 0) return 0;
    return S_ISREG(st.st_mode);
}

static inline int safe_is_directory(const char* path) {
    if (path == NULL) return 0;
    struct stat st;
    if (stat(path, &st) != 0) return 0;
    return S_ISDIR(st.st_mode);
}

static inline int safe_is_symlink(const char* path) {
    if (path == NULL) return 0;
    struct stat st;
    if (lstat(path, &st) != 0) return 0;
    return S_ISLNK(st.st_mode);
}

static inline int safe_is_readable(const char* path) {
    if (path == NULL) return 0;
    return (access(path, R_OK) == 0);
}

static inline int safe_is_writable(const char* path) {
    if (path == NULL) return 0;
    return (access(path, W_OK) == 0);
}

static inline int safe_is_executable(const char* path) {
    if (path == NULL) return 0;
    return (access(path, X_OK) == 0);
}

// ==================== ПОЛУЧЕНИЕ ИНФОРМАЦИИ ====================

static inline SafeFileInfo safe_get_file_info(const char* path) {
    SafeFileInfo info;
    memset(&info, 0, sizeof(info));
    
    if (path) {
        strncpy(info.path, path, sizeof(info.path) - 1);
        info.path[sizeof(info.path) - 1] = '\0';
        
        const char* slash = strrchr(path, '/');
        if (slash) {
            strncpy(info.filename, slash + 1, sizeof(info.filename) - 1);
        } else {
            strncpy(info.filename, path, sizeof(info.filename) - 1);
        }
        info.filename[sizeof(info.filename) - 1] = '\0';
        
        const char* dot = strrchr(info.filename, '.');
        if (dot && dot != info.filename) {
            strncpy(info.extension, dot + 1, sizeof(info.extension) - 1);
            info.extension[sizeof(info.extension) - 1] = '\0';
        }
    }
    
    struct stat st;
    if (stat(path, &st) == 0) {
        info.size = st.st_size;
        info.mode = st.st_mode;
        info.uid = st.st_uid;
        info.gid = st.st_gid;
        info.mtime = st.st_mtime;
        info.ctime = st.st_ctime;
        info.atime = st.st_atime;
        info.is_file = S_ISREG(st.st_mode);
        info.is_dir = S_ISDIR(st.st_mode);
        info.is_link = S_ISLNK(st.st_mode);
        info.is_readable = (access(path, R_OK) == 0);
        info.is_writable = (access(path, W_OK) == 0);
        info.is_executable = (access(path, X_OK) == 0);
    }
    
    return info;
}

static inline off_t safe_get_file_size(const char* path) {
    if (path == NULL) return -1;
    struct stat st;
    if (stat(path, &st) != 0) return -1;
    return st.st_size;
}

static inline time_t safe_get_mtime(const char* path) {
    if (path == NULL) return 0;
    struct stat st;
    if (stat(path, &st) != 0) return 0;
    return st.st_mtime;
}

static inline time_t safe_get_ctime(const char* path) {
    if (path == NULL) return 0;
    struct stat st;
    if (stat(path, &st) != 0) return 0;
    return st.st_ctime;
}

static inline time_t safe_get_atime(const char* path) {
    if (path == NULL) return 0;
    struct stat st;
    if (stat(path, &st) != 0) return 0;
    return st.st_atime;
}

// ==================== УТИЛИТЫ ====================

/**
 * Сравнение путей (нормализация слешей)
 */
static inline int safe_path_compare(const char* p1, const char* p2) {
    if (p1 == NULL && p2 == NULL) return 0;
    if (p1 == NULL) return -1;
    if (p2 == NULL) return 1;
    
    while (*p1 && *p2) {
        while (*p1 == '/' && *(p1 + 1) == '/') p1++;
        while (*p2 == '/' && *(p2 + 1) == '/') p2++;
        
        if (*p1 != *p2) return (int)((unsigned char)*p1 - (unsigned char)*p2);
        p1++;
        p2++;
    }
    
    while (*p1 == '/' && *(p1 + 1) == '/') p1++;
    while (*p2 == '/' && *(p2 + 1) == '/') p2++;
    
    return (int)((unsigned char)*p1 - (unsigned char)*p2);
}

/**
 * Получить строку ошибки
 */
static inline const char* safe_strerror(int err) {
    switch (err) {
        case SAFE_OK: return "Success";
        case SAFE_ERROR_FILE_NOT_FOUND: return "File not found";
        case SAFE_ERROR_FILE_TOO_LARGE: return "File too large (max 1MB)";
        case SAFE_ERROR_PERMISSION_DENIED: return "Permission denied";
        case SAFE_ERROR_OUT_OF_MEMORY: return "Out of memory";
        case SAFE_ERROR_READ_FAILED: return "Read failed";
        case SAFE_ERROR_INVALID_PATH: return "Invalid path";
        case SAFE_ERROR_TIMEOUT: return "Timeout";
        case SAFE_ERROR_NOT_A_FILE: return "Not a file";
        case SAFE_ERROR_IS_DIRECTORY: return "Is a directory";
        case SAFE_ERROR_UNKNOWN: return "Unknown error";
        default: 
            if (err > 0) return strerror(err);
            return "Unknown error";
    }
}

/**
 * Проверить, является ли путь безопасным (не содержит ..)
 */
static inline int safe_is_path_safe(const char* path) {
    if (path == NULL) return 0;
    
    const char* p = path;
    while (*p) {
        if (*p == '.' && *(p + 1) == '.' && 
            (p == path || *(p - 1) == '/') &&
            (*(p + 2) == '/' || *(p + 2) == '\0')) {
            return 0;
        }
        p++;
    }
    return 1;
}

#endif // SAFE_READ_H
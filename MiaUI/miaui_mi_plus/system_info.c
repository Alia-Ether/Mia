//╔═════════════════════════════╗                       
//║  Link: t.me/FrontendVSCode                       ║                         
//║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║    
//║  lang: C                                         ║                     
//║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║                      
//║  build:3.10.15                                   ║
//║  files: syste_info.c                             ║    
//╚═════════════════════════════╝       
                                                      

// Python API must be first
#include <Python.h>

// Standard libc
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <ctype.h>

// System
#include <sys/types.h>
#include <sys/utsname.h>
#include <sys/sysinfo.h>

// Optional headers (Android safe)
#if defined(__has_include)

#  if __has_include(<sys/statvfs.h>)
#    include <sys/statvfs.h>
#    define HAVE_STATVFS 1
#  endif

#  if __has_include(<sys/statfs.h>)
#    include <sys/statfs.h>
#    define HAVE_STATFS 1
#  endif

#  if __has_include(<ifaddrs.h>)
#    include <ifaddrs.h>
#    define HAVE_IFADDRS 1
#  endif

#  if defined(__linux__) && __has_include(<linux/if_packet.h>)
#    include <linux/if_packet.h>
#    define HAVE_LINUX_IF_PACKET 1
#  endif

#  if __has_include(<sys/system_properties.h>)
#    include <sys/system_properties.h>
#    define HAVE_SYSTEM_PROPERTIES 1
#  endif

#endif // __has_include

// Networking
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netdb.h>
#include <net/if.h>
#include <sys/ioctl.h>

// FS / process
#include <dirent.h>

#ifndef PROP_VALUE_MAX
#define PROP_VALUE_MAX 92
#endif


// --------------------------------------------------
// Безопасная обёртка для system property / getprop
// если <sys/system_properties.h> доступен — используем __system_property_get,
// иначе делаем popen("getprop KEY") как fallback.
// Возвращает число прочитанных символов (0 если нет), как __system_property_get.
// --------------------------------------------------
static int safe_getprop(const char* key, char* out, size_t n) {
#ifdef HAVE_SYSTEM_PROPERTIES
    // __system_property_get возвращает длину
    int r = __system_property_get(key, out);
    if (r > 0) {
        out[r < (int)n ? r : (int)(n-1)] = '\0';
        return r;
    }
    return 0;
#else
    // fallback: popen("getprop key")
    char cmd[256];
    FILE *f;
    int len = 0;
    if (snprintf(cmd, sizeof(cmd), "getprop %s", key) >= (int)sizeof(cmd))
        return 0;
    f = popen(cmd, "r");
    if (!f) return 0;
    if (fgets(out, n, f) != NULL) {
        out[strcspn(out, "\r\n")] = 0;
        len = strlen(out);
    }
    pclose(f);
    return len;
#endif
}

// ========================================================
// БЛОК 1:  ОТКРЫТИЕ БЛОКОВ
// Возвращает dict с kernel/sysname/release/version/machine
// ========================================================
static PyObject* get_kernel_info(PyObject* self, PyObject* args) {
    struct utsname buffer;

    if (uname(&buffer) != 0) {
        PyErr_SetString(PyExc_RuntimeError, "uname() failed");
        return NULL;
    }

    PyObject* dict = PyDict_New();
    if (!dict) return PyErr_NoMemory();

    PyObject *tmp = NULL;

    tmp = PyUnicode_FromString(buffer.sysname);
    if (!tmp) { Py_DECREF(dict); return PyErr_NoMemory(); }
    PyDict_SetItemString(dict, "sysname", tmp);
    Py_DECREF(tmp);

    tmp = PyUnicode_FromString(buffer.release);
    if (!tmp) { Py_DECREF(dict); return PyErr_NoMemory(); }
    PyDict_SetItemString(dict, "release", tmp);
    Py_DECREF(tmp);

    tmp = PyUnicode_FromString(buffer.version);
    if (!tmp) { Py_DECREF(dict); return PyErr_NoMemory(); }
    PyDict_SetItemString(dict, "version", tmp);
    Py_DECREF(tmp);

    tmp = PyUnicode_FromString(buffer.machine);
    if (!tmp) { Py_DECREF(dict); return PyErr_NoMemory(); }
    PyDict_SetItemString(dict, "machine", tmp);
    Py_DECREF(tmp);

    return dict;
}


// ========================================================
// БЛОК 2:  RAM / UPTIME / PROCESS COUNT
// Возвращает dict: total_ram_mb, free_ram_mb, available_ram_mb, procs, uptime
// ========================================================
static PyObject* get_ram_info(PyObject* self, PyObject* args) {
    FILE *f = fopen("/proc/meminfo", "r");
    unsigned long long total = 0, free = 0, available = 0;
    char line[256];

    if (f) {
        while (fgets(line, sizeof(line), f)) {
            if (sscanf(line, "MemTotal: %llu kB", &total) == 1) continue;
            if (sscanf(line, "MemFree: %llu kB", &free) == 1) continue;
            if (sscanf(line, "MemAvailable: %llu kB", &available) == 1) continue;
        }
        fclose(f);
    }

    struct sysinfo info;
    sysinfo(&info); 
    unsigned long long mem_unit = info.mem_unit ? info.mem_unit : 1;

    PyObject* dict = PyDict_New();
    if (!dict) return PyErr_NoMemory();

    if (total > 0) {
        // Из /proc/meminfo (уже в kB)
        PyDict_SetItemString(dict, "total_ram_mb", PyLong_FromUnsignedLongLong(total / 1024));
        PyDict_SetItemString(dict, "free_ram_mb", PyLong_FromUnsignedLongLong(free / 1024));
        PyDict_SetItemString(dict, "available_ram_mb", PyLong_FromUnsignedLongLong(available / 1024));
    } else {
        // Fallback на sysinfo (учитываем mem_unit)
        unsigned long long total_bytes = (unsigned long long)info.totalram * mem_unit;
        unsigned long long free_bytes = (unsigned long long)info.freeram * mem_unit;
        unsigned long long buffer_bytes = (unsigned long long)info.bufferram * mem_unit;
        
        PyDict_SetItemString(dict, "total_ram_mb", PyLong_FromUnsignedLongLong(total_bytes / (1024 * 1024)));
        PyDict_SetItemString(dict, "free_ram_mb", PyLong_FromUnsignedLongLong(free_bytes / (1024 * 1024)));
        // available_ram примерно free + buffers
        PyDict_SetItemString(dict, "available_ram_mb", PyLong_FromUnsignedLongLong((free_bytes + buffer_bytes) / (1024 * 1024)));
    }

    PyDict_SetItemString(dict, "procs", PyLong_FromLong((long)info.procs));
    PyDict_SetItemString(dict, "uptime", PyLong_FromLong((long)info.uptime));

    return dict;
}


// ========================================================
// БЛОК 3:  READ HARDWARE FILE (/sys /proc)
// Принимает путь, возвращает первое содержимое строки (строка без \n).
// Если доступ запрещен, просит SU.
// ========================================================
static PyObject* get_hw_stat(PyObject* self, PyObject* args) {
    const char* path;
    if (!PyArg_ParseTuple(args, "s", &path)) return NULL;

    FILE *f = fopen(path, "r");
    if (!f) {
        if (errno == EACCES || errno == EPERM) {
            return PyUnicode_FromString("Извините, для этого требуются su права супер пользователя 🛡️");
        }
        if (errno == ENOENT) {
            return PyUnicode_FromString("Извините, возможно эта команда предназначена для su или Rish 🔍");
        }
        char err_msg[256];
        snprintf(err_msg, sizeof(err_msg), "Ошибка: %s", strerror(errno));
        return PyUnicode_FromString(err_msg);
    }

    char buffer[256];
    if (!fgets(buffer, sizeof(buffer), f)) {
        fclose(f);
        return PyUnicode_FromString("Данные отсутствуют 📭");
    }
    fclose(f);

    buffer[strcspn(buffer, "\r\n")] = 0;
    return PyUnicode_FromString(buffer);
}


// ========================================================
// БЛОК 4:  DISK SPACE INFO (statvfs)
// Возвращает dict total_mb, free_mb
// ========================================================
static PyObject* get_disk_info(PyObject* self, PyObject* args) {
    const char* path;
#if !defined(HAVE_STATVFS)
    // statvfs may be unavailable; fail early
#endif
    if (!PyArg_ParseTuple(args, "s", &path)) return NULL;

#ifdef HAVE_STATVFS
    struct statvfs vfs;
    if (statvfs(path, &vfs) != 0) {
        PyErr_SetFromErrnoWithFilename(PyExc_OSError, path);
        return NULL;
    }

    unsigned long long block_size = (unsigned long long)vfs.f_frsize;
    unsigned long long total = (unsigned long long)vfs.f_blocks * block_size;
    unsigned long long free = (unsigned long long)vfs.f_bavail * block_size;
#else
    struct statfs sfs;
    if (statfs(path, &sfs) != 0) {
        PyErr_SetFromErrnoWithFilename(PyExc_OSError, path);
        return NULL;
    }
    unsigned long long block_size = (unsigned long long)sfs.f_bsize;
    unsigned long long total = (unsigned long long)sfs.f_blocks * block_size;
    unsigned long long free = (unsigned long long)sfs.f_bavail * block_size;
#endif

    PyObject* dict = PyDict_New();
    if (!dict) return PyErr_NoMemory();

    PyObject* tmp = PyLong_FromUnsignedLongLong(total / 1048576ULL);
    if (!tmp) { Py_DECREF(dict); return PyErr_NoMemory(); }
    PyDict_SetItemString(dict, "total_mb", tmp);
    Py_DECREF(tmp);

    tmp = PyLong_FromUnsignedLongLong(free / 1048576ULL);
    if (!tmp) { Py_DECREF(dict); return PyErr_NoMemory(); }
    PyDict_SetItemString(dict, "free_mb", tmp);
    Py_DECREF(tmp);

    return dict;
}


// ========================================================
// БЛОК 5:  CPU TEMPERATURE (thermal zones)
// Ищет несколько зон, возвращает float Celsius или сообщение о SU
// ========================================================
static PyObject* get_temperature(PyObject* self, PyObject* args) {
    const char* zones[] = {
        "/sys/class/thermal/thermal_zone0/temp",
        "/sys/class/thermal/thermal_zone1/temp",
        "/sys/class/thermal/thermal_zone2/temp",
        "/sys/class/thermal/thermal_message/s_temp",
        NULL
    };

    FILE* f = NULL;
    int temp = -1;
    int access_denied = 0;

    for (int i = 0; zones[i] != NULL; ++i) {
        f = fopen(zones[i], "r");
        if (!f) {
            if (errno == EACCES) access_denied = 1;
            continue;
        }
        if (fscanf(f, "%d", &temp) == 1) {
            fclose(f);
            return PyFloat_FromDouble((double)temp / 1000.0);
        }
        fclose(f);
    }

    // Если ничего не нашли, пробуем termux-api (если есть)
    FILE* api = popen("termux-battery-status 2>/dev/null", "r");
    if (api) {
        char buf[512];
        while (fgets(buf, sizeof(buf), api)) {
            char* t = strstr(buf, "\"temperature\":");
            if (t) {
                double bt;
                if (sscanf(t, "\"temperature\": %lf", &bt) == 1) {
                    pclose(api);
                    return PyFloat_FromDouble(bt);
                }
            }
        }
        pclose(api);
    }

    if (access_denied) {
        return PyUnicode_FromString("Извините, для температуры нужны SU права 🛡️");
    }

    return PyUnicode_FromString("Температура недоступна 🌡️");
}


// ========================================================
// БЛОК 6:  BATTERY DETAILS (Android sysfs power_supply)
// Возвращает dict: health, voltage_v, technology
// ========================================================
static PyObject* get_battery_details(PyObject* self, PyObject* args) {
    const char* bases[] = {
        "/sys/class/power_supply/battery/",
        "/sys/class/power_supply/BAT0/",
        "/sys/class/power_supply/bms/",
        NULL
    };

    char path[256];
    char health[32] = "Unknown";
    char tech[32] = "Unknown";
    long voltage = -1;
    FILE* f = NULL;
    int has_sysfs = 0;

    for (int i = 0; bases[i] != NULL; ++i) {
        snprintf(path, sizeof(path), "%shealth", bases[i]);
        f = fopen(path, "r");
        if (f) {
            if (fscanf(f, "%31s", health) == 1) has_sysfs = 1;
            fclose(f);
        }

        snprintf(path, sizeof(path), "%svoltage_now", bases[i]);
        f = fopen(path, "r");
        if (f) {
            fscanf(f, "%ld", &voltage);
            fclose(f);
        }

        snprintf(path, sizeof(path), "%stechnology", bases[i]);
        f = fopen(path, "r");
        if (f) {
            fscanf(f, "%31s", tech);
            fclose(f);
        }
    }

    // Если в sysfs пусто или нет данных, пробуем termux-api
    if (!has_sysfs || voltage <= 0) {
        FILE* api = popen("termux-battery-status 2>/dev/null", "r");
        if (api) {
            char buf[1024];
            while (fgets(buf, sizeof(buf), api)) {
                char* h = strstr(buf, "\"health\":");
                if (h) sscanf(h, "\"health\": \"%31[^\"]\"", health);
                
                char* v = strstr(buf, "\"voltage\":");
                if (v) {
                    double v_double;
                    if (sscanf(v, "\"voltage\": %lf", &v_double) == 1) {
                        voltage = (long)(v_double * 1000000); // В микровольты для унификации
                    }
                }
            }
            pclose(api);
        }
    }

    PyObject* dict = PyDict_New();
    if (!dict) return PyErr_NoMemory();

    PyDict_SetItemString(dict, "health", PyUnicode_FromString(health));

    if (voltage > 0) {
        // Подгоняем к вольтам (sysfs обычно в мкВ)
        double v_final = (voltage > 1000000) ? (double)voltage / 1000000.0 : (double)voltage / 1000.0;
        PyDict_SetItemString(dict, "voltage_v", PyFloat_FromDouble(v_final));
    } else {
        Py_INCREF(Py_None);
        PyDict_SetItemString(dict, "voltage_v", Py_None);
        Py_DECREF(Py_None);
    }

    PyDict_SetItemString(dict, "technology", PyUnicode_FromString(tech));

    return dict;
}


// ========================================================
// БЛОК 7: CPU FREQUENCY (динамическое число ядер, Android-safe)
// Возвращает list частот в MHz (или -1 если не доступно)
// ========================================================
static PyObject* get_cpu_freq(PyObject* self, PyObject* args) {
    long cores = sysconf(_SC_NPROCESSORS_CONF);
    if (cores < 1) cores = 8;

    long *freqs = (long*)calloc((size_t)cores, sizeof(long));
    if (!freqs) return PyErr_NoMemory();

    int access_denied_count = 0;
    char path[256];
    for (int i = 0; i < (int)cores; ++i) {
        long freq = -1;
        FILE *f = NULL;

        snprintf(path, sizeof(path),
                 "/sys/devices/system/cpu/cpu%d/cpufreq/scaling_cur_freq", i);
        f = fopen(path, "r");
        if (!f) {
            if (errno == EACCES) access_denied_count++;
            snprintf(path, sizeof(path),
                     "/sys/devices/system/cpu/cpu%d/cpufreq/cpuinfo_cur_freq", i);
            f = fopen(path, "r");
        }
        if (f) {
            if (fscanf(f, "%ld", &freq) != 1) freq = -1;
            fclose(f);
            if (freq > 0) freq /= 1000; // kHz -> MHz
        }
        freqs[i] = freq;
    }

    if (access_denied_count == cores) {
        free(freqs);
        return PyUnicode_FromString("Извините, для частот CPU нужны SU права 🛡️");
    }

    PyObject* list = PyList_New(0);
    if (!list) { free(freqs); return PyErr_NoMemory(); }

    for (int i = 0; i < (int)cores; ++i) {
        PyObject* tmp = PyLong_FromLong((long)freqs[i]);
        if (!tmp) { Py_DECREF(list); free(freqs); return PyErr_NoMemory(); }
        PyList_Append(list, tmp);
        Py_DECREF(tmp);
    }

    free(freqs);
    return list;
}


// ========================================================
// БЛОК 8: LOCAL IP ADDRESS (Android / Termux safe)
// Возвращает IPv4 адрес активного интерфейса или "127.0.0.1"
// ========================================================
static PyObject* get_local_ip(PyObject* self, PyObject* args) {
#if !defined(HAVE_IFADDRS)
    // Если getifaddrs не доступен — возвращаем loopback
    return PyUnicode_FromString("127.0.0.1");
#else
    struct ifaddrs *ifaddr = NULL, *ifa;
    char ip[INET_ADDRSTRLEN] = "127.0.0.1";

    if (getifaddrs(&ifaddr) == -1) {
        return PyUnicode_FromString(ip);
    }

    for (ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next) {
        if (!ifa->ifa_addr) continue;
        if (ifa->ifa_addr->sa_family == AF_INET) {
            if (strcmp(ifa->ifa_name, "lo") == 0) continue;
            struct sockaddr_in* sa = (struct sockaddr_in*)ifa->ifa_addr;
            inet_ntop(AF_INET, &sa->sin_addr, ip, sizeof(ip));
            break;
        }
    }

    freeifaddrs(ifaddr);
    return PyUnicode_FromString(ip);
#endif
}


// ========================================================
// БЛОК 9: MAC ADDRESS (Termux-safe)
// Возвращает MAC первого доступного AF_PACKET интерфейса
// Если не доступно — возвращает "00:00:00:00:00:00"
// ========================================================
static PyObject* get_mac_address(PyObject* self, PyObject* args) {
    char mac_str[18] = "00:00:00:00:00:00";

#if defined(HAVE_IFADDRS) && defined(HAVE_LINUX_IF_PACKET)
    struct ifaddrs *ifaddr = NULL, *ifa;
    if (getifaddrs(&ifaddr) == -1) {
        return PyUnicode_FromString(mac_str);
    }

    for (ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next) {
        if (!ifa->ifa_addr) continue;
        if (ifa->ifa_addr->sa_family == AF_PACKET) {
            struct sockaddr_ll *s = (struct sockaddr_ll *)ifa->ifa_addr;
            if (s->sll_halen == 6) {
                snprintf(mac_str, sizeof(mac_str),
                         "%02x:%02x:%02x:%02x:%02x:%02x",
                         (unsigned char)s->sll_addr[0], (unsigned char)s->sll_addr[1],
                         (unsigned char)s->sll_addr[2], (unsigned char)s->sll_addr[3],
                         (unsigned char)s->sll_addr[4], (unsigned char)s->sll_addr[5]);
                break;
            }
        }
    }

    freeifaddrs(ifaddr);
    return PyUnicode_FromString(mac_str);
#else
    // fallback: попытаться ioctl на стандартных интерфейсах
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) return PyUnicode_FromString(mac_str);

    struct ifreq ifr;
    const char* ifnames[] = {"wlan0", "eth0", "rmnet_data0", NULL};
    for (int i = 0; ifnames[i] != NULL; ++i) {
        memset(&ifr, 0, sizeof(ifr));
        strncpy(ifr.ifr_name, ifnames[i], IFNAMSIZ-1);
        if (ioctl(sock, SIOCGIFHWADDR, &ifr) == 0) {
            unsigned char *mac = (unsigned char *)ifr.ifr_hwaddr.sa_data;
            snprintf(mac_str, sizeof(mac_str),
                     "%02x:%02x:%02x:%02x:%02x:%02x",
                     mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
            break;
        }
    }
    close(sock);
    return PyUnicode_FromString(mac_str);
#endif
}


// ========================================================
// БЛОК 10: PROCESS LIST (/proc PID scan, Termux-safe)
// Возвращает список строк PID
// ========================================================
static PyObject* get_process_list(PyObject* self, PyObject* args) {
    PyObject* list = PyList_New(0);
    if (!list) return PyErr_NoMemory();

    DIR *dir = opendir("/proc");
    if (!dir) {
        Py_DECREF(list);
        PyErr_SetString(PyExc_PermissionError, "Cannot open /proc");
        return NULL;
    }

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        const char *name = entry->d_name;
        int numeric = 1;
        for (int i = 0; name[i]; ++i) {
            if (!isdigit((unsigned char)name[i])) { numeric = 0; break; }
        }
        if (numeric) {
            PyObject *pid = PyUnicode_FromString(name);
            if (!pid) continue;
            PyList_Append(list, pid);
            Py_DECREF(pid);
        }
    }
    closedir(dir);
    return list;
}


// ========================================================
// БЛОК 11: ANDROID SECURITY STATUS (SELinux / Debug / Crypto)
// Возвращает dict: selinux_boot, adb_debug, encryption
// ========================================================
static PyObject* get_security_status(PyObject* self, PyObject* args) {
    PyObject* dict = PyDict_New();
    if (!dict) return PyErr_NoMemory();

    char value[PROP_VALUE_MAX] = {0};
    int len = 0;
    PyObject* tmp = NULL;

    // SELinux boot state
    len = safe_getprop("ro.boot.selinux", value, sizeof(value));
    tmp = PyUnicode_FromString(len > 0 ? value : "unknown");
    if (!tmp) { Py_DECREF(dict); return PyErr_NoMemory(); }
    PyDict_SetItemString(dict, "selinux_boot", tmp);
    Py_DECREF(tmp);

    // adb/debug
    memset(value, 0, sizeof(value));
    len = safe_getprop("ro.debuggable", value, sizeof(value));
    tmp = PyUnicode_FromString((len > 0 && value[0] == '1') ? "ENABLED" : "disabled");
    if (!tmp) { Py_DECREF(dict); return PyErr_NoMemory(); }
    PyDict_SetItemString(dict, "adb_debug", tmp);
    Py_DECREF(tmp);

    // encryption
    memset(value, 0, sizeof(value));
    len = safe_getprop("ro.crypto.state", value, sizeof(value));
    tmp = PyUnicode_FromString(len > 0 ? value : "unencrypted");
    if (!tmp) { Py_DECREF(dict); return PyErr_NoMemory(); }
    PyDict_SetItemString(dict, "encryption", tmp);
    Py_DECREF(tmp);

    return dict;
}


// ========================================================
// БЛОК 12: DISPLAY STATS (ЯРКОСТЬ ЭКРАНА + ТИП ПАНЕЛИ)
// Возвращает dict: brightness, panel_type
// ========================================================
static PyObject* get_display_stats(PyObject* self, PyObject* args) {
    const char* paths[] = {
        "/sys/class/backlight/panel0-backlight/brightness",
        "/sys/class/backlight/backlight/brightness",
        "/sys/class/leds/lcd-backlight/brightness",
        NULL
    };

    FILE* f = NULL;
    int brightness = -1;
    for (int i = 0; paths[i] != NULL; ++i) {
        f = fopen(paths[i], "r");
        if (f) {
            if (fscanf(f, "%d", &brightness) != 1) brightness = -1;
            fclose(f);
            break;
        }
    }

    PyObject* dict = PyDict_New();
    if (!dict) return PyErr_NoMemory();

    PyObject* tmp = PyLong_FromLong(brightness);
    if (!tmp) { Py_DECREF(dict); return PyErr_NoMemory(); }
    PyDict_SetItemString(dict, "brightness", tmp);
    Py_DECREF(tmp);

    char panel[PROP_VALUE_MAX] = {0};
    if (safe_getprop("ro.boot.panel_type", panel, sizeof(panel)) <= 0) {
        strncpy(panel, "Unknown", sizeof(panel)-1);
        panel[sizeof(panel)-1] = '\0';
    }

    tmp = PyUnicode_FromString(panel);
    if (!tmp) { Py_DECREF(dict); return PyErr_NoMemory(); }
    PyDict_SetItemString(dict, "panel_type", tmp);
    Py_DECREF(tmp);

    return dict;
}


// ========================================================
// БЛОК 13: TOP CPU RESOURCE HOG
// Возвращает dict: pid, name, cpu_ticks
// ========================================================
static PyObject* get_top_resource_hog(PyObject* self, PyObject* args) {
    DIR *dir = opendir("/proc");
    if (!dir) {
        PyErr_SetString(PyExc_PermissionError, "Cannot open /proc");
        return NULL;
    }

    struct dirent *entry;
    unsigned long max_time = 0;
    int hog_pid = -1;
    char hog_comm[256] = "None";

    while ((entry = readdir(dir)) != NULL) {
        if (!isdigit((unsigned char)entry->d_name[0])) continue;

        char stat_path[512];
        snprintf(stat_path, sizeof(stat_path), "/proc/%s/stat", entry->d_name);
        FILE *f = fopen(stat_path, "r");
        if (!f) continue;

        int pid = 0;
        char comm[256] = {0};
        char state;
        unsigned long utime = 0, stime = 0;

        if (fscanf(f, "%d ", &pid) == 1) {
            if (fscanf(f, " (%255[^)]) %c", comm, &state) == 2) {
                for (int i = 0; i < 11; ++i) fscanf(f, "%*s");
                if (fscanf(f, "%lu %lu", &utime, &stime) == 2) {
                    unsigned long total = utime + stime;
                    if (total > max_time) {
                        max_time = total;
                        hog_pid = pid;
                        strncpy(hog_comm, comm, sizeof(hog_comm)-1);
                        hog_comm[sizeof(hog_comm)-1] = '\0';
                    }
                }
            }
        }
        fclose(f);
    }
    closedir(dir);

    PyObject* dict = PyDict_New();
    if (!dict) return PyErr_NoMemory();

    PyObject* tmp = PyLong_FromLong(hog_pid);
    if (!tmp) { Py_DECREF(dict); return PyErr_NoMemory(); }
    PyDict_SetItemString(dict, "pid", tmp);
    Py_DECREF(tmp);

    tmp = PyUnicode_FromString(hog_comm);
    if (!tmp) { Py_DECREF(dict); return PyErr_NoMemory(); }
    PyDict_SetItemString(dict, "name", tmp);
    Py_DECREF(tmp);

    tmp = PyLong_FromUnsignedLong(max_time);
    if (!tmp) { Py_DECREF(dict); return PyErr_NoMemory(); }
    PyDict_SetItemString(dict, "cpu_ticks", tmp);
    Py_DECREF(tmp);

    return dict;
}


// ========================================================
// БЛОК 14: NETWORK TRAFFIC MONITOR
// Возвращает dict: interface, down_mb, up_mb
// ========================================================
static PyObject* get_net_traffic(PyObject* self, PyObject* args) {
    DIR *netdir = opendir("/sys/class/net");
    if (!netdir) {
        // возвращаем пустой dict с интерфейс unknown
        PyObject* d = PyDict_New();
        if (!d) return PyErr_NoMemory();
        PyObject* tmp = PyUnicode_FromString("unknown");
        PyDict_SetItemString(d, "interface", tmp);
        Py_DECREF(tmp);
        tmp = PyFloat_FromDouble(0.0);
        PyDict_SetItemString(d, "down_mb", tmp); Py_DECREF(tmp);
        tmp = PyFloat_FromDouble(0.0);
        PyDict_SetItemString(d, "up_mb", tmp); Py_DECREF(tmp);
        return d;
    }

    struct dirent *ent;
    unsigned long long rx = 0, tx = 0;
    char iface[64] = "unknown";

    while ((ent = readdir(netdir)) != NULL) {
        if (ent->d_name[0] == '.') continue;
        if (strcmp(ent->d_name, "lo") == 0) continue;

        char oper_path[256];
        snprintf(oper_path, sizeof(oper_path), "/sys/class/net/%s/operstate", ent->d_name);
        FILE* f = fopen(oper_path, "r");
        if (!f) continue;
        char state[16] = {0};
        if (!fgets(state, sizeof(state), f)) { fclose(f); continue; }
        fclose(f);
        if (strncmp(state, "up", 2) != 0) continue;

        strncpy(iface, ent->d_name, sizeof(iface)-1);
        iface[sizeof(iface)-1] = '\0';

        char rx_path[256], tx_path[256];
        snprintf(rx_path, sizeof(rx_path), "/sys/class/net/%s/statistics/rx_bytes", iface);
        snprintf(tx_path, sizeof(tx_path), "/sys/class/net/%s/statistics/tx_bytes", iface);

        f = fopen(rx_path, "r");
        if (f) {
            fscanf(f, "%llu", &rx);
            fclose(f);
        }
        f = fopen(tx_path, "r");
        if (f) {
            fscanf(f, "%llu", &tx);
            fclose(f);
        }
        break;
    }
    closedir(netdir);

    PyObject* dict = PyDict_New();
    if (!dict) return PyErr_NoMemory();

    PyObject* tmp = PyUnicode_FromString(iface);
    if (!tmp) { Py_DECREF(dict); return PyErr_NoMemory(); }
    PyDict_SetItemString(dict, "interface", tmp);
    Py_DECREF(tmp);

    tmp = PyFloat_FromDouble((double)rx / 1048576.0);
    if (!tmp) { Py_DECREF(dict); return PyErr_NoMemory(); }
    PyDict_SetItemString(dict, "down_mb", tmp);
    Py_DECREF(tmp);

    tmp = PyFloat_FromDouble((double)tx / 1048576.0);
    if (!tmp) { Py_DECREF(dict); return PyErr_NoMemory(); }
    PyDict_SetItemString(dict, "up_mb", tmp);
    Py_DECREF(tmp);

    return dict;
}



// ========================================================
// БЛОК 15: ACTIVE ANDROID ACTIVITY / FOREGROUND APP
// Возвращает строку с output dumpsys
// ========================================================
static PyObject* get_active_activity(PyObject* self, PyObject* args)
{
    const char* command = "dumpsys window 2>/dev/null | grep -E 'mCurrentFocus|mFocusedApp'";

    FILE* fp = popen(command, "r");
    if (!fp) {
        return PyUnicode_FromString("Извините, возможно эта команда предназначена для su или Rish 🔍");
    }

    char buffer[1024];
    PyObject* result = PyUnicode_New(0, 127);
    if (!result) {
        pclose(fp);
        return PyErr_NoMemory();
    }

    int found = 0;
    while (fgets(buffer, sizeof(buffer), fp)) {
        found = 1;
        PyObject* chunk = PyUnicode_FromString(buffer);
        if (chunk) {
            PyUnicode_Append(&result, chunk);
            Py_DECREF(chunk);
        }
    }

    pclose(fp);

    if (!found) {
        Py_DECREF(result);
        return PyUnicode_FromString("Извините, для доступа к активности требуются su права 🛡️");
    }

    return result;
}


// ========================================================
// БЛОК 16: SYSTEM LOAD AVERAGE (Android / Termux)
// Читается только через /proc/loadavg
// ========================================================
static PyObject* get_load_avg(PyObject* self, PyObject* args) {

    FILE *f = fopen("/proc/loadavg", "r");
    if (!f) {
        PyErr_SetString(PyExc_RuntimeError,
                        "loadavg unavailable");
        return NULL;
    }

    double l1 = 0.0, l5 = 0.0, l15 = 0.0;

    if (fscanf(f, "%lf %lf %lf", &l1, &l5, &l15) != 3) {
        fclose(f);
        PyErr_SetString(PyExc_RuntimeError,
                        "failed parsing /proc/loadavg");
        return NULL;
    }

    fclose(f);

    PyObject* dict = PyDict_New();
    if (!dict)
        return PyErr_NoMemory();

    PyObject* tmp;

    tmp = PyFloat_FromDouble(l1);
    if (!tmp) { Py_DECREF(dict); return PyErr_NoMemory(); }
    PyDict_SetItemString(dict, "1min", tmp);
    Py_DECREF(tmp);

    tmp = PyFloat_FromDouble(l5);
    if (!tmp) { Py_DECREF(dict); return PyErr_NoMemory(); }
    PyDict_SetItemString(dict, "5min", tmp);
    Py_DECREF(tmp);

    tmp = PyFloat_FromDouble(l15);
    if (!tmp) { Py_DECREF(dict); return PyErr_NoMemory(); }
    PyDict_SetItemString(dict, "15min", tmp);
    Py_DECREF(tmp);

    return dict;
}
// ========================================================
// БЛОК 17: NETWORK SOCKET COUNT (TCP)
// Возвращает int — количество записей в /proc/net/tcp (без заголовка)
// ========================================================
static PyObject* get_socket_count(PyObject* self, PyObject* args) {
    FILE *f = fopen("/proc/net/tcp", "r");
    if (!f) {
        if (errno == EACCES || errno == EPERM) {
            return PyUnicode_FromString("Извините, для этого требуются su права супер пользователя 🛡️");
        }
        return PyLong_FromLong(0);
    }

    int count = -1;
    char buffer[256];
    while (fgets(buffer, sizeof(buffer), f)) count++;
    fclose(f);
    if (count < 0) count = 0;
    return PyLong_FromLong(count);
}


// ========================================================
// БЛОК 18: KERNEL ENTROPY POOL
// Возвращает int entropy_available
// ========================================================
static PyObject* get_entropy(PyObject* self, PyObject* args) {

    const char* entropy_path =
        "/proc/sys/kernel/random/entropy_avail";

    FILE* f = fopen(entropy_path, "r");
    if (!f) {
        if (errno == EACCES || errno == EPERM) {
            return PyUnicode_FromString("Извините, для этого требуются su права супер пользователя 🛡️");
        }
        return PyLong_FromLong(0);
    }

    int entropy = 0;

    if (fscanf(f, "%d", &entropy) != 1) {
        fclose(f);
        return PyLong_FromLong(0);
    }

    fclose(f);

    return PyLong_FromLong(entropy);
}

// ========================================================
// БЛОК 19: CPU USAGE PERCENT (delta since last call)
// Возвращает float 0..100
// ========================================================
static PyObject* get_cpu_usage(PyObject* self, PyObject* args) {

    static unsigned long long prev_total = 0;
    static unsigned long long prev_idle  = 0;

    FILE *f = fopen("/proc/stat", "r");
    if (!f) {
        if (errno == EACCES || errno == EPERM) {
            return PyUnicode_FromString("Извините, для этого требуются su права супер пользователя 🛡️");
        }
        return PyFloat_FromDouble(0.0);
    }

    char cpu_label[16];

    unsigned long long user = 0,
                       nice = 0,
                       system = 0,
                       idle = 0,
                       iowait = 0,
                       irq = 0,
                       softirq = 0,
                       steal = 0;

    if (fscanf(
            f,
            "%15s %llu %llu %llu %llu %llu %llu %llu %llu",
            cpu_label,
            &user,
            &nice,
            &system,
            &idle,
            &iowait,
            &irq,
            &softirq,
            &steal) < 8) {

        fclose(f);
        return PyFloat_FromDouble(0.0);
    }

    fclose(f);

    unsigned long long idle_all =
        idle + iowait;

    unsigned long long total =
        user + nice + system +
        idle + iowait +
        irq + softirq + steal;

    double usage = 0.0;

    if (prev_total != 0) {

        unsigned long long totald =
            total - prev_total;

        unsigned long long idled =
            idle_all - prev_idle;

        if (totald > 0)
            usage =
                (double)(totald - idled)
                * 100.0 / (double)totald;
    }

    prev_total = total;
    prev_idle  = idle_all;

    return PyFloat_FromDouble(usage);
}
// ========================================================
// БЛОК 20: SYSTEM PULSE SNAPSHOT
// Возвращает dict: cpu_cores_total, cpu_cores_online, max_open_files, free_storage_mb, swap_total_mb, swap_free_mb, swap_present
// ========================================================
static PyObject* get_system_pulse(PyObject* self, PyObject* args) {
    PyObject* dict = PyDict_New();
    if (!dict) return PyErr_NoMemory();

    long total = sysconf(_SC_NPROCESSORS_CONF);
    long online = sysconf(_SC_NPROCESSORS_ONLN);
    if (total > 0) { PyObject* tmp = PyLong_FromLong(total); PyDict_SetItemString(dict, "cpu_cores_total", tmp); Py_DECREF(tmp); }
    if (online > 0) { PyObject* tmp = PyLong_FromLong(online); PyDict_SetItemString(dict, "cpu_cores_online", tmp); Py_DECREF(tmp); }

    long open_max = sysconf(_SC_OPEN_MAX);
    if (open_max > 0) { PyObject* tmp = PyLong_FromLong(open_max); PyDict_SetItemString(dict, "max_open_files", tmp); Py_DECREF(tmp); }

    // Storage: try Termux home then /data then /
#ifdef HAVE_STATFS
    struct statfs sf;
    if (statfs("/data/data/com.termux/files/home", &sf) != 0) {
        if (statfs("/data", &sf) != 0) statfs("/", &sf);
    }
    unsigned long long free_bytes = (unsigned long long)sf.f_bsize * (unsigned long long)sf.f_bavail;
    PyObject* tmp = PyLong_FromUnsignedLongLong(free_bytes / 1048576ULL);
    PyDict_SetItemString(dict, "free_storage_mb", tmp); Py_DECREF(tmp);
#else
    // fallback: unknown
    PyObject* tmp = PyLong_FromLong(-1);
    PyDict_SetItemString(dict, "free_storage_mb", tmp); Py_DECREF(tmp);
#endif

    // Swap
    struct sysinfo si;
    if (sysinfo(&si) == 0) {
        PyObject* tmp2 = PyLong_FromLong((long)(si.totalswap / 1024 / 1024));
        PyDict_SetItemString(dict, "swap_total_mb", tmp2); Py_DECREF(tmp2);
        tmp2 = PyLong_FromLong((long)(si.freeswap / 1024 / 1024));
        PyDict_SetItemString(dict, "swap_free_mb", tmp2); Py_DECREF(tmp2);
        tmp2 = PyBool_FromLong(si.totalswap > 0);
        PyDict_SetItemString(dict, "swap_present", tmp2); Py_DECREF(tmp2);
    }

    return dict;
}

// ========================================================
// BLOCK 21: ANDROID ERROR EXPLAINER (RU + EN)
// Human readable system error decoder
// ========================================================


static PyObject* mia_android_error(
        const char* metric,
        const char* path,
        const char* syscall
) {
    int err = errno;

    const char* en_reason = "Unknown system error.";
    const char* ru_reason = "Неизвестная системная ошибка.";

    const char* hint_en = "Check permissions or execution context.";
    const char* hint_ru = "Проверь права доступа и окружение выполнения.";

    switch (err) {

        case EACCES:
            en_reason = "Permission denied by Android sandbox or SELinux.";
            ru_reason = "Доступ запрещён Android sandbox или SELinux.";

            hint_en = "Requires root, adb shell, or privileged app.";
            hint_ru = "Требуется root, adb shell или привилегированное приложение.";
            break;

        case EPERM:
            en_reason = "Operation not permitted.";
            ru_reason = "Операция запрещена.";

            hint_en = "Kernel security policy blocked this action.";
            hint_ru = "Политика безопасности ядра заблокировала действие.";
            break;

        case ENOENT:
            en_reason = "File or interface does not exist.";
            ru_reason = "Файл или интерфейс отсутствует.";

            hint_en = "Path may differ on this device or Android version.";
            hint_ru = "Путь может отличаться на этой версии Android.";
            break;

        case EBUSY:
            en_reason = "Resource busy.";
            ru_reason = "Ресурс занят.";

            hint_en = "Try again later.";
            hint_ru = "Попробуйте позже.";
            break;

        case EROFS:
            en_reason = "Read-only filesystem.";
            ru_reason = "Файловая система только для чтения.";

            hint_en = "Mount namespace restricts write access.";
            hint_ru = "Namespace Android запрещает запись.";
            break;

        case ENOTDIR:
            en_reason = "Invalid path component.";
            ru_reason = "Некорректный путь.";

            hint_en = "One of path elements is not a directory.";
            hint_ru = "Один из элементов пути не является каталогом.";
            break;

        case ENOSYS:
            en_reason = "Kernel interface not implemented.";
            ru_reason = "Интерфейс не реализован в ядре.";

            hint_en = "This metric is unsupported on this device.";
            hint_ru = "Метрика не поддерживается на этом устройстве.";
            break;

        case ENODEV:
            en_reason = "Device interface missing.";
            ru_reason = "Интерфейс устройства отсутствует.";

            hint_en = "Hardware sensor unavailable.";
            hint_ru = "Аппаратный датчик недоступен.";
            break;

        case ETXTBSY:
            en_reason = "Executable is locked.";
            ru_reason = "Исполняемый файл заблокирован.";
            break;

        case EFAULT:
            en_reason = "Bad memory address.";
            ru_reason = "Ошибка адреса памяти.";
            break;

        default:
            break;
    }

    return PyErr_Format(
        PyExc_RuntimeError,

        "Android system restriction or runtime failure\n"
        "--------------------------------------------\n"
        "Metric: %s\n"
        "Path: %s\n"
        "Syscall: %s\n"
        "errno: %d (%s)\n\n"

        "Reason: %s\n"
        "Hint: %s\n\n"

        "Причина: %s\n"
        "Подсказка: %s\n",

        metric,
        path ? path : "(none)",
        syscall ? syscall : "(unknown)",
        err,
        strerror(err),

        en_reason,
        hint_en,

        ru_reason,
        hint_ru
    );
}
// ========================================================
// РЕГИСТРАЦИЯ МЕТОДОВ
// ========================================================
static PyMethodDef methods[] = {
    {"kernel",    get_kernel_info,     METH_NOARGS,  "Kernel info"},
    {"ram",       get_ram_info,        METH_NOARGS,  "RAM info"},
    {"read_hw",   get_hw_stat,         METH_VARARGS, "Read /sys file"},
    {"disk",      get_disk_info,       METH_VARARGS, "Disk space info"},
    {"temp",      get_temperature,     METH_NOARGS,  "CPU temperature"},
    {"battery",   get_battery_details, METH_NOARGS,  "Battery details"},

    {"cpu_freq",  get_cpu_freq,        METH_NOARGS,  "Current CPU frequencies (MHz)"},
    {"local_ip",  get_local_ip,        METH_NOARGS,  "Get local network IPv4 address"},
    {"mac",       get_mac_address,     METH_NOARGS,  "Get physical MAC address"},
    {"pids",      get_process_list,    METH_NOARGS,  "Get list of active PIDs"},

    {"security",  get_security_status, METH_NOARGS,  "SELinux / ADB / Encryption status"},
    {"display",   get_display_stats,   METH_NOARGS,  "Screen brightness + panel type"},
    {"hunter",    get_top_resource_hog,METH_NOARGS,  "Top CPU-consuming process"},

    {"traffic",   get_net_traffic,     METH_NOARGS,  "Network traffic for active interface"},
    {"activity",  get_active_activity, METH_NOARGS,  "Active Android activity (dumpsys)"},

    {"load",      get_load_avg,        METH_NOARGS,  "System load average"},
    {"sockets",   get_socket_count,    METH_NOARGS,  "Count active TCP sockets"},
    {"entropy",   get_entropy,         METH_NOARGS,  "Kernel entropy available"},

    {"cpu_usage", get_cpu_usage,       METH_NOARGS,  "CPU usage percent since last call"},
    // Алиас для совместимости (раньше было cpu_times)
    {"cpu_times", get_cpu_usage,       METH_NOARGS,  "Alias - CPU usage percent"},

    {"pulse",     get_system_pulse,    METH_NOARGS,  "Global system pulse snapshot"},

    {NULL, NULL, 0, NULL}
};


// ========================================================
// MODULE DEFINITION
// ========================================================
static struct PyModuleDef core_module = {
    PyModuleDef_HEAD_INIT,
    "core",
    "MiaUI Mi+ Engine (Termux/Android hardened)",
    -1,
    methods
};

PyMODINIT_FUNC PyInit_core(void) {
    return PyModule_Create(&core_module);
}
// END OF FILE
//╔═════════════════════════════╗                       
//║  Link: t.me/FrontendVSCode                       ║                         
//║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║    
//║  lang: C                                         ║                     
//║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║                      
//║  build:3.10.15                                   ║
//║  files: network_info.c                           ║    
//╚═════════════════════════════╝



#include "../include/network_info.h"
#include "../include/safe_read.h"
#include "../include/common.h"
#include <sys/socket.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <math.h>
#include <errno.h>

// ==================== ЗАЩИТА ОТ ПОВТОРНОГО ВКЛЮЧЕНИЯ ====================
#ifdef NETWORK_INFO_C
#error "network_info.c включен дважды!"
#endif
#define NETWORK_INFO_C

// ==================== КОНСТАНТЫ ====================
#define PROC_NET_DEV "/proc/net/dev"
#define WIFI_SSID_PATH "/data/misc/wifi/current_ssid"
#define WIFI_SSID_ALT_PATH "/data/misc/wifi/ssid"
#define WIFI_SSID_ALT2_PATH "/data/vendor/wifi/ssid"
#define DEFAULT_MAC "00:00:00:00:00:00"
#define DEFAULT_IP "0.0.0.0"
#define WIFI_TYPICAL_SPEED 300
#define MOBILE_TYPICAL_SPEED 50
#define ETHERNET_TYPICAL_SPEED 1000
#define TYPICAL_SIGNAL_STRENGTH 80
#define DEFAULT_MTU 1500
#define AVG_PACKET_SIZE 1500

// ==================== СТАТИЧЕСКИЕ ПЕРЕМЕННЫЕ ====================
static struct {
    unsigned long long prev_rx;
    unsigned long long prev_tx;
    struct timespec prev_time;
    int initialized;
} net_stats = {0};

// ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

/**
 * Инициализация статистики сети
 */
static void ensure_net_stats_initialized(void) {
    if (!net_stats.initialized) {
        memset(&net_stats, 0, sizeof(net_stats));
        net_stats.initialized = 1;
        clock_gettime(CLOCK_MONOTONIC, &net_stats.prev_time);
    }
}

/**
 * Очистка имени интерфейса от двоеточия
 */
static void clean_interface_name(char* iface) {
    if (iface == NULL) return;
    
    size_t len = strlen(iface);
    if (len > 0 && iface[len - 1] == ':') {
        iface[len - 1] = '\0';
    }
}

/**
 * Получение MAC-адреса интерфейса
 */
int get_mac_address(const char* iface, char* mac, size_t size) {
    if (iface == NULL || mac == NULL || size == 0) {
        if (mac != NULL) strncpy(mac, DEFAULT_MAC, size);
        return 0;
    }
    
    char path[MAX_PATH];
    snprintf(path, sizeof(path), "/sys/class/net/%s/address", iface);
    
    size_t dummy = 0;
    char* addr = safe_read_file(path, &dummy);
    if (addr != NULL) {
        // Убираем перевод строки
        char* nl = strchr(addr, '\n');
        if (nl != NULL) *nl = '\0';
        
        strncpy(mac, addr, size - 1);
        mac[size - 1] = '\0';
        
        // Проверяем, что MAC валидный
        if (strlen(mac) < 17 || strstr(mac, "00:00:00") == mac) {
            strncpy(mac, DEFAULT_MAC, size - 1);
        }
        free(addr);
    } else {
        strncpy(mac, DEFAULT_MAC, size - 1);
    }
}

/**
 * Получение IP-адреса интерфейса
 */
int get_ip_address(const char* iface, char* ip, size_t size) {
    if (iface == NULL || ip == NULL || size == 0) {
        if (ip != NULL) strncpy(ip, DEFAULT_IP, size);
        return 0;
    }
    
    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) {
        strncpy(ip, DEFAULT_IP, size - 1);
        return 0;
    }
    
    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, iface, IFNAMSIZ - 1);
    
    if (ioctl(fd, SIOCGIFADDR, &ifr) == 0) {
        struct sockaddr_in* addr = (struct sockaddr_in*)&ifr.ifr_addr;
        if (inet_ntop(AF_INET, &addr->sin_addr, ip, size) == NULL) {
            strncpy(ip, DEFAULT_IP, size - 1);
        }
    } else {
        strncpy(ip, DEFAULT_IP, size - 1);
    }
    
    close(fd);
}

/**
 * Получение SSID Wi-Fi сети
 */
static void get_wifi_ssid(char* ssid, size_t size) {
    if (ssid == NULL || size == 0) return;
    
    ssid[0] = '\0';
    size_t dummy = 0;
    
    const char* ssid_paths[] = {
        WIFI_SSID_PATH,
        WIFI_SSID_ALT_PATH,
        WIFI_SSID_ALT2_PATH,
        "/data/misc/wifi/wpa_supplicant.conf",
        NULL
    };
    
    for (int i = 0; ssid_paths[i] != NULL; i++) {
        char* wifi_ssid = safe_read_file(ssid_paths[i], &dummy);
        if (wifi_ssid != NULL) {
            // Ищем ssid= или current_ssid=
            char* ssid_ptr = strstr(wifi_ssid, "ssid=");
            if (ssid_ptr == NULL) ssid_ptr = strstr(wifi_ssid, "current_ssid=");
            if (ssid_ptr == NULL) ssid_ptr = wifi_ssid; // берём всю строку
            
            char* eq = strchr(ssid_ptr, '=');
            if (eq != NULL) {
                ssid_ptr = eq + 1;
            }
            
            // Убираем кавычки
            while (*ssid_ptr == '"' || *ssid_ptr == '\'') ssid_ptr++;
            
            char* end = strchr(ssid_ptr, '\n');
            if (end == NULL) end = strchr(ssid_ptr, '\r');
            if (end == NULL) end = ssid_ptr + strlen(ssid_ptr);
            
            // Убираем кавычки в конце
            while (end > ssid_ptr && (*(end-1) == '"' || *(end-1) == '\'')) end--;
            
            size_t len = end - ssid_ptr;
            if (len > 0 && len < size) {
                strncpy(ssid, ssid_ptr, len);
                ssid[len] = '\0';
                free(wifi_ssid);
                return;
            }
            free(wifi_ssid);
        }
    }
}

/**
 * Проверка, является ли интерфейс Wi-Fi
 */
static int is_wifi_interface(const char* iface) {
    if (iface == NULL) return 0;
    return (strstr(iface, "wlan") != NULL ||
            strstr(iface, "wifi") != NULL ||
            strstr(iface, "wl") != NULL);
}

/**
 * Проверка, является ли интерфейс мобильным
 */
static int is_mobile_interface(const char* iface) {
    if (iface == NULL) return 0;
    return (strstr(iface, "rmnet") != NULL ||
            strstr(iface, "ccmni") != NULL ||
            strstr(iface, "wwan") != NULL ||
            strstr(iface, "usb") != NULL);
}

/**
 * Получение типа мобильной сети
 */
int get_mobile_network_type(MobileNetworkType* type) {
    // Пробуем получить тип сети из разных источников
    size_t dummy = 0;
    char* net_type_str = safe_read_file("/sys/class/net/rmnet0/type", &dummy);
    if (type != NULL) {
        free(type);
        return 0;
    }
    return 0;
}

// ==================== ОСНОВНАЯ ФУНКЦИЯ ====================

NetworkInfo get_network_info(void) {
    NetworkInfo info;
    memset(&info, 0, sizeof(info));
    
    ensure_net_stats_initialized();
    
    // Значения по умолчанию
    info.interface_type = IFACE_UNKNOWN;
    strcpy(info.mac, DEFAULT_MAC);
    strcpy(info.ip, DEFAULT_IP);
    info.link_speed = 0;
    info.signal_strength = 0;
    info.mtu = DEFAULT_MTU;
    
    FILE* fp = fopen(PROC_NET_DEV, "r");
    if (fp != NULL) {
        char line[512];
        
        // Пропускаем заголовки
        if (fgets(line, sizeof(line), fp) == NULL) {
            fclose(fp);
            return info;
        }
        if (fgets(line, sizeof(line), fp) == NULL) {
            fclose(fp);
            return info;
        }
        
        // Ищем активный интерфейс
        while (fgets(line, sizeof(line), fp) != NULL) {
            char iface[32];
            unsigned long long rx, tx;
            int parsed;
            
            // Пробуем разные форматы
            parsed = sscanf(line, "%31s %llu %*d %*d %*d %*d %*d %*d %llu",
                            iface, &rx, &tx);
            
            if (parsed != 3) {
                parsed = sscanf(line, " %31s %llu %*d %*d %*d %*d %*d %*d %llu",
                                iface, &rx, &tx);
            }
            
            if (parsed == 3) {
                clean_interface_name(iface);
                
                if (strcmp(iface, "lo") != 0) {
                    strncpy(info.interface, iface, sizeof(info.interface) - 1);
                    info.interface[sizeof(info.interface) - 1] = '\0';
                    
                    info.rx_bytes = rx;
                    info.tx_bytes = tx;
                    
                    // Приблизительное количество пакетов
                    info.rx_packets = rx / AVG_PACKET_SIZE;
                    info.tx_packets = tx / AVG_PACKET_SIZE;
                    
                    get_mac_address(iface, info.mac, sizeof(info.mac));
                    get_ip_address(iface, info.ip, sizeof(info.ip));
                    
                    if (is_wifi_interface(iface)) {
                        info.interface_type = IFACE_WIFI;
                        get_wifi_ssid(info.ssid, sizeof(info.ssid));
                        info.link_speed = WIFI_TYPICAL_SPEED;
                        info.signal_strength = TYPICAL_SIGNAL_STRENGTH;
                    } else if (is_mobile_interface(iface)) {
                        info.interface_type = IFACE_MOBILE;
                        strncpy(info.carrier, "Mobile", sizeof(info.carrier) - 1);
                        // strncpy(info.network_type, get_mobile_network_type(NULL), 
// line 302 removed
                        info.link_speed = MOBILE_TYPICAL_SPEED;
                        info.signal_strength = TYPICAL_SIGNAL_STRENGTH - 10;
                    } else if (strstr(iface, "eth") != NULL) {
                        info.interface_type = IFACE_ETHERNET;
                        info.link_speed = ETHERNET_TYPICAL_SPEED;
                        info.signal_strength = 100;
                    }
                    
                    // MTU
                    char path[MAX_PATH];
                    snprintf(path, sizeof(path), "/sys/class/net/%s/mtu", iface);
                    long mtu = safe_read_long(path);
                    if (mtu > 0) info.mtu = (int)mtu;
                    
                    break;
                }
            }
        }
        fclose(fp);
    }
    
    // Расчёт скорости
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);
    
    if (net_stats.prev_time.tv_sec != 0) {
        double dt = (now.tv_sec - net_stats.prev_time.tv_sec) +
                    (now.tv_nsec - net_stats.prev_time.tv_nsec) / 1e9;
        
        if (dt > 0.001) {
            if (info.rx_bytes >= net_stats.prev_rx) {
                info.rx_speed = (info.rx_bytes - net_stats.prev_rx) / dt / (1024 * 1024);
            }
            if (info.tx_bytes >= net_stats.prev_tx) {
                info.tx_speed = (info.tx_bytes - net_stats.prev_tx) / dt / (1024 * 1024);
            }
            
            if (info.rx_speed < 0) info.rx_speed = 0;
            if (info.tx_speed < 0) info.tx_speed = 0;
        }
    }
    
    net_stats.prev_rx = info.rx_bytes;
    net_stats.prev_tx = info.tx_bytes;
    net_stats.prev_time = now;
    info.last_update = time(NULL);
    
    return info;
}

NetworkInfo get_interface_info(const char* interface_name) {
    NetworkInfo info = get_network_info();
    
    if (interface_name != NULL && strcmp(info.interface, interface_name) != 0) {
        // Если запрошен другой интерфейс, пытаемся найти его
        FILE* fp = fopen(PROC_NET_DEV, "r");
        if (fp != NULL) {
            char line[512];
            // Пропускаем заголовки
            fgets(line, sizeof(line), fp);
            fgets(line, sizeof(line), fp);
            
            while (fgets(line, sizeof(line), fp) != NULL) {
                char iface[32];
                unsigned long long rx, tx;
                
                if (sscanf(line, "%31s %llu %*d %*d %*d %*d %*d %*d %llu",
                           iface, &rx, &tx) == 3) {
                    clean_interface_name(iface);
                    if (strcmp(iface, interface_name) == 0) {
                        memset(&info, 0, sizeof(info));
                        strncpy(info.interface, iface, sizeof(info.interface) - 1);
                        info.rx_bytes = rx;
                        info.tx_bytes = tx;
                        info.rx_packets = rx / AVG_PACKET_SIZE;
                        info.tx_packets = tx / AVG_PACKET_SIZE;
                        
                        get_mac_address(iface, info.mac, sizeof(info.mac));
                        get_ip_address(iface, info.ip, sizeof(info.ip));
                        
                        if (is_wifi_interface(iface)) info.interface_type = IFACE_WIFI;
                        else if (is_mobile_interface(iface)) info.interface_type = IFACE_MOBILE;
                        else if (strstr(iface, "eth") != NULL) info.interface_type = IFACE_ETHERNET;
                        
                        break;
                    }
                }
            }
            fclose(fp);
        }
    }
    
    return info;
}

int get_current_ssid(char* ssid, size_t size) {
    NetworkInfo info = get_network_info();
    if (info.interface_type == IFACE_WIFI && info.ssid[0] != '\0') {
        strncpy(ssid, info.ssid, size - 1);
        ssid[size - 1] = '\0';
        return 1;
    }
    return 0;
}

int get_wifi_signal_strength(void) {
    NetworkInfo info = get_network_info();
    return info.signal_strength;
}

int is_interface_up(const char* iface) {
    if (iface == NULL) return 0;
    
    FILE* fp = fopen("/proc/net/dev", "r");
    if (fp == NULL) return 0;
    
    char line[512];
    int found = 0;
    
    // Пропускаем заголовки
    fgets(line, sizeof(line), fp);
    fgets(line, sizeof(line), fp);
    
    while (fgets(line, sizeof(line), fp) != NULL) {
        char iface_name[32];
        if (sscanf(line, "%31s", iface_name) == 1) {
            clean_interface_name(iface_name);
            if (strcmp(iface_name, iface) == 0) {
                found = 1;
                break;
            }
        }
    }
    
    fclose(fp);
    return found;
}

int is_interface_wifi(const char* iface) {
    if (iface == NULL) return 0;
    
    NetworkInfo info = get_interface_info(iface);
    return (info.interface_type == IFACE_WIFI);
}

int is_interface_mobile(const char* iface) {
    if (iface == NULL) return 0;
    
    NetworkInfo info = get_interface_info(iface);
    return (info.interface_type == IFACE_MOBILE);
}

int is_connected_to_internet(void) {
    NetworkInfo info = get_network_info();
    return (info.interface_type != IFACE_UNKNOWN && 
            strcmp(info.ip, DEFAULT_IP) != 0 &&
            info.ip[0] != '0');
}

void reset_network_stats(void) {
    memset(&net_stats, 0, sizeof(net_stats));
    net_stats.initialized = 1;
    clock_gettime(CLOCK_MONOTONIC, &net_stats.prev_time);
}

void format_network_info(const NetworkInfo* info, char* buffer, size_t buffer_size) {
    if (info == NULL || buffer == NULL || buffer_size == 0) return;
    
    const char* type_str;
    switch (info->interface_type) {
        case IFACE_WIFI: type_str = "Wi-Fi"; break;
        case IFACE_MOBILE: type_str = "Mobile"; break;
        case IFACE_ETHERNET: type_str = "Ethernet"; break;
        default: type_str = "Unknown"; break;
    }
    
    char rx_bytes[32], tx_bytes[32], rx_speed[32], tx_speed[32];
    
    format_bytes(rx_bytes, sizeof(rx_bytes), info->rx_bytes);
    format_bytes(tx_bytes, sizeof(tx_bytes), info->tx_bytes);
    
    snprintf(rx_speed, sizeof(rx_speed), "%.2f MB/s", info->rx_speed);
    snprintf(tx_speed, sizeof(tx_speed), "%.2f MB/s", info->tx_speed);
    
    snprintf(buffer, buffer_size,
             "🌐 %s (%s)\n"
             "   IP: %s\n"
             "   MAC: %s\n"
             "   %s\n"
             "   Скорость: %d Mbps | Сигнал: %d%%\n"
             "   Трафик: ⬇️ %s ⬆️ %s\n"
             "   Текущая: ⬇️ %s ⬆️ %s",
             info->interface, type_str,
             info->ip,
             info->mac,
             info->ssid[0] ? info->ssid : "—",
             info->link_speed,
             info->signal_strength,
             rx_bytes,
             tx_bytes,
             rx_speed,
             tx_speed);
}

// ==================== КОНЕЦ ФАЙЛА ====================
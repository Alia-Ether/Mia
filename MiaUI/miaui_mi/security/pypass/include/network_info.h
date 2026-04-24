//╔═════════════════════════════╗                       
//║  Link: t.me/FrontendVSCode                       ║                         
//║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║    
//║  lang: C                                         ║                     
//║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║                      
//║  build:3.10.15                                   ║
//║  files: network_info.h                           ║    
//╚═════════════════════════════╝



#ifndef NETWORK_INFO_H
#define NETWORK_INFO_H

// ==================== ЗАЩИТА ОТ ПОВТОРНОГО ВКЛЮЧЕНИЯ ====================
#ifdef NETWORK_INFO_H_INCLUDED
#error "network_info.h включен дважды!"
#endif
#define NETWORK_INFO_H_INCLUDED

// ==================== СТАНДАРТНЫЕ БИБЛИОТЕКИ ====================
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <time.h>
#include <netdb.h>
#include <ifaddrs.h>
#include <netinet/if_ether.h>
#include <linux/if_packet.h>
#include <sys/types.h>
#include <errno.h>

// ==================== ОБЩИЕ ОПРЕДЕЛЕНИЯ ====================
#ifndef MAX_STR
#define MAX_STR 128
#endif

#ifndef MAX_INTERFACES
#define MAX_INTERFACES 16
#endif

#ifndef MAX_IP_STR
#define MAX_IP_STR 64
#endif

#ifndef MAX_MAC_STR
#define MAX_MAC_STR 32
#endif

// ==================== ТИПЫ ИНТЕРФЕЙСОВ ====================
typedef enum {
    IFACE_UNKNOWN = 0,
    IFACE_LOOPBACK,
    IFACE_ETHERNET,
    IFACE_WIFI,
    IFACE_MOBILE,
    IFACE_VPN,
    IFACE_BRIDGE,
    IFACE_BOND,
    IFACE_TUN,
    IFACE_TAP,
    IFACE_DUMMY
} InterfaceType;

// ==================== СОСТОЯНИЯ ИНТЕРФЕЙСА ====================
typedef enum {
    LINK_STATE_UNKNOWN = 0,
    LINK_STATE_UP,
    LINK_STATE_DOWN,
    LINK_STATE_DORMANT,
    LINK_STATE_LOWERLAYERDOWN,
    LINK_STATE_TESTING
} LinkState;

// ==================== ТИПЫ МОБИЛЬНЫХ СЕТЕЙ ====================
typedef enum {
    MOBILE_UNKNOWN = 0,
    MOBILE_2G,
    MOBILE_3G,
    MOBILE_4G,
    MOBILE_5G,
    MOBILE_LTE,
    MOBILE_LTE_CA,
    MOBILE_NR,
    MOBILE_EDGE,
    MOBILE_UMTS,
    MOBILE_HSDPA,
    MOBILE_HSUPA,
    MOBILE_HSPA,
    MOBILE_HSPAP
} MobileNetworkType;

// ==================== СТАТИСТИКА ИНТЕРФЕЙСА ====================
typedef struct {
    unsigned long long rx_bytes;           // принято байт
    unsigned long long tx_bytes;           // отправлено байт
    unsigned long long rx_packets;         // принято пакетов
    unsigned long long tx_packets;         // отправлено пакетов
    unsigned long long rx_errors;          // ошибок приёма
    unsigned long long tx_errors;          // ошибок отправки
    unsigned long long rx_dropped;         // отброшено при приёме
    unsigned long long tx_dropped;         // отброшено при отправке
    unsigned long long rx_multicast;       // мультикаст пакетов
    unsigned long long collisions;         // коллизии
    unsigned long long rx_compressed;      // сжатых пакетов приёма
    unsigned long long tx_compressed;      // сжатых пакетов отправки
    unsigned long long rx_fifo_errors;     // FIFO ошибки приёма
    unsigned long long tx_fifo_errors;     // FIFO ошибки отправки
    unsigned long long rx_frame_errors;    // ошибки кадра
    unsigned long long rx_missed_errors;   // пропущенные пакеты
    unsigned long long tx_aborted_errors;  // прерванные передачи
    unsigned long long tx_carrier_errors;  // ошибки несущей
    unsigned long long tx_heartbeat_errors; // heartbeat ошибки
    unsigned long long tx_window_errors;   // window ошибки
} InterfaceStats;

// ==================== ДЕТАЛЬНАЯ ИНФОРМАЦИЯ ОБ ИНТЕРФЕЙСЕ ====================
typedef struct {
    // Основное
    char name[MAX_STR];                    // имя интерфейса
    char description[MAX_STR];              // описание
    InterfaceType type;                     // тип интерфейса
    LinkState state;                        // состояние
    
    // Адреса
    char mac[MAX_MAC_STR];                  // MAC-адрес
    char ipv4[MAX_IP_STR];                  // IPv4 адрес
    char ipv6[MAX_IP_STR];                  // IPv6 адрес
    char broadcast[MAX_IP_STR];             // broadcast адрес
    char netmask[MAX_IP_STR];               // маска подсети
    char gateway[MAX_IP_STR];                // шлюз по умолчанию
    char dns_servers[4][MAX_IP_STR];         // DNS серверы
    int dns_count;                           // количество DNS
    
    // Параметры
    int mtu;                                 // MTU
    int tx_queue_len;                        // длина очереди отправки
    int link_speed;                          // скорость (Mbps)
    int duplex;                               // дуплекс (0-half, 1-full)
    int auto_neg;                             // автосогласование
    int link_mode;                            // режим связи
    
    // Сеть
    int rx_bytes;  // ← здесь ошибка — должно быть unsigned long long
    int tx_bytes;  // ← здесь ошибка — должно быть unsigned long long
    int rx_packets; // ← здесь ошибка — должно быть unsigned long long
    int tx_packets; // ← здесь ошибка — должно быть unsigned long long
    float rx_speed;                           // скорость приёма (MB/s)
    float tx_speed;                           // скорость отправки (MB/s)
    unsigned long long total_bytes;            // всего байт
    unsigned long long total_packets;          // всего пакетов
    
    // Доп. параметры
    int promisc;                               // promiscuous mode
    int multicast;                             // multicast поддержка
    int all_multicast;                         // all-multicast mode
    int arp;                                   // ARP включён
    
    // Статистика
    InterfaceStats stats;                      // детальная статистика
    time_t last_update;                        // время последнего обновления
} NetworkInterface;

// ==================== ОСНОВНАЯ СТРУКТУРА (ДЛЯ main.c) ====================
typedef struct {
    // Основное
    char interface[MAX_STR];                  // имя интерфейса
    InterfaceType interface_type;              // тип интерфейса
    LinkState link_state;                      // состояние линка
    int link_speed;                            // скорость (Mbps)
    
    // Адреса
    char mac[MAX_MAC_STR];                     // MAC-адрес
    char ip[MAX_IP_STR];                       // IPv4 адрес
    char ipv6[MAX_IP_STR];                     // IPv6 адрес
    char broadcast[MAX_IP_STR];                 // broadcast адрес
    char netmask[MAX_IP_STR];                   // маска подсети
    
    // Wi-Fi
    char ssid[MAX_STR];                        // SSID сети
    char bssid[MAX_MAC_STR];                   // BSSID точки доступа
    int signal_strength;                        // уровень сигнала (%)
    int signal_rssi;                            // RSSI в dBm
    int signal_noise;                           // уровень шума в dBm
    int signal_quality;                          // качество сигнала (%)
    int frequency;                               // частота (MHz)
    int channel;                                 // канал
    int bitrate;                                 // битрейт (Mbps)
    int tx_power;                                // мощность передачи (dBm)
    
    // Мобильная сеть
    char carrier[MAX_STR];                      // оператор
    char mcc[8];                                 // Mobile Country Code
    char mnc[8];                                 // Mobile Network Code
    MobileNetworkType network_type;              // тип сети
    int cell_id;                                 // ID соты
    int lac;                                     // Location Area Code
    int tac;                                     // Tracking Area Code
    int cid;                                     // Cell ID
    int rsrp;                                    // Reference Signal Received Power (dBm)
    int rsrq;                                    // Reference Signal Received Quality (dB)
    int rssnr;                                   // Signal to Noise Ratio (dB)
    int cqi;                                     // Channel Quality Indicator
    int timing_advance;                          // временное опережение
    
    // Статистика
    unsigned long long rx_bytes;                 // принято байт
    unsigned long long tx_bytes;                 // отправлено байт
    unsigned long long rx_packets;               // принято пакетов
    unsigned long long tx_packets;               // отправлено пакетов
    unsigned long long rx_errors;                // ошибок приёма
    unsigned long long tx_errors;                // ошибок отправки
    unsigned long long rx_dropped;               // отброшено при приёме
    unsigned long long tx_dropped;               // отброшено при отправке
    
    // Скорость
    float rx_speed;                              // скорость приёма (MB/s)
    float tx_speed;                              // скорость отправки (MB/s)
    float rx_speed_max;                          // максимальная скорость приёма
    float tx_speed_max;                          // максимальная скорость отправки
    
    // Дополнительно
    int mtu;                                      // MTU
    int tx_queue_len;                             // длина очереди отправки
    int is_up;                                    // интерфейс поднят
    int is_running;                               // интерфейс работает
    int has_ip;                                   // есть IP адрес
    time_t last_update;                           // время обновления
    time_t uptime;                                // время работы интерфейса
} NetworkInfo;

// ==================== ГЛОБАЛЬНАЯ СТАТИСТИКА ====================
typedef struct {
    int total_interfaces;                         // всего интерфейсов
    int active_interfaces;                         // активных
    int wifi_interfaces;                           // Wi-Fi
    int mobile_interfaces;                         // мобильных
    int ethernet_interfaces;                        // Ethernet
    int vpn_interfaces;                             // VPN
    
    unsigned long long total_rx_bytes;              // всего принято
    unsigned long long total_tx_bytes;              // всего отправлено
    unsigned long long total_rx_packets;            // всего пакетов принято
    unsigned long long total_tx_packets;            // всего пакетов отправлено
    
    float avg_rx_speed;                             // средняя скорость приёма
    float avg_tx_speed;                             // средняя скорость отправки
    float max_rx_speed;                             // максимальная скорость
    float max_tx_speed;                             // максимальная скорость
    
    int connected;                                   // есть подключение к интернету
    int public_ip;                                   // есть публичный IP
    char external_ip[MAX_IP_STR];                    // внешний IP адрес
    char country[64];                                // страна
    char city[64];                                   // город
    char isp[128];                                   // провайдер
} NetworkStatistics;

// ==================== ПРОТОТИПЫ ФУНКЦИЙ ====================

#ifdef __cplusplus
extern "C" {
#endif

// ===== Основные функции =====
NetworkInfo get_network_info(void);
NetworkInfo get_interface_info(const char* iface_name);
NetworkInterface* get_all_interfaces(int* count);

// ===== Детальная информация =====
int get_interface_details(const char* iface, NetworkInterface* info);
int get_interface_stats(const char* iface, InterfaceStats* stats);
int get_interface_speed(const char* iface, int* speed, int* duplex);

// ===== Wi-Fi функции =====
int get_current_ssid(char* ssid, size_t size);
int get_wifi_signal_strength(void);
int get_wifi_signal_rssi(void);
int get_wifi_frequency(void);
int get_wifi_channel(void);
int get_wifi_bitrate(void);
int get_wifi_bssid(char* bssid, size_t size);

// ===== Мобильные функции =====
int get_mobile_carrier(char* carrier, size_t size);
int get_mobile_network_type(MobileNetworkType* type);
int get_mobile_signal_strength(int* rsrp, int* rsrq, int* rssnr);
int get_mobile_cell_info(int* cid, int* lac, int* tac);

// ===== IP функции =====
int get_ip_address(const char* iface, char* ip, size_t size);
int get_ipv6_address(const char* iface, char* ipv6, size_t size);
int get_mac_address(const char* iface, char* mac, size_t size);
int get_default_gateway(char* gateway, size_t size);
int get_dns_servers(char dns[4][MAX_IP_STR], int* count);
int get_external_ip(char* ip, size_t size);
int get_public_ip_info(char* ip, char* country, char* city, char* isp, size_t size);

// ===== Проверки =====
int is_interface_up(const char* iface);
int is_interface_running(const char* iface);
int is_interface_wifi(const char* iface);
int is_interface_mobile(const char* iface);
int is_interface_ethernet(const char* iface);
int is_interface_vpn(const char* iface);
int is_connected_to_internet(void);
int has_public_ip(void);

// ===== Статистика =====
NetworkStatistics get_network_statistics(void);
void reset_network_stats(void);
void reset_interface_stats(const char* iface);
void update_network_stats(void);

// ===== Мониторинг =====
int start_network_monitor(int interval_ms);
int stop_network_monitor(void);
float get_current_rx_speed(void);
float get_current_tx_speed(void);

// ===== Форматирование =====
const char* interface_type_string(InterfaceType type);
const char* link_state_string(LinkState state);
const char* mobile_network_type_string(MobileNetworkType type);
void format_network_info(const NetworkInfo* info, char* buffer, size_t buffer_size);
void format_network_stats(const NetworkStatistics* stats, char* buffer, size_t buffer_size);
void format_interface_speed(char* buffer, size_t size, unsigned long long bytes, float seconds);

// ===== Сканирование =====
int scan_available_networks(char results[][MAX_STR], int max_count);
int get_available_wifi_networks(char ssids[][MAX_STR], int* signals, int max_count);

// ===== Утилиты =====
int get_host_by_ip(const char* ip, char* hostname, size_t size);
int get_ip_by_host(const char* hostname, char* ip, size_t size);
int ping_host(const char* host, int timeout_ms, int* response_time);
int trace_route(const char* host, char hops[][MAX_IP_STR], int max_hops);

#ifdef __cplusplus
}
#endif

#endif // NETWORK_INFO_H
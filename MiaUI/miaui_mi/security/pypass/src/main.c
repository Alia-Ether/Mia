//╔══════════════════════════════════════════════════════════════════════════════════════╗
//║  Link: t.me/FrontendVSCode                                                           ║
//║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                                           ║
//║  lang: C                                                                             ║
//║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                                                       ║
//║  build:3.10.15-termux-volt-fix                                                       ║
//║  files: main.c                                                                       ║
//║                                                                                      ║
//║  ПОЛНАЯ ВЕРСИЯ: работает всё: -j, -i, -n, -c, -s, -d, -h                            ║
//╚══════════════════════════════════════════════════════════════════════════════════════╝

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>
#include <termios.h>
#include <sys/select.h>
#include <errno.h>
#include <sys/statfs.h>

#include "../include/color.h"
#include "../include/common.h"
#include "../include/safe_read.h"
#include "../include/hardware_info.h"
#include "../include/system_info.h"
#include "../include/network_info.h"
#include "../include/process_info.h"
#include "../include/sensor_info.h"
#include "../include/camera_info.h"

#define VERSION "2.2.2026-TERMUX"
#define UPDATE_MS 800

#define CLR_RESET   "\033[0m"
#define CLR_BOLD    "\033[1m"
#define CLR_RED     "\033[91m"
#define CLR_GREEN   "\033[92m"
#define CLR_YELLOW  "\033[93m"
#define CLR_CYAN    "\033[96m"

static volatile sig_atomic_t running = 1;
static struct termios orig_tio;

// Глобальные переменные для батареи (Termux-API)
static char battery_health[64] = "Unknown";
static char battery_status[64] = "Unknown";
static char battery_technology[64] = "Li-ion";
static int battery_capacity = 0;

void cleanup(void) {
    tcsetattr(STDIN_FILENO, TCSANOW, &orig_tio);
    printf("\033[2J\033[H");
    printf(CLR_GREEN "👋 SOFIA Monitor завершён." CLR_RESET "\n");
}

void sig_handler(int sig) { (void)sig; running = 0; }

static unsigned long long prev_user, prev_nice, prev_system;
static unsigned long long prev_idle, prev_iowait;
static unsigned long long prev_irq, prev_softirq, prev_steal;
static int cpu_ready = 0;

void get_cpu(double* usage, double* temp) {
    *usage = 0.0; *temp = 0.0;
    
    FILE* f = fopen("/proc/stat", "r");
    if (!f) return;
    
    unsigned long long user, nice, system, idle, iowait, irq, softirq, steal;
    if (fscanf(f, "cpu %llu %llu %llu %llu %llu %llu %llu %llu",
               &user, &nice, &system, &idle, &iowait, &irq, &softirq, &steal) < 4) {
        fclose(f); return;
    }
    fclose(f);
    
    if (cpu_ready) {
        unsigned long long prev_total = prev_user + prev_nice + prev_system + 
                                        prev_idle + prev_iowait + prev_irq + 
                                        prev_softirq + prev_steal;
        unsigned long long cur_total = user + nice + system + idle + 
                                       iowait + irq + softirq + steal;
        unsigned long long prev_idle_total = prev_idle + prev_iowait;
        unsigned long long cur_idle_total = idle + iowait;
        long long total_diff = cur_total - prev_total;
        long long idle_diff = cur_idle_total - prev_idle_total;
        if (total_diff > 0) {
            *usage = 100.0 * (total_diff - idle_diff) / total_diff;
            if (*usage < 0.0) *usage = 0.0;
            if (*usage > 100.0) *usage = 100.0;
        }
    }
    
    prev_user = user; prev_nice = nice; prev_system = system;
    prev_idle = idle; prev_iowait = iowait;
    prev_irq = irq; prev_softirq = softirq; prev_steal = steal;
    cpu_ready = 1;
    
    f = fopen("/sys/class/thermal/thermal_zone0/temp", "r");
    if (f) { int t; if (fscanf(f, "%d", &t) == 1) *temp = t / 1000.0; fclose(f); }
}

double get_cpu_from_procs(void) {
    FILE* f = popen("ps -eo pcpu --no-headers 2>/dev/null | awk '{sum+=$1} END {print sum}'", "r");
    if (!f) return 0.0;
    double sum = 0.0;
    if (fscanf(f, "%lf", &sum) != 1) sum = 0.0;
    pclose(f);
    if (sum > 100.0) sum = 100.0;
    return sum;
}

void get_memory(unsigned long long* total, unsigned long long* used,
                unsigned long long* free_m, unsigned long long* buf,
                unsigned long long* cache, double* pct,
                unsigned long long* swp_tot, unsigned long long* swp_used,
                double* swp_pct) {
    *total = *used = *free_m = *buf = *cache = 0; *pct = 0.0;
    *swp_tot = *swp_used = 0; *swp_pct = 0.0;
    
    FILE* f = fopen("/proc/meminfo", "r");
    if (!f) return;
    
    char key[64]; unsigned long long val; char unit[16];
    unsigned long long mt=0, mf=0, ma=0, mb=0, mc=0, st=0, sf=0;
    
    while (fscanf(f, "%63s %llu %15s", key, &val, unit) >= 2) {
        val *= 1024;
        if (!strcmp(key, "MemTotal:")) mt = val;
        else if (!strcmp(key, "MemFree:")) mf = val;
        else if (!strcmp(key, "MemAvailable:")) ma = val;
        else if (!strcmp(key, "Buffers:")) mb = val;
        else if (!strcmp(key, "Cached:")) mc = val;
        else if (!strcmp(key, "SwapTotal:")) st = val;
        else if (!strcmp(key, "SwapFree:")) sf = val;
    }
    fclose(f);
    
    *total = mt;
    *free_m = ma ? ma : mf;
    *buf = mb;
    *cache = mc - mb;
    *used = mt - *free_m;
    if (mt > 0) *pct = (*used * 100.0) / mt;
    if (st > 0) { *swp_tot = st; *swp_used = st - sf; *swp_pct = (*swp_used * 100.0) / st; }
}

static unsigned long long prv_rx, prv_tx;
static struct timespec prv_tm;
static int net_ready = 0;

int get_network(double* rx, double* tx, char* iface, char* ip) {
    *rx = *tx = 0.0; iface[0] = '\0'; ip[0] = '\0';
    
    FILE* f = fopen("/proc/net/dev", "r");
    if (!f) return 0;
    
    char buf[256];
    fgets(buf, sizeof(buf), f); fgets(buf, sizeof(buf), f);
    
    unsigned long long trx=0, ttx=0; int found=0;
    
    while (fgets(buf, sizeof(buf), f)) {
        char nm[32]; unsigned long long r, t;
        if (sscanf(buf, " %31[^:]: %llu %*u %*u %*u %*u %*u %*u %*u %llu", nm, &r, &t) >= 3) {
            if (!strcmp(nm, "lo")) continue;
            trx += r; ttx += t;
            if (!found) { strncpy(iface, nm, 31); iface[31]='\0'; found=1; }
        }
    }
    fclose(f);
    if (!found) return 0;
    
    struct timespec now; clock_gettime(CLOCK_MONOTONIC, &now);
    
    if (net_ready) {
        double dt = (now.tv_sec - prv_tm.tv_sec) + (now.tv_nsec - prv_tm.tv_nsec) / 1e9;
        if (dt > 0.1) { *rx = (trx - prv_rx) / dt; *tx = (ttx - prv_tx) / dt; }
    } else net_ready = 1;
    prv_rx = trx; prv_tx = ttx; prv_tm = now;
    
    f = popen("ip addr show 2>/dev/null | grep 'inet ' | grep -v 127.0.0.1 | head -1 | awk '{print $2}'", "r");
    if (f) { if (fgets(ip, 32, f)) { char* nl = strchr(ip, '\n'); if (nl) *nl = '\0'; } pclose(f); }
    
    return 1;
}

void get_battery(int* lvl, double* volt, int* temp) {
    *lvl = -1; *volt = -1.0; *temp = -1;
    strcpy(battery_health, "Unknown");
    strcpy(battery_status, "Unknown");
    strcpy(battery_technology, "Li-ion");
    battery_capacity = 0;
    
    FILE* f = popen("termux-battery-status 2>/dev/null", "r");
    if (!f) return;
    char buf[4096]; 
    size_t len = fread(buf, 1, sizeof(buf)-1, f); 
    pclose(f);
    if (len == 0) return; 
    buf[len] = '\0';
    
    char* p = strstr(buf, "\"percentage\":"); if (p) *lvl = atoi(p + 13);
    p = strstr(buf, "\"voltage\":"); if (p) *volt = atof(p + 10) / 1000.0;
    p = strstr(buf, "\"temperature\":"); if (p) *temp = atoi(p + 14);
    p = strstr(buf, "\"health\":"); if (p) sscanf(p + 9, "\"%63[^\"]\"", battery_health);
    p = strstr(buf, "\"status\":"); if (p) sscanf(p + 9, "\"%63[^\"]\"", battery_status);
    p = strstr(buf, "\"technology\":"); if (p) sscanf(p + 13, "\"%63[^\"]\"", battery_technology);
    p = strstr(buf, "\"capacity\":"); if (p) battery_capacity = atoi(p + 11);
}

int get_procs(char names[][16], double* cpus, unsigned long long* mems, int max) {
    FILE* f = popen("ps -eo comm,pcpu,rss --no-headers 2>/dev/null | grep -v 'ps$' | grep -v 'sort$' | grep -v 'sh$' | grep -v 'head$' | sort -k2 -nr | head -5", "r");
    if (!f) return 0;
    int cnt = 0; char line[256];
    while (fgets(line, sizeof(line), f) && cnt < max) {
        char nm[256]; double cpu; unsigned long long rss;
        if (sscanf(line, "%255s %lf %llu", nm, &cpu, &rss) >= 3) {
            strncpy(names[cnt], nm, 15); names[cnt][15] = '\0';
            cpus[cnt] = cpu; mems[cnt] = rss * 1024; cnt++;
        }
    }
    pclose(f); return cnt;
}

void get_sysinfo(char* android, char* vendor, char* model) {
    android[0] = vendor[0] = model[0] = '\0';
    FILE* f = popen("getprop ro.build.version.release 2>/dev/null", "r");
    if (f) { if (fgets(android, 16, f)) { char* nl = strchr(android, '\n'); if (nl) *nl = '\0'; } pclose(f); }
    f = popen("getprop ro.product.manufacturer 2>/dev/null", "r");
    if (f) { if (fgets(vendor, 32, f)) { char* nl = strchr(vendor, '\n'); if (nl) *nl = '\0'; } pclose(f); }
    f = popen("getprop ro.product.model 2>/dev/null", "r");
    if (f) { if (fgets(model, 32, f)) { char* nl = strchr(model, '\n'); if (nl) *nl = '\0'; } pclose(f); }
}

void fmt_bytes(unsigned long long b, char* buf, size_t sz) {
    if (b >= 1073741824ULL) snprintf(buf, sz, "%.2f GB", b / 1073741824.0);
    else if (b >= 1048576ULL) snprintf(buf, sz, "%.2f MB", b / 1048576.0);
    else if (b >= 1024ULL) snprintf(buf, sz, "%.2f KB", b / 1024.0);
    else snprintf(buf, sz, "%llu B", b);
}

void bar(double pct, int w) {
    if (pct < 0) pct = 0; if (pct > 100) pct = 100;
    int f = (int)(w * pct / 100.0);
    for (int i = 0; i < w; i++) fputs(i < f ? "█" : "░", stdout);
}

// ==================== РЕЖИМЫ ОТОБРАЖЕНИЯ ====================

void draw_detailed_mode(void) {
    double cpu_use, cpu_tmp;
    get_cpu(&cpu_use, &cpu_tmp);
    if (cpu_use == 0.0) cpu_use = get_cpu_from_procs();
    
    printf(CLR_CYAN "📊 ДЕТАЛЬНАЯ ИНФОРМАЦИЯ CPU:%s\n", CLR_RESET);
    printf("  Общая загрузка: %.1f%%\n", cpu_use);
    if (cpu_tmp > 0) printf("  Температура: %.0f°C\n", cpu_tmp);
    printf("  Ядер онлайн: %d\n", (int)sysconf(_SC_NPROCESSORS_ONLN));
}

void draw_device_info_mode(void) {
    char aver[16], vend[32], mod[32];
    get_sysinfo(aver, vend, mod);
    
    int bat_l, bat_t; double bat_v;
    get_battery(&bat_l, &bat_v, &bat_t);
    
    printf(CLR_CYAN "📱 ПОЛНАЯ ИНФОРМАЦИЯ ОБ УСТРОЙСТВЕ:%s\n", CLR_RESET);
    printf("  Производитель: %s%s%s\n", CLR_YELLOW, vend, CLR_RESET);
    printf("  Модель: %s%s%s\n", CLR_YELLOW, mod, CLR_RESET);
    printf("  Android: %s%s%s\n", CLR_YELLOW, aver, CLR_RESET);
    printf("  Root: %s%s%s\n", 
           (access("/system/bin/su", F_OK) == 0) ? CLR_RED : CLR_GREEN,
           (access("/system/bin/su", F_OK) == 0) ? "ЕСТЬ" : "НЕТ",
           CLR_RESET);
    
    if (bat_l >= 0) {
        printf("\n%s🔋 БАТАРЕЯ:%s\n", CLR_CYAN, CLR_RESET);
        printf("  Уровень: %d%%\n", bat_l);
        printf("  Напряжение: %.2f V\n", bat_v);
        printf("  Температура: %d°C\n", bat_t);
        printf("  Здоровье: %s\n", battery_health);
        printf("  Статус: %s\n", battery_status);
        printf("  Технология: %s\n", battery_technology);
    }
}

void draw_network_mode(void) {
    double rx, tx; char iface[32], ip[32];
    int ok = get_network(&rx, &tx, iface, ip);
    
    printf(CLR_CYAN "🌐 СЕТЕВАЯ ИНФОРМАЦИЯ:%s\n", CLR_RESET);
    if (ok) {
        printf("  Интерфейс: %s%s%s\n", CLR_YELLOW, iface, CLR_RESET);
        printf("  IP адрес: %s%s%s\n", CLR_YELLOW, ip, CLR_RESET);
        printf("  Скорость приёма: ⬇️ %.2f MB/s\n", rx / 1048576.0);
        printf("  Скорость отправки: ⬆️ %.2f MB/s\n", tx / 1048576.0);
        printf("  Всего принято: %llu байт\n", prv_rx);
        printf("  Всего отправлено: %llu байт\n", prv_tx);
    } else {
        printf("  %sНет данных или нет прав доступа%s\n", CLR_YELLOW, CLR_RESET);
    }
}

void draw_camera_mode(void) {
    printf(CLR_CYAN "📸 ИНФОРМАЦИЯ О КАМЕРАХ:%s\n", CLR_RESET);
    printf("  %sДля доступа к камерам используйте termux-api%s\n", CLR_YELLOW, CLR_RESET);
    printf("  %sУстановка: pkg install termux-api%s\n", CLR_YELLOW, CLR_RESET);
    
    // Попытка получить данные через termux-camera-info
    FILE* f = popen("termux-camera-info 2>/dev/null | head -30", "r");
    if (f) {
        char buf[256];
        int found = 0;
        while (fgets(buf, sizeof(buf), f)) {
            if (strstr(buf, "device") || strstr(buf, "facing") || strstr(buf, "id")) {
                if (!found) printf("\n%s  Доступные камеры:%s\n", CLR_CYAN, CLR_RESET);
                found = 1;
                printf("  %s", buf);
            }
        }
        pclose(f);
    }
}

void draw_sensor_mode(void) {
    printf(CLR_CYAN "🎯 ИНФОРМАЦИЯ О ДАТЧИКАХ:%s\n", CLR_RESET);
    printf("  %sДля доступа к датчикам используйте termux-sensor%s\n", CLR_YELLOW, CLR_RESET);
    printf("  %sУстановка: pkg install termux-api%s\n", CLR_YELLOW, CLR_RESET);
    
    // Попытка получить данные через termux-sensor
    FILE* f = popen("termux-sensor -l 2>/dev/null | head -20", "r");
    if (f) {
        char buf[256];
        int found = 0;
        while (fgets(buf, sizeof(buf), f)) {
            if (strstr(buf, "Sensor") || strstr(buf, "ACCELEROMETER") || 
                strstr(buf, "GYROSCOPE") || strstr(buf, "LIGHT") ||
                strstr(buf, "PROXIMITY") || strstr(buf, "MAGNETIC")) {
                if (!found) printf("\n%s  Доступные датчики:%s\n", CLR_CYAN, CLR_RESET);
                found = 1;
                printf("  %s", buf);
            }
        }
        pclose(f);
    }
}

void print_json_enhanced(void) {
    double cpu_use, cpu_tmp;
    get_cpu(&cpu_use, &cpu_tmp);
    if (cpu_use == 0.0) cpu_use = get_cpu_from_procs();
    
    unsigned long long mt, mu, mf, mb, mc; double mp;
    unsigned long long st, su; double sp;
    get_memory(&mt, &mu, &mf, &mb, &mc, &mp, &st, &su, &sp);
    
    double rx, tx; char iface[32], ip[32];
    int net_ok = get_network(&rx, &tx, iface, ip);
    
    int bat_l, bat_t; double bat_v; 
    get_battery(&bat_l, &bat_v, &bat_t);
    char aver[16], vend[32], mod[32]; 
    get_sysinfo(aver, vend, mod);
    
    unsigned long long disk_total = 0, disk_used = 0, disk_free = 0;
    int disk_percent = 0;
    struct statfs stfs;
    if (statfs("/data", &stfs) == 0) {
        disk_total = (unsigned long long)stfs.f_blocks * stfs.f_bsize;
        disk_free = (unsigned long long)stfs.f_bfree * stfs.f_bsize;
        disk_used = disk_total - disk_free;
        if (disk_total > 0) disk_percent = (int)((disk_used * 100) / disk_total);
    }
    
    double uptime = 0;
    FILE* f = fopen("/proc/uptime", "r");
    if (f) { fscanf(f, "%lf", &uptime); fclose(f); }
    
    printf("{\n");
    printf("  \"version\": \"%s\",\n", VERSION);
    printf("  \"timestamp\": %ld,\n", time(NULL));
    printf("  \"uptime_seconds\": %.0f,\n", uptime);
    printf("  \"cpu\": {\n");
    printf("    \"usage_percent\": %.1f,\n", cpu_use);
    printf("    \"temperature_celsius\": %.1f,\n", cpu_tmp);
    printf("    \"cores\": %d\n", (int)sysconf(_SC_NPROCESSORS_ONLN));
    printf("  },\n");
    printf("  \"memory\": {\n");
    printf("    \"total_bytes\": %llu,\n", mt);
    printf("    \"used_bytes\": %llu,\n", mu);
    printf("    \"free_bytes\": %llu,\n", mf);
    printf("    \"buffers_bytes\": %llu,\n", mb);
    printf("    \"cache_bytes\": %llu,\n", mc);
    printf("    \"used_percent\": %.1f,\n", mp);
    printf("    \"swap_total_bytes\": %llu,\n", st);
    printf("    \"swap_used_bytes\": %llu,\n", su);
    printf("    \"swap_percent\": %.1f\n", sp);
    printf("  },\n");
    printf("  \"storage\": {\n");
    printf("    \"total_bytes\": %llu,\n", disk_total);
    printf("    \"used_bytes\": %llu,\n", disk_used);
    printf("    \"free_bytes\": %llu,\n", disk_free);
    printf("    \"used_percent\": %d\n", disk_percent);
    printf("  },\n");
    printf("  \"network\": {\n");
    printf("    \"interface\": \"%s\",\n", net_ok ? iface : "none");
    printf("    \"ip\": \"%s\",\n", net_ok ? ip : "none");
    printf("    \"rx_speed_mbps\": %.2f,\n", net_ok ? (rx / 1048576.0) : 0);
    printf("    \"tx_speed_mbps\": %.2f,\n", net_ok ? (tx / 1048576.0) : 0);
    printf("    \"rx_bytes\": %llu,\n", net_ok ? prv_rx : 0);
    printf("    \"tx_bytes\": %llu\n", net_ok ? prv_tx : 0);
    printf("  },\n");
    printf("  \"battery\": {\n");
    printf("    \"level_percent\": %d,\n", bat_l);
    printf("    \"voltage_volts\": %.3f,\n", bat_v);
    printf("    \"temperature_celsius\": %d,\n", bat_t);
    printf("    \"health\": \"%s\",\n", battery_health);
    printf("    \"status\": \"%s\",\n", battery_status);
    printf("    \"technology\": \"%s\",\n", battery_technology);
    printf("    \"capacity_mah\": %d\n", battery_capacity);
    printf("  },\n");
    printf("  \"system\": {\n");
    printf("    \"android_version\": \"%s\",\n", aver);
    printf("    \"manufacturer\": \"%s\",\n", vend);
    printf("    \"model\": \"%s\",\n", mod);
    printf("    \"root_available\": %s\n", (access("/system/bin/su", F_OK) == 0) ? "true" : "false");
    printf("  },\n");
    
    char pn[5][16]; double pc[5]; unsigned long long pm[5];
    int pcnt = get_procs(pn, pc, pm, 5);
    printf("  \"top_processes\": [\n");
    for (int i = 0; i < pcnt; i++) {
        printf("    {\"name\": \"%s\", \"cpu_percent\": %.1f, \"memory_bytes\": %llu}%s\n",
               pn[i], pc[i], pm[i], (i == pcnt-1) ? "" : ",");
    }
    printf("  ],\n");
    
    printf("  \"sensors\": {\n");
    printf("    \"termux_api_available\": %s\n", 
           (access("/data/data/com.termux/files/usr/bin/termux-sensor", X_OK) == 0) ? "true" : "false");
    printf("  }\n");
    printf("}\n");
}

// ==================== ВАША ИДЕАЛЬНАЯ РАМКА ====================
void draw_frame(void) {
    double cpu_use, cpu_tmp;
    get_cpu(&cpu_use, &cpu_tmp);
    if (cpu_use == 0.0) cpu_use = get_cpu_from_procs();
    
    unsigned long long mt, mu, mf, mb, mc; double mp;
    unsigned long long st, su; double sp;
    get_memory(&mt, &mu, &mf, &mb, &mc, &mp, &st, &su, &sp);
    
    double rx, tx; char iface[32], ip[32];
    int net_ok = get_network(&rx, &tx, iface, ip);
    
    int bat_l, bat_t; double bat_v; get_battery(&bat_l, &bat_v, &bat_t);
    char aver[16], vend[32], mod[32]; get_sysinfo(aver, vend, mod);
    
    char pn[5][16]; double pc[5]; unsigned long long pm[5];
    int pcnt = get_procs(pn, pc, pm, 5);
    
    char mts[32], mus[32], mfs[32], mbs[32], mcs[32];
    fmt_bytes(mt, mts, 32); fmt_bytes(mu, mus, 32);
    fmt_bytes(mf, mfs, 32); fmt_bytes(mb, mbs, 32); fmt_bytes(mc, mcs, 32);
    
    printf(CLR_CYAN "┌─────────────────────────────────────────────────────┐" CLR_RESET "\n");
    printf(CLR_CYAN "│" CLR_RESET "  " CLR_BOLD CLR_GREEN "🖥️  SOFIA SYSTEM MONITOR v" VERSION CLR_RESET "                    " CLR_CYAN "│" CLR_RESET "\n");
    printf(CLR_CYAN "├─────────────────────────────────────────────────────┤" CLR_RESET "\n");
    
    printf(CLR_CYAN "│" CLR_RESET "  CPU: [");
    bar(cpu_use, 28);
    printf("] %5.1f%%", cpu_use);
    if (cpu_tmp > 0) printf("  %s🔥 %3.0f°C" CLR_RESET, cpu_tmp > 60 ? CLR_RED : CLR_YELLOW, cpu_tmp);
    printf("               " CLR_CYAN "│" CLR_RESET "\n");
    
    printf(CLR_CYAN "│" CLR_RESET "  RAM: [");
    bar(mp, 26);
    printf("] %5.1f%%  %s/%s     " CLR_CYAN "│" CLR_RESET "\n", mp, mus, mts);
    printf(CLR_CYAN "│" CLR_RESET "    📊 Free: %-41s" CLR_CYAN "│" CLR_RESET "\n", mfs);
    printf(CLR_CYAN "│" CLR_RESET "    📦 Buffers: %-38s" CLR_CYAN "│" CLR_RESET "\n", mbs);
    printf(CLR_CYAN "│" CLR_RESET "    💾 Cache: %-39s" CLR_CYAN "│" CLR_RESET "\n", mcs);
    
    if (st > 0) {
        char sts[32], sus[32]; fmt_bytes(st, sts, 32); fmt_bytes(su, sus, 32);
        printf(CLR_CYAN "│" CLR_RESET "    🔄 Swap: %s/%s (%.0f%%)" CLR_CYAN "│" CLR_RESET "\n", sus, sts, sp);
    }
    
    if (net_ok) {
        printf(CLR_CYAN "│" CLR_RESET "  NET:  ⬇️ %5.2f MB/s  ⬆️ %5.2f MB/s  🌐 %-10s" CLR_CYAN "│" CLR_RESET "\n",
               rx / 1048576.0, tx / 1048576.0, iface[0] ? iface : "unknown");
        if (ip[0]) printf(CLR_CYAN "│" CLR_RESET "    📡 IP: %-42s" CLR_CYAN "│" CLR_RESET "\n", ip);
    } else {
        printf(CLR_CYAN "│" CLR_RESET "  " CLR_YELLOW "⚠️  NET: Нужны права su или Rish" CLR_RESET "                   " CLR_CYAN "│" CLR_RESET "\n");
    }
    
    printf(CLR_CYAN "├─────────────────────────────────────────────────────┤" CLR_RESET "\n");
    printf(CLR_CYAN "│" CLR_RESET "  " CLR_BOLD CLR_YELLOW "🔝 ТОП ПРОЦЕССЫ (по CPU)" CLR_RESET "                       " CLR_CYAN "│" CLR_RESET "\n");
    
    if (pcnt > 0) {
        for (int i = 0; i < pcnt; i++) {
            char pms[32]; fmt_bytes(pm[i], pms, 32);
            printf(CLR_CYAN "│" CLR_RESET "   %d. " CLR_GREEN "%-15s" CLR_RESET " %5.1f%% " CLR_YELLOW "%-12s" CLR_RESET " " CLR_CYAN "│" CLR_RESET "\n",
                   i+1, pn[i], pc[i], pms);
        }
    } else {
        printf(CLR_CYAN "│" CLR_RESET "    " CLR_YELLOW "Нет данных о процессах" CLR_RESET "                         " CLR_CYAN "│" CLR_RESET "\n");
    }
    
    printf(CLR_CYAN "├─────────────────────────────────────────────────────┤" CLR_RESET "\n");
    printf(CLR_CYAN "│" CLR_RESET "  " CLR_GREEN "📱 ANDROID:" CLR_RESET " " CLR_YELLOW "%-8s" CLR_RESET " " CLR_GREEN "🔐 ROOT:" CLR_RESET " %s%s" CLR_RESET "       " CLR_CYAN "│" CLR_RESET "\n",
           aver[0] ? aver : "N/A",
           (access("/system/bin/su", F_OK) == 0) ? CLR_RED : CLR_GREEN,
           (access("/system/bin/su", F_OK) == 0) ? "ЕСТЬ" : "НЕТ");
    printf(CLR_CYAN "│" CLR_RESET "  " CLR_GREEN "🏭 ПРОИЗВОДИТЕЛЬ:" CLR_RESET " " CLR_YELLOW "%-20s" CLR_RESET " " CLR_CYAN "│" CLR_RESET "\n", vend[0] ? vend : "Неизвестно");
    printf(CLR_CYAN "│" CLR_RESET "  " CLR_GREEN "📱 МОДЕЛЬ:" CLR_RESET " " CLR_YELLOW "%-25s" CLR_RESET " " CLR_CYAN "│" CLR_RESET "\n", mod[0] ? mod : "Неизвестно");
    
    if (bat_l >= 0) {
        printf(CLR_CYAN "│" CLR_RESET "  " CLR_GREEN "🔋 БАТАРЕЯ:" CLR_RESET " %s%d%%" CLR_RESET " (%.2fV) " CLR_GREEN "🔥 %d°C" CLR_RESET "              " CLR_CYAN "│" CLR_RESET "\n",
               bat_l < 20 ? CLR_RED : CLR_YELLOW, bat_l, bat_v, bat_t);
        if (strcmp(battery_health, "Unknown") != 0) {
            printf(CLR_CYAN "│" CLR_RESET "    💊 Здоровье: %s | 📊 Статус: %s" CLR_CYAN "│" CLR_RESET "\n",
                   battery_health, battery_status);
        }
    } else {
        printf(CLR_CYAN "│" CLR_RESET "  " CLR_YELLOW "⚠️  Батарея: установите termux-api" CLR_RESET "                " CLR_CYAN "│" CLR_RESET "\n");
    }
    
    printf(CLR_CYAN "├─────────────────────────────────────────────────────┤" CLR_RESET "\n");
    printf(CLR_CYAN "│" CLR_RESET "  " CLR_GREEN "💡 'q' выход | '0' перезапуск | -d -i -n -c -s -j" CLR_RESET "    " CLR_CYAN "│" CLR_RESET "\n");
    printf(CLR_CYAN "└─────────────────────────────────────────────────────┘" CLR_RESET "\n");
}

void print_help(void) {
    printf(CLR_CYAN "════════════════════════════════════════════════════════════════%s\n", CLR_RESET);
    printf(CLR_BOLD CLR_GREEN "📊 SOFIA SYSTEM MONITOR v%s%s\n", VERSION, CLR_RESET);
    printf(CLR_CYAN "════════════════════════════════════════════════════════════════%s\n", CLR_RESET);
    printf("\n");
    printf("  %sИспользование:%s sofia [опции]\n", CLR_YELLOW, CLR_RESET);
    printf("\n");
    printf("  %sОпции:%s\n", CLR_YELLOW, CLR_RESET);
    printf("    %s-d%s           Детальный режим (все ядра CPU)\n", CLR_GREEN, CLR_RESET);
    printf("    %s-i%s           Информация об устройстве\n", CLR_GREEN, CLR_RESET);
    printf("    %s-n%s           Сетевая информация\n", CLR_GREEN, CLR_RESET);
    printf("    %s-c%s           Информация о камерах\n", CLR_GREEN, CLR_RESET);
    printf("    %s-s%s           Информация о датчиках (сенсорах)\n", CLR_GREEN, CLR_RESET);
    printf("    %s-j%s           Вывод в JSON (30+ пунктов)\n", CLR_GREEN, CLR_RESET);
    printf("    %s-h%s           Эта справка\n", CLR_GREEN, CLR_RESET);
    printf("\n");
    printf("  %sБез опций:%s запускается интерактивный монитор\n", CLR_YELLOW, CLR_RESET);
    printf("    'q' - выход\n");
    printf("    '0' - перезапуск монитора\n");
    printf("\n");
    printf(CLR_CYAN "════════════════════════════════════════════════════════════════%s\n", CLR_RESET);
}

// ==================== ОСНОВНАЯ ФУНКЦИЯ ====================
int main(int argc, char* argv[]) {
    // Парсинг аргументов командной строки
    if (argc >= 2) {
        if (strcmp(argv[1], "-j") == 0) {
            print_json_enhanced();
            return 0;
        }
        if (strcmp(argv[1], "-i") == 0) {
            draw_device_info_mode();
            return 0;
        }
        if (strcmp(argv[1], "-n") == 0) {
            draw_network_mode();
            return 0;
        }
        if (strcmp(argv[1], "-c") == 0) {
            draw_camera_mode();
            return 0;
        }
        if (strcmp(argv[1], "-s") == 0) {
            draw_sensor_mode();
            return 0;
        }
        if (strcmp(argv[1], "-d") == 0) {
            draw_detailed_mode();
            return 0;
        }
        if (strcmp(argv[1], "-h") == 0 || strcmp(argv[1], "--help") == 0) {
            print_help();
            return 0;
        }
    }
    
    // Интерактивный режим
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);
    tcgetattr(STDIN_FILENO, &orig_tio);
    atexit(cleanup);
    
    struct termios raw = orig_tio;
    raw.c_lflag &= ~(ICANON | ECHO);
    raw.c_cc[VMIN] = 0;
    raw.c_cc[VTIME] = 0;
    tcsetattr(STDIN_FILENO, TCSANOW, &raw);
    
    printf("\033[2J\033[H");
    draw_frame();
    fflush(stdout);
    
    while (running) {
        fd_set fds;
        struct timeval tv = { .tv_sec = UPDATE_MS/1000, .tv_usec = (UPDATE_MS%1000)*1000 };
        FD_ZERO(&fds);
        FD_SET(STDIN_FILENO, &fds);
        
        int ready = select(STDIN_FILENO + 1, &fds, NULL, NULL, &tv);
        if (ready < 0) {
            if (errno == EINTR || errno == EAGAIN) continue;
            break;
        }
        
        if (ready > 0) {
            char c;
            while (read(STDIN_FILENO, &c, 1) == 1) {
                if (c == 'q' || c == 'Q') {
                    running = 0;
                    break;
                } else if (c == '0') {
                    printf("\033[2J\033[H");
                    draw_frame();
                    fflush(stdout);
                    break;
                }
            }
            if (!running) break;
        }
        
        printf("\033[H");
        draw_frame();
        fflush(stdout);
    }
    
    return 0;
}
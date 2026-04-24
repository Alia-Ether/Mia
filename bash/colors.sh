#!/bin/bash
# colors.sh — полная палитра терминала Алии 🌸

# === ТВОИ ОРИГИНАЛЬНЫЕ ЦВЕТА ===
export RESET='\033[0m'
export NC='\033[0m'                 # Сброс (синоним RESET)
export PY_BLUE='\033[38;5;33m'      # Синий как у Python
export PY_YELLOW='\033[38;5;220m'   # Жёлтый как у Python
export PINK='\033[38;5;205m'        # Розовый
export GREEN='\033[38;5;82m'        # Зелёный

# === ДОПОЛНИТЕЛЬНЫЕ ЦВЕТА ===
export PURPLE='\033[38;5;93m'       # Фиолетовый
export CYAN='\033[1;36m'            # Голубой
export BLUE='\033[1;34m'            # Синий
export YELLOW='\033[1;33m'          # Жёлтый
export RED='\033[1;31m'             # Красный
export WHITE='\033[1;37m'           # Белый
export BLACK='\033[1;30m'           # Чёрный

# === СТИЛИ ===
export BOLD='\033[1m'               # Жирный
export DIM='\033[2m'                # Тусклый
export ITALIC='\033[3m'             # Курсив
export UNDERLINE='\033[4m'          # Подчёркнутый
export BLINK='\033[5m'              # Мигающий
export REVERSE='\033[7m'            # Инвертированный

# === КОМБИНАЦИИ ===
export BOLD_PINK='\033[1;38;5;205m'
export BOLD_PURPLE='\033[1;38;5;93m'
export BOLD_CYAN='\033[1;36m'
export BOLD_GREEN='\033[1;38;5;82m'
export DIM_WHITE='\033[2;37m'

# === ФОНОВЫЕ ЦВЕТА ===
export BG_PINK='\033[48;5;205m'
export BG_PURPLE='\033[48;5;93m'
export BG_BLACK='\033[40m'
export BG_WHITE='\033[47m'
export BG_PY_BLUE='\033[48;5;33m'

echo -e "${PINK}🌸 Цвета загружены! 🌸${RESET}"

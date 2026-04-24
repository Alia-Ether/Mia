#!/bin/bash

# Полная очистка экрана и буфера перед стартом
echo -ne "\033[2J\033[3J\033[H"

# Цвета
RED='\033[0;31m'
NC='\033[0m'
PINK_BRIGHT='\033[38;5;205;3m'

# Определение языка системы
LANG_CURRENT=$(echo $LANG)
if [[ "$LANG_CURRENT" == *"ru"* ]]; then IS_RU=true; else IS_RU=false; fi

print_mia() {
    local msg_ru="$1"
    local msg_en="$2"
    local final_msg
    if [ "$IS_RU" = true ]; then final_msg="$msg_ru"; else final_msg="$msg_en"; fi
    python3 -c "from rich.console import Console; Console().print(\"$final_msg\", style='#FF69B4 bold italic')" 2>/dev/null || echo -e "${PINK_BRIGHT}$final_msg${NC}"
}

# 1. Жесткая проверка Termux
if [ ! -d "/data/data/com.termux" ]; then
    echo -e "${RED}❌ ERROR: Locked to Termux only.${NC}"
    exit 1
fi

print_mia "🚀 Инициализация Mia Ecosystem (EUL)..." "🚀 Initializing Mia Ecosystem (EUL)..."

# 2. Проверка интернета
print_mia "🌐 Проверка сетевого соединения..." "🌐 Checking connection..."
if ping -c 1 8.8.8.8 &>/dev/null; then
    IS_OFFLINE=false
    EXTRA_FLAGS=""
    print_mia "✅ Online режим" "✅ Online mode"
else
    IS_OFFLINE=true
    EXTRA_FLAGS="--no-build-isolation --no-deps"
    print_mia "⚠️ Offline режим: установка без внешних зависимостей" "⚠️ Offline mode"
fi

# 3. Проверка системных пакетов
DEPS=("clang" "python" "lua" "termux-api" "payload-dumper-go")
for pkg in "${DEPS[@]}"; do
    if dpkg -s "$pkg" &>/dev/null || command -v "$pkg" &>/dev/null; then
        print_mia "  [OK] $pkg найден" "  [OK] $pkg found"
    else
        if [ "$IS_OFFLINE" = false ]; then
            [ "$IS_RU" = true ] && msg="❓ $pkg не найден. Установить? (y/n): " || msg="❓ $pkg not found. Install? (y/n): "
            echo -en "${PINK_BRIGHT}$msg${NC}"
            read -n 1 -r REPLY
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                pkg install "$pkg" -y > /dev/null 2>&1
            else
                print_mia "❌ Отказ от установки. Сборка невозможна." "❌ Refused. Build impossible."
                exit 1
            fi
        else
            print_mia "❌ Ошибка: $pkg не найден!" "❌ Error: $pkg not found!"
            exit 1
        fi
    fi
done

# 4. Выбор версии Python
print_mia "🐍 Выберите номер Python:" "🐍 Select Python version:"
mapfile -t PY_VERSIONS < <(compgen -c python3. | grep -E '^python3\.[0-9]+$' | sort -u)
for i in "${!PY_VERSIONS[@]}"; do
    echo -e "${PINK_BRIGHT}$((i+1))) ${PY_VERSIONS[$i]}${NC}"
done
echo -en "${PINK_BRIGHT}> ${NC}"
read CHOICE
PY_BIN="${PY_VERSIONS[$((CHOICE-1))]}"

# 5. Выбор режима установки
print_mia "🛠️ Тип: 1-Обычный, 2-Разработчик (-e)" "🛠️ Type: 1-Normal, 2-Dev (-e)"
echo -en "${PINK_BRIGHT}> ${NC}"
read MODE
INSTALL_CMD="."
[ "$MODE" == "2" ] && INSTALL_CMD="-e ."

# 6. Сборка
print_mia "📦 Запуск сборки Mia в $PY_BIN..." "📦 Building Mia in $PY_BIN..."
$PY_BIN -m pip install --force-reinstall $INSTALL_CMD $EXTRA_FLAGS 2>&1 | $PY_BIN -c "
import sys
from rich.console import Console
console = Console()
for line in sys.stdin:
    line = line.strip()
    if line: console.print(f'  [#FFB6C1 italic]→ {line}[/]')
"

if [ ${PIPESTATUS} -eq 0 ]; then
    print_mia "✨ Mia успешно установлена!" "✨ Mia successfully installed!"
    
    # === ИНСТРУКЦИЯ ПОСЛЕ УСТАНОВКИ ===
    echo -e "\n${PINK_BRIGHT}========================================${NC}"
    print_mia "📝 ЧТОБЫ SOFIA РАБОТАЛА, ДОБАВЬ ЭТО В ~/.bashrc:" "📝 TO MAKE SOFIA WORK, ADD THIS TO ~/.bashrc:"
    echo -e "${PINK_BRIGHT}----------------------------------------${NC}"
    echo -e "sofia() {"
    echo -e "    local dev_path=\"\$HOME/Mia/MiaUI/miaui_mi/security/pypass/sofia_monitor\""
    echo -e "    local sys_path=\"/data/data/com.termux/files/usr/lib/$PY_BIN/site-packages/miaui_mi/security/pypass/sofia_monitor\""
    echo -e "    if [[ -f \"\$dev_path\" ]]; then \"\$dev_path\" \"\$@\""
    echo -e "    else \"\$sys_path\" \"\$@\"; fi"
    echo -e "}"
    echo -e "${PINK_BRIGHT}----------------------------------------${NC}"
    print_mia "↻ Затем выполни: source ~/.bashrc" "↻ Then run: source ~/.bashrc"
    echo -e "${PINK_BRIGHT}========================================${NC}\n"
else
    print_mia "❌ Ошибка сборки." "❌ Build error."
fi


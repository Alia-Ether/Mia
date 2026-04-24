#!/usr/bin/env bash
# main.sh — Галерея баннеров MIA ✨

# ==============================
# БАЗА
# ==============================

clear

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BANNERS_DIR="$SCRIPT_DIR/banners"
THEME_FILE="$HOME/.current_theme"
PS1_FILE="$HOME/.current_ps1"
BASHRC="$HOME/.bashrc"

mkdir -p "$BANNERS_DIR"

# ==============================
# ЦВЕТА
# ==============================

if [[ -f "$SCRIPT_DIR/colors.sh" ]]; then
    source "$SCRIPT_DIR/colors.sh"
else
    RED='\033[1;31m'
    GREEN='\033[1;32m'
    CYAN='\033[1;36m'
    PINK='\033[38;5;205m'
    PURPLE='\033[38;5;93m'
    YELLOW='\033[1;33m'
    BLUE='\033[1;34m'
    WHITE='\033[1;37m'
    RESET='\033[0m'
fi

# ==============================
# БАННЕРЫ СО ВШИТЫМИ ЦВЕТАМИ
# ==============================
SPECIAL_BANNERS=("17.txt" "19.txt" "20.txt" "21.txt")

# ==============================
# ФУНКЦИЯ ПОКАЗА ЦВЕТНОГО ПРЕВЬЮ
# ==============================

show_color_preview() {
    local color_code="$1"
    echo -e "${color_code}████████████████████████████████████████████████████${RESET}"
}

# ==============================
# 255-ЦВЕТНАЯ ПАЛИТРА
# ==============================

show_256_palette() {
    echo -e "${CYAN}🎨 256-цветная палитра ANSI:${RESET}"
    echo
    for i in {0..255}; do
        printf "\033[38;5;${i}m%3d\033[0m " "$i"
        if [[ $(( (i + 1) % 16 )) == 0 ]]; then
            echo
        fi
    done
    echo
}

choose_color_256() {
    echo -e "${CYAN}🌈 Выбери цвет из 256-цветной палитры:${RESET}"
    echo
    
    # Превью базовых цветов
    echo -e "1) ${RED}$(show_color_preview "$RED")${RESET}"
    echo -e "2) ${GREEN}$(show_color_preview "$GREEN")${RESET}"
    echo -e "3) ${CYAN}$(show_color_preview "$CYAN")${RESET}"
    echo -e "4) ${PINK}$(show_color_preview "$PINK")${RESET}"
    echo -e "5) ${PURPLE}$(show_color_preview "$PURPLE")${RESET}"
    echo -e "6) ${YELLOW}$(show_color_preview "$YELLOW")${RESET}"
    echo -e "7) ${BLUE}$(show_color_preview "$BLUE")${RESET}"
    echo -e "8) ${WHITE}$(show_color_preview "$WHITE")${RESET}"
    echo -e "9) 🎨 Выбрать из палитры"
    echo -e "0) 🔢 Ввести номер цвета (0-255)"
    echo
    read -rp "> " c

    case "$c" in
        1) BANNER_COLOR="$RED" ;;
        2) BANNER_COLOR="$GREEN" ;;
        3) BANNER_COLOR="$CYAN" ;;
        4) BANNER_COLOR="$PINK" ;;
        5) BANNER_COLOR="$PURPLE" ;;
        6) BANNER_COLOR="$YELLOW" ;;
        7) BANNER_COLOR="$BLUE" ;;
        8) BANNER_COLOR="$WHITE" ;;
        9) 
            show_256_palette
            echo
            read -rp "Введи номер цвета (0-255): " color_num
            if [[ "$color_num" =~ ^[0-9]+$ ]] && [[ "$color_num" -ge 0 ]] && [[ "$color_num" -le 255 ]]; then
                BANNER_COLOR="\033[38;5;${color_num}m"
                echo -e "${BANNER_COLOR}✅ Цвет $color_num выбран! $(show_color_preview "$BANNER_COLOR")${RESET}"
            else
                echo -e "${RED}❌ Неверный номер, использую PINK${RESET}"
                BANNER_COLOR="$PINK"
            fi
            ;;
        0)
            read -rp "Введи номер цвета (0-255): " color_num
            if [[ "$color_num" =~ ^[0-9]+$ ]] && [[ "$color_num" -ge 0 ]] && [[ "$color_num" -le 255 ]]; then
                BANNER_COLOR="\033[38;5;${color_num}m"
                echo -e "${BANNER_COLOR}✅ Цвет $color_num выбран! $(show_color_preview "$BANNER_COLOR")${RESET}"
            else
                echo -e "${RED}❌ Неверный номер, использую PINK${RESET}"
                BANNER_COLOR="$PINK"
            fi
            ;;
        *) BANNER_COLOR="$PINK" ;;
    esac
}

# ==============================
# PYTHON-БАННЕР (20.txt)
# ==============================

create_python_banner() {
    cat > "$BANNERS_DIR/20.txt" << 'EOF'
\033[38;5;33m      .⢀⣤⣴⣶⣶⣶⣶⣶⣦⣄
\033[38;5;33m⠀⠀⠀⠀⠀⠀⢀⣾⠟⠛⢿⣿⣿⣿⣿⣿⣿⣷
\033[38;5;33m⠀⠀⠀⠀⠀⠀⢸⣿⣄⣀⣼⣿⣿⣿⣿⣿⣿⣿\033[38;5;220m⢀⣀⣀⣀⡀
\033[38;5;33m⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠉⠉⣿⣿⣿⣿⣿\033[38;5;220m⢸⣿⣿⣿⣿⣦
\033[38;5;33m⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\033[38;5;220m⢸⣿⣿⣿⣿⣿⡇
\033[38;5;33m⢰⣿⣿⣿⣿⣿⣿⣿⣿⠿⠿⠿⠿⠿⠿⠿⠿⠋\033[38;5;220m⣼⣿⣿⣿⣿⣿⡇
\033[38;5;33m⢸⣿⣿⣿⣿⣿⡿⠉\033[38;5;220m⣠⣤⣤⣤⣤⣤⣤⣤⣴⣾⣿⣿⣿⣿⣿⣿⡇
\033[38;5;33m⢸⣿⣿⣿⣿⣿⡇\033[38;5;220m⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿
\033[38;5;33m⠘⣿⣿⣿⣿⣿⡇\033[38;5;220m⣿⣿⣿⣿⣿⠛⠛⠛⠛⠛⠛⠛⠛⠛⠋
\033[38;5;33m⠀⠈⠛⠻⠿⠿⠇\033[38;5;220m⣿⣿⣿⣿⣿⣿⣿⣿⠿⠿⣿⡇
\033[38;5;220m⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣧⣀⣀⣿⠇
\033[38;5;220m⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢿⣿⣿⣿⣿⣿⣿⣿⡿⠋\033[0m
EOF
}

# ==============================
# ВЫВОД БАННЕРА
# ==============================

show_banner() {
    local file="$1"
    local name=$(basename "$file")

    local is_special=false
    for special in "${SPECIAL_BANNERS[@]}"; do
        if [[ "$name" == "$special" ]]; then
            is_special=true
            break
        fi
    done

    if [[ "$is_special" == true ]]; then
        echo -ne "\033[2J\033[3;1f"
        while IFS= read -r line; do
            echo -e "$line"
        done < "$file"
        printf "\n\n"
    else
        echo -e "${BANNER_COLOR:-$PINK}"
        cat "$file"
        echo -e "$RESET"
    fi
}

# ==============================
# .bashrc
# ==============================

update_bashrc() {
    local START="# >>> MIA TERMINAL THEME >>>"
    local END="# <<< MIA TERMINAL THEME <<<"

    if grep -q "$START" "$BASHRC" 2>/dev/null; then
        sed -i "/$START/,/$END/d" "$BASHRC"
    fi

    local TEMP_FILE=$(mktemp)
    
    cat > "$TEMP_FILE" << EOF
$START
if [[ -f "$THEME_FILE" ]]; then
    source "$THEME_FILE"
    if [[ -n "\$SELECTED_BANNER" ]]; then
        case "\$(basename "\$SELECTED_BANNER")" in
            17.txt|19.txt|20.txt|21.txt)
                echo -ne "\033[2J\033[3;1f"
                while IFS= read -r line; do echo -e "\$line"; done < "\$SELECTED_BANNER"
                printf "\n\n"
                ;;
            *)
                echo -e "\$BANNER_COLOR"
                cat "\$SELECTED_BANNER"
                echo -e "\033[0m"
                ;;
        esac
    fi
fi
[[ -f "$PS1_FILE" ]] && source "$PS1_FILE"
$END

EOF

    if [[ -f "$BASHRC" ]]; then
        cat "$BASHRC" >> "$TEMP_FILE"
    fi

    mv "$TEMP_FILE" "$BASHRC"
}

# ==============================
# PS1
# ==============================

save_ps1() {
    if [[ -f "$SCRIPT_DIR/PS1.sh" ]]; then
        source "$SCRIPT_DIR/PS1.sh"
        if [[ -n "$PS1" ]]; then
            echo "export PS1='$PS1'" > "$PS1_FILE"
            export PS1="$PS1"
        fi
    fi
}

# ==============================
# ГАЛЕРЕЯ
# ==============================

gallery() {
    [[ ! -f "$BANNERS_DIR/20.txt" ]] && create_python_banner

    mapfile -t BANNERS < <(ls "$BANNERS_DIR"/*.txt 2>/dev/null | sort -V)

    if [[ ${#BANNERS[@]} -eq 0 ]]; then
        echo "❌ Нет баннеров"
        return 1
    fi

    local i=0

    while true; do
        clear
        show_banner "${BANNERS[$i]}"

        echo
        echo -e "${CYAN}[ $((i+1)) / ${#BANNERS[@]} ]${RESET}"
        echo -e "1 → вперёд | 2 → назад | Enter → выбрать | 0 → выход"

        read -rsn1 key

        case "$key" in
            1) ((i=(i+1)%${#BANNERS[@]})) ;;
            2) ((i=(i-1+${#BANNERS[@]})%${#BANNERS[@]})) ;;
            "")
                SELECTED_BANNER="${BANNERS[$i]}"

                echo "BANNER_COLOR='$BANNER_COLOR'" > "$THEME_FILE"
                echo "SELECTED_BANNER='$SELECTED_BANNER'" >> "$THEME_FILE"

                save_ps1
                update_bashrc

                clear
                show_banner "$SELECTED_BANNER"

                echo
                echo -e "${GREEN}✔ Применено!${RESET}"
                echo -e "${YELLOW}↻ Выполни: source ~/.bashrc${RESET}"
                echo
                echo -e "${CYAN}Нажми любую клавишу чтобы продолжить...${RESET}"
                read -rsn1

                return 0
                ;;
            0) 
                return 0
                ;;
        esac
    done
}

# ==============================
# ВЫБОР ЦВЕТА
# ==============================

clear
echo -e "${CYAN}Выбери цвет:${RESET}"
echo
choose_color_256

gallery

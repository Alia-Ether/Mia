# ╔═════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                       ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║
# ║  lang: python                                    ║
# ║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║
# ║  build:3.10.15                                   ║
# ║  files: pin_manager.py                           ║
# ╚═════════════════════════════╝

import os
import json
import hashlib
from colorama import init, Fore

init(autoreset=True)

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

# ===================== ХЕШИРОВАНИЕ PIN =====================


def hash_pin(pin):
    """Хеширует PIN-код с солью"""
    salt = "VORTEXUI_SONYA_2026"  # фиксированная соль
    combined = pin + salt
    return hashlib.sha256(combined.encode()).hexdigest()

# ===================== ПРОВЕРКА ПЕРВОГО ЗАПУСКА =====================


def is_first_run():
    """Проверяет, первый ли это запуск"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return 'pin_hash' not in config
        except Exception:
            return True
    return True

# ===================== СОЗДАНИЕ PIN =====================


def create_pin():
    """Создаёт новый PIN-код (при первом запуске)"""
    print(f"\n{Fore.CYAN}╔════════════════════════════════════╗")
    print(f"║    🔐 ПЕРВОНАЧАЛЬНАЯ НАСТРОЙКА    ║")
    print(f"╚════════════════════════════════════╝{Fore.RESET}\n")  # ← ИСПРАВЛЕНО!

    while True:
        pin1 = input(f"{Fore.YELLOW}👉 Придумай PIN-код (4-8 цифр): {Fore.RESET}").strip()  # ← ИСПРАВЛЕНО!

        # Проверка на цифры
        if not pin1.isdigit():
            print(f"{Fore.RED}❌ Только цифры!{Fore.RESET}")  # ← ИСПРАВЛЕНО!
            continue

        # Проверка длины
        if len(pin1) < 4 or len(pin1) > 8:
            print(f"{Fore.RED}❌ PIN должен быть от 4 до 8 цифр!{Fore.RESET}")  # ← ИСПРАВЛЕНО!
            continue

        pin2 = input(f"{Fore.YELLOW}👉 Повтори PIN-код: {Fore.RESET}").strip()  # ← ИСПРАВЛЕНО!

        if pin1 == pin2:
            # Сохраняем хеш
            pin_hash = hash_pin(pin1)

            # Загружаем или создаём конфиг
            config = {}
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)

            config['pin_hash'] = pin_hash
            config['base_path'] = "/storage/emulated/0/Alarms"  # путь по умолчанию

            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)

            print(f"\n{Fore.GREEN}✅ PIN-код успешно создан!{Fore.RESET}")  # ← ИСПРАВЛЕНО!
            return True
        else:
            print(f"{Fore.RED}❌ PIN-коды не совпадают!{Fore.RESET}")  # ← ИСПРАВЛЕНО!

# ===================== ПРОВЕРКА PIN =====================


def check_pin():
    """Проверяет введённый PIN-код"""
    if not os.path.exists(CONFIG_FILE):
        return False

    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            saved_hash = config.get('pin_hash')

            if not saved_hash:
                return False

        attempts = 3
        while attempts > 0:
            pin = input(f"{Fore.YELLOW}🔐 Введи PIN-код ({attempts} попытки): {Fore.RESET}").strip()  # ← ИСПРАВЛЕНО!

            if hash_pin(pin) == saved_hash:
                return True

            attempts -= 1
            if attempts > 0:
                print(f"{Fore.RED}❌ Неверный PIN! Осталось попыток: {attempts}{Fore.RESET}")  # ← ИСПРАВЛЕНО!

        print(f"{Fore.RED}⛔ Превышено число попыток!{Fore.RESET}")  # ← ИСПРАВЛЕНО!
        return False

    except Exception as e:
        print(f"{Fore.RED}❌ Ошибка: {e}{Fore.RESET}")  # ← ИСПРАВЛЕНО!
        return False

# ===================== ПОЛУЧЕНИЕ ПУТИ =====================


def get_base_path():
    """Возвращает сохранённый путь из конфига"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get('base_path', "/storage/emulated/0/Alarms")
        except Exception:
            return "/storage/emulated/0/Alarms"
    return "/storage/emulated/0/Alarms"

# ===================== ИЗМЕНЕНИЕ ПУТИ =====================


def change_base_path():
    """Меняет путь сохранения файлов"""
    current = get_base_path()

    print(f"\n{Fore.CYAN}╔════════════════════════════════════╗")
    print(f"║    📁 ИЗМЕНЕНИЕ ПУТИ СОХРАНЕНИЯ   ║")
    print(f"╚════════════════════════════════════╝{Fore.RESET}\n")  # ← ИСПРАВЛЕНО!

    print(f"{Fore.GREEN}Текущий путь: {Fore.YELLOW}{current}{Fore.RESET}\n")  # ← ИСПРАВЛЕНО!
    print(f"{Fore.CYAN}Примеры:{Fore.RESET}")  # ← ИСПРАВЛЕНО!
    print(f"  • /storage/emulated/0/Download")
    print(f"  • /storage/emulated/0/Alarms")
    print(f"  • /storage/emulated/0/DCIM\n")

    new_path = input(f"{Fore.YELLOW}👉 Введи новый путь: {Fore.RESET}").strip()  # ← ИСПРАВЛЕНО!

    if not new_path:
        print(f"{Fore.RED}❌ Путь не может быть пустым!{Fore.RESET}")  # ← ИСПРАВЛЕНО!
        return False

    # Создаём папку, если её нет
    try:
        os.makedirs(new_path, exist_ok=True)

        # Сохраняем в конфиг
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        else:
            config = {}

        config['base_path'] = new_path

        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)

        print(f"\n{Fore.GREEN}✅ Путь успешно изменён!{Fore.RESET}")  # ← ИСПРАВЛЕНО!
        return True

    except Exception as e:
        print(f"{Fore.RED}❌ Ошибка при создании папки: {e}{Fore.RESET}")  # ← ИСПРАВЛЕНО!
        return False

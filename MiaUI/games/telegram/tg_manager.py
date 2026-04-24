# ╔═════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                       ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║
# ║  lang: python                                    ║
# ║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║
# ║  build:3.10.15                                   ║
# ║  files: tg_manager                               ║
# ╚═════════════════════════════╝

"""

TG MANAGER PANEL 2026 — PREMIUM EDITION

License — Usage Only

Copyright (c) 2007 𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍

All rights reserved.

Permission is granted to use this software only internally. 
Selling, redistribution, or publication without permission is prohibited.
"""

import os
import asyncio
import json
from telethon import TelegramClient, errors, events
from colorama import init, Fore, Style

init(autoreset=True)

# ===================== КОНСТАНТЫ =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
DB_FOLDER = os.path.join(BASE_DIR, "sessions_db")
TEST_DB_FOLDER = os.path.join(BASE_DIR, "sessions_test")

os.makedirs(DB_FOLDER, exist_ok=True)
os.makedirs(TEST_DB_FOLDER, exist_ok=True)

TEST_DC = {
    "id": 2,
    "ip": "149.154.167.40",
    "port": 443,
}

# ===================== ЦВЕТА =====================


class Colors:
    PINK = '\033[95m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    END = '\033[0m'
    BOLD = '\033[1m'


# ===================== БАННЕР =====================
BANNER = f"""
{Colors.PINK}╔════════════════════════════════════════════════════════════════╗
║                                                                    ║
║     {Colors.CYAN}████████╗ ██████╗     ███╗   ███╗ █████╗ ███╗   ██╗ █████╗  {Colors.PINK}   ║
║     {Colors.CYAN}╚══██╔══╝██╔════╝     ████╗ ████║██╔══██╗████╗  ██║██╔══██╗ {Colors.PINK}   ║
║     {Colors.CYAN}   ██║   ██║  ███╗    ██╔████╔██║███████║██╔██╗ ██║███████║ {Colors.PINK}   ║
║     {Colors.CYAN}   ██║   ██║   ██║    ██║╚██╔╝██║██╔══██║██║╚██╗██║██╔══██║ {Colors.PINK}   ║
║     {Colors.CYAN}   ██║   ╚██████╔╝    ██║ ╚═╝ ██║██║  ██║██║ ╚████║██║  ██║ {Colors.PINK}   ║
║     {Colors.CYAN}   ╚═╝    ╚═════╝     ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝ {Colors.PINK}   ║
║                                                                    ║
║              {Colors.MAGENTA}⚡ PREMIUM EDITION 2026 ⚡{Colors.PINK}                           ║
║              {Colors.GREEN}Author: 𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍 🌷{Colors.PINK}                         ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝{Colors.END}
"""

# ===================== ФУНКЦИИ =====================


def clear():
    """Очистка экрана"""
    os.system("clear" if os.name == "posix" else "cls")


def print_header(text):
    """Печать заголовка"""
    width = 60
    print(f"\n{Colors.CYAN}╔{'═' * width}╗{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.YELLOW}{text.center(width)}{Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}╚{'═' * width}╝{Colors.END}\n")


def wait_enter():
    """Ожидание нажатия Enter"""
    input(f"\n{Colors.CYAN}Нажмите Enter чтобы продолжить...{Colors.END}")

# -------------------------
# API CONFIG
# -------------------------


def load_or_create_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
    else:
        clear()
        print(BANNER)
        print_header("🔄 ПЕРВОНАЧАЛЬНАЯ НАСТРОЙКА")
        print(f"{Fore.YELLOW}Файл config.json не найден. Введите данные Telegram API.{Fore.END}\n")
        cfg = {}
        while True:
            try:
                cfg["API_ID"] = int(input(f"{Colors.CYAN}👉 Введите API_ID: {Colors.END}").strip())
                break
            except ValueError:
                print(f"{Colors.RED}❌ API_ID должен быть числом!{Colors.END}")
        cfg["API_HASH"] = input(f"{Colors.CYAN}👉 Введите API_HASH: {Colors.END}").strip()
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=4)
        print(f"\n{Colors.GREEN}✅ Конфигурация сохранена.{Colors.END}")
        wait_enter()
    return cfg


cfg = load_or_create_config()
API_ID = cfg.get("API_ID")
API_HASH = cfg.get("API_HASH")

# -------------------------
# UTILS
# -------------------------


def ask_server():
    print(f"{Colors.CYAN}\n📡 Выберите сервер:{Colors.END}")
    print(f"{Colors.WHITE}1. Обычный Telegram{Colors.END}")
    print(f"{Colors.YELLOW}2. Beta / Test Telegram{Colors.END}")
    return input(f"\n{Colors.PINK}👉 {Colors.END}").strip() == "2"


def get_folder(test):
    return TEST_DB_FOLDER if test else DB_FOLDER


async def create_client(path, test):
    client = TelegramClient(path, API_ID, API_HASH)
    if test:
        print(f"{Colors.YELLOW}→ Используется TEST Telegram DC{Colors.END}")
        client.session.set_dc(
            TEST_DC["id"],
            TEST_DC["ip"],
            TEST_DC["port"],
        )
        client.session.save()
    await client.connect()
    return client

# -------------------------
# ADD ACCOUNT
# -------------------------


async def add_account():
    clear()
    print(BANNER)
    print_header("➕ ДОБАВЛЕНИЕ НОВОГО АККАУНТА")

    test_mode = ask_server()
    name = input(f"\n{Colors.CYAN}📝 Введите имя сессии: {Colors.END}").strip()
    if not name:
        return
    folder = get_folder(test_mode)
    path = os.path.join(folder, name)
    try:
        client = await create_client(path, test_mode)
        await client.start()
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"\n{Colors.GREEN}✅ Аккаунт @{me.username or me.id} сохранён в {folder}{Colors.END}")
        await client.disconnect()
    except errors.PasswordHashInvalidError:
        print(f"\n{Colors.RED}❌ Неверный 2FA пароль.{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}⚠️ Ошибка: {e}{Colors.END}")
    wait_enter()

# -------------------------
# LIST ACCOUNTS
# -------------------------


async def list_accounts():
    clear()
    print(BANNER)
    print_header("📋 СПИСОК СЕССИЙ")

    test_mode = ask_server()
    folder = get_folder(test_mode)
    files = [f for f in os.listdir(folder) if f.endswith(".session")]

    if not files:
        print(f"\n{Colors.RED}📭 Пусто. Нет сохранённых сессий.{Colors.END}")
    else:
        print(f"\n{Colors.GREEN}Найдено сессий: {len(files)}{Colors.END}\n")
        for i, f in enumerate(files, 1):
            print(f"{Colors.CYAN}{i:2d}.{Colors.WHITE} {f.replace('.session', '')}{Colors.END}")

    wait_enter()

# -------------------------
# CHECK ACCOUNTS
# -------------------------


async def check_accounts():
    clear()
    print(BANNER)
    print_header("🔍 ПРОВЕРКА АККАУНТОВ")

    test_mode = ask_server()
    folder = get_folder(test_mode)
    files = [f for f in os.listdir(folder) if f.endswith(".session")]

    if not files:
        print(f"\n{Colors.RED}📭 Нет сессий для проверки.{Colors.END}")
    else:
        print(f"\n{Colors.GREEN}Проверка {len(files)} сессий...{Colors.END}\n")
        for f in files:
            name = f.replace(".session", "")
            path = os.path.join(folder, name)
            try:
                client = await create_client(path, test_mode)
                if await client.is_user_authorized():
                    print(f"{Colors.GREEN}✅ {name}: OK{Colors.END}")
                else:
                    print(f"{Colors.RED}❌ {name}: OFFLINE{Colors.END}")
                await client.disconnect()
            except Exception:
                print(f"{Colors.RED}❌ {name}: ERROR{Colors.END}")

    wait_enter()

# -------------------------
# LISTEN FOR CODES
# -------------------------


async def listen_for_code():
    clear()
    print(BANNER)
    print_header("📡 ПРОСЛУШКА TELEGRAM (777000)")

    test_mode = ask_server()
    folder = get_folder(test_mode)
    files = [f for f in os.listdir(folder) if f.endswith(".session")]

    if not files:
        print(f"\n{Colors.RED}📭 Нет сессий.{Colors.END}")
        wait_enter()
        return

    print(f"\n{Colors.GREEN}Доступные сессии:{Colors.END}\n")
    for i, f in enumerate(files, 1):
        print(f"{Colors.CYAN}{i:2d}.{Colors.WHITE} {f.replace('.session', '')}{Colors.END}")

    try:
        idx = int(input(f"\n{Colors.PINK}👉 Выберите номер: {Colors.END}")) - 1
        name = files[idx].replace(".session", "")
        path = os.path.join(folder, name)

        client = await create_client(path, test_mode)
        await client.start()

        clear()
        print(BANNER)
        print_header(f"📡 ПРОСЛУШКА: {name}")
        print(f"{Colors.GREEN}✅ Сессия активна!{Colors.END}")
        print(f"{Colors.YELLOW}📡 Жду сообщения от Telegram (777000)...{Colors.END}")
        print(f"{Colors.RED}⚠️  Ctrl+C для выхода{Colors.END}\n")

        @client.on(events.NewMessage(from_users=777000))
        async def handler(event):
            print(f"\n{Colors.CYAN}{'='*50}{Colors.END}")
            print(f"{Colors.GREEN}📩 TELEGRAM MESSAGE:{Colors.END}")
            print(f"{Colors.WHITE}{event.text}{Colors.END}")
            print(f"{Colors.CYAN}{'='*50}{Colors.END}\n")

        await client.run_until_disconnected()

    except IndexError:
        print(f"\n{Colors.RED}❌ Неверный номер!{Colors.END}")
        wait_enter()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\n{Colors.RED}⚠️ Ошибка: {e}{Colors.END}")
        wait_enter()

# -------------------------
# MAIN MENU
# -------------------------


async def main_menu():
    while True:
        clear()
        print(BANNER)

        print(f"\n{Colors.YELLOW}{Style.BRIGHT}            ❯❯❯  ГЛАВНОЕ МЕНЮ  ❮❮❮{Colors.END}\n")

        menu_items = [
            ("1", "➕ Добавить аккаунт", "Новая сессия Telegram"),
            ("2", "📋 Список сессий", "Показать все сохранённые"),
            ("3", "🔍 Проверить", "Статус аккаунтов"),
            ("4", "📡 Слушать Telegram", "Мониторинг 777000"),
            ("0", "🔙 Назад", "Вернуться в Telegram Tools"),
        ]

        for num, name, desc in menu_items:
            color = Colors.CYAN if num not in ["0"] else Colors.RED
            print(f"{color}  {num}. {name}{Colors.END}")
            print(f"{Colors.GREEN}     → {desc}{Colors.END}\n")

        choice = input(f"{Colors.PINK}👉 Введи номер: {Colors.END}").strip()

        if choice == "1":
            await add_account()
        elif choice == "2":
            await list_accounts()
        elif choice == "3":
            await check_accounts()
        elif choice == "4":
            await listen_for_code()
        elif choice == "0":
            print(f"\n{Colors.GREEN}🔙 Возвращаюсь...{Colors.END}")
            break
        else:
            print(f"\n{Colors.RED}❌ Неверный выбор!{Colors.END}")
            wait_enter()

# -------------------------
# ENTRY POINT
# -------------------------

if __name__ == "__main__":
    try:
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Выход по запросу...{Colors.END}")

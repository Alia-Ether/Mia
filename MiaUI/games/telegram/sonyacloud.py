# ╔═════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                       ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║
# ║  lang: python                                    ║
# ║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║
# ║  build:3.10.15                                   ║
# ║  files: sonyacloud.py                            ║
# ╚═════════════════════════════╝


"""SonyaCloud v2.0 — файловое облако на Telegram с выбором диалогов

Copyright (c) 2007-2026 𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍

All rights reserved.

Permission is granted to use this software only internally.
Selling, redistribution, or publication without permission is prohibited.
"""

import os
import asyncio
import json
from telethon import TelegramClient
from telethon.tl.types import (
    User, Chat, Channel
)
from colorama import init, Style

init(autoreset=True)

# ===================== ПУТИ =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

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
║     {Colors.CYAN}███████╗ ██████╗ ███╗   ██╗██╗   ██╗ █████╗  ██████╗██╗      {Colors.PINK} ║
║     {Colors.CYAN}██╔════╝██╔═══██╗████╗  ██║╚██╗ ██╔╝██╔══██╗██╔════╝██║      {Colors.PINK} ║
║     {Colors.CYAN}███████╗██║   ██║██╔██╗ ██║ ╚████╔╝ ███████║██║     ██║      {Colors.PINK} ║
║     {Colors.CYAN}╚════██║██║   ██║██║╚██╗██║  ╚██╔╝  ██╔══██║██║     ██║      {Colors.PINK} ║
║     {Colors.CYAN}███████║╚██████╔╝██║ ╚████║   ██║   ██║  ██║╚██████╗███████╗ {Colors.PINK} ║
║     {Colors.CYAN}╚══════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝╚══════╝ {Colors.PINK} ║
║                                                                    ║
║              {Colors.MAGENTA}☁️  ОБЛАКО TELEGRAM v2.0  ☁️{Colors.PINK}                       ║
║              {Colors.GREEN}Author: 𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍 🌷{Colors.PINK}                         ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝{Colors.END}
"""

# ===================== ФУНКЦИИ UI =====================


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

# ===================== ЗАГРУЗКА КОНФИГА =====================


def load_config():
    """Загружает конфигурацию из config.json"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config
        except Exception:
            return {}
    return {}


def save_config(config):
    """Сохраняет конфигурацию"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)


def get_api_credentials():
    """Получает API ID и HASH из конфига или запрашивает"""
    config = load_config()

    if config.get('API_ID') and config.get('API_HASH'):
        return config['API_ID'], config['API_HASH']

    clear()
    print(BANNER)
    print_header("🔄 ПЕРВОНАЧАЛЬНАЯ НАСТРОЙКА")

    print(f"{Colors.YELLOW}Для работы SonyaCloud нужны API данные Telegram{Colors.END}\n")
    print(f"{Colors.CYAN}Получить их можно на my.telegram.org{Colors.END}\n")

    while True:
        try:
            api_id = int(input(f"{Colors.GREEN}👉 Введите API_ID: {Colors.END}").strip())
            break
        except ValueError:
            print(f"{Colors.RED}❌ API_ID должен быть числом!{Colors.END}")

    api_hash = input(f"{Colors.GREEN}👉 Введите API_HASH: {Colors.END}").strip()

    config['API_ID'] = api_id
    config['API_HASH'] = api_hash
    save_config(config)

    print(f"\n{Colors.GREEN}✅ Данные сохранены в config.json{Colors.END}")
    wait_enter()

    return api_id, api_hash


def get_base_path():
    """Получает путь сохранения из конфига или использует умолчание"""
    config = load_config()
    return config.get('base_path', "/storage/emulated/0/Alarms")


def set_base_path(new_path):
    """Устанавливает новый путь сохранения"""
    config = load_config()
    config['base_path'] = new_path
    save_config(config)


def get_selected_dialog():
    """Получает ID выбранного диалога из конфига"""
    config = load_config()
    return config.get('selected_dialog', "@hikka_q2uthl_bot")


def set_selected_dialog(dialog_id):
    """Устанавливает ID выбранного диалога"""
    config = load_config()
    config['selected_dialog'] = dialog_id
    save_config(config)


# ===================== НАСТРОЙКИ =====================
API_ID, API_HASH = get_api_credentials()
CHAT_ID = get_selected_dialog()
BASE_PATH = get_base_path()
PER_PAGE = 10

# ===================== КЛИЕНТ =====================
SESSION_FILE = os.path.join(BASE_DIR, "sonya_session")
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# ===================== КАТЕГОРИИ =====================
CATEGORIES = {
    "1": ("Приложения", "Applications", ".apk"),
    "2": ("Изображения", "Images", (".jpg", ".png", ".jpeg", ".webp", ".gif")),
    "3": ("Видео", "Video", (".mp4", ".mkv", ".avi", ".mov")),
    "4": ("Музыка", "Music", (".mp3", ".wav", ".ogg", ".flac")),
    "5": ("Архивы", "Archives", (".zip", ".rar", ".7z", ".tar")),
    "6": ("Документы", "Documents", (".pdf", ".txt", ".doc", ".docx")),
    "7": ("Прочие", "Other", None),
}

# ===================== ЛОГОТИП =====================


def print_logo():
    """Печатает ASCII-логотип"""
    pink = "\033[95m"
    reset = "\033[0m"

    ascii_art = r"""
♡                                                          𝕔𝕦𝕥𝕖𝕤𝕪
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⠿⠛⠿⣦⣄⣠⣶⠿⠟⠉⠉⠙⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣴⡟⠁⠀⠀⠀⠈⢿⣯⠁⠀⠀⠀⠀⠀⠘⣿⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣰⣿⠛⠛⠻⠿⢶⣶⣄⣠⣤⣶⠶⠾⠿⠛⢻⣿⠀⠀⢠⣶⠷⣶⣾⡿⠿⢶⣦⣤⣴⡶⠶⢿⣷⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣿⠃⠀⠀⠀⠀⠀⠈⠙⠋⠉⠀⠀⠀⠀⠀⢸⣿⠀⠀⠸⣧⣰⡿⠃⠀⠀⠀⠙⣿⣇⡀⠀⠀⢹⣷⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣄⡀⠀⠙⣿⣇⠀⠀⠀⠀⢀⣿⠏⣷⠀⠀⢸⡿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣿⣇⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠻⠷⠞⠛⢻⣧⣤⣤⣴⡾⠿⠴⠋⠀⢠⣿⣧⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠘⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠹⣷⣄⣀⣠⣼⡿⠁⢿⣧⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢠⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠛⠛⠁⠀⠀⠀⣿⣦⠀⣀⣀⣀
⠀⠀⠀⠀⣼⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡶⢿⣿⠛⠛⠛⠋
⠀⠀⠀⠀⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠀⠀⠀⠀⢠⣿⡀⠀⠀⠀
⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⢠⣀⣠⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⠿⠿⣶⠟⠀⣀⣀⠘⢻⣿⠛⠛⠛⠃
⣠⣤⣴⠶⣿⡷⠚⠻⠧⠀⠀⠀⠹⣿⣿⣷⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⠀⠀⠀⠀⠙⠃⠀⠀⠉⠀⡼⣻⣻⢿⠿⣿⣆⠀⠀⠀
⠙⠉⠀⠀⠘⣿⡀⢀⣀⡀⠀⠀⠀⠘⠿⠋⠀⠀⠀⠀⠀⠀⣿⡉⣉⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⣸⢣⡏⢹⠛⠓⢒⣿⣤⣄⠀
⠀⠀⠀⣀⣠⣿⣿⡟⠉⠁⠀⠀⠀⠀⠀⠀⢀⣀⣀⡀⠀⠀⠉⠉⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⢰⣏⡿⠀⢻⣿⠄⣾⠁⠈⠉⠀
⠀⠀⠀⠛⠁⠀⠘⢿⣦⣠⡼⠆⠀⠀⠀⢠⣿⠋⠛⠿⠿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡟⡽⠁⢀⣨⣧⣴⠻⣧⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣤⡿⠛⠿⣶⣤⣄⣠⣾⠟⠀⠀⠀⠀⠈⣿⣀⣀⣀⣀⣀⣀⣤⣴⣶⢿⡿⣸⠃⣰⡿⠋⠉⠁⣾⡟⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠻⠏⠀⠀⠀⠀⠈⢹⡿⠃⠀⠀⠀⠀⠀⣸⡿⠛⠛⠛⢉⡿⠋⠉⢹⣧⣸⣷⡏⢸⡏⠀⠀⠀⠀⣿⠇⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢾⣇⠀⠀⠀⢀⣠⣾⠿⠷⠦⠴⠾⠛⠁⠀⠀⠀⢻⣏⠛⠓⠚⢿⣦⠀⣠⣾⠟⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⣿⣿⣿⣟⠛⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣷⣶⣤⣤⠾⠟⠛⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⡿⠋⠀⠀⠉⣹⡿⠛⠓⠲⠦⠤⠤⠤⠶⠶⢾⣟⠉⠉⠻⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⠏⠀⠀⠀⠀⠘⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠃⠀⠀⠈⢿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢿⣶⣤⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣼⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢹⣟⠛⠿⠿⠶⠶⣶⣶⣶⣶⣶⣴⣶⣶⣶⠶⠶⠶⠿⠟⢿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠶⢤⣤⣤⣀⣀⣀⣄⣼⣿⣤⣀⣀⣀⣀⣀⣤⠤⢶⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣆⠀⠀⠀⠀⠈⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⢀⣼⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣷⣦⣀⣀⣀⣀⣠⣾⣿⣤⣀⣀⣀⣀⣠⠛⠛⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠙⠛⠛⠛⠉⠁⠀⠉⠙⠛⠛⠛⠛⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀♡
"""
    print(pink + ascii_art + reset)
    print("")

# ===================== ВЫБОР ДИАЛОГА =====================


async def choose_dialog():
    """Позволяет пользователю выбрать диалог из списка"""
    clear()
    print(BANNER)
    print_logo()
    print_header("📋 ВЫБОР ДИАЛОГА")

    print(f"{Colors.CYAN}Получаю список диалогов...{Colors.END}\n")

    dialogs = await client.get_dialogs()
    dialog_list = []

    for i, dialog in enumerate(dialogs[:20], 1):  # Покажем первые 20
        entity = dialog.entity

        if isinstance(entity, User):
            name = f"{entity.first_name or ''} {entity.last_name or ''}".strip()
            if not name:
                name = entity.username or f"User {entity.id}"
            emoji = "👤"
            chat_id = entity.id
        elif isinstance(entity, Chat):
            name = entity.title or f"Chat {entity.id}"
            emoji = "👥"
            chat_id = entity.id
        elif isinstance(entity, Channel):
            name = entity.title or f"Channel {entity.id}"
            emoji = "📢"
            chat_id = entity.username or entity.id
        else:
            name = f"Dialog {entity.id}"
            emoji = "💬"
            chat_id = entity.id

        dialog_list.append({
            'id': chat_id,
            'name': name,
            'emoji': emoji,
            'entity': entity
        })

        print(f"{Colors.CYAN}{i:2d}.{Colors.END} {emoji} {Colors.WHITE}{name}{Colors.END}")

    print(f"\n{Colors.YELLOW}0. Отмена{Colors.END}")

    try:
        choice = int(input(f"\n{Colors.PINK}👉 Выберите диалог: {Colors.END}").strip())
        if 1 <= choice <= len(dialog_list):
            selected = dialog_list[choice-1]

            # Определяем ID для сохранения
            if isinstance(selected['entity'], Channel) and selected['entity'].username:
                dialog_id = f"@{selected['entity'].username}"
            else:
                dialog_id = str(selected['id'])

            set_selected_dialog(dialog_id)

            print(f"\n{Colors.GREEN}✅ Выбран: {selected['emoji']} {selected['name']}{Colors.END}")
            print(f"{Colors.CYAN}ID: {dialog_id}{Colors.END}")
            wait_enter()
            return dialog_id
        else:
            return None
    except ValueError:
        return None

# ===================== ИЗМЕНЕНИЕ ПУТИ =====================


def change_base_path_menu():
    """Меню изменения пути сохранения"""
    clear()
    print(BANNER)
    print_logo()
    print_header("📁 ИЗМЕНЕНИЕ ПУТИ СОХРАНЕНИЯ")

    current = get_base_path()
    print(f"{Colors.GREEN}Текущий путь:{Colors.END} {Colors.WHITE}{current}{Colors.END}\n")

    print(f"{Colors.CYAN}Примеры:{Colors.END}")
    print(f"  • /storage/emulated/0/Download")
    print(f"  • /storage/emulated/0/Alarms")
    print(f"  • /storage/emulated/0/DCIM")
    print(f"  • /sdcard/VortexCloud\n")

    new_path = input(f"{Colors.PINK}👉 Введите новый путь (Enter = отмена): {Colors.END}").strip()

    if new_path and new_path != current:
        try:
            os.makedirs(new_path, exist_ok=True)
            set_base_path(new_path)
            print(f"\n{Colors.GREEN}✅ Путь изменён на:{Colors.END}")
            print(f"{Colors.WHITE}{new_path}{Colors.END}")
        except Exception as e:
            print(f"\n{Colors.RED}❌ Ошибка: {e}{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}⚠️ Путь не изменён{Colors.END}")

    wait_enter()
    return get_base_path()

# ===================== СБОР ФАЙЛОВ =====================


async def collect_all_files(chat_id):
    """Собирает все файлы из выбранного Telegram чата"""
    files = {k: [] for k in CATEGORIES}

    print(f"{Colors.CYAN}📂 Сканирую {chat_id}...{Colors.END}")

    try:
        async for msg in client.iter_messages(
            chat_id,
            reverse=True,
            limit=None
        ):
            if not (msg.file or msg.photo):
                continue

            if msg.photo:
                files["2"].append({
                    "msg": msg,
                    "name": f"photo_{msg.id}.jpg"
                })
                continue

            name = msg.file.name or f"file_{msg.id}"
            ext = name.lower()

            obj = {"msg": msg, "name": name}

            added = False

            for key, (_, _, exts) in CATEGORIES.items():
                if isinstance(exts, tuple) and ext.endswith(exts):
                    files[key].append(obj)
                    added = True
                    break

                if exts == ".apk" and ext.endswith(".apk"):
                    files[key].append(obj)
                    added = True
                    break

            if not added:
                files["7"].append(obj)

        total = sum(len(v) for v in files.values())
        print(f"{Colors.GREEN}✅ Найдено файлов: {total}{Colors.END}")
        return files

    except Exception as e:
        print(f"{Colors.RED}❌ Ошибка сканирования: {e}{Colors.END}")
        wait_enter()
        return None

# ===================== ЗАГРУЗКА =====================


async def download_file(msg, name, folder):
    """Скачивает файл"""
    path_dir = os.path.join(BASE_PATH, folder)
    os.makedirs(path_dir, exist_ok=True)

    path = os.path.join(path_dir, name)

    if os.path.exists(path):
        print(f"{Colors.YELLOW}⚠ Такой файл уже существует — отменено.{Colors.END}")
        return

    print(f"\n{Colors.CYAN}⬇ Скачивание: {name}{Colors.END}")

    await client.download_media(msg, file=path)

    print(f"{Colors.GREEN}✅ Готово: {path}{Colors.END}")

# ===================== ПРОСМОТР =====================


async def browse_category(key, items):
    """Просмотр файлов в категории"""
    if not items:
        print(f"{Colors.YELLOW}📭 В этой категории нет файлов.{Colors.END}")
        wait_enter()
        return

    page = 0

    while True:
        clear()
        print(BANNER)
        print_logo()
        print_header(f"📁 {CATEGORIES[key][0]}")

        start = page * PER_PAGE
        end = start + PER_PAGE
        chunk = items[start:end]

        total_pages = (len(items) - 1) // PER_PAGE + 1

        print(f"\n{Colors.CYAN}📄 Страница {page+1}/{total_pages}{Colors.END}\n")

        for i, f in enumerate(chunk, start=1):
            # Обрезаем длинные имена
            name = f['name']
            if len(name) > 50:
                name = name[:47] + "..."
            print(f"{Colors.GREEN}[{i}]{Colors.WHITE} {name}{Colors.END}")

        print(f"\n{Colors.YELLOW} n — далее | p — назад | 0 — назад{Colors.END}")

        choice = input(f"\n{Colors.PINK}👉 Выбор: {Colors.END}").strip()

        if choice == "n" and page + 1 < total_pages:
            page += 1
            continue

        if choice == "p" and page > 0:
            page -= 1
            continue

        if choice == "0":
            return

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(chunk):
                f = chunk[idx]
                folder = CATEGORIES[key][1]
                await download_file(f["msg"], f["name"], folder)
                wait_enter()
        else:
            print(f"{Colors.RED}❌ Неверный ввод.{Colors.END}")
            wait_enter()

# ===================== МЕНЮ =====================


def print_menu(current_dialog, current_path):
    """Печатает меню"""
    print(f"\n{Colors.YELLOW}{Style.BOLD}========== SONYACLOUD v2.0 =========={Colors.END}\n")

    print(f"{Colors.CYAN}📌 Текущий диалог:{Colors.END} {Colors.WHITE}{current_dialog}{Colors.END}")
    print(f"{Colors.CYAN}📁 Путь сохранения:{Colors.END} {Colors.WHITE}{current_path}{Colors.END}\n")

    for k, (name, _, _) in CATEGORIES.items():
        print(f"{Colors.CYAN}{k}.{Colors.WHITE} {name}{Colors.END}")

    print(f"\n{Colors.MAGENTA}s.{Colors.WHITE} 🔄 Сменить диалог{Colors.END}")
    print(f"{Colors.MAGENTA}p.{Colors.WHITE} 📁 Изменить путь{Colors.END}")
    print(f"{Colors.RED}0. Выход{Colors.END}")

# ===================== MAIN =====================


async def main():
    """Главная функция"""
    global BASE_PATH, CHAT_ID

    clear()
    print(BANNER)
    print_logo()

    print(f"{Colors.CYAN}📡 Подключаюсь к Telegram...{Colors.END}")
    await client.start()

    me = await client.get_me()
    print(f"{Colors.GREEN}✅ Подключено как: @{me.username or me.id}{Colors.END}")

    # Обновляем значения из конфига
    BASE_PATH = get_base_path()
    CHAT_ID = get_selected_dialog()

    print(f"{Colors.CYAN}📌 Текущий диалог: {CHAT_ID}{Colors.END}")
    print(f"{Colors.CYAN}📁 Путь: {BASE_PATH}{Colors.END}\n")

    # Сразу сканируем выбранный диалог
    files = await collect_all_files(CHAT_ID)
    if files is None:
        return

    wait_enter()

    while True:
        clear()
        print(BANNER)
        print_logo()
        print_menu(CHAT_ID, BASE_PATH)

        choice = input(f"\n{Colors.PINK}👉 Выбор: {Colors.END}").strip().lower()

        if choice == "0":
            break

        elif choice == "s":
            new_dialog = await choose_dialog()
            if new_dialog:
                CHAT_ID = new_dialog
                files = await collect_all_files(CHAT_ID)

        elif choice == "p":
            new_path = change_base_path_menu()
            if new_path:
                BASE_PATH = new_path

        elif choice in CATEGORIES:
            if files and choice in files:
                await browse_category(choice, files[choice])
            else:
                print(f"{Colors.RED}❌ Нет файлов в этой категории{Colors.END}")
                wait_enter()
        else:
            print(f"{Colors.RED}❌ Неверный выбор{Colors.END}")
            wait_enter()

# ===================== СТАРТ =====================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Выход по запросу...{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Ошибка: {e}{Colors.END}")
        wait_enter()

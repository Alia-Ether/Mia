# ╔═════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                       ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║
# ║  lang: python                                    ║
# ║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║
# ║  build:3.10.15                                   ║
# ║  files: bot.py                                   ║
# ╚═════════════════════════════╝


import asyncio
import sys
import os
import platform
import socket
import json
from datetime import datetime
from typing import Dict, Any

# ==================== КОНСТАНТЫ ====================
VERSION = "1.0.2026"
AUTHOR = "Alia Ether 🌷"
PRICE = "$5,000 REAL 💰"

# Данные админа
ADMIN_ID = 8174117949  # @FrontendVSCode
ADMIN_USERNAME = "FrontendVSCode"

# Токен бота (тот же, что и в Telegram боте)
BOT_TOKEN = "8067456520:AAFxNiatgZCBpYQe_XZ0PMqEvgyCX382qcE"

# Цвета для терминала
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RED = '\033[91m'
CYAN = '\033[96m'
WHITE = '\033[97m'  # Добавлен отсутствующий цвет
BOLD = '\033[1m'
END = '\033[0m'

# ==================== ФУНКЦИЯ ДЛЯ ЭКРАНИРОВАНИЯ MARKDOWN ====================


def escape_markdown(text):
    """Экранирует специальные символы Markdown"""
    if not text:
        return ""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

# ==================== КЛАСС ДЛЯ СБОРА ДАННЫХ ====================


class SupportData:
    def __init__(self):
        self.problem = ""
        self.tried = ""
        self.logs = ""
        self.contact = ""
        self.system_info = self.get_system_info()
        self.timestamp = datetime.now().isoformat()

    def get_system_info(self) -> Dict[str, str]:
        """Собирает информацию о системе"""
        info = {
            'platform': platform.platform(),
            'python': sys.version,
            'hostname': socket.gethostname(),
            'cwd': os.getcwd(),
            'user': os.environ.get('USER', 'unknown'),
            'termux': self.check_termux()
        }

        # Пытаемся получить больше информации
        try:
            # Версия ОС
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('PRETTY_NAME='):
                            info['os'] = line.split('=')[1].strip().strip('"')
                            break
        except Exception:
            info['os'] = 'unknown'

        return info

    def check_termux(self) -> str:
        """Проверяет, запущено ли в Termux"""
        if 'com.termux' in os.environ.get('PREFIX', ''):
            return "Да (Termux)"
        return "Нет"

    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует в словарь для отправки"""
        return {
            'problem': self.problem,
            'tried': self.tried,
            'logs': self.logs,
            'contact': self.contact,
            'system': self.system_info,
            'timestamp': self.timestamp
        }

    def format_for_admin(self) -> str:
        """Форматирует данные для отправки админу (с экранированием)"""
        text = f"""
📬 НОВОЕ ОБРАЩЕНИЕ В ПОДДЕРЖКУ (ИЗ TERMUX)

👤 Контакт: {escape_markdown(self.contact or 'Не указан')}

❓ Проблема:
{escape_markdown(self.problem)}

🔧 Что пробовал:
{escape_markdown(self.tried)}

📋 Логи / Доп. информация:
{escape_markdown(self.logs or 'Не предоставлено')}

🖥️ Система:
• Платформа: {escape_markdown(self.system_info['platform'])}
• Python: {escape_markdown(self.system_info['python'][:50])}...
• Termux: {escape_markdown(self.system_info['termux'])}
• Директория: {escape_markdown(self.system_info['cwd'])}

⏱️ Время: {self.timestamp}
"""
        return text

# ==================== ФУНКЦИИ ДЛЯ РАБОТЫ С TELEGRAM ====================


async def send_to_admin(data: SupportData):
    """Отправляет данные админу через Telegram"""
    from aiogram import Bot

    bot = Bot(token=BOT_TOKEN)

    try:
        # Формируем сообщение
        text = data.format_for_admin()

        # Отправляем без Markdown, чтобы избежать ошибок
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=text,
            parse_mode=None  # Убрал Markdown, чтобы избежать ошибок парсинга
        )

        print(f"\n{GREEN}✅ Данные отправлены админу @{ADMIN_USERNAME}{END}")
        return True

    except Exception as e:
        print(f"\n{RED}❌ Ошибка отправки: {e}{END}")

        # Пробуем отправить частями
        try:
            text = data.format_for_admin()
            parts = [text[i:i+4000] for i in range(0, len(text), 4000)]

            for i, part in enumerate(parts):
                await bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"📦 Часть {i+1}/{len(parts)}:\n\n{part}",
                    parse_mode=None
                )

            print(f"\n{GREEN}✅ Данные отправлены частями{END}")
            return True
        except Exception as e2:
            print(f"\n{RED}❌ Не удалось отправить: {e2}{END}")
            print(f"{YELLOW}👉 Отправьте любое сообщение боту от @{ADMIN_USERNAME}{END}")
            return False
    finally:
        await bot.session.close()

# ==================== ФУНКЦИИ ВВОДА В TERMINAL ====================


def clear_screen():
    """Очищает экран терминала"""
    os.system('clear' if os.name == 'posix' else 'cls')


def print_header():
    """Выводит шапку программы"""
    clear_screen()
    print(f"{BOLD}{CYAN}{'='*60}{END}")
    print(f"{BOLD}{CYAN}🔧 TERMINAL SUPPORT BOT v{VERSION}{END}")
    print(f"{BOLD}{CYAN}👤 Author: {AUTHOR}{END}")
    print(f"{BOLD}{CYAN}{'='*60}{END}")
    print()


def print_welcome():
    """Выводит приветственное сообщение"""
    welcome = f"""
{GREEN}🔧 Добро пожаловать в поддержку Support!{END}

Если у тебя возникли вопросы, ошибки или нужна помощь — просто заполни форму ниже.

{YELLOW}Пожалуйста, укажи:{END}

{BLUE}1. Твою проблему (как можно подробнее){END}
{BLUE}2. Что ты уже пробовал сделать{END}
{BLUE}3. Логи или дополнительная информация{END}
{BLUE}4. Контакт для связи (email/tg/phone){END}

{WHITE}📩 После заполнения данные отправятся админу @{ADMIN_USERNAME}{END}
{WHITE}Спасибо за обращение!{END}

{'-'*60}
"""
    print(welcome)


def get_multiline_input(prompt: str, min_lines: int = 1) -> str:
    """Получает многострочный ввод от пользователя"""
    print(f"\n{YELLOW}{prompt}{END}")
    print(f"{CYAN}(Введи текст, для завершения введи пустую строку){END}")

    lines = []
    while True:
        line = input(f"{GREEN}>>> {END}")
        if not line and lines:  # Пустая строка и уже есть текст
            break
        elif not line and not lines:  # Пустая строка в начале
            continue
        lines.append(line)

    return '\n'.join(lines)


def get_single_input(prompt: str) -> str:
    """Получает однострочный ввод"""
    return input(f"{YELLOW}{prompt}{END} ")


def collect_support_data() -> SupportData:
    """Собирает данные от пользователя"""
    data = SupportData()

    print_header()
    print_welcome()

    # 1. Проблема
    data.problem = get_multiline_input("1️⃣ Опиши проблему подробно:")

    # 2. Что пробовал
    data.tried = get_multiline_input("2️⃣ Что ты уже пробовал сделать?")

    # 3. Логи
    print(f"\n{YELLOW}3️⃣ Логи или дополнительная информация{END}")
    print(f"{CYAN}(Можно вставить текст логов или описать подробнее){END}")
    data.logs = get_multiline_input("")

    # 4. Контакт
    data.contact = get_single_input("4️⃣ Контакт для связи (tg/email/phone):")

    return data


def show_summary(data: SupportData):
    """Показывает сводку собранных данных"""
    print(f"\n{BLUE}{'='*60}{END}")
    print(f"{BOLD}{GREEN}📋 СВОДКА ДАННЫХ:{END}")
    print(f"{BLUE}{'='*60}{END}")

    print(f"\n{YELLOW}1. Проблема:{END}")
    print(f"   {data.problem}")

    print(f"\n{YELLOW}2. Что пробовал:{END}")
    print(f"   {data.tried}")

    print(f"\n{YELLOW}3. Логи:{END}")
    print(f"   {data.logs[:200]}{'...' if len(data.logs) > 200 else ''}")

    print(f"\n{YELLOW}4. Контакт:{END}")
    print(f"   {data.contact or 'Не указан'}")

    print(f"\n{BLUE}{'='*60}{END}")

# ==================== ОСНОВНАЯ ФУНКЦИЯ ====================


async def main():
    """Главная функция"""

    print_header()

    # Показываем информацию о боте
    print(f"{BOLD}{GREEN}💰 Цена скрипта: {PRICE}{END}")
    print(f"{BOLD}{BLUE}👤 Админ: @{ADMIN_USERNAME}{END}")
    print()

    # Собираем данные
    data = collect_support_data()

    # Показываем сводку
    show_summary(data)

    # Спрашиваем подтверждение
    print(f"\n{YELLOW}Отправить эти данные админу?{END}")
    confirm = input(f"{GREEN}(y/n): {END}").lower()

    if confirm == 'y':
        print(f"\n{CYAN}📤 Отправка данных...{END}")

        # Отправляем админу
        success = await send_to_admin(data)

        if success:
            print(f"\n{GREEN}✅ Готово! Админ ответит в ближайшее время.{END}")

            # Сохраняем локальную копию
            try:
                filename = f"support_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data.to_dict(), f, indent=2, ensure_ascii=False)
                print(f"{CYAN}📁 Локальная копия сохранена: {filename}{END}")
            except Exception as e:
                print(f"{RED}❌ Не удалось сохранить локальную копию: {e}{END}")
    else:
        print(f"\n{YELLOW}❌ Отправка отменена{END}")

        # Сохраняем черновик
        try:
            filename = f"support_draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data.to_dict(), f, indent=2, ensure_ascii=False)
            print(f"{CYAN}📁 Черновик сохранён: {filename}{END}")
        except Exception as e:
            print(f"{RED}❌ Не удалось сохранить черновик: {e}{END}")

    print(f"\n{GREEN}Нажми Enter для выхода...{END}")
    input()

# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}\n👋 Выход...{END}")
    except Exception as e:
        print(f"\n{RED}❌ Ошибка: {e}{END}")

        # Отправляем ошибку автоматически
        print(f"\n{CYAN}📤 Отправка отчёта об ошибке...{END}")

        error_data = SupportData()
        error_data.problem = f"Критическая ошибка в скрипте: {e}"
        error_data.tried = "Запустил скрипт, получил ошибку"
        error_data.logs = str(e)
        error_data.contact = "auto_report"

        try:
            asyncio.run(send_to_admin(error_data))
        except Exception:
            print(f"{RED}❌ Не удалось отправить отчёт об ошибке{END}")

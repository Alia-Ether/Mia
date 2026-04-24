# ╔═════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                       ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║
# ║  lang: python                                    ║
# ║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║
# ║  build:3.10.15                                   ║
# ║  files: main.py                                  ║
# ╚═════════════════════════════╝


import pin_manager
import os
import sys
import time
from colorama import init, Style

# Инициализация Colorama
init(autoreset=True)

# Импорт менеджера PIN-кода

# ===================== КОНСТАНТЫ =====================
PER_PAGE = 10

# Цвета для красоты


class Colors:
    PINK = '\033[95m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


# ===================== ПРЕДУПРЕЖДЕНИЕ =====================
ETHICAL_WARNING = f"""
{Colors.RED}{Style.BRIGHT}╔════════════════════════════════════════════════════════════════╗
║                     ⚠️  ЭТИЧНОЕ ИСПОЛЬЗОВАНИЕ  ⚠️                 ║
╠════════════════════════════════════════════════════════════════╣
║  Все инструменты в этом меню предназначены ТОЛЬКО для:        ║
║  ✅ Ваших СОБСТВЕННЫХ аккаунтов Telegram                      ║
║  ✅ Образовательных целей                                      ║
║  ✅ Исследований безопасности                                  ║
║                                                                ║
║  ❌ ЗАПРЕЩЕНО использовать для:                                ║
║  • Чужих аккаунтов без разрешения                             ║
║  • Кражи данных или подарков                                   ║
║  • Мошенничества или обмана                                    ║
║  • Любых противоправных действий                               ║
║                                                                ║
║  Используя эти инструменты, вы принимаете:                     ║
║  • Полную ответственность за свои действия                     ║
║  • Обязательство соблюдать законы вашей страны                 ║
║  • Условия использования Telegram                              ║
║                                                                ║
║  Автор не несёт ответственности за неправомерное              ║
║  использование данных инструментов.                            ║
╚════════════════════════════════════════════════════════════════╝{Colors.END}
"""

# ===================== БАННЕР =====================
BANNER = f"""
{Colors.PINK}╔════════════════════════════════════════════════════════════════╗
║                                                                    ║
║     {Colors.CYAN}████████╗███████╗██╗     ███████╗ ██████╗ ██████╗  █████╗ {Colors.PINK}    ║
║     {Colors.CYAN}╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝ ██╔══██╗██╔══██╗{Colors.PINK}    ║
║     {Colors.CYAN}   ██║   █████╗  ██║     █████╗  ██║  ███╗██████╔╝███████║{Colors.PINK}    ║
║     {Colors.CYAN}   ██║   ██╔══╝  ██║     ██╔══╝  ██║   ██║██╔══██╗██╔══██║{Colors.PINK}    ║
║     {Colors.CYAN}   ██║   ███████╗███████╗███████╗╚██████╔╝██║  ██║██║  ██║{Colors.PINK}    ║
║     {Colors.CYAN}   ╚═╝   ╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝{Colors.PINK}    ║
║                                                                    ║
║              {Colors.MAGENTA}☁️  TELEGRAM TOOLS v2.0  ☁️{Colors.PINK}                         ║
║         {Colors.GREEN}Author: 𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍 🌷 @FrontendVSCode{Colors.PINK}                ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝{Colors.END}
"""

# ===================== ПРИНЯТИЕ ЭТИЧЕСКИХ УСЛОВИЙ =====================


def accept_ethical_terms():
    """Показывает предупреждение и запрашивает подтверждение"""
    clear()
    print(BANNER)
    print(ETHICAL_WARNING)
    print(f"\n{Colors.YELLOW}Для продолжения работы необходимо принять условия этичного использования.{Colors.END}\n")

    choice = input(
        f"{Colors.GREEN}Я принимаю условия и обязуюсь использовать инструменты только этично (y/n): {Colors.END}").strip().lower()

    if choice in ['y', 'yes', 'д', 'да']:
        print(f"\n{Colors.GREEN}✅ Условия приняты. Загрузка...{Colors.END}")
        time.sleep(1)
        return True
    else:
        print(f"\n{Colors.RED}❌ Вы не приняли условия. Выход в главное меню.{Colors.END}")
        time.sleep(2)
        return False

# ===================== УТИЛИТЫ =====================


def clear():
    """Очистка экрана"""
    os.system("clear" if os.name == "posix" else "cls")


def print_slow(text, delay=0.03):
    """Печать с задержкой (как Соня)"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def wait_enter():
    """Ожидание нажатия Enter"""
    input(f"\n{Colors.CYAN}Нажмите Enter чтобы продолжить...{Colors.END}")

# ===================== ПРОВЕРКА PIN БЕЗ ПОТОКОВ =====================


def check_pin_simple():
    """Быстрая проверка PIN без потоков (не зависает)"""
    try:
        if pin_manager.is_first_run():
            print(f"{Colors.YELLOW}⚙️ Первый запуск — настройка PIN...{Colors.END}")
            time.sleep(1)
            return pin_manager.create_pin()
        else:
            return pin_manager.check_pin()
    except Exception as e:
        print(f"{Colors.RED}❌ Ошибка PIN: {e}{Colors.END}")
        wait_enter()
        return False

# ===================== ИМПОРТЫ МОДУЛЕЙ (ЛАЗИ) =====================


def load_sonyacloud():
    """Ленивая загрузка модуля SonyaCloud"""
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        import sonyacloud
        return sonyacloud
    except ImportError:
        return None


def load_session_manager():
    """Ленивая загрузка менеджера сессий"""
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        import tg_manager
        return tg_manager
    except ImportError:
        return None


def load_gift_bot():
    """Ленивая загрузка Gift Bot (NFT)"""
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        import gift_bot
        return gift_bot
    except ImportError:
        return None

# ===================== НАСТРОЙКИ =====================


def settings_menu():
    """Меню настроек"""
    while True:
        clear()
        print(BANNER)
        print(f"\n{Colors.YELLOW}{Style.BRIGHT}            ❯❯❯  НАСТРОЙКИ  ❮❮❮{Colors.END}\n")

        current_path = pin_manager.get_base_path()
        print(f"{Colors.CYAN}📁 Текущий путь сохранения:{Colors.END}")
        print(f"{Colors.GREEN}   {current_path}{Colors.END}\n")

        print(f"{Colors.MAGENTA}  1. Изменить путь сохранения{Colors.END}")
        print(f"{Colors.RED}   0. Назад в меню{Colors.END}\n")

        choice = input(f"{Colors.PINK}👉 Введи номер: {Colors.END}").strip()

        if choice == "1":
            pin_manager.change_base_path()
            wait_enter()
        elif choice == "0":
            break
        else:
            print(f"{Colors.RED}❌ Неверный выбор!{Colors.END}")
            wait_enter()

# ===================== ОСНОВНОЕ МЕНЮ =====================


def show_menu():
    """Отображение главного меню"""
    clear()
    print(BANNER)
    print(f"\n{Colors.YELLOW}{Style.BRIGHT}            ❯❯❯  ВЫБЕРИ ДЕЙСТВИЕ  ❮❮❮{Colors.END}\n")

    menu_items = [
        ("1", "☁️  SonyaCloud", "Файловое облако на Telegram"),
        ("2", "📱  Менеджер сессий", "Управление Telegram аккаунтами"),
        ("3", "🎁  Gift Bot (NFT)", "Управление подарками и звёздами"),
        ("4", "⚙️  Настройки", "Изменить путь сохранения"),
        ("0", "🔙  Назад", "Вернуться в Games Tools"),
    ]

    for num, name, desc in menu_items:
        color = Colors.CYAN if num not in ["0", "4"] else Colors.RED if num == "0" else Colors.YELLOW
        print(f"{color}  {num}. {name}{Colors.END}")
        print(f"{Colors.GREEN}     → {desc}{Colors.END}\n")

# ===================== ЗАПУСК МОДУЛЕЙ =====================


def run_sonyacloud():
    """Запуск SonyaCloud"""
    print(f"{Colors.GREEN}✅ Загружаю SonyaCloud...{Colors.END}")
    sonyacloud = load_sonyacloud()
    if sonyacloud:
        clear()
        if hasattr(sonyacloud, 'BASE_PATH'):
            sonyacloud.BASE_PATH = pin_manager.get_base_path()

        if hasattr(sonyacloud, 'main'):
            import asyncio
            asyncio.run(sonyacloud.main())
        else:
            print(f"{Colors.RED}❌ В sonyacloud.py нет функции main(){Colors.END}")
            wait_enter()
    else:
        print(f"{Colors.RED}❌ Модуль sonyacloud.py не найден!{Colors.END}")
        wait_enter()


def run_session_manager():
    """Запуск менеджера сессий"""
    print(f"{Colors.GREEN}✅ Загружаю Менеджер сессий...{Colors.END}")
    session_mgr = load_session_manager()
    if session_mgr:
        clear()
        if hasattr(session_mgr, 'main_menu'):
            import asyncio
            asyncio.run(session_mgr.main_menu())
        elif hasattr(session_mgr, 'main'):
            import asyncio
            asyncio.run(session_mgr.main())
        else:
            print(f"{Colors.RED}❌ В менеджере сессий нет функции запуска{Colors.END}")
            wait_enter()
    else:
        print(f"{Colors.RED}❌ Модуль tg_manager.py не найден!{Colors.END}")
        wait_enter()


def run_gift_bot():
    """Запуск Gift Bot (NFT)"""
    print(f"{Colors.GREEN}✅ Загружаю Gift Bot...{Colors.END}")
    gift_bot = load_gift_bot()
    if gift_bot:
        clear()
        if hasattr(gift_bot, 'main'):
            import asyncio
            asyncio.run(gift_bot.main())
        else:
            print(f"{Colors.RED}❌ В gift_bot.py нет функции main(){Colors.END}")
            wait_enter()
    else:
        print(f"{Colors.RED}❌ Модуль gift_bot.py не найден!{Colors.END}")
        print(f"{Colors.YELLOW}📁 Создай файл telegram/gift_bot.py{Colors.END}")
        wait_enter()

# ===================== ГЛАВНЫЙ ЦИКЛ =====================


def main():
    """Главная функция"""
    # Сначала показываем этическое предупреждение
    if not accept_ethical_terms():
        return

    # Проверяем PIN-код
    if not check_pin_simple():
        print(f"\n{Colors.RED}⛔ Доступ запрещён!{Colors.END}")
        time.sleep(2)
        return

    while True:
        show_menu()

        choice = input(f"{Colors.PINK}👉 Введи номер: {Colors.END}").strip()

        if choice == "1":
            run_sonyacloud()

        elif choice == "2":
            run_session_manager()

        elif choice == "3":
            run_gift_bot()

        elif choice == "4":
            settings_menu()

        elif choice == "0":
            print(f"\n{Colors.GREEN}🔙 Возвращаюсь в Games Tools...{Colors.END}")
            time.sleep(1)
            break

        else:
            print(f"\n{Colors.RED}❌ Неверный выбор!{Colors.END}")
            wait_enter()


# ===================== ТОЧКА ВХОДА =====================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Выход по запросу...{Colors.END}")
        time.sleep(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Критическая ошибка: {e}{Colors.END}")
        time.sleep(3)

# ╔═════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                       ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║
# ║  lang: python                                    ║
# ║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║
# ║  build:3.10.15                                   ║
# ║  files: main.py                                  ║
# ╚═════════════════════════════╝


import os
import sys
import subprocess
import signal
from colorama import init, Fore, Style
import pyfiglet
import time

# Добавляем текущую папку в путь для импортов
sys.path.insert(0, os.path.dirname(__file__))

# Инициализация Colorama
init(autoreset=True)

# ---- Импорт внешних модулей ----
try:
    import X
except ImportError:
    print(Fore.RED + "❌ Не найден X.py")
    X = None

try:
    import shake
except ImportError:
    print(Fore.RED + "❌ Не найден shake.py")
    shake = None

try:
    import Wind_Fighter
except ImportError:
    print(Fore.RED + "❌ Не найден Wind_Fighter.py")
    Wind_Fighter = None

try:
    import dino
except ImportError:
    print(Fore.RED + "❌ Не найден dino.py")
    dino = None

try:
    import maze
except ImportError:
    print(Fore.RED + "❌ Не найден maze.py")
    maze = None

try:
    import cyber_defender
except ImportError:
    print(Fore.RED + "❌ Не найден cyber_defender.py")
    cyber_defender = None

# ========== ПУНКТ ДЛЯ TELEGRAM ==========
TELEGRAM_MAIN_PATH = os.path.join(os.path.dirname(__file__), "telegram", "main.py")


def run_telegram_tools():
    """Запуск Telegram инструментов — БЫСТРЫЙ И НАДЁЖНЫЙ"""
    if os.path.exists(TELEGRAM_MAIN_PATH):
        print(Fore.YELLOW + "📱 Запускаем Telegram Tools...")
        time.sleep(1)

        # Сохраняем текущую директорию
        current_dir = os.getcwd()

        # Меняем директорию на папку с игрой
        os.chdir(os.path.dirname(__file__))

        # Полностью сбрасываем терминал (важно для curses)
        os.system('reset')

        # Запускаем в том же процессе (без subprocess)
        # Это самый быстрый способ
        try:
            # Заменяем текущий процесс новым
            os.execl(sys.executable, sys.executable, TELEGRAM_MAIN_PATH)
        except Exception as e:
            print(Fore.RED + f"❌ Ошибка: {e}")
            input(Fore.CYAN + "Нажмите Enter для возврата..." + Fore.RESET)

        # Сюда мы не дойдём, если execl сработает
        os.chdir(current_dir)
        clear()

    else:
        print(Fore.RED + "❌ telegram/main.py не найден!")
        print(Fore.YELLOW + "📁 Создаю структуру...")

        # Создаём папку
        telegram_dir = os.path.join(os.path.dirname(__file__), "telegram")
        os.makedirs(telegram_dir, exist_ok=True)

        print(Fore.GREEN + "✅ Папка telegram создана!")
        print(Fore.CYAN + "📝 Теперь нужно добавить свой код в:")
        print(Fore.CYAN + f"   {TELEGRAM_MAIN_PATH}")
        time.sleep(2)

# ========== ЗАПАСНОЙ ВАРИАНТ ==========


def run_telegram_tools_fallback():
    """Запасной вариант без os.execl"""
    if os.path.exists(TELEGRAM_MAIN_PATH):
        print(Fore.YELLOW + "📱 Запускаем Telegram Tools...")
        time.sleep(1)

        # Сохраняем текущую директорию
        current_dir = os.getcwd()

        # Меняем директорию на папку с игрой
        os.chdir(os.path.dirname(__file__))

        # Сбрасываем curses
        try:
            import curses
            curses.endwin()
        except Exception:
            pass

        # Сбрасываем терминал
        os.system('reset')

        # Запускаем и ждём завершения
        try:
            # Игнорируем Ctrl+C пока
            original_sigint = signal.signal(signal.SIGINT, signal.SIG_IGN)

            # Запускаем процесс
            process = subprocess.Popen(
                [sys.executable, TELEGRAM_MAIN_PATH],
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr
            )

            # Ждём завершения
            process.wait()

            # Возвращаем обработку Ctrl+C
            signal.signal(signal.SIGINT, original_sigint)

        except Exception as e:
            print(Fore.RED + f"❌ Ошибка: {e}")
            input(Fore.CYAN + "Нажмите Enter для возврата..." + Fore.RESET)

        # Возвращаемся обратно
        os.chdir(current_dir)
        clear()

    else:
        print(Fore.RED + "❌ telegram/main.py не найден!")
        print(Fore.YELLOW + "📁 Создаю структуру...")
        telegram_dir = os.path.join(os.path.dirname(__file__), "telegram")
        os.makedirs(telegram_dir, exist_ok=True)
        print(Fore.GREEN + "✅ Папка telegram создана!")
        print(Fore.CYAN + "📝 Теперь нужно добавить свой код в:")
        print(Fore.CYAN + f"   {TELEGRAM_MAIN_PATH}")
        time.sleep(2)

# ---- Утилиты ----


def clear():
    os.system("clear" if os.name == "posix" else "cls")


def print_banner():
    banner = pyfiglet.figlet_format("Games Tools", font="slant")
    print(Fore.MAGENTA + banner)
    print(Fore.CYAN + Style.BRIGHT + "💗 Добро пожаловать в Games Tools 💗\n")

# ---- Главное меню ----


def main():
    while True:
        clear()
        print_banner()
        print(Fore.MAGENTA + """
1 • Генераторы
2 • Змейка
3 • Wind Fighter
4 • Dino 🦖
5 • Maze 🧙
6 • Cyber Defender 🛡️
7 • Telegram Tools 📱
0 • Выход
""")
        choice = input("> ").strip().lower()

        if choice == "1":
            if X:
                print(Fore.YELLOW + "Открываем генераторы... 😎")
                X.main()
            else:
                print(Fore.RED + "❌ X.py не найден")
            input("Нажмите Enter для возврата в меню...")

        elif choice == "2":
            if shake:
                print(Fore.YELLOW + "Запускаем змейку... 🐍")
                if hasattr(shake, "start_game"):
                    shake.start_game()
                elif hasattr(shake, "main"):
                    shake.main()
                else:
                    print(Fore.RED + "❌ shake.py не имеет функции запуска")
            else:
                print(Fore.RED + "❌ shake.py не найден")
            input("Нажмите Enter для возврата в меню...")

        elif choice == "3":
            if Wind_Fighter:
                print(Fore.YELLOW + "Запускаем Wind Fighter... 🛩✨")
                if hasattr(Wind_Fighter, "start_game"):
                    Wind_Fighter.start_game()
                else:
                    print(Fore.RED + "❌ Wind_Fighter.py не имеет функции запуска")
            else:
                print(Fore.RED + "❌ Wind_Fighter.py не найден")
            input("Нажмите Enter для возврата в меню...")

        elif choice == "4":
            if dino:
                print(Fore.YELLOW + "Запускаем Dino... 🦖🔥")
                if hasattr(dino, "start_game"):
                    dino.start_game()
                elif hasattr(dino, "main"):
                    dino.main()
                else:
                    print(Fore.RED + "❌ dino.py не имеет функции запуска")
            else:
                print(Fore.RED + "❌ dino.py не найден")
            input("Нажмите Enter для возврата в меню...")

        elif choice == "5":
            if maze:
                print(Fore.YELLOW + "Запускаем Maze... 🧙✨")
                if hasattr(maze, "start_game"):
                    maze.start_game()
                elif hasattr(maze, "main"):
                    maze.main()
                else:
                    print(Fore.RED + "❌ maze.py не имеет функции запуска")
            else:
                print(Fore.RED + "❌ maze.py не найден")
            input("Нажмите Enter для возврата в меню...")

        elif choice == "6":
            if cyber_defender:
                print(Fore.YELLOW + "🛡️ Запускаем Cyber Defender...")
                if hasattr(cyber_defender, "run"):
                    cyber_defender.run()
                elif hasattr(cyber_defender, "main"):
                    cyber_defender.main()
                else:
                    print(Fore.RED + "❌ cyber_defender.py не имеет функции запуска")
            else:
                print(Fore.RED + "❌ cyber_defender.py не найден")
            input("Нажмите Enter для возврата в меню...")

        # ========== ПУНКТ 7 ==========
        elif choice == "7":
            # Используем основной быстрый вариант
            run_telegram_tools()
        # =============================

        elif choice == "0":
            print(Fore.CYAN + "Выход... Пока! 💖")
            break

        else:
            print(Fore.RED + "❌ Неверный выбор")
            input("Enter...")


if __name__ == "__main__":
    main()

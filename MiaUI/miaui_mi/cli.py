#!/usr/bin/env python3
# ╔════════════════════════════════════════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                                     ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                   ║
# ║  lang: python                                                  ║
# ║  build: 3.10.15                                                ║
# ║  files: cli.py                                                 ║
# ╚════════════════════════════════════════════════════════════════╝

import sys
import subprocess
import os
import shutil
from pathlib import Path

# =========================================================
# АВТОМАТИЧЕСКАЯ НАСТРОЙКА ПУТЕЙ (PYTHONPATH)
# =========================================================
# Этот блок заменяет ручной 'export PYTHONPATH'
current_file = Path(__file__).resolve()
# Если файл лежит в MiaUI/miaui_mi/cli.py, то корень - это MiaUI
if current_file.parent.name == "miaui_mi":
    project_pkg_root = current_file.parent.parent
    if str(project_pkg_root) not in sys.path:
        sys.path.insert(0, str(project_pkg_root))

# Теперь можно безопасно импортировать свои модули
try:
    from miaui_mi.help.help import run_ai
except ImportError:
    # Запасной вариант на случай странных путей
    sys.path.append(os.getcwd())
    from miaui_mi.help.help import run_ai


# ==============================
# BASH
# ==============================
def run_bash_script(args):
    import miaui_mi
    # Сначала ищем в корне проекта (рядом с папкой MiaUI)
    project_root = Path(miaui_mi.__file__).parent.parent.parent
    script = project_root / "bash" / "main.sh"
    
    if not args and not script.exists():
        # Если не нашли в корне, ищем в site-packages/bash/main.sh
        pkg_path = Path(miaui_mi.__file__).parent.parent
        script = pkg_path / "bash" / "main.sh"
    elif args:
        script = Path(args[0]).expanduser()

    if not script.exists():
        print(f"❌ Файл не найден: {script}")
        return

    print(f"🐚 Запуск bash: {script}")
    subprocess.run(["bash", str(script)] + (args[1:] if args else []))


# ==============================
# GAMES
# ==============================
def run_games():
    base = Path(__file__).resolve().parent.parent / "games"
    main_game = base / "main.py"

    if not main_game.exists():
        print(f"❌ Error: {main_game} not found")
        return

    subprocess.run([sys.executable, str(main_game)] + sys.argv[2:])


# ==============================
# SOFIA
# ==============================
def run_sofia_monitor():
    print("💜 Initializing SOFIA Monitor...")

    base_path = Path(__file__).resolve().parent / "security" / "pypass"
    if not base_path.exists():
        print(f"❌ Error: Directory {base_path} not found!")
        return

    original_cwd = os.getcwd()
    try:
        os.chdir(base_path)

        makefile_path = base_path / "Makefile"
        if makefile_path.exists():
            print("⚙️ Building from Makefile (make all)...")
            # Добавили 'all', чтобы запустить сборку
            build = subprocess.run(["make", "all"], capture_output=True, text=True)
            if build.returncode != 0:
                print("❌ Build failed")
                print(build.stderr)
                # Если бинарник уже есть, попробуем продолжить
                if not (base_path / "sofia_monitor").exists():
                    return
            else:
                print("✅ Build successful")

        executable = None
        # Основное имя из Makefile
        possible_names = ["sofia_monitor", "sofia", "sofia.bin", "sofia.out"]
        for name in possible_names:
            candidate = base_path / name
            if candidate.exists() and os.access(candidate, os.X_OK):
                executable = candidate
                break

        if executable is None:
            for f in base_path.iterdir():
                if f.is_file() and os.access(f, os.X_OK) and f.suffix not in [".py", ".sh", ".txt", ".md", ".c", ".h", ".o"]:
                    executable = f
                    break

        if executable is None:
            print("❌ Binary not found!")
            return

        print(f"🚀 Running {executable.name}...")
        # Передаем аргументы бинарнику
        subprocess.run([str(executable)] + sys.argv[2:])

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        os.chdir(original_cwd)


# ==============================
# REPORT
# ==============================
def run_report():
    report_bot = Path(__file__).parent.parent / "report" / "bot.py"

    if not report_bot.exists():
        print("❌ Ошибка: Файл отчёта не найден!")
        print(f"   Путь: {report_bot}")
        return

    print("📬 Запуск системы отчётов...")
    subprocess.run([sys.executable, str(report_bot)])


# ==============================
# LUA
# ==============================
def run_lua_command(command, args):
    lua_bin = "lua"
    if not shutil.which(lua_bin):
        print("❌ Lua не установлен")
        return

    base = Path(__file__).parent.parent / "miaui_mi_pro"
    lua_file = base / "import.lua"

    if not lua_file.exists():
        print(f"❌ Ошибка: {lua_file} не найден")
        return

    subprocess.run([lua_bin, str(lua_file), command] + list(args))


# ==============================
# LOCAL
# ==============================
def run_local():
    project_root = Path(__file__).parent.parent.parent
    script_path = project_root / "The_program" / "main.py"

    if script_path.exists():
        print(f"🚀 Запуск: {script_path.name}...")
        subprocess.run([sys.executable, str(script_path)])
    else:
        print(f"❌ Ошибка: Скрипт не найден: {script_path}")


# ==============================
# SCAN (импорт внутри)
# ==============================
def run_scan():
    try:
        from miaui_mi.security.engine import full_scan
        from miaui_mi.security.ui import display_results
        display_results(full_scan())
    except ImportError as e:
        print(f"❌ Import error: {e}")


# ==============================
# MAIN
# ==============================
def main():
    if len(sys.argv) > 1 and sys.argv[1].lower() == "help":
        lang = os.environ.get("LANG", "").lower()
        is_ru = "ru" in lang
        help_dir = Path(__file__).parent / "help"
        help_file = help_dir / f"help{'_ru.txt' if is_ru else '.txt'}"

        purple = '\033[38;2;180;0;255m'
        reset = '\033[0m'

        if help_file.exists():
            print(f"{purple}{help_file.read_text(encoding='utf-8')}{reset}")
        else:
            print(f"{purple}❌ Help file not found{reset}")
        return

    if len(sys.argv) < 2:
        return

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    if command == "scan":
        run_scan()
    elif command == "games":
        run_games()
    elif command == "sofia":
        run_sofia_monitor()
    elif command == "ai":
        run_ai()
    elif command == "report":
        run_report()
    elif command == "local":
        run_local()
    elif command == "bash":
        run_bash_script(args)
    else:
        run_lua_command(command, args)


if __name__ == "__main__":
    main()

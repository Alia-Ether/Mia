# Cpython/main.py
# ╔════════════════════════════════════════════════════════════════╗
# ║  Project: MIA Core - AVB Tool                                 ║
# ║  Link: t.me/FrontendVSCode                                    ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                  ║
# ║  lang: python                                                 ║
# ║  [AVB-HASH-01] ΞΩ77Λβ99PPHD8A71                               ║
# ║  build: 3.10.15                                               ║
# ║  files: main.py                                               ║
# ╚════════════════════════════════════════════════════════════════╝

import sys
import subprocess
from pathlib import Path
import difflib

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, str(Path(__file__).parent))

# Путь к miatool.py
MIATOOL_PATH = Path(__file__).parent.parent / "plugin/mia/miatool.py"

# Пробуем Rich для красивой рамки
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# ANSI fallback
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
BOLD = '\033[1m'
RESET = '\033[0m'


def show_help():
    if RICH_AVAILABLE:
        console.print()
        console.print(Panel(
            Text("MIA Core v3.10.15", style="bold #FF69B4"),
            border_style="#FF69B4",
        ))

        table = Table(title="📋 КОМАНДЫ", border_style="cyan", title_style="bold cyan")
        table.add_column("Команда", style="bold green")
        table.add_column("Описание", style="white")

        table.add_row("info <файл>", "Красивый вывод")
        table.add_row("info -e <файл>", "Сырой вывод miatool")
        table.add_row("info_image <файл>", "Информация об образе (AVB)")
        table.add_row("make_vbmeta_image", "Создать vbmeta образ")
        table.add_row("add_hash_footer", "Добавить hash-футер")
        table.add_row("add_hashtree_footer", "Добавить hashtree-футер")
        table.add_row("verify_image", "Проверить подпись")
        table.add_row("erase_footer", "Удалить AVB футер")
        table.add_row("extract_public_key", "Извлечь публичный ключ")
        table.add_row("calculate_vbmeta_digest", "VBMeta дайджест")
        table.add_row("calculate_kernel_cmdline", "Командная строка ядра")
        table.add_row("make_certificate", "Создать сертификат")
        table.add_row("version", "Версия miatool")
        table.add_row("help, --help, -h", "Справка")

        console.print(table)

        console.print(Panel(
            "[cyan]Примеры:[/cyan]\n"
            "  mia-core info boot.img\n"
            "  mia-core info_image vendor.img\n"
            "  mia-core make_vbmeta_image --output vbmeta.img --key key.pem\n"
            "  mia-core --help   справка по miatool",
            border_style="magenta"
        ))
    else:
        print(f"""
{MAGENTA}{BOLD}╔══════════════════════════════════════════════════════════════╗
║                      MIA Core v3.10.15                        ║
╠══════════════════════════════════════════════════════════════╣
║  {BOLD}Команды:{RESET}                                                 ║
║  {GREEN}info{RESET} <файл>                   - Красивый вывод             ║
║  {GREEN}info{RESET} -e <файл>                - Сырой вывод                ║
║  {CYAN}info_image{RESET} <файл>              - Информация об образе       ║
║  {CYAN}make_vbmeta_image{RESET}              - Создать vbmeta образ       ║
║  {CYAN}add_hash_footer{RESET}                - Добавить hash-футер        ║
║  {CYAN}add_hashtree_footer{RESET}            - Добавить hashtree-футер    ║
║  {CYAN}verify_image{RESET}                   - Проверить подпись          ║
║  {CYAN}erase_footer{RESET}                   - Удалить AVB футер          ║
║  {CYAN}extract_public_key{RESET}             - Извлечь публичный ключ     ║
║  {CYAN}calculate_vbmeta_digest{RESET}        - VBMeta дайджест           ║
║  {CYAN}calculate_kernel_cmdline{RESET}       - Командная строка ядра      ║
║  {CYAN}make_certificate{RESET}               - Создать сертификат         ║
║  {CYAN}version{RESET}                        - Версия miatool             ║
║                                                              ║
║  {YELLOW}help{RESET}                         - Справка MIA                ║
║  {YELLOW}--help{RESET}                       - Полная справка miatool     ║
╚══════════════════════════════════════════════════════════════╝{RESET}
        """)


def find_similar_commands(input_cmd, known_commands, limit=3):
    """Поиск похожих команд"""
    matches = difflib.get_close_matches(input_cmd, known_commands, n=limit, cutoff=0.4)
    return matches


def run_miatool_direct(args, silent=False):
    """Запуск miatool.py напрямую с аргументами"""
    cmd = [sys.executable, str(MIATOOL_PATH)] + args
    if silent:
        result = subprocess.run(cmd, capture_output=True, text=True)
    else:
        result = subprocess.run(cmd)
    return result.returncode


def main():
    # ВСЕ оригинальные команды miatool.py
    miatool_commands = [
        'generate_test_image', 'version', 'check_mldsa_support',
        'extract_public_key', 'extract_public_key_digest',
        'make_vbmeta_image', 'add_hash_footer', 'append_vbmeta_image',
        'add_hashtree_footer', 'erase_footer', 'zero_hashtree',
        'extract_vbmeta_image', 'resize_image', 'info_image', 'verify_image',
        'print_partition_digests', 'calculate_vbmeta_digest', 'calculate_kernel_cmdline',
        'set_ab_metadata', 'make_certificate', 'make_atx_certificate',
        'make_cert_permanent_attributes', 'make_atx_permanent_attributes',
        'make_cert_metadata', 'make_atx_metadata',
        'make_cert_unlock_credential', 'make_atx_unlock_credential',
        'update_partition_descriptor', 'resign_image'
    ]

    # Добавляем сокращённые команды MIA
    all_commands = miatool_commands + ['info', 'help', '-h', '--help']

    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    # Особая обработка: mia-core -e info_image --image boot.img
    if '-e' in sys.argv:
        e_index = sys.argv.index('-e')
        if e_index == 1 and len(sys.argv) > 2:
            sys.argv = [sys.argv[0], sys.argv[2], '-e'] + sys.argv[3:]

    command = sys.argv[1]

    # Справка MIA
    if command in ['help', '-h']:
        show_help()
        return

    # Справка miatool
    if command == '--help':
        run_miatool_direct(['--help'])
        return

    # Старый стиль: mia-core info <файл>
    if command == 'info':
        try:
            from info_img import run_info
            run_info()
        except ImportError as e:
            print(f"{RED}❌ Ошибка импорта: {e}{RESET}")
            sys.exit(1)
        return

    # Проверяем, является ли команда оригинальной командой miatool
    if command in miatool_commands:
        try:
            from info_img import main as info_main
            info_main()
        except (ImportError, SystemExit):
            run_miatool_direct(sys.argv[1:])
        return

    # Команда не найдена — короткое сообщение
    print(f"\n{RED}❌ Упс! MIA Core не знает команду: {command}{RESET}")

    similar = find_similar_commands(command, all_commands)
    if similar:
        print(f"{YELLOW}🤔 Возможно, вы имели в виду:{RESET}")
        for cmd in similar:
            print(f"   {CYAN}→ {cmd}{RESET}")

    print(f"\n{YELLOW}Введите '{GREEN}mia-core help{YELLOW}' для списка команд.{RESET}\n")
    sys.exit(1)


if __name__ == "__main__":
    main()

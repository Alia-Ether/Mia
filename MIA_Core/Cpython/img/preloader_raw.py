# img/preloader_raw.py
# ╔════════════════════════════════════════════════════════════════╗
# ║  Project: MIA Core - Preloader Raw Image Handler              ║
# ║  Link: t.me/FrontendVSCode                                    ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                  ║
# ║  lang: python                                                 ║
# ║  [MIA-HASH-01] ΞΩ77Λβ99PPHD8A71                               ║
# ║  build: 3.10.15                                               ║
# ║  files: preloader_raw.py                                      ║
# ╚════════════════════════════════════════════════════════════════╝

from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
WHITE = '\033[97m'
BOLD = '\033[1m'
RESET = '\033[0m'
BRIGHT_RED = '\033[1;91m'


def format_size(size):
    try:
        size = int(size)
    except Exception:
        return str(size)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def print_info(image_name, _mia_output=None):
    path = Path(image_name)
    if not path.exists():
        if RICH_AVAILABLE:
            console.print(f"[red]❌ File not found: {image_name}[/red]")
        else:
            print(f"{RED}❌ File not found: {image_name}{RESET}")
        return

    size = path.stat().st_size

    if RICH_AVAILABLE:
        console.print()
        console.print(Panel(Text(f"▓▒░ {image_name} ░▒▓ ❯", style="#8700af bold"), border_style="#8700af"))

        table = Table(title="🔐 ОСНОВНАЯ ИНФОРМАЦИЯ", title_style="bright_red", border_style="cyan")
        table.add_column("Параметр", style="bold white")
        table.add_column("Значение", style="green")
        table.add_row("Размер", format_size(size))
        table.add_row("Тип", "PRELOADER_RAW")
        table.add_row("Назначение", "Первичный загрузчик MediaTek")
        console.print(table)

        console.print(Panel(
            "[yellow]ℹ️ ИНФОРМАЦИЯ[/yellow]\n\n"
            "PRELOADER_RAW — это первичный загрузчик (BootROM) для устройств на MediaTek.\n"
            "Загружается до Little Kernel (LK) и инициализирует DRAM.",
            border_style="yellow"
        ))
    else:
        print(f"\n  {MAGENTA}▓▒░ {image_name} ░▒▓ {CYAN}❯{RESET}")
        print(f"  {'═' * 50}")
        print(f"\n  {BRIGHT_RED}{BOLD}🔐 ОСНОВНАЯ ИНФОРМАЦИЯ{RESET}")
        print(f"  {'─' * 45}")
        print(f"  {BOLD}Размер:{RESET} {GREEN}{format_size(size)}{RESET}")
        print(f"  {BOLD}Тип:{RESET} {YELLOW}PRELOADER_RAW{RESET}")
        print()

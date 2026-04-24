# img/spmfw.py
# ╔════════════════════════════════════════════════════════════════╗
# ║  Project: MIA Core - SPMFW Image Handler                      ║
# ║  Link: t.me/FrontendVSCode                                    ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                  ║
# ║  lang: python                                                 ║
# ║  [MIA-HASH-01] ΞΩ77Λβ99PPHD8A71                               ║
# ║  build: 3.10.15                                               ║
# ║  files: spmfw.py                                              ║
# ╚════════════════════════════════════════════════════════════════╝

import re
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
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
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"


def extract_strings(data, min_len=4):
    pattern = rb'[\x20-\x7E]{%d,}' % min_len
    return [s.decode("ascii", errors="ignore") for s in re.findall(pattern, data)]


def detect_format(data):
    if data.startswith(b'\x7fELF'):
        return "ELF"
    if data[:4] == b'SPMF' or b'spmfw' in data[:0x100].lower():
        return "SPMFW Firmware"
    if data[:4] == b'TINY':
        return "TinySys Firmware"
    return "Unknown"


def print_info(image_name, _mia_output=None):
    path = Path(image_name)
    if not path.exists():
        path = Path.cwd() / image_name
    if not path.exists():
        if RICH_AVAILABLE:
            console.print(f"[red]❌ File not found: {image_name}[/red]")
        else:
            print(f"{RED}❌ File not found: {image_name}{RESET}")
        return

    data = path.read_bytes()
    size = len(data)

    if RICH_AVAILABLE:
        console.print()
        console.print(Panel(Text(f"▓▒░ {image_name} ░▒▓ ❯", style="#8700af bold"), border_style="#8700af"))

        table = Table(title="🔐 ОСНОВНАЯ ИНФОРМАЦИЯ", title_style="bright_red", border_style="cyan")
        table.add_column("Параметр", style="bold white")
        table.add_column("Значение", style="green")
        table.add_row("Размер", format_size(size))
        table.add_row("Тип", detect_format(data))
        table.add_row("Назначение", "System Power Management Firmware")
        console.print(table)

        hex_table = Table(title="🔢 HEX (первые 32 байта)", title_style="bright_red", border_style="cyan")
        hex_table.add_column("Смещение", style="bold white")
        hex_table.add_column("HEX", style="magenta")
        hex_table.add_column("ASCII", style="green")
        for i in range(0, min(32, size), 16):
            chunk = data[i:i+16]
            hex_str = " ".join(f"{b:02x}" for b in chunk)
            ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            hex_table.add_row(f"0x{i:04x}", hex_str, ascii_str)
        console.print(hex_table)

        strings = extract_strings(data, min_len=4)
        if strings:
            filtered = [s for s in strings if not s.isdigit() and len(s) > 2]
            if filtered:
                str_table = Table(title="📝 НАЙДЕННЫЕ СТРОКИ", title_style="bright_red", border_style="cyan")
                str_table.add_column("Текст", style="green")
                seen = set()
                for s in filtered[:15]:
                    if s not in seen:
                        seen.add(s)
                        str_table.add_row(s[:47] + "..." if len(s) > 50 else s)
                console.print(str_table)

        desc_table = Table(title="ℹ️ ЧТО ТАКОЕ SPMFW", title_style="bright_red", border_style="cyan")
        desc_table.add_column("Описание", style="bold white")
        desc_table.add_column("Значение", style="green")
        desc_table.add_row("Расшифровка", "System Power Management Firmware")
        desc_table.add_row("Процессор", "Сопроцессор MediaTek")
        desc_table.add_row("Функция", "Управление питанием, частотами, термоконтроль")
        console.print(desc_table)
    else:
        print(f"\n  {MAGENTA}▓▒░ {image_name} ░▒▓ {CYAN}❯{RESET}")
        print(f"  {'═' * 50}")
        print(f"\n  {BRIGHT_RED}{BOLD}🔐 ОСНОВНАЯ ИНФОРМАЦИЯ{RESET}")
        print(f"  {'─' * 45}")
        print(f"  {BOLD}Размер:{RESET} {GREEN}{format_size(size)}{RESET}")
        print(f"  {BOLD}Тип:{RESET} {YELLOW}{detect_format(data)}{RESET}")
        print()

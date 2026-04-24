# img/system_ext.py
# ╔════════════════════════════════════════════════════════════════╗
# ║  Project: MIA Core - System Ext Image Handler                 ║
# ║  Link: t.me/FrontendVSCode                                    ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                  ║
# ║  lang: python                                                 ║
# ║  [MIA-HASH-01] ΞΩ77Λβ99PPHD8A71                               ║
# ║  build: 3.10.15                                               ║
# ║  files: system_ext.py                                         ║
# ╚════════════════════════════════════════════════════════════════╝

import re
import struct
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


def format_size(bytes_size):
    try:
        size = int(bytes_size)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.2f} GB"
    except Exception:
        return bytes_size


def parse_avb_footer_direct(image_path):
    path = Path(image_path)
    if not path.exists():
        return None
    try:
        with open(path, 'rb') as f:
            f.seek(-64, 2)
            footer = f.read(64)
        if footer[:4] not in (b'AVBf', b'AVB0'):
            return None
        return {
            'magic': footer[:4].decode('ascii'),
            'version_major': struct.unpack('>I', footer[4:8])[0],
            'version_minor': struct.unpack('>I', footer[8:12])[0],
            'vbmeta_offset': struct.unpack('>Q', footer[16:24])[0],
            'vbmeta_size': struct.unpack('>Q', footer[24:32])[0],
        }
    except Exception:
        return None


def print_info(image_name, miatool_output):
    path = Path(image_name)
    file_size = path.stat().st_size if path.exists() else 0

    if miatool_output is None:
        miatool_output = ""

    if not miatool_output or "Footer version:" not in miatool_output:
        avb_info = parse_avb_footer_direct(image_name)

        if RICH_AVAILABLE:
            console.print()
            console.print(Panel(Text(f"▓▒░ {image_name} ░▒▓ ❯", style="#8700af bold"), border_style="#8700af"))
            table = Table(title="🔐 ОСНОВНАЯ ИНФОРМАЦИЯ", title_style="bright_red", border_style="cyan")
            table.add_column("Параметр", style="bold white")
            table.add_column("Значение", style="green")
            table.add_row("Размер", format_size(file_size))
            if avb_info:
                table.add_row("AVB Magic", f"[green]{avb_info['magic']}[/green]")
                table.add_row("AVB Version", f"{avb_info['version_major']}.{avb_info['version_minor']}")
            else:
                table.add_row("Статус", "[yellow]Образ не содержит AVB футера[/yellow]")
            console.print(table)
        else:
            print(f"\n  {MAGENTA}▓▒░ {image_name} ░▒▓ {CYAN}❯{RESET}")
            print(f"  {'═' * 50}")
            print(f"\n  {BRIGHT_RED}{BOLD}🔐 ОСНОВНАЯ ИНФОРМАЦИЯ{RESET}")
            print(f"  {'─' * 45}")
            print(f"  {BOLD}Размер:{RESET} {GREEN}{format_size(file_size)}{RESET}")
            if avb_info:
                print(f"  {BOLD}AVB Magic:{RESET} {GREEN}{avb_info['magic']}{RESET}")
        return

    footer_version = re.search(r'Footer version:\s+(\S+)', miatool_output)
    image_size = re.search(r'Image size:\s+(\d+)\s+bytes', miatool_output)
    algorithm = re.search(r'Algorithm:\s+(\S+)', miatool_output)
    rollback = re.search(r'Rollback Index:\s+(\d+)', miatool_output)
    partition_name = re.search(r'Partition Name:\s+(\S+)', miatool_output)
    os_version = re.search(r'com\.android\.build\.system_ext\.os_version\s+->\s+\'([^\']+)\'', miatool_output)
    fingerprint = re.search(r'com\.android\.build\.system_ext\.fingerprint\s+->\s+\'([^\']+)\'', miatool_output)

    if RICH_AVAILABLE:
        console.print()
        console.print(Panel(Text(f"▓▒░ {image_name} ░▒▓ ❯", style="#8700af bold"), border_style="#8700af"))

        table = Table(title="🔐 ОСНОВНАЯ ИНФОРМАЦИЯ", title_style="bright_red", border_style="cyan")
        table.add_column("Параметр", style="bold white")
        table.add_column("Значение", style="green")
        if footer_version:
            table.add_row("Версия Footer", footer_version.group(1))
        if image_size:
            table.add_row("Размер", format_size(image_size.group(1)))
        if algorithm:
            table.add_row("Алгоритм", algorithm.group(1))
        if rollback:
            table.add_row("Rollback Index", rollback.group(1))
        if partition_name:
            table.add_row("Раздел", partition_name.group(1))
        console.print(table)

        if os_version or fingerprint:
            props = Table(title="📱 СВОЙСТВА", title_style="bright_red", border_style="cyan")
            props.add_column("Параметр", style="bold white")
            props.add_column("Значение", style="green")
            if os_version:
                props.add_row("OS Version", os_version.group(1))
            if fingerprint:
                fp = fingerprint.group(1)
                props.add_row("Fingerprint", fp[:50] + "..." if len(fp) > 50 else fp)
            console.print(props)
    else:
        print(f"\n  {MAGENTA}▓▒░ {image_name} ░▒▓ {CYAN}❯{RESET}")
        print(f"  {'═' * 50}")
        if footer_version:
            print(f"  {BOLD}Footer:{RESET} {GREEN}{footer_version.group(1)}{RESET}")
        if image_size:
            print(f"  {BOLD}Size:{RESET} {GREEN}{format_size(image_size.group(1))}{RESET}")
        print()

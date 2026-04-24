# img/system.py
# ╔════════════════════════════════════════════════════════════════╗
# ║  Project: MIA Core - System Image Handler                     ║
# ║  Link: t.me/FrontendVSCode                                    ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                  ║
# ║  lang: python                                                 ║
# ║  [MIA-HASH-01] ΞΩ77Λβ99PPHD8A71                               ║
# ║  build: 3.10.15                                               ║
# ║  files: system.py                                             ║
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

# ANSI Fallback
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
WHITE = '\033[97m'
BOLD = '\033[1m'
RESET = '\033[0m'

# Ярко-красный для заголовков
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
    """Прямое чтение AVB футера из файла (big-endian)"""
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
    """Вывод информации для system.img"""

    path = Path(image_name)
    file_size = path.stat().st_size if path.exists() else 0

    if miatool_output is None:
        miatool_output = ""

    # Если вывод miatool пустой — пробуем прямое чтение футера
    if not miatool_output or "Footer version:" not in miatool_output:
        avb_info = parse_avb_footer_direct(image_name)

        if RICH_AVAILABLE:
            console.print()
            console.print(Panel(
                Text(f"▓▒░ {image_name} ░▒▓ ❯", style="#8700af bold"),
                border_style="#8700af"
            ))

            table = Table(title="🔐 ОСНОВНАЯ ИНФОРМАЦИЯ", title_style="bright_red", border_style="cyan")
            table.add_column("Параметр", style="bold white")
            table.add_column("Значение", style="green")
            table.add_row("Размер", format_size(file_size))

            if avb_info:
                table.add_row("AVB Magic", f"[green]{avb_info['magic']}[/green]")
                table.add_row("AVB Version", f"{avb_info['version_major']}.{avb_info['version_minor']}")
                table.add_row("VBMeta offset", str(avb_info['vbmeta_offset']))
                table.add_row("VBMeta size", format_size(avb_info['vbmeta_size']))
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
            else:
                print(f"  {BOLD}Статус:{RESET} {YELLOW}Образ не содержит AVB футера{RESET}")
            print()
        return

    # ========== ПАРСИНГ MIATOOL ==========
    footer_version = re.search(r'Footer version:\s+(\S+)', miatool_output)
    image_size = re.search(r'Image size:\s+(\d+)\s+bytes', miatool_output)
    original_size = re.search(r'Original image size:\s+(\d+)\s+bytes', miatool_output)
    vbmeta_offset = re.search(r'VBMeta offset:\s+(\d+)', miatool_output)
    vbmeta_size = re.search(r'VBMeta size:\s+(\d+)\s+bytes', miatool_output)

    min_libmia = re.search(r'Minimum libmia version:\s+(\S+)', miatool_output)
    header_block = re.search(r'Header Block:\s+(\d+)\s+bytes', miatool_output)
    auth_block = re.search(r'Authentication Block:\s+(\d+)\s+bytes', miatool_output)
    aux_block = re.search(r'Auxiliary Block:\s+(\d+)\s+bytes', miatool_output)
    algorithm = re.search(r'Algorithm:\s+(\S+)', miatool_output)
    rollback = re.search(r'Rollback Index:\s+(\d+)', miatool_output)
    flags = re.search(r'Flags:\s+(\d+)', miatool_output)
    rollback_loc = re.search(r'Rollback Index Location:\s+(\d+)', miatool_output)
    release_string = re.search(r"Release String:\s+'([^']+)'", miatool_output)

    dm_version = re.search(r'Version of dm-verity:\s+(\d+)', miatool_output)
    hash_image_size = re.search(r'Image Size:\s+(\d+)\s+bytes', miatool_output)
    tree_offset = re.search(r'Tree Offset:\s+(\d+)', miatool_output)
    tree_size = re.search(r'Tree Size:\s+(\d+)\s+bytes', miatool_output)
    data_block = re.search(r'Data Block Size:\s+(\d+)\s+bytes', miatool_output)
    hash_block = re.search(r'Hash Block Size:\s+(\d+)\s+bytes', miatool_output)
    fec_roots = re.search(r'FEC num roots:\s+(\d+)', miatool_output)
    fec_offset = re.search(r'FEC offset:\s+(\d+)', miatool_output)
    fec_size = re.search(r'FEC size:\s+(\d+)\s+bytes', miatool_output)
    hash_alg = re.search(r'Hash Algorithm:\s+(\S+)', miatool_output)
    partition_name = re.search(r'Partition Name:\s+(\S+)', miatool_output)
    salt = re.search(r'Salt:\s+(\S+)', miatool_output)
    root_digest = re.search(r'Root Digest:\s+(\S+)', miatool_output)
    hashtree_flags = re.search(r'Flags:\s+(\d+)\s*$', miatool_output, re.MULTILINE)

    os_version = re.search(r'com\.android\.build\.system\.os_version\s+->\s+\'([^\']+)\'', miatool_output)
    fingerprint = re.search(r'com\.android\.build\.system\.fingerprint\s+->\s+\'([^\']+)\'', miatool_output)
    security_patch = re.search(r'com\.android\.build\.system\.security_patch\s+->\s+\'([^\']+)\'', miatool_output)

    if RICH_AVAILABLE:
        console.print()
        console.print(Panel(
            Text(f"▓▒░ {image_name} ░▒▓ ❯", style="#8700af bold"),
            border_style="#8700af"
        ))

        table_main = Table(title="🔐 ОСНОВНАЯ ИНФОРМАЦИЯ", title_style="bright_red", border_style="cyan")
        table_main.add_column("Параметр", style="bold white")
        table_main.add_column("Значение", style="green")

        if footer_version:
            table_main.add_row("Версия Footer", footer_version.group(1))
        if image_size:
            table_main.add_row("Размер образа", f"{format_size(image_size.group(1))} ({image_size.group(1)} bytes)")
        if original_size:
            table_main.add_row("Оригинальный размер",
                               f"{format_size(original_size.group(1))} ({original_size.group(1)} bytes)")
        if vbmeta_offset:
            table_main.add_row("VBMeta смещение", vbmeta_offset.group(1))
        if vbmeta_size:
            table_main.add_row("VBMeta размер", f"{vbmeta_size.group(1)} bytes")

        console.print(table_main)

        table_headers = Table(title="📋 ЗАГОЛОВКИ", title_style="bright_red", border_style="cyan")
        table_headers.add_column("Параметр", style="bold white")
        table_headers.add_column("Значение", style="yellow")

        if min_libmia:
            table_headers.add_row("Min libmia версия", min_libmia.group(1))
        if header_block:
            table_headers.add_row("Header Block", f"{header_block.group(1)} bytes")
        if auth_block:
            table_headers.add_row("Authentication Block", f"{auth_block.group(1)} bytes")
        if aux_block:
            table_headers.add_row("Auxiliary Block", f"{aux_block.group(1)} bytes")
        if algorithm:
            color = "red" if algorithm.group(1) == "NONE" else "green"
            table_headers.add_row("Алгоритм", f"[{color}]{algorithm.group(1)}[/{color}]")
        if rollback:
            table_headers.add_row("Rollback Index", rollback.group(1))
        if flags:
            table_headers.add_row("Флаги", flags.group(1))
        if rollback_loc:
            table_headers.add_row("Rollback Index Location", rollback_loc.group(1))
        if release_string:
            table_headers.add_row("Release String", f"[cyan]{release_string.group(1)}[/cyan]")

        console.print(table_headers)

        if partition_name:
            table_hash = Table(title="🌳 HASHTREE DESCRIPTOR (dm-verity)", title_style="bright_red", border_style="cyan")
            table_hash.add_column("Параметр", style="bold white")
            table_hash.add_column("Значение", style="green")

            if dm_version:
                table_hash.add_row("Версия dm-verity", dm_version.group(1))
            if partition_name:
                table_hash.add_row("Имя раздела", f"[bold green]{partition_name.group(1)}[/bold green]")
            if hash_alg:
                table_hash.add_row("Хеш алгоритм", f"[yellow]{hash_alg.group(1)}[/yellow]")
            if hash_image_size:
                table_hash.add_row(
                    "Размер данных", f"{format_size(hash_image_size.group(1))} ({hash_image_size.group(1)} bytes)")
            if tree_offset:
                table_hash.add_row("Смещение дерева", tree_offset.group(1))
            if tree_size:
                table_hash.add_row("Размер дерева", format_size(tree_size.group(1)))
            if data_block:
                table_hash.add_row("Блок данных", f"{data_block.group(1)} bytes")
            if hash_block:
                table_hash.add_row("Блок хешей", f"{hash_block.group(1)} bytes")
            if fec_roots:
                table_hash.add_row("FEC корней", fec_roots.group(1))
            if fec_offset:
                table_hash.add_row("FEC смещение", fec_offset.group(1))
            if fec_size:
                table_hash.add_row("FEC размер", format_size(fec_size.group(1)))
            if salt:
                salt_val = salt.group(1)
                salt_display = f"[magenta]{salt_val[:47]}...[/magenta]" if len(salt_val) > 50 else f"[magenta]{salt_val}[/magenta]"
                table_hash.add_row("Salt", salt_display)
            if root_digest:
                digest_val = root_digest.group(1)
                digest_display = f"[magenta]{digest_val[:47]}...[/magenta]" if len(digest_val) > 50 else f"[magenta]{digest_val}[/magenta]"
                table_hash.add_row("Root Digest", digest_display)
            if hashtree_flags:
                table_hash.add_row("Флаги", hashtree_flags.group(1))

            console.print(table_hash)

        if os_version or security_patch or fingerprint:
            table_props = Table(title="📱 СВОЙСТВА ПРОШИВКИ", title_style="bright_red", border_style="cyan")
            table_props.add_column("Параметр", style="bold white")
            table_props.add_column("Значение", style="green")

            if os_version:
                table_props.add_row("Версия Android OS", f"[green]{os_version.group(1)}[/green]")
            if security_patch:
                table_props.add_row("Патч безопасности", f"[yellow]{security_patch.group(1)}[/yellow]")
            if fingerprint:
                fp = fingerprint.group(1)
                table_props.add_row(
                    "Fingerprint", f"[cyan]{fp[:57]}...[/cyan]" if len(fp) > 60 else f"[cyan]{fp}[/cyan]")

            console.print(table_props)

        console.print()

    else:
        # ANSI Fallback
        print(f"\n  {MAGENTA}▓▒░ {image_name} ░▒▓ {CYAN}❯{RESET}")
        print(f"  {'═' * 50}")

        print(f"\n  {BRIGHT_RED}{BOLD}🔐 ОСНОВНАЯ ИНФОРМАЦИЯ{RESET}")
        print(f"  {'─' * 45}")
        if footer_version:
            print(f"  {BOLD}Версия Footer:{RESET} {GREEN}{footer_version.group(1)}{RESET}")
        if image_size:
            print(f"  {BOLD}Размер образа:{RESET} {GREEN}{format_size(image_size.group(1))}{RESET}")
        if algorithm:
            color = RED if algorithm.group(1) == "NONE" else GREEN
            print(f"  {BOLD}Алгоритм:{RESET} {color}{algorithm.group(1)}{RESET}")

        if partition_name:
            print(f"\n  {BRIGHT_RED}{BOLD}🌳 HASHTREE{RESET}")
            print(f"  {'─' * 45}")
            print(f"  {BOLD}Раздел:{RESET} {GREEN}{partition_name.group(1)}{RESET}")
            if hash_alg:
                print(f"  {BOLD}Хеш:{RESET} {YELLOW}{hash_alg.group(1)}{RESET}")

        if os_version or security_patch:
            print(f"\n  {BRIGHT_RED}{BOLD}📱 СВОЙСТВА{RESET}")
            print(f"  {'─' * 45}")
            if os_version:
                print(f"  {BOLD}Android OS:{RESET} {GREEN}{os_version.group(1)}{RESET}")
            if security_patch:
                print(f"  {BOLD}Патч:{RESET} {YELLOW}{security_patch.group(1)}{RESET}")

        print()

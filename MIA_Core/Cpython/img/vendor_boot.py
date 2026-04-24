# img/vendor_boot.py
# ╔════════════════════════════════════════════════════════════════╗
# ║  Project: MIA Core - Vendor Boot Image Handler                ║
# ║  Link: t.me/FrontendVSCode                                    ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                  ║
# ║  lang: python                                                 ║
# ║  [MIA-HASH-01] ΞΩ77Λβ99PPHD8A71                               ║
# ║  build: 3.10.15                                               ║
# ║  files: vendor_boot.py                                        ║
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
        return str(bytes_size)


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
    """Вывод информации для vendor_boot.img"""

    path = Path(image_name)
    file_size = path.stat().st_size if path.exists() else 0

    if miatool_output is None:
        miatool_output = ""

    # Если вывод miatool пустой — пробуем прямое чтение футера
    if not miatool_output or "Footer version:" not in miatool_output:
        avb_info = parse_avb_footer_direct(image_name)

        if RICH_AVAILABLE:
            console.print()
            console.print(Panel(Text(f"📦 VENDOR_BOOT ОБРАЗ: {image_name}",
                          style="bold magenta"), border_style="magenta"))

            table = Table(title="🔐 ОСНОВНАЯ ИНФОРМАЦИЯ", border_style="cyan")
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

            if not avb_info:
                console.print(Panel(
                    "[yellow]⚠️ VENDOR_BOOT — раздел с ramdisk для вендора[/yellow]\n"
                    "Содержит vendor-специфичные файлы для первого этапа загрузки.",
                    border_style="yellow"
                ))
        else:
            print(f"\n  {BOLD}{MAGENTA}📦 VENDOR_BOOT ОБРАЗ: {image_name}{RESET}")
            print(f"  {'═' * 50}")
            print(f"\n  {BOLD}Размер:{RESET} {GREEN}{format_size(file_size)}{RESET}")
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

    hash_image_size = re.search(r'Hash descriptor:\s+Image Size:\s+(\d+)\s+bytes', miatool_output)
    hash_algorithm = re.search(r'Hash Algorithm:\s+(\S+)', miatool_output)
    partition_name = re.search(r'Partition Name:\s+(\S+)', miatool_output)
    salt = re.search(r'Salt:\s+(\S+)', miatool_output)
    digest = re.search(r'Digest:\s+(\S+)', miatool_output)
    hash_flags = re.search(r'Flags:\s+(\d+)\s*$', miatool_output, re.MULTILINE)

    fingerprint = re.search(r'com\.android\.build\.vendor_boot\.fingerprint\s+->\s+\'([^\']+)\'', miatool_output)

    if RICH_AVAILABLE:
        console.print()
        console.print(Panel(Text(f"📦 VENDOR_BOOT ОБРАЗ: {image_name}", style="bold magenta"), border_style="magenta"))

        table_main = Table(title="🔐 ОСНОВНАЯ ИНФОРМАЦИЯ", border_style="cyan")
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

        table_headers = Table(title="📋 ЗАГОЛОВКИ", border_style="cyan")
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
            table_hash = Table(title="🔒 HASH DESCRIPTOR", border_style="cyan")
            table_hash.add_column("Параметр", style="bold white")
            table_hash.add_column("Значение", style="green")

            if partition_name:
                table_hash.add_row("Имя раздела", f"[bold green]{partition_name.group(1)}[/bold green]")
            if hash_algorithm:
                table_hash.add_row("Хеш алгоритм", f"[yellow]{hash_algorithm.group(1)}[/yellow]")
            if hash_image_size:
                table_hash.add_row(
                    "Размер образа", f"{format_size(hash_image_size.group(1))} ({hash_image_size.group(1)} bytes)")
            if salt:
                table_hash.add_row("Salt", f"[magenta]{salt.group(1)}[/magenta]")
            if digest:
                table_hash.add_row("Digest", f"[magenta]{digest.group(1)}[/magenta]")
            if hash_flags:
                table_hash.add_row("Флаги", hash_flags.group(1))

            console.print(table_hash)

        if fingerprint:
            table_props = Table(title="📱 СВОЙСТВА ПРОШИВКИ", border_style="cyan")
            table_props.add_column("Параметр", style="bold white")
            table_props.add_column("Значение", style="green")
            table_props.add_row("Fingerprint", f"[cyan]{fingerprint.group(1)}[/cyan]")
            console.print(table_props)

        console.print()

    else:
        # ANSI Fallback
        print(f"\n  {BOLD}{MAGENTA}📦 VENDOR_BOOT ОБРАЗ: {image_name}{RESET}")
        print(f"  {'═' * 50}")

        if footer_version:
            print(f"\n  {BOLD}{CYAN}🔐 ОСНОВНАЯ ИНФОРМАЦИЯ{RESET}")
            print(f"  {'─' * 45}")
            print(f"  {BOLD}Версия Footer:{RESET} {GREEN}{footer_version.group(1)}{RESET}")
            if image_size:
                print(f"  {BOLD}Размер образа:{RESET} {GREEN}{format_size(image_size.group(1))}{RESET}")
            if partition_name:
                print(f"  {BOLD}Раздел:{RESET} {GREEN}{partition_name.group(1)}{RESET}")
            if algorithm:
                print(f"  {BOLD}Алгоритм:{RESET} {YELLOW}{algorithm.group(1)}{RESET}")

        if fingerprint:
            print(f"\n  {BOLD}Fingerprint:{RESET} {CYAN}{fingerprint.group(1)}{RESET}")

        print()

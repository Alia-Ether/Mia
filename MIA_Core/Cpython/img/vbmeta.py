# img/vbmeta.py
# ╔════════════════════════════════════════════════════════════════╗
# ║  Project: MIA Core - VBMeta Image Handler                     ║
# ║  Link: t.me/FrontendVSCode                                    ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                  ║
# ║  lang: python                                                 ║
# ║  [MIA-HASH-01] ΞΩ77Λβ99PPHD8A71                               ║
# ║  build: 3.10.15                                               ║
# ║  files: vbmeta.py                                             ║
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
    """Вывод информации для vbmeta.img"""

    path = Path(image_name)
    file_size = path.stat().st_size if path.exists() else 0

    if miatool_output is None:
        miatool_output = ""

    # Если вывод miatool пустой — пробуем прямое чтение футера
    if not miatool_output or "Minimum libmia version:" not in miatool_output:
        avb_info = parse_avb_footer_direct(image_name)

        if RICH_AVAILABLE:
            console.print()
            # Название файла в стиле PS1: ▓▒░ filename ░▒▓ ❯
            console.print(Panel(
                Text(f"▓▒░ {image_name} ░▒▓ ❯", style="#8700af bold"),
                border_style="#8700af"
            ))

            table = Table(title=f"{BRIGHT_RED}🔐 ОСНОВНАЯ ИНФОРМАЦИЯ{RESET}" if not RICH_AVAILABLE else "🔐 ОСНОВНАЯ ИНФОРМАЦИЯ",
                          border_style="cyan", title_style="bright_red")
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
    min_libmia = re.search(r'Minimum libmia version:\s+(\S+)', miatool_output)
    header_block = re.search(r'Header Block:\s+(\d+)\s+bytes', miatool_output)
    auth_block = re.search(r'Authentication Block:\s+(\d+)\s+bytes', miatool_output)
    aux_block = re.search(r'Auxiliary Block:\s+(\d+)\s+bytes', miatool_output)
    algorithm = re.search(r'Algorithm:\s+(\S+)', miatool_output)
    rollback = re.search(r'Rollback Index:\s+(\d+)', miatool_output)
    flags = re.search(r'Flags:\s+(\d+)', miatool_output)
    rollback_loc = re.search(r'Rollback Index Location:\s+(\d+)', miatool_output)
    release_string = re.search(r"Release String:\s+'([^']+)'", miatool_output)
    public_key = re.search(r'Public key \(sha1\):\s+(\S+)', miatool_output)

    chain_pattern = re.compile(
        r'Chain Partition descriptor:\s+Partition Name:\s+(\S+)\s+Rollback Index Location:\s+(\d+)\s+Public key \(sha1\):\s+(\S+)\s+Flags:\s+(\d+)', re.DOTALL)
    chains = chain_pattern.findall(miatool_output)

    hash_pattern = re.compile(
        r'Hash descriptor:\s+Image Size:\s+(\d+)\s+bytes\s+Hash Algorithm:\s+(\S+)\s+Partition Name:\s+(\S+)\s+Salt:\s+(\S+)\s+Digest:\s+(\S+)\s+Flags:\s+(\d+)', re.DOTALL)
    hashes = hash_pattern.findall(miatool_output)

    hashtree_pattern = re.compile(r'Hashtree descriptor:\s+Version of dm-verity:\s+(\d+)\s+Image Size:\s+(\d+)\s+bytes\s+Tree Offset:\s+(\d+)\s+Tree Size:\s+(\d+)\s+bytes\s+Data Block Size:\s+(\d+)\s+bytes\s+Hash Block Size:\s+(\d+)\s+bytes\s+FEC num roots:\s+(\d+)\s+FEC offset:\s+(\d+)\s+FEC size:\s+(\d+)\s+bytes\s+Hash Algorithm:\s+(\S+)\s+Partition Name:\s+(\S+)\s+Salt:\s+(\S+)\s+Root Digest:\s+(\S+)\s+Flags:\s+(\d+)', re.DOTALL)
    hashtrees = hashtree_pattern.findall(miatool_output)

    props = {}
    prop_pattern = re.compile(r'Prop:\s+([^\s]+)\s+->\s+\'([^\']+)\'')
    for match in prop_pattern.finditer(miatool_output):
        props[match.group(1)] = match.group(2)

    if RICH_AVAILABLE:
        console.print()
        # Название файла в стиле PS1
        console.print(Panel(
            Text(f"▓▒░ {image_name} ░▒▓ ❯", style="#8700af bold"),
            border_style="#8700af"
        ))

        table_main = Table(title="🔐 ОСНОВНАЯ ИНФОРМАЦИЯ", title_style="bright_red", border_style="cyan")
        table_main.add_column("Параметр", style="bold white")
        table_main.add_column("Значение", style="green")

        if min_libmia:
            table_main.add_row("Min libmia версия", min_libmia.group(1))
        if header_block:
            table_main.add_row("Header Block", f"{header_block.group(1)} bytes")
        if auth_block:
            table_main.add_row("Authentication Block", f"{auth_block.group(1)} bytes")
        if aux_block:
            table_main.add_row("Auxiliary Block", f"{aux_block.group(1)} bytes")
        if public_key:
            table_main.add_row("Публичный ключ (SHA1)", f"[magenta]{public_key.group(1)}[/magenta]")
        if algorithm:
            table_main.add_row("Алгоритм", f"[green]{algorithm.group(1)}[/green]")
        if rollback:
            table_main.add_row("Rollback Index", rollback.group(1))
        if flags:
            table_main.add_row("Флаги", flags.group(1))
        if rollback_loc:
            table_main.add_row("Rollback Index Location", rollback_loc.group(1))
        if release_string:
            table_main.add_row("Release String", f"[cyan]{release_string.group(1)}[/cyan]")

        console.print(table_main)

        if chains:
            table_chains = Table(title="🔗 ЦЕПОЧКИ ДОВЕРИЯ (Chain Partitions)",
                                 title_style="bright_red", border_style="cyan")
            table_chains.add_column("Раздел", style="bold white")
            table_chains.add_column("Слот отката", style="yellow")
            table_chains.add_column("Ключ (SHA1)", style="magenta")
            for chain in chains:
                table_chains.add_row(chain[0], chain[1], chain[2][:16] + "...")
            console.print(table_chains)

        if hashes:
            table_hashes = Table(title="🔒 ХЕШИРОВАННЫЕ РАЗДЕЛЫ (Hash Descriptors)",
                                 title_style="bright_red", border_style="cyan")
            table_hashes.add_column("Раздел", style="bold white")
            table_hashes.add_column("Размер", style="green")
            table_hashes.add_column("Алгоритм", style="yellow")
            for h in hashes:
                table_hashes.add_row(h[2], format_size(h[0]), h[1])
            console.print(table_hashes)

        if hashtrees:
            table_hashtrees = Table(title="🌳 HASHTREE РАЗДЕЛЫ (dm-verity)",
                                    title_style="bright_red", border_style="cyan")
            table_hashtrees.add_column("Раздел", style="bold white")
            table_hashtrees.add_column("Размер", style="green")
            table_hashtrees.add_column("Алгоритм", style="yellow")
            for ht in hashtrees:
                table_hashtrees.add_row(ht[11], format_size(ht[1]), ht[10])
            console.print(table_hashtrees)

        if props:
            table_props = Table(title="📱 СВОЙСТВА ПРОШИВКИ", title_style="bright_red", border_style="cyan")
            table_props.add_column("Параметр", style="bold white")
            table_props.add_column("Значение", style="green")
            for key, value in props.items():
                if 'fingerprint' in key:
                    table_props.add_row(key, f"[cyan]{value[:47]}...[/cyan]" if len(value)
                                        > 50 else f"[cyan]{value}[/cyan]")
                elif 'security_patch' in key:
                    table_props.add_row(key, f"[yellow]{value}[/yellow]")
                elif 'os_version' in key:
                    table_props.add_row(key, f"[green]{value}[/green]")
                else:
                    table_props.add_row(key, value[:47] + "..." if len(value) > 50 else value)
            console.print(table_props)

        console.print()

    else:
        # ANSI Fallback
        print(f"\n  {MAGENTA}▓▒░ {image_name} ░▒▓ {CYAN}❯{RESET}")
        print(f"  {'═' * 50}")

        print(f"\n  {BRIGHT_RED}{BOLD}🔐 ОСНОВНАЯ ИНФОРМАЦИЯ{RESET}")
        print(f"  {'─' * 45}")
        if min_libmia:
            print(f"  {BOLD}Min libmia:{RESET} {WHITE}{min_libmia.group(1)}{RESET}")
        if algorithm:
            print(f"  {BOLD}Алгоритм:{RESET} {GREEN}{algorithm.group(1)}{RESET}")
        if rollback:
            print(f"  {BOLD}Rollback Index:{RESET} {YELLOW}{rollback.group(1)}{RESET}")

        if chains:
            print(f"\n  {BRIGHT_RED}{BOLD}🔗 ЦЕПОЧКИ ДОВЕРИЯ{RESET}")
            print(f"  {'─' * 45}")
            for chain in chains[:5]:
                print(f"  {GREEN}{chain[0]}{RESET} | slot={chain[1]} | key={chain[2][:16]}...")

        if hashes:
            print(f"\n  {BRIGHT_RED}{BOLD}🔒 ХЕШИРОВАННЫЕ РАЗДЕЛЫ{RESET}")
            print(f"  {'─' * 45}")
            for h in hashes[:5]:
                print(f"  {GREEN}{h[2]}{RESET} | {format_size(h[0])} | {h[1]}")

        if props:
            print(f"\n  {BRIGHT_RED}{BOLD}📱 СВОЙСТВА{RESET}")
            print(f"  {'─' * 45}")
            for key, value in list(props.items())[:5]:
                print(f"  {BOLD}{key}:{RESET} {value[:50]}")

        print()

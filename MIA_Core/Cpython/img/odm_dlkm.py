# img/odm_dlkm.py
# ╔════════════════════════════════════════════════════════════════╗
# ║  Project: MIA Core - ODM_DLKM Image Handler                   ║
# ║  Link: t.me/FrontendVSCode                                    ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                  ║
# ║  lang: python                                                 ║
# ║  [MIA-HASH-01] ΞΩ77Λβ99PPHD8A71                               ║
# ║  build: 3.10.15                                               ║
# ║  files: odm_dlkm.py                                           ║
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


def read_file_chunk(path, offset=0, size=65536):
    try:
        with open(path, 'rb') as f:
            f.seek(offset)
            return f.read(size)
    except Exception:
        return b''


def read_file_tail(path, size=64):
    try:
        with open(path, 'rb') as f:
            f.seek(0, 2)
            file_size = f.tell()
            if file_size < size:
                f.seek(0)
                return f.read(), file_size
            f.seek(-size, 2)
            return f.read(size), file_size
    except Exception:
        return b'', 0


def get_file_size(path):
    return Path(path).stat().st_size


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


def extract_strings(data, min_len=4):
    pattern = rb'[\x20-\x7E]{%d,}' % min_len
    return [s.decode("ascii", errors="ignore") for s in re.findall(pattern, data)]


def detect_format(data, footer):
    if footer and footer[:4] == b'AVB0':
        return "MIA AVB"
    if footer and footer[:4] == b'AVBf':
        return "Android AVB"
    if data[:4] == b'\xe2\xe1\xf5\xe0':
        return "EROFS"
    if len(data) > 0x438 and data[0x438:0x43A] == b'\x53\xef':
        return "EXT4"
    return "Unknown"


def parse_avb_footer(footer):
    info = {}
    if len(footer) >= 64 and footer[:4] in (b'AVB0', b'AVBf'):
        info['magic'] = footer[:4].decode('ascii')
        info['version_major'] = struct.unpack('>I', footer[4:8])[0]
        info['version_minor'] = struct.unpack('>I', footer[8:12])[0]
    return info


def find_kernel_modules(strings):
    return [s for s in strings if s.endswith('.ko')]


def print_info(image_name, _mia_output=None):
    path = Path(image_name)
    if not path.exists():
        if RICH_AVAILABLE:
            console.print(f"[red]❌ File not found: {image_name}[/red]")
        else:
            print(f"{RED}❌ File not found: {image_name}{RESET}")
        return

    size = get_file_size(image_name)
    data = read_file_chunk(image_name, offset=0, size=min(size, 65536))
    footer, _ = read_file_tail(image_name, size=64)
    img_format = detect_format(data, footer)
    avb_info = parse_avb_footer(footer)
    strings = extract_strings(data, min_len=4)
    modules = find_kernel_modules(strings)

    if RICH_AVAILABLE:
        console.print()
        console.print(Panel(Text(f"▓▒░ {image_name} ░▒▓ ❯", style="#8700af bold"), border_style="#8700af"))

        table = Table(title="🔐 BASIC INFO", title_style="bright_red", border_style="cyan")
        table.add_column("Field", style="bold white")
        table.add_column("Value", style="green")
        table.add_row("Size", format_size(size))
        table.add_row("Format", img_format)
        table.add_row("Type", "ODM Dynamic Kernel Modules")
        if avb_info:
            table.add_row("AVB Magic", f"[yellow]{avb_info.get('magic', 'N/A')}[/yellow]")
            if 'version_major' in avb_info:
                table.add_row("AVB Version", f"{avb_info['version_major']}.{avb_info['version_minor']}")
        console.print(table)

        if modules:
            mod_table = Table(title="🔧 KERNEL MODULES", title_style="bright_red", border_style="cyan")
            mod_table.add_column("Module", style="green")
            for mod in modules[:20]:
                mod_table.add_row(mod)
            console.print(mod_table)

        hex_table = Table(title="🔢 HEX (first 64 bytes)", title_style="bright_red", border_style="cyan")
        hex_table.add_column("Offset")
        hex_table.add_column("Hex")
        hex_table.add_column("ASCII")
        for i in range(0, min(64, len(data)), 16):
            chunk = data[i:i+16]
            hex_str = " ".join(f"{b:02x}" for b in chunk)
            ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            hex_table.add_row(f"0x{i:04x}", hex_str, ascii_str)
        console.print(hex_table)

        console.print(
            Panel("[yellow]📌 NOTE[/yellow]\n\nODM_DLKM contains ODM-specific kernel modules.", border_style="yellow"))
    else:
        print(f"\n  {MAGENTA}▓▒░ {image_name} ░▒▓ {CYAN}❯{RESET}")
        print(f"  {'═' * 50}")
        print(f"\n  {BRIGHT_RED}{BOLD}🔐 BASIC INFO{RESET}")
        print(f"  {'─' * 45}")
        print(f"  {BOLD}Size:{RESET} {GREEN}{format_size(size)}{RESET}")
        print(f"  {BOLD}Format:{RESET} {YELLOW}{img_format}{RESET}")
        print()

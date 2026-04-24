# img/logo.py
# ╔════════════════════════════════════════════════════════════════╗
# ║  Project: MIA Core - Logo Image Handler                       ║
# ║  Link: t.me/FrontendVSCode                                    ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                  ║
# ║  lang: python                                                 ║
# ║  [MIA-HASH-01] ΞΩ77Λβ99PPHD8A71                               ║
# ║  build: 3.10.15                                               ║
# ║  files: logo.py                                               ║
# ╚════════════════════════════════════════════════════════════════╝

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
BLUE = '\033[94m'
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


def detect_logo_format(data):
    if data[:2] == b'BM':
        return "BMP Image"
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return "PNG Image"
    if data[:3] == b'\xff\xd8\xff':
        return "JPEG Image"
    if data[:4] == b'LOGO':
        return "MediaTek Logo"
    if data[:8] == b'MTK_LOGO':
        return "MediaTek Logo (MTK)"
    return "Raw Image / Splash Screen"


def parse_image_info(data, size):
    info = {}
    if data[:2] == b'BM' and len(data) >= 54:
        info['format'] = 'BMP'
        info['width'] = struct.unpack('<I', data[18:22])[0]
        info['height'] = struct.unpack('<I', data[22:26])[0]
        info['bpp'] = struct.unpack('<H', data[28:30])[0]
    elif data[:8] == b'\x89PNG\r\n\x1a\n':
        info['format'] = 'PNG'
        if b'IHDR' in data[:0x100]:
            idx = data.find(b'IHDR')
            if idx > 0 and len(data) >= idx + 16:
                info['width'] = struct.unpack('>I', data[idx+4:idx+8])[0]
                info['height'] = struct.unpack('>I', data[idx+8:idx+12])[0]
    elif data[:3] == b'\xff\xd8\xff':
        info['format'] = 'JPEG'
    return info


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
    logo_format = detect_logo_format(data)
    info_data = parse_image_info(data, size)

    if RICH_AVAILABLE:
        console.print()
        console.print(Panel(Text(f"▓▒░ {image_name} ░▒▓ ❯", style="#8700af bold"), border_style="#8700af"))

        table = Table(title="🔐 BASIC INFO", title_style="bright_red", border_style="cyan")
        table.add_column("Field", style="bold white")
        table.add_column("Value", style="green")
        table.add_row("Size", format_size(size))
        table.add_row("Format", logo_format)
        table.add_row("Type", "Boot Logo / Splash Screen")
        if info_data.get('width') and info_data.get('height'):
            table.add_row("Resolution", f"[green]{info_data['width']} x {info_data['height']}[/green]")
        if info_data.get('bpp'):
            table.add_row("BPP", f"[blue]{info_data['bpp']}[/blue]")
        console.print(table)

        hex_table = Table(title="🔢 HEX (first 32 bytes)", title_style="bright_red", border_style="cyan")
        hex_table.add_column("Offset")
        hex_table.add_column("Hex")
        hex_table.add_column("ASCII")
        for i in range(0, min(32, len(data)), 16):
            chunk = data[i:i+16]
            hex_str = " ".join(f"{b:02x}" for b in chunk)
            ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            hex_table.add_row(f"0x{i:04x}", hex_str, ascii_str)
        console.print(hex_table)

        console.print(Panel("[yellow]📌 NOTE[/yellow]\n\nLogo displayed during boot.", border_style="yellow"))
    else:
        print(f"\n  {MAGENTA}▓▒░ {image_name} ░▒▓ {CYAN}❯{RESET}")
        print(f"  {'═' * 50}")
        print(f"\n  {BRIGHT_RED}{BOLD}🔐 BASIC INFO{RESET}")
        print(f"  {'─' * 45}")
        print(f"  {BOLD}Size:{RESET} {GREEN}{format_size(size)}{RESET}")
        print(f"  {BOLD}Format:{RESET} {YELLOW}{logo_format}{RESET}")
        print()

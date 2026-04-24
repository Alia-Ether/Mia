# img/md1.py
# ╔════════════════════════════════════════════════════════════════╗
# ║  Project: MIA Core - MD1 Image Handler                        ║
# ║  Link: t.me/FrontendVSCode                                    ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                  ║
# ║  lang: python                                                 ║
# ║  [MIA-HASH-01] ΞΩ77Λβ99PPHD8A71                               ║
# ║  build: 3.10.15                                               ║
# ║  files: md1.py                                                ║
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
BLUE = '\033[94m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
WHITE = '\033[97m'
BOLD = '\033[1m'
RESET = '\033[0m'
BRIGHT_RED = '\033[1;91m'


def read_file_chunk(path, offset=0, size=131072):
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


def detect_md1_format(data):
    if data[:4] == b'MD1\x00':
        return "MediaTek MD1 (Modem)"
    if data[:4] == b'MTK\x00':
        return "MediaTek Modem (MTK)"
    if data[:8] == b'MD1_FW\x00':
        return "MediaTek MD1 Firmware"
    if data[:4] == b'\x7fELF':
        e_machine = struct.unpack('<H', data[18:20])[0] if len(data) > 20 else 0
        arch_map = {0x28: "ARM", 0xB7: "AArch64", 0xF3: "RISC-V"}
        arch = arch_map.get(e_machine, "Unknown")
        return f"ELF ({arch}) - Modem"
    return "Unknown Modem Firmware"


def parse_md1_header(data):
    info = {}
    if data[:4] == b'MD1\x00':
        info['magic'] = 'MD1'
        if len(data) >= 8:
            info['version'] = struct.unpack('<I', data[4:8])[0]
    version_match = re.search(rb'md1[_\-]?fw[_\-]?v?([0-9]+\.[0-9]+(?:\.[0-9]+)?)', data[:0x2000], re.IGNORECASE)
    if version_match:
        info['fw_version'] = version_match.group(1).decode('ascii')
    bb_match = re.search(rb'MOLY\.LR[0-9A-Z\.]+', data[:0x3000])
    if bb_match:
        info['baseband'] = bb_match.group().decode('ascii')
    date_match = re.search(rb'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+[0-9]{1,2}\s+[0-9]{4}', data[:0x4000])
    if date_match:
        info['build_date'] = date_match.group().decode('ascii')
    return info


def detect_architecture(data):
    if data[:4] == b'\x7fELF' and len(data) >= 20:
        e_machine = struct.unpack('<H', data[18:20])[0]
        if e_machine == 0xB7:
            return "ARM64"
        elif e_machine == 0x28:
            return "ARM32"
        elif e_machine == 0xF3:
            return "RISC-V"
    if len(data) >= 4:
        if b'\x00\x00\xa0\xe1' in data[:0x200] or b'\x1e\xff\x2f\xe1' in data[:0x200]:
            return "ARM32"
    if len(data) >= 8:
        if b'\x1f\x20\x03\xd5' in data[:0x200] or b'\xc0\x03\x5f\xd6' in data[:0x200]:
            return "ARM64"
    return "Unknown"


def print_info(image_name, _mia_output=None):
    path = Path(image_name)
    if not path.exists():
        if RICH_AVAILABLE:
            console.print(f"[red]❌ File not found: {image_name}[/red]")
        else:
            print(f"{RED}❌ File not found: {image_name}{RESET}")
        return

    size = get_file_size(image_name)
    data = read_file_chunk(image_name, offset=0, size=min(size, 131072))
    md1_format = detect_md1_format(data)
    info_data = parse_md1_header(data)
    arch = detect_architecture(data)

    if RICH_AVAILABLE:
        console.print()
        console.print(Panel(Text(f"▓▒░ {image_name} ░▒▓ ❯", style="#8700af bold"), border_style="#8700af"))

        table = Table(title="🔐 BASIC INFO", title_style="bright_red", border_style="cyan")
        table.add_column("Field", style="bold white")
        table.add_column("Value", style="green")
        table.add_row("Size", format_size(size))
        table.add_row("Format", md1_format)
        table.add_row("Type", "Modem Firmware")
        if info_data.get('magic'):
            table.add_row("Magic", f"[magenta]{info_data['magic']}[/magenta]")
        if info_data.get('fw_version'):
            table.add_row("FW Version", f"[green]{info_data['fw_version']}[/green]")
        if info_data.get('baseband'):
            table.add_row("Baseband", f"[yellow]{info_data['baseband']}[/yellow]")
        if info_data.get('build_date'):
            table.add_row("Build Date", f"[blue]{info_data['build_date']}[/blue]")
        console.print(table)

        arch_table = Table(title="🏛️ ARCHITECTURE", title_style="bright_red", border_style="cyan")
        arch_table.add_column("Field", style="bold white")
        arch_table.add_column("Value", style="green")
        arch_table.add_row("Detected", arch)
        console.print(arch_table)

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

        console.print(Panel("[yellow]📡 NOTE[/yellow]\n\nMD1 is MediaTek's modem firmware.", border_style="yellow"))
    else:
        print(f"\n  {MAGENTA}▓▒░ {image_name} ░▒▓ {CYAN}❯{RESET}")
        print(f"  {'═' * 50}")
        print(f"\n  {BRIGHT_RED}{BOLD}🔐 BASIC INFO{RESET}")
        print(f"  {'─' * 45}")
        print(f"  {BOLD}Size:{RESET} {GREEN}{format_size(size)}{RESET}")
        print(f"  {BOLD}Format:{RESET} {YELLOW}{md1_format}{RESET}")
        print(f"  {BOLD}Arch:{RESET} {BLUE}{arch}{RESET}")
        print()

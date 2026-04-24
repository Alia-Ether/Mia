# img/product.py
# ╔════════════════════════════════════════════════════════════════╗
# ║  Project: MIA Core - Product Image Handler                    ║
# ║  Link: t.me/FrontendVSCode                                    ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                  ║
# ║  lang: python                                                 ║
# ║  [MIA-HASH-01] ΞΩ77Λβ99PPHD8A71                               ║
# ║  build: 3.10.15                                               ║
# ║  files: product.py                                            ║
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

# ANSI цвета
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


def read_file_chunk(path, offset=0, size=8192):
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


def detect_format_from_header(header, footer, file_size):
    if footer and footer[:4] == b'AVB0':
        return "MIA AVB (AVB0 footer)"
    if footer and footer[:4] == b'AVBf':
        return "Android AVB (AVBf footer)"
    if len(header) > 0x438 and header[0x438:0x43A] == b'\x53\xef':
        return "EXT4 Filesystem"
    if header[:4] == b'\xe2\xe1\xf5\xe0':
        return "EROFS Filesystem"
    if len(header) > 0x400 and header[0x400:0x404] == b'\x10\x20\xf5\xf2':
        return "F2FS Filesystem"
    if header[:4] == b'\x3a\xff\x26\xed':
        return "Android Sparse Image"
    return "Unknown / Raw"


def parse_avb_footer(footer):
    info = {}
    if len(footer) < 64:
        return info
    if footer[:4] in (b'AVB0', b'AVBf'):
        info['magic'] = footer[:4].decode('ascii')
        info['version_major'] = struct.unpack('>I', footer[4:8])[0]
        info['version_minor'] = struct.unpack('>I', footer[8:12])[0]
        info['vbmeta_offset'] = struct.unpack('>Q', footer[16:24])[0]
        info['vbmeta_size'] = struct.unpack('>Q', footer[24:32])[0]
    return info


def parse_filesystem_info(header):
    info = {}
    if len(header) > 0x438 and header[0x438:0x43A] == b'\x53\xef':
        info['fs_type'] = 'EXT4'
        if len(header) >= 0x408:
            block_size = 1024 << struct.unpack('<I', header[0x400:0x404])[0]
            info['block_size'] = block_size
            info['blocks_count'] = struct.unpack('<I', header[0x404:0x408])[0]
            info['fs_size'] = info['blocks_count'] * block_size
            vol_name = header[0x478:0x488].decode('ascii', errors='ignore').strip('\x00')
            if vol_name:
                info['volume_name'] = vol_name
    elif header[:4] == b'\xe2\xe1\xf5\xe0':
        info['fs_type'] = 'EROFS'
        if len(header) >= 0x40:
            info['block_size'] = 1 << struct.unpack('<I', header[0x1C:0x20])[0]
    elif len(header) > 0x400 and header[0x400:0x404] == b'\x10\x20\xf5\xf2':
        info['fs_type'] = 'F2FS'
    elif header[:4] == b'\x3a\xff\x26\xed':
        info['fs_type'] = 'Sparse Image'
        if len(header) >= 28:
            info['block_size'] = struct.unpack('<I', header[12:16])[0]
            info['total_blocks'] = struct.unpack('<I', header[16:20])[0]
            info['total_chunks'] = struct.unpack('<I', header[20:24])[0]
    return info


def parse_miatool_output(output):
    if not output:
        return {}
    data = {}
    patterns = {
        'footer_version': r'Footer version:\s+(\S+)',
        'image_size': r'Image size:\s+(\d+)\s+bytes',
        'algorithm': r'Algorithm:\s+(\S+)',
        'rollback_index': r'Rollback Index:\s+(\d+)',
        'release_string': r"Release String:\s+'([^']+)'",
        'partition_name': r'Partition Name:\s+(\S+)',
        'hash_algorithm': r'Hash Algorithm:\s+(\S+)',
        'os_version': r'com\.android\.build\.product\.os_version\s+->\s+\'([^\']+)\'',
        'fingerprint': r'com\.android\.build\.product\.fingerprint\s+->\s+\'([^\']+)\'',
        'security_patch': r'com\.android\.build\.product\.security_patch\s+->\s+\'([^\']+)\'',
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, output[:50000] if output else '')
        if match:
            data[key] = match.group(1)
    return data


def print_info(image_name, _mia_output=None):
    path = Path(image_name)
    if not path.exists():
        if RICH_AVAILABLE:
            console.print(f"[red]❌ File not found: {image_name}[/red]")
        else:
            print(f"{RED}❌ File not found: {image_name}{RESET}")
        return

    size = get_file_size(image_name)
    header = read_file_chunk(image_name, offset=0, size=8192)
    footer, _ = read_file_tail(image_name, size=64)

    img_format = detect_format_from_header(header, footer, size)
    fs_info = parse_filesystem_info(header)
    avb_info = parse_avb_footer(footer)

    mia_data = {}
    if _mia_output:
        mia_data = parse_miatool_output(_mia_output)

    if RICH_AVAILABLE:
        console.print()
        console.print(Panel(Text(f"▓▒░ {image_name} ░▒▓ ❯", style="#8700af bold"), border_style="#8700af"))

        table = Table(title="🔐 BASIC INFO", title_style="bright_red", border_style="cyan")
        table.add_column("Field", style="bold white")
        table.add_column("Value", style="green")
        table.add_row("Size", format_size(size))
        table.add_row("Format", img_format)
        table.add_row("Type", "Product Partition")

        if fs_info:
            table.add_row("Filesystem", f"[cyan]{fs_info.get('fs_type', 'N/A')}[/cyan]")
            if fs_info.get('volume_name'):
                table.add_row("Volume Name", fs_info['volume_name'])
            if fs_info.get('fs_size'):
                table.add_row("FS Size", format_size(fs_info['fs_size']))

        if avb_info:
            table.add_row("AVB Magic", f"[yellow]{avb_info.get('magic', 'N/A')}[/yellow]")
            if 'version_major' in avb_info:
                table.add_row("AVB Version", f"{avb_info['version_major']}.{avb_info['version_minor']}")

        console.print(table)

        if mia_data:
            mia_table = Table(title="🔒 MIA / AVB INFO", title_style="bright_red", border_style="cyan")
            mia_table.add_column("Field", style="bold white")
            mia_table.add_column("Value", style="yellow")
            if mia_data.get('algorithm'):
                color = "red" if mia_data['algorithm'] == "NONE" else "green"
                mia_table.add_row("Algorithm", f"[{color}]{mia_data['algorithm']}[/{color}]")
            if mia_data.get('rollback_index'):
                mia_table.add_row("Rollback Index", mia_data['rollback_index'])
            if mia_data.get('release_string'):
                mia_table.add_row("Release String", f"[cyan]{mia_data['release_string']}[/cyan]")
            if mia_data.get('partition_name'):
                mia_table.add_row("Partition", f"[bold green]{mia_data['partition_name']}[/bold green]")
            if mia_data.get('hash_algorithm'):
                mia_table.add_row("Hash Algorithm", f"[yellow]{mia_data['hash_algorithm']}[/yellow]")
            console.print(mia_table)

            if any(k in mia_data for k in ['os_version', 'security_patch', 'fingerprint']):
                props_table = Table(title="📱 BUILD PROPERTIES", title_style="bright_red", border_style="cyan")
                props_table.add_column("Field", style="bold white")
                props_table.add_column("Value", style="green")
                if mia_data.get('os_version'):
                    props_table.add_row("Android OS", f"[green]{mia_data['os_version']}[/green]")
                if mia_data.get('security_patch'):
                    props_table.add_row("Security Patch", f"[yellow]{mia_data['security_patch']}[/yellow]")
                if mia_data.get('fingerprint'):
                    fp = mia_data['fingerprint']
                    props_table.add_row(
                        "Fingerprint", f"[cyan]{fp[:50]}...[/cyan]" if len(fp) > 50 else f"[cyan]{fp}[/cyan]")
                console.print(props_table)

        # HEX preview
        if header:
            hex_table = Table(title="🔢 HEX (first 64 bytes)", title_style="bright_red", border_style="cyan")
            hex_table.add_column("Offset")
            hex_table.add_column("Hex")
            hex_table.add_column("ASCII")
            for i in range(0, min(64, len(header)), 16):
                chunk = header[i:i+16]
                hex_str = " ".join(f"{b:02x}" for b in chunk)
                ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
                hex_table.add_row(f"0x{i:04x}", hex_str, ascii_str)
            console.print(hex_table)

        # AVB Footer preview
        if avb_info and footer:
            footer_table = Table(title="📌 AVB FOOTER (last 64 bytes)", title_style="bright_red", border_style="cyan")
            footer_table.add_column("Offset")
            footer_table.add_column("Hex")
            footer_table.add_column("ASCII")
            for i in range(0, min(64, len(footer)), 16):
                chunk = footer[i:i+16]
                hex_str = " ".join(f"{b:02x}" for b in chunk)
                ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
                footer_table.add_row(f"-{64-i:02x}", hex_str, ascii_str)
            console.print(footer_table)

        console.print(Panel(
            "[yellow]⚠️ SECURITY NOTE[/yellow]\n\n"
            "Product partition contains system customizations and vendor-specific apps.\n"
            "AVB footer provides verified boot integrity for this partition.",
            border_style="yellow"
        ))
        console.print(Panel(
            "🇷🇺 Product раздел содержит кастомизации системы.\n"
            "AVB футер обеспечивает целостность при verified boot.\n\n"
            "🇬🇧 Product partition holds system customizations.\n"
            "AVB footer ensures integrity during verified boot.",
            border_style="red"
        ))
    else:
        # ANSI Fallback
        print(f"\n  {MAGENTA}▓▒░ {image_name} ░▒▓ {CYAN}❯{RESET}")
        print(f"  {'═' * 50}")
        print(f"\n  {BRIGHT_RED}{BOLD}🔐 BASIC INFO{RESET}")
        print(f"  {'─' * 45}")
        print(f"  {BOLD}Size:{RESET} {GREEN}{format_size(size)}{RESET}")
        print(f"  {BOLD}Format:{RESET} {YELLOW}{img_format}{RESET}")
        if fs_info:
            print(f"  {BOLD}Filesystem:{RESET} {MAGENTA}{fs_info.get('fs_type', 'N/A')}{RESET}")
        if avb_info:
            print(f"  {BOLD}AVB Magic:{RESET} {YELLOW}{avb_info.get('magic', 'N/A')}{RESET}")
        if mia_data.get('os_version'):
            print(f"  {BOLD}Android:{RESET} {GREEN}{mia_data['os_version']}{RESET}")
        if mia_data.get('security_patch'):
            print(f"  {BOLD}Security:{RESET} {YELLOW}{mia_data['security_patch']}{RESET}")
        print()

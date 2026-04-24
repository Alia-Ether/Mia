# img/scp.py
# ╔════════════════════════════════════════════════════════════════╗
# ║  Project: MIA Core - SCP Image Handler                        ║
# ║  Link: t.me/FrontendVSCode                                    ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                  ║
# ║  lang: python                                                 ║
# ║  [MIA-HASH-01] ΞΩ77Λβ99PPHD8A71                               ║
# ║  build: 3.10.15                                               ║
# ║  files: scp.py                                                ║
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


def extract_strings(data, min_len=4):
    pattern = rb'[\x20-\x7E]{%d,}' % min_len
    return [s.decode("ascii", errors="ignore") for s in re.findall(pattern, data)]


def detect_scp_format(data):
    if data[:4] == b'SCP\x00':
        return "MediaTek SCP"
    if data[:4] == b'MTK\x00':
        return "MediaTek SCP (MTK)"
    if data[:8] == b'SCP_FW\x00\x00':
        return "MediaTek SCP Firmware"
    if len(data) >= 4:
        if data[0:4] in [b'\x00\x00\xa0\xe1', b'\x1e\xff\x2f\xe1']:
            return "SCP (ARM32 boot)"
    if data[:4] == b'\x7fELF':
        e_machine = struct.unpack('<H', data[18:20])[0] if len(data) > 20 else 0
        arch_map = {0x28: "ARM", 0xB7: "AArch64"}
        arch = arch_map.get(e_machine, "Unknown")
        return f"ELF ({arch})"
    return "Unknown SCP Firmware"


def parse_scp_header(data):
    info = {}
    if data[:4] == b'SCP\x00':
        info['magic'] = 'SCP'
        if len(data) >= 8:
            info['version'] = struct.unpack('<I', data[4:8])[0]
    elif data[:4] == b'MTK\x00':
        info['magic'] = 'MTK'
    version_match = re.search(rb'scp[_\-]?fw[_\-]?v?([0-9]+\.[0-9]+(?:\.[0-9]+)?)', data[:0x1000], re.IGNORECASE)
    if version_match:
        info['fw_version'] = version_match.group(1).decode('ascii')
    date_match = re.search(rb'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+[0-9]{1,2}\s+[0-9]{4}', data[:0x2000])
    if date_match:
        info['build_date'] = date_match.group().decode('ascii')
    git_match = re.search(rb'[0-9a-f]{40}', data[:0x2000])
    if git_match:
        info['git_hash'] = git_match.group().decode('ascii')
    return info


def detect_architecture(data):
    if len(data) >= 4:
        for p in [b'\x00\x00\xa0\xe1', b'\x1e\xff\x2f\xe1']:
            if p in data[:0x200]:
                return "ARM32"
    if len(data) >= 8:
        for p in [b'\x1f\x20\x03\xd5', b'\xc0\x03\x5f\xd6']:
            if p in data[:0x200]:
                return "ARM64"
    if len(data) >= 2 and data[:0x200].count(b'\x00\xbf') > 5:
        return "ARM32 (Thumb-2)"
    return "Unknown"


def find_scp_features(strings):
    features = []
    keywords = ['sensor', 'audio', 'voice', 'dsp', 'power', 'clock', 'pmic', 'thermal', 'battery']
    for s in strings:
        s_lower = s.lower()
        for kw in keywords:
            if kw in s_lower:
                features.append(s)
                break
    return features


def print_info(image_name, _mia_output=None):
    path = Path(image_name)
    if not path.exists():
        if RICH_AVAILABLE:
            console.print(f"[red]❌ File not found: {image_name}[/red]")
        else:
            print(f"{RED}❌ File not found: {image_name}{RESET}")
        return

    size = get_file_size(image_name)
    read_size = min(size, 65536)
    data = read_file_chunk(image_name, offset=0, size=read_size)

    scp_format = detect_scp_format(data)
    info_data = parse_scp_header(data)
    arch = detect_architecture(data)
    strings = extract_strings(data, min_len=4)
    features = find_scp_features(strings)

    if RICH_AVAILABLE:
        console.print()
        console.print(Panel(Text(f"▓▒░ {image_name} ░▒▓ ❯", style="#8700af bold"), border_style="#8700af"))

        table = Table(title="🔐 BASIC INFO", title_style="bright_red", border_style="cyan")
        table.add_column("Field", style="bold white")
        table.add_column("Value", style="green")
        table.add_row("Size", format_size(size))
        table.add_row("Format", scp_format)
        table.add_row("Type", "System Control Processor")
        if info_data.get('magic'):
            table.add_row("Magic", f"[magenta]{info_data['magic']}[/magenta]")
        if info_data.get('fw_version'):
            table.add_row("FW Version", f"[green]{info_data['fw_version']}[/green]")
        if info_data.get('build_date'):
            table.add_row("Build Date", f"[yellow]{info_data['build_date']}[/yellow]")
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

        if features:
            feat_table = Table(title="📡 SCP FEATURES", title_style="bright_red", border_style="cyan")
            feat_table.add_column("Feature", style="green")
            seen = set()
            for f in features[:15]:
                if f not in seen:
                    seen.add(f)
                    feat_table.add_row(f[:57] + "..." if len(f) > 60 else f)
            console.print(feat_table)

        if strings:
            filtered = [s for s in strings if len(s) > 3 and not s.isdigit()]
            unique_strings = list(dict.fromkeys(filtered))
            str_table = Table(title="📝 STRINGS", title_style="bright_red", border_style="cyan")
            str_table.add_column("Text", style="white")
            for s in unique_strings[:20]:
                str_table.add_row(s[:57] + "..." if len(s) > 60 else s)
            console.print(str_table)

        console.print(Panel(
            "[yellow]⚠️ SECURITY NOTE[/yellow]\n\n"
            "SCP runs on a separate Cortex-M core (Secure World).\n"
            "Manages sensors, audio, voice triggers, and power.",
            border_style="yellow"
        ))
        console.print(Panel(
            "🇷🇺 SCP работает на отдельном Cortex-M ядре.\n"
            "Управляет сенсорами, аудио, голосовыми триггерами.\n\n"
            "🇬🇧 SCP runs on dedicated Cortex-M core in Secure World.",
            border_style="red"
        ))
    else:
        print(f"\n  {MAGENTA}▓▒░ {image_name} ░▒▓ {CYAN}❯{RESET}")
        print(f"  {'═' * 50}")
        print(f"\n  {BRIGHT_RED}{BOLD}🔐 BASIC INFO{RESET}")
        print(f"  {'─' * 45}")
        print(f"  {BOLD}Size:{RESET} {GREEN}{format_size(size)}{RESET}")
        print(f"  {BOLD}Format:{RESET} {YELLOW}{scp_format}{RESET}")
        print(f"  {BOLD}Arch:{RESET} {BLUE}{arch}{RESET}")
        if info_data.get('fw_version'):
            print(f"  {BOLD}FW Ver:{RESET} {GREEN}{info_data['fw_version']}{RESET}")
        print()

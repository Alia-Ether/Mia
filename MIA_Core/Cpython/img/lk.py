# img/lk.py
# ╔════════════════════════════════════════════════════════════════╗
# ║  Project: MIA Core - LK Image Handler                         ║
# ║  Link: t.me/FrontendVSCode                                    ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                  ║
# ║  lang: python                                                 ║
# ║  [MIA-HASH-01] ΞΩ77Λβ99PPHD8A71                               ║
# ║  build: 3.10.15                                               ║
# ║  files: lk.py                                                 ║
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


def format_size(size):
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def extract_strings(data, min_len=4):
    pattern = rb'[\x20-\x7E]{%d,}' % min_len
    return [s.decode("ascii", errors="ignore") for s in re.findall(pattern, data)]


def detect_lk_variant(data):
    if data[:4] == b'LKT\x00':
        return "LK Trusty"
    if data[:8] == b'LK_TRAMP':
        return "LK Trampoline"
    version_match = re.search(rb'lk/([0-9\.]+)', data[:0x1000])
    if version_match:
        return f"LK {version_match.group(1).decode('ascii')}"
    if data[0:4] in [b'\x00\x00\x00\x00', b'\x00\x00\xa0\xe1']:
        return "LK (ARM boot vector)"
    return "LK (Unknown variant)"


def parse_lk_header(data):
    info = {}
    if data[:4] == b'LKT\x00':
        info['magic'] = 'LKT'
        if len(data) > 4:
            info['header_size'] = struct.unpack('<I', data[4:8])[0] if len(data) >= 8 else None
    elif data[:8] == b'LK_TRAMP':
        info['magic'] = 'LK_TRAMP'
    version_match = re.search(rb'lk[ /\-]([0-9]+\.[0-9]+(?:\.[0-9]+)?)', data[:0x2000])
    if version_match:
        info['version'] = version_match.group(1).decode('ascii')
    git_match = re.search(rb'[0-9a-f]{40}', data[:0x2000])
    if git_match:
        info['git_hash'] = git_match.group().decode('ascii')
    date_match = re.search(rb'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+[0-9]{1,2}\s+[0-9]{4}', data[:0x4000])
    if date_match:
        info['build_date'] = date_match.group().decode('ascii')
    platform_patterns = [
        (rb'mt[0-9]{4,5}', "MediaTek"),
        (rb'qcom', "Qualcomm"),
        (rb'msm[0-9]{4}', "Qualcomm MSM"),
        (rb'exynos', "Samsung Exynos"),
        (rb'kirin', "HiSilicon Kirin"),
        (rb'sprd', "Spreadtrum"),
        (rb'generic', "Generic"),
    ]
    for pattern, name in platform_patterns:
        if re.search(pattern, data[:0x8000], re.IGNORECASE):
            info['platform'] = name
            break
    return info


def detect_architecture(data):
    if len(data) >= 4:
        for p in [b'\x00\x00\xa0\xe1', b'\x1e\xff\x2f\xe1']:
            if p in data[:0x100]:
                return "ARM32 (AArch32)"
    if len(data) >= 8:
        for p in [b'\x1f\x20\x03\xd5', b'\xc0\x03\x5f\xd6']:
            if p in data[:0x100]:
                return "ARM64 (AArch64)"
    if len(data) >= 2 and data[:0x100].count(b'\x00\xbf') > 5:
        return "ARM32 (Thumb/Thumb-2)"
    return "Unknown"


def find_trusty_reference(data):
    patterns = [rb'trusty', rb'com\.android\.trusty', rb'secure\s+os', rb'tee[\s_-]os']
    found = []
    for pattern in patterns:
        if re.search(pattern, data, re.IGNORECASE):
            found.append(pattern.decode('ascii', errors='ignore'))
    return found


def print_info(image_name, _mia_output=None):
    path = Path(image_name)
    if not path.exists():
        if RICH_AVAILABLE:
            console.print(f"[red]❌ File not found: {image_name}[/red]")
        else:
            print(f"{RED}❌ File not found: {image_name}{RESET}")
        return

    data = path.read_bytes()
    size = len(data)
    lk_variant = detect_lk_variant(data)
    lk_info = parse_lk_header(data)
    arch = detect_architecture(data)
    tee_refs = find_trusty_reference(data)
    # strings = extract_strings(data, min_len=4)

    if RICH_AVAILABLE:
        console.print()
        console.print(Panel(Text(f"▓▒░ {image_name} ░▒▓ ❯", style="#8700af bold"), border_style="#8700af"))

        table = Table(title="🔐 BASIC INFO", title_style="bright_red", border_style="cyan")
        table.add_column("Field", style="bold white")
        table.add_column("Value", style="green")
        table.add_row("Size", format_size(size))
        table.add_row("Variant", lk_variant)
        table.add_row("Type", "Bootloader / TEE Loader")
        if 'version' in lk_info:
            table.add_row("Version", f"[yellow]{lk_info['version']}[/yellow]")
        if 'git_hash' in lk_info:
            git_short = lk_info['git_hash'][:8]
            table.add_row("Git Hash", f"[dim]{lk_info['git_hash'][:16]}...[/dim] ({git_short})")
        if 'build_date' in lk_info:
            table.add_row("Build Date", f"[green]{lk_info['build_date']}[/green]")
        if 'platform' in lk_info:
            table.add_row("Platform", f"[magenta]{lk_info['platform']}[/magenta]")
        console.print(table)

        arch_table = Table(title="🏛️ ARCHITECTURE", title_style="bright_red", border_style="cyan")
        arch_table.add_column("Field", style="bold white")
        arch_table.add_column("Value", style="green")
        arch_table.add_row("Detected", arch)
        console.print(arch_table)

        if tee_refs:
            tee_table = Table(title="🔒 TEE REFERENCES", title_style="bright_red", border_style="cyan")
            tee_table.add_column("Pattern", style="yellow")
            for ref in set(tee_refs):
                tee_table.add_row(ref)
            console.print(tee_table)

        hex_table = Table(title="🔢 HEX (first 64 bytes)", title_style="bright_red", border_style="cyan")
        hex_table.add_column("Offset")
        hex_table.add_column("Hex")
        hex_table.add_column("ASCII")
        for i in range(0, min(64, size), 16):
            chunk = data[i:i+16]
            hex_str = " ".join(f"{b:02x}" for b in chunk)
            ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            hex_table.add_row(f"0x{i:04x}", hex_str, ascii_str)
        console.print(hex_table)

        console.print(Panel(
            "[yellow]⚠️ SECURITY NOTE[/yellow]\n\n"
            "Little Kernel (LK) runs in Secure World (EL3).\n"
            "It loads Trusted OS and manages secure hardware.",
            border_style="yellow"
        ))
        console.print(Panel(
            "🇷🇺 LK — загрузчик в Secure World.\n"
            "🇬🇧 LK runs in Secure World (EL3).",
            border_style="red"
        ))
    else:
        print(f"\n  {MAGENTA}▓▒░ {image_name} ░▒▓ {CYAN}❯{RESET}")
        print(f"  {'═' * 50}")
        print(f"\n  {BRIGHT_RED}{BOLD}🔐 BASIC INFO{RESET}")
        print(f"  {'─' * 45}")
        print(f"  {BOLD}Size:{RESET} {GREEN}{format_size(size)}{RESET}")
        print(f"  {BOLD}Variant:{RESET} {YELLOW}{lk_variant}{RESET}")
        print(f"  {BOLD}Arch:{RESET} {BLUE}{arch}{RESET}")
        print()

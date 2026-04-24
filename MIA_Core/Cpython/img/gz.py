# img/gz.py
# ╔════════════════════════════════════════════════════════════════╗
# ║  Project: MIA Core - GZ Image Handler                         ║
# ║  Link: t.me/FrontendVSCode                                    ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                  ║
# ║  lang: python                                                 ║
# ║  [MIA-HASH-01] ΞΩ77Λβ99PPHD8A71                               ║
# ║  build: 3.10.15                                               ║
# ║  files: gz.py                                                 ║
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


def extract_strings(data, min_len=4):
    pattern = rb'[\x20-\x7E]{%d,}' % min_len
    return [s.decode("ascii", errors="ignore") for s in re.findall(pattern, data)]


def detect_gz_format(data):
    if data[:4] == b'GZ\x00\x00':
        return "MediaTek GZ (Secure OS)"
    if data[:4] == b'MTK\x00':
        return "MediaTek GZ (MTK)"
    if data[:8] == b'GZ_BOOT\x00':
        return "MediaTek GZ Bootloader"
    if data[:4] == b'GZFW':
        return "MediaTek GZ Firmware"
    if data[:4] == b'ATF\x00':
        return "ARM Trusted Firmware (ATF)"
    if data[:4] == b'\x7fELF':
        e_machine = struct.unpack('<H', data[18:20])[0] if len(data) > 20 else 0
        arch_map = {0x28: "ARM", 0xB7: "AArch64"}
        arch = arch_map.get(e_machine, "Unknown")
        return f"ELF ({arch}) - Secure World"
    return "Unknown GZ / Secure OS"


def parse_gz_header(data):
    info = {}
    if data[:4] == b'GZ\x00\x00':
        info['magic'] = 'GZ'
        if len(data) >= 8:
            info['version'] = struct.unpack('<I', data[4:8])[0]
    elif data[:4] == b'MTK\x00':
        info['magic'] = 'MTK'
    elif data[:4] == b'ATF\x00':
        info['magic'] = 'ATF'

    version_patterns = [
        rb'gz[_\-]?fw[_\-]?v?([0-9]+\.[0-9]+(?:\.[0-9]+)?)',
        rb'Trusted\s+Firmware\s+v([0-9]+\.[0-9]+(?:\.[0-9]+)?)',
        rb'ATF\s+v([0-9]+\.[0-9]+(?:\.[0-9]+)?)',
        rb'secure\s+os\s+v?([0-9]+\.[0-9]+(?:\.[0-9]+)?)',
    ]
    for pattern in version_patterns:
        version_match = re.search(pattern, data[:0x2000], re.IGNORECASE)
        if version_match:
            info['fw_version'] = version_match.group(1).decode('ascii')
            break

    date_match = re.search(rb'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+[0-9]{1,2}\s+[0-9]{4}', data[:0x3000])
    if date_match:
        info['build_date'] = date_match.group().decode('ascii')

    git_match = re.search(rb'[0-9a-f]{40}', data[:0x3000])
    if git_match:
        info['git_hash'] = git_match.group().decode('ascii')

    compiler_match = re.search(rb'GCC:\s*\([^\)]+\)\s*[0-9]+\.[0-9]+\.[0-9]+', data[:0x4000])
    if compiler_match:
        info['compiler'] = compiler_match.group().decode('ascii', errors='ignore')

    return info


def detect_architecture(data):
    if data[:4] == b'\x7fELF' and len(data) >= 20:
        e_machine = struct.unpack('<H', data[18:20])[0]
        if e_machine == 0xB7:
            return "ARM64 (AArch64) - Secure EL1/EL3"
        elif e_machine == 0x28:
            return "ARM32 (AArch32) - Secure World"
    if len(data) >= 8:
        for p in [b'\x1f\x20\x03\xd5', b'\xc0\x03\x5f\xd6', b'\xfd\x7b\xbf\xa9']:
            if p in data[:0x200]:
                return "ARM64 (AArch64) - Secure World"
    if len(data) >= 4:
        for p in [b'\x00\x00\xa0\xe1', b'\x1e\xff\x2f\xe1', b'\x00\xf0\x20\xe3']:
            if p in data[:0x200]:
                return "ARM32 (AArch32) - Secure World"
    return "Unknown"


def find_security_features(strings):
    features = []
    keywords = ['trustzone', 'secure', 'monitor', 'smc', 'hvc', 'el1', 'el3',
                'tee', 'trusty', 'optee', 'keymaster', 'gatekeeper', 'keystore',
                'crypto', 'aes', 'rsa', 'sha', 'hmac', 'cert', 'attestation']
    for s in strings:
        s_lower = s.lower()
        for kw in keywords:
            if kw in s_lower:
                features.append(s)
                break
    return features


def find_services(strings):
    services = []
    service_keywords = ['service', 'server', 'daemon', 'handler', 'dispatcher']
    for s in strings:
        s_lower = s.lower()
        if any(kw in s_lower for kw in service_keywords):
            if 'secure' in s_lower or 'trust' in s_lower or 'tee' in s_lower:
                services.append(s)
    return services


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

    gz_format = detect_gz_format(data)
    info_data = parse_gz_header(data)
    arch = detect_architecture(data)
    strings = extract_strings(data, min_len=4)
    features = find_security_features(strings)
    services = find_services(strings)

    if RICH_AVAILABLE:
        console.print()
        console.print(Panel(Text(f"▓▒░ {image_name} ░▒▓ ❯", style="#8700af bold"), border_style="#8700af"))

        table = Table(title="🔐 BASIC INFO", title_style="bright_red", border_style="cyan")
        table.add_column("Field", style="bold white")
        table.add_column("Value", style="green")
        table.add_row("Size", format_size(size))
        table.add_row("Format", gz_format)
        table.add_row("Type", "Secure OS / TrustZone")
        if info_data.get('magic'):
            table.add_row("Magic", f"[magenta]{info_data['magic']}[/magenta]")
        if info_data.get('version'):
            table.add_row("Version", f"[green]{info_data['version']}[/green]")
        if info_data.get('fw_version'):
            table.add_row("FW Version", f"[green]{info_data['fw_version']}[/green]")
        if info_data.get('build_date'):
            table.add_row("Build Date", f"[yellow]{info_data['build_date']}[/yellow]")
        if info_data.get('git_hash'):
            table.add_row("Git Hash", f"[dim]{info_data['git_hash'][:8]}...[/dim]")
        if info_data.get('compiler'):
            comp = info_data['compiler']
            table.add_row("Compiler", f"[blue]{comp[:47]}...[/blue]" if len(comp) > 50 else f"[blue]{comp}[/blue]")
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
            feat_table = Table(title="🔑 SECURITY FEATURES", title_style="bright_red", border_style="cyan")
            feat_table.add_column("Feature", style="green")
            seen = set()
            for f in features[:15]:
                if f not in seen:
                    seen.add(f)
                    feat_table.add_row(f[:57] + "..." if len(f) > 60 else f)
            console.print(feat_table)

        if services:
            serv_table = Table(title="📡 SECURE SERVICES", title_style="bright_red", border_style="cyan")
            serv_table.add_column("Service", style="yellow")
            seen = set()
            for s in services[:10]:
                if s not in seen:
                    seen.add(s)
                    serv_table.add_row(s[:57] + "..." if len(s) > 60 else s)
            console.print(serv_table)

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
            "GZ (Genie Zone) is MediaTek's Secure OS running in TrustZone (EL3).\n"
            "It manages critical security services:\n"
            "• Keymaster — hardware-backed key storage\n"
            "• Gatekeeper — authentication/verification\n"
            "• Crypto — secure cryptographic operations\n\n"
            "Communication with Normal World occurs via SMC calls.",
            border_style="yellow"
        ))
        console.print(Panel(
            "🇷🇺 GZ (Genie Zone) — Secure OS от MediaTek в TrustZone (EL3).\n"
            "Управляет критическими сервисами безопасности:\n"
            "• Keymaster — аппаратное хранение ключей\n"
            "• Gatekeeper — аутентификация\n"
            "• Crypto — криптографические операции\n\n"
            "🇬🇧 GZ is MediaTek's Secure OS in TrustZone (EL3).\n"
            "Manages Keymaster, Gatekeeper, and Crypto services.",
            border_style="red"
        ))
    else:
        print(f"\n  {MAGENTA}▓▒░ {image_name} ░▒▓ {CYAN}❯{RESET}")
        print(f"  {'═' * 50}")
        print(f"\n  {BRIGHT_RED}{BOLD}🔐 BASIC INFO{RESET}")
        print(f"  {'─' * 45}")
        print(f"  {BOLD}Size:{RESET} {GREEN}{format_size(size)}{RESET}")
        print(f"  {BOLD}Format:{RESET} {YELLOW}{gz_format}{RESET}")
        print(f"  {BOLD}Arch:{RESET} {BLUE}{arch}{RESET}")
        if info_data.get('fw_version'):
            print(f"  {BOLD}FW Ver:{RESET} {GREEN}{info_data['fw_version']}{RESET}")
        print()

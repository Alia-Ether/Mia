# img/tee.py

import re
import struct
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

# =========================
# Utils
# =========================


def format_size(size):
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def extract_strings(data, min_len=4):
    """Извлекает читаемые ASCII строки"""
    pattern = rb'[\x20-\x7E]{%d,}' % min_len
    return [s.decode("ascii", errors="ignore") for s in re.findall(pattern, data)]


def detect_format(data):
    """Определение формата TEE образа"""
    if data.startswith(b'\x7fELF'):
        return "ELF (Executable)"

    # Проверяем ATF (ARM Trusted Firmware)
    if b'atf' in data[:0x100]:
        return "ARM Trusted Firmware (ATF)"

    # Проверяем Trusty TEE (обычно магия "TRUSTY" или "TEE")
    if data[:6] == b'TRUSTY':
        return "Trusty TEE"
    if data[:4] == b'TEE\x00':
        return "Trusty TEE"

    # Проверяем OP-TEE (магия "OPTEE" или "OP-TEE")
    if b'OPTEE' in data[:0x200] or b'OP-TEE' in data[:0x200]:
        return "OP-TEE"

    # Проверяем Little Kernel (lk) как загрузчик TEE
    if data[:4] == b'LKT\x00' or data[:8] == b'LK_TRAMP':
        return "LK (Little Kernel) - TEE Bootloader"

    return "Unknown / Raw"


def parse_trusty_header(data):
    """Парсинг заголовка Trusty TEE"""
    info = {}

    if data[:6] == b'TRUSTY':
        info['magic'] = 'TRUSTY'
        if len(data) > 6:
            info['version'] = data[6:10].decode('ascii', errors='ignore')
    elif data[:4] == b'TEE\x00':
        info['magic'] = 'TEE'
        if len(data) > 4:
            # Попытка найти версию
            version_match = re.search(rb'v[0-9]+\.[0-9]+', data[:0x100])
            if version_match:
                info['version'] = version_match.group().decode('ascii')

    return info


def parse_optee_header(data):
    """Парсинг заголовка OP-TEE"""
    info = {}

    # Ищем строку с версией
    version_match = re.search(rb'OP-TEE version: ([0-9]+\.[0-9]+\.[0-9]+)', data[:0x1000])
    if version_match:
        info['version'] = version_match.group(1).decode('ascii')

    # Ищем UUID приложений
    uuid_pattern = re.compile(rb'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.IGNORECASE)
    uuids = uuid_pattern.findall(data[:0x2000])
    if uuids:
        info['uuids'] = [u.decode('ascii') for u in uuids[:5]]

    return info


# =========================
# Main
# =========================
def print_info(image_name, _mia_output=None):
    path = Path(image_name)

    if not path.exists():
        console.print(f"[red]❌ File not found: {image_name}[/red]")
        return

    data = path.read_bytes()
    size = len(data)
    tee_format = detect_format(data)

    console.print()
    console.print(Panel(
        Text(f"🔒 TEE IMAGE ANALYSIS: {image_name}", style="bold magenta"),
        border_style="magenta"
    ))

    # --- Basic info ---
    table = Table(title="🔐 BASIC INFO", border_style="cyan")
    table.add_column("Field", style="bold")
    table.add_column("Value", style="green")

    table.add_row("Size", format_size(size))
    table.add_row("Format", tee_format)
    table.add_row("Type", "Trusted Execution Environment")

    # Дополнительная информация в зависимости от формата
    if "Trusty" in tee_format:
        trusty_info = parse_trusty_header(data)
        if 'version' in trusty_info:
            table.add_row("Trusty Version", f"[yellow]{trusty_info['version']}[/yellow]")

    elif "OP-TEE" in tee_format:
        optee_info = parse_optee_header(data)
        if 'version' in optee_info:
            table.add_row("OP-TEE Version", f"[yellow]{optee_info['version']}[/yellow]")
        if 'uuids' in optee_info:
            table.add_row("Found UUIDs", str(len(optee_info['uuids'])))

    console.print(table)

    # --- Architecture detection ---
    if data.startswith(b'\x7fELF'):
        # Определяем архитектуру ELF
        arch_table = Table(title="🏛️ ARCHITECTURE", border_style="cyan")
        arch_table.add_column("Field", style="bold")
        arch_table.add_column("Value", style="green")

        e_machine = struct.unpack('<H', data[18:20])[0] if len(data) > 20 else 0
        arch_map = {0x28: "ARM", 0xB7: "ARM64/AArch64", 0x03: "x86", 0x3E: "x86_64"}
        arch = arch_map.get(e_machine, f"Unknown (0x{e_machine:04x})")

        arch_table.add_row("Architecture", arch)
        arch_table.add_row("Type", "Executable binary")

        console.print(arch_table)

    # --- Hex preview ---
    table_hex = Table(title="🔢 HEX (first 32 bytes)", border_style="cyan")
    table_hex.add_column("Offset")
    table_hex.add_column("Hex")
    table_hex.add_column("ASCII")

    for i in range(0, min(32, size), 16):
        chunk = data[i:i+16]
        hex_str = " ".join(f"{b:02x}" for b in chunk)
        ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        table_hex.add_row(f"0x{i:02x}", hex_str, ascii_str)

    console.print(table_hex)

    # --- Strings (расширенный) ---
    strings = extract_strings(data, min_len=4)

    if strings:
        # Фильтруем мусор
        filtered = [s for s in strings if not s.isdigit() and len(s) > 2]

        if filtered:
            table_str = Table(title="📝 STRINGS (preview)", border_style="cyan")
            table_str.add_column("Text", style="green")

            # Показываем уникальные строки
            seen = set()
            unique_strings = []
            for s in filtered:
                if s not in seen and len(s) > 3:
                    seen.add(s)
                    unique_strings.append(s)

            for s in unique_strings[:20]:
                # Ограничиваем длину строки
                if len(s) > 60:
                    s = s[:57] + "..."
                table_str.add_row(s)

            console.print(table_str)

    # --- Search for crypto related strings ---
    crypto_keywords = ['key', 'encrypt', 'decrypt', 'aes', 'rsa', 'sha', 'hmac', 'secure', 'trust']
    found_crypto = []
    for s in extract_strings(data, min_len=3):
        s_lower = s.lower()
        for kw in crypto_keywords:
            if kw in s_lower:
                found_crypto.append(s)
                break

    if found_crypto:
        table_crypto = Table(title="🔑 CRYPTO-RELATED STRINGS", border_style="yellow")
        table_crypto.add_column("Text", style="yellow")
        for s in found_crypto[:10]:
            if len(s) > 50:
                s = s[:47] + "..."
            table_crypto.add_row(s)
        console.print(table_crypto)

    # --- Security note ---
    console.print()
    console.print(Panel(
        "[yellow]⚠️ SECURITY NOTICE[/yellow]\n\n"
        "This tool extracts only readable text and metadata.\n"
        "Cryptographic keys and secure data stored in TEE cannot be extracted.\n"
        "TEE operates in Secure World and is isolated from normal OS access.",
        border_style="yellow"
    ))

    # --- Final notice RU/EN ---
    console.print()
    console.print(Panel(
        "🇷🇺 Этот образ содержит Trusted OS.\n"
        "Ключи и чувствительные данные защищены аппаратно.\n"
        "Извлечь их невозможно без использования уязвимостей.\n\n"
        "🇬🇧 This image contains Trusted OS.\n"
        "Keys and sensitive data are hardware-protected.\n"
        "Extraction is impossible without exploits.",
        border_style="red"
    ))

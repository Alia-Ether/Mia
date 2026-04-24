# img/boot.py
# ╔════════════════════════════════════════════════════════════════╗
# ║  Project: MIA Core - Boot Image Handler                       ║
# ║  Link: t.me/FrontendVSCode                                    ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                  ║
# ║  lang: python                                                 ║
# ║  [MIA-HASH-01] ΞΩ77Λβ99PPHD8A71                               ║
# ║  build: 3.10.15                                               ║
# ║  files: boot.py                                               ║
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


def extract_strings(data, min_len=4):
    """Извлечение ASCII строк из бинарных данных"""
    pattern = rb'[\x20-\x7E]{' + str(min_len).encode() + b',}'
    strings = []
    for match in re.findall(pattern, data):
        try:
            s = match.decode('ascii', errors='ignore')
            if len(s) >= min_len and not s.isspace():
                strings.append(s)
        except Exception:
            pass
    return strings


def detect_compression(data):
    """Определение типа сжатия ядра"""
    if len(data) < 6:
        return None
    if data[:2] == b'\x1f\x8b':
        return "GZIP"
    if data[:2] == b'\xfd7':
        return "XZ"
    if data[:3] == b'BZh':
        return "BZIP2"
    if data[:4] == b'\x02\x21\x4c\x18':
        return "LZ4"
    if data[:6] == b'\x89LZO\x00\x0d':
        return "LZO"
    if data[:2] == b'PK':
        return "ZIP"
    if data[:4] == b'\x5d\x00\x00\x00':
        return "LZMA"
    return None


def parse_android_bootimg(data, size):
    """Парсинг структуры Android boot.img"""
    info = {}

    # Проверяем магию ANDROID!
    if len(data) < 40 or data[:8] != b'ANDROID!':
        return None

    info['magic'] = 'ANDROID!'

    # Парсим заголовок boot_img_hdr_v4 (или более старые версии)
    kernel_size = struct.unpack('<I', data[8:12])[0]
    kernel_addr = struct.unpack('<I', data[12:16])[0]
    ramdisk_size = struct.unpack('<I', data[16:20])[0]
    ramdisk_addr = struct.unpack('<I', data[20:24])[0]
    second_size = struct.unpack('<I', data[24:28])[0]
    second_addr = struct.unpack('<I', data[28:32])[0]
    tags_addr = struct.unpack('<I', data[32:36])[0]
    page_size = struct.unpack('<I', data[36:40])[0]

    # Защита от нулевого page_size
    if page_size == 0:
        page_size = 2048  # Значение по умолчанию

    info['kernel_size'] = kernel_size
    info['kernel_addr'] = f"0x{kernel_addr:08x}"
    info['ramdisk_size'] = ramdisk_size
    info['ramdisk_addr'] = f"0x{ramdisk_addr:08x}"
    info['second_size'] = second_size
    info['second_addr'] = f"0x{second_addr:08x}"
    info['tags_addr'] = f"0x{tags_addr:08x}"
    info['page_size'] = page_size

    # Версия заголовка (смещение 40)
    header_version = 0
    if len(data) >= 44:
        header_version = struct.unpack('<I', data[40:44])[0]
    info['header_version'] = header_version

    # OS version и patch level (смещение 44-48)
    if len(data) > 44:
        os_version = struct.unpack('<I', data[44:48])[0]
        if os_version:
            patch_year = (os_version >> 4) & 0x7f + 2000
            patch_month = (os_version >> 0) & 0xf
            info['os_version'] = f"{patch_year}-{patch_month:02d}"

    # Product name (смещение 48-64)
    if len(data) > 48:
        name_bytes = data[48:64].rstrip(b'\x00')
        if name_bytes:
            info['name'] = name_bytes.decode('ascii', errors='ignore')

    # Cmdline (смещение 64-576)
    if len(data) > 64:
        cmdline_bytes = data[64:576].rstrip(b'\x00')
        if cmdline_bytes:
            cmdline = cmdline_bytes.decode('ascii', errors='ignore')
            info['cmdline'] = cmdline
            # Извлекаем важные параметры
            for param in ['androidboot.slot_suffix', 'androidboot.slot', 'skip_override']:
                match = re.search(rf'{param}=(\S+)', cmdline)
                if match:
                    info[f'cmdline_{param}'] = match.group(1)

    # ID (SHA1 хеш)
    if len(data) > 576:
        id_bytes = data[576:608]
        if id_bytes and any(b != 0 for b in id_bytes):
            info['id'] = id_bytes.hex()

    # Дополнительные поля для v2+
    if header_version >= 1 and len(data) > 1640:
        dtb_size = struct.unpack('<I', data[1640:1644])[0]
        info['dtb_size'] = dtb_size

    if header_version >= 2 and len(data) > 1648:
        dtb_addr = struct.unpack('<Q', data[1648:1656])[0]
        info['dtb_addr'] = f"0x{dtb_addr:016x}"

    return info


def detect_kernel_info(data, kernel_size, page_size):
    """Анализ ядра"""
    info = {}

    if page_size == 0:
        page_size = 2048

    # Вычисляем смещение ядра (обычно page_size)
    kernel_offset = page_size
    if len(data) > kernel_offset and kernel_size > 0:
        kernel_data = data[kernel_offset:kernel_offset+min(kernel_size, 65536)]

        # Проверяем сжатие
        compression = detect_compression(kernel_data)
        if compression:
            info['compression'] = compression

        # Ищем версию ядра
        version_match = re.search(rb'Linux version (\S+)', kernel_data)
        if version_match:
            info['linux_version'] = version_match.group(1).decode('ascii', errors='ignore')

        # Ищем компилятор
        compiler_match = re.search(rb'GCC: \([^)]+\) (\d+\.\d+\.\d+)', kernel_data)
        if compiler_match:
            info['compiler'] = f"GCC {compiler_match.group(1).decode('ascii')}"

        # Архитектура
        if b'ARM64' in kernel_data or b'AArch64' in kernel_data:
            info['arch'] = 'ARM64'
        elif b'ARM' in kernel_data:
            info['arch'] = 'ARM'
        elif b'x86_64' in kernel_data:
            info['arch'] = 'x86_64'
        elif b'i386' in kernel_data or b'i686' in kernel_data:
            info['arch'] = 'x86'

    return info


def parse_ramdisk(data, ramdisk_size, page_size, kernel_size):
    """Анализ ramdisk"""
    info = {}

    # Защита от нулевого page_size
    if page_size == 0:
        page_size = 2048

    if ramdisk_size == 0:
        return info

    # Смещение ramdisk = page_size + выровненный kernel_size
    kernel_aligned = ((kernel_size + page_size - 1) // page_size) * page_size
    ramdisk_offset = page_size + kernel_aligned

    if len(data) > ramdisk_offset and ramdisk_size > 0:
        read_size = min(ramdisk_size, 131072)
        if ramdisk_offset + read_size > len(data):
            read_size = len(data) - ramdisk_offset

        if read_size > 0:
            ramdisk_data = data[ramdisk_offset:ramdisk_offset+read_size]

            # Проверяем сжатие
            compression = detect_compression(ramdisk_data)
            if compression:
                info['compression'] = compression
            else:
                # Проверяем cpio
                if len(ramdisk_data) >= 6:
                    if ramdisk_data[:6] == b'070701' or ramdisk_data[:6] == b'070702':
                        info['format'] = 'CPIO'
                    elif len(ramdisk_data) >= 5 and ramdisk_data[:5] == b'07070':
                        info['format'] = 'CPIO (old)'

            # Ищем важные файлы
            strings = extract_strings(ramdisk_data, min_len=5)
            important = []
            for s in strings:
                if any(x in s for x in ['init', 'fstab', '.rc', 'default.prop', 'sepolicy']):
                    important.append(s)
            if important:
                info['files'] = important[:10]

    return info


def print_info(image_name, miatool_output):
    """Главная функция вывода"""

    # Проверка на None
    if miatool_output is None:
        miatool_output = ""

    path = Path(image_name)
    if not path.exists():
        if RICH_AVAILABLE:
            console.print(f"[red]❌ Файл не найден: {image_name}[/red]")
        else:
            print(f"{RED}❌ Файл не найден: {image_name}{RESET}")
        return

    # Читаем файл для сырого анализа (первые 10MB)
    file_size = path.stat().st_size
    read_size = min(file_size, 10 * 1024 * 1024)
    with open(path, 'rb') as f:
        data = f.read(read_size)
    size = len(data)

    # Парсим bootimg структуру
    boot_info = parse_android_bootimg(data, size)

    # Если есть AVB вывод - парсим его
    avb_info = {}
    if miatool_output and "Footer version:" in miatool_output:
        avb_info['footer_version'] = re.search(r'Footer version:\s+(\S+)', miatool_output)
        avb_info['image_size'] = re.search(r'Image size:\s+(\d+)\s+bytes', miatool_output)
        avb_info['algorithm'] = re.search(r'Algorithm:\s+(\S+)', miatool_output)
        avb_info['rollback'] = re.search(r'Rollback Index:\s+(\d+)', miatool_output)
        avb_info['public_key'] = re.search(r'Public key \(sha1\):\s+(\S+)', miatool_output)
        avb_info['partition_name'] = re.search(r'Partition Name:\s+(\S+)', miatool_output)

    # Анализ ядра и ramdisk
    kernel_info = {}
    ramdisk_info = {}
    if boot_info:
        kernel_info = detect_kernel_info(data, boot_info.get('kernel_size', 0), boot_info.get('page_size', 2048))
        ramdisk_info = parse_ramdisk(data, boot_info.get('ramdisk_size', 0),
                                     boot_info.get('page_size', 2048),
                                     boot_info.get('kernel_size', 0))

    if RICH_AVAILABLE:
        console.print()
        console.print(Panel(Text(f"🚀 BOOT IMAGE ANALYSIS: {image_name}", style="bold magenta"), border_style="magenta"))

        # === БАЗОВАЯ ИНФОРМАЦИЯ ===
        table_basic = Table(title="📦 БАЗОВАЯ ИНФОРМАЦИЯ", border_style="cyan")
        table_basic.add_column("Параметр", style="bold white")
        table_basic.add_column("Значение", style="green")

        table_basic.add_row("Размер файла", format_size(file_size))
        table_basic.add_row("Тип", "Android Boot Image" if boot_info else "Raw / Unknown")

        if boot_info:
            table_basic.add_row("Header версия", str(boot_info.get('header_version', '0')))
            if boot_info.get('name'):
                table_basic.add_row("Имя", f"[cyan]{boot_info['name']}[/cyan]")
            if boot_info.get('os_version'):
                table_basic.add_row("OS Version", boot_info['os_version'])

        console.print(table_basic)

        # === ЗАГОЛОВОК BOOT.IMG ===
        if boot_info:
            table_header = Table(title="📋 ЗАГОЛОВОК BOOT.IMG", border_style="blue")
            table_header.add_column("Параметр", style="bold white")
            table_header.add_column("Значение", style="yellow")

            table_header.add_row(
                "Kernel size", f"{format_size(boot_info['kernel_size'])} ({boot_info['kernel_size']} bytes)")
            table_header.add_row("Kernel addr", boot_info['kernel_addr'])
            table_header.add_row(
                "Ramdisk size", f"{format_size(boot_info['ramdisk_size'])} ({boot_info['ramdisk_size']} bytes)")
            table_header.add_row("Ramdisk addr", boot_info['ramdisk_addr'])
            table_header.add_row("Second size", f"{format_size(boot_info['second_size'])}")
            table_header.add_row("Second addr", boot_info['second_addr'])
            table_header.add_row("Tags addr", boot_info['tags_addr'])
            table_header.add_row("Page size", f"{boot_info['page_size']} bytes")

            if boot_info.get('dtb_size'):
                table_header.add_row("DTB size", f"{format_size(boot_info['dtb_size'])}")
            if boot_info.get('dtb_addr'):
                table_header.add_row("DTB addr", boot_info['dtb_addr'])
            if boot_info.get('id'):
                table_header.add_row("ID (SHA1)", f"[dim]{boot_info['id'][:32]}...[/dim]")

            console.print(table_header)

        # === ЯДРО (KERNEL) ===
        if kernel_info:
            table_kernel = Table(title="⚙️ ЯДРО (KERNEL)", border_style="green")
            table_kernel.add_column("Параметр", style="bold white")
            table_kernel.add_column("Значение", style="green")

            if kernel_info.get('linux_version'):
                table_kernel.add_row("Linux Version", kernel_info['linux_version'])
            if kernel_info.get('compression'):
                table_kernel.add_row("Сжатие", kernel_info['compression'])
            if kernel_info.get('arch'):
                table_kernel.add_row("Архитектура", kernel_info['arch'])
            if kernel_info.get('compiler'):
                table_kernel.add_row("Компилятор", kernel_info['compiler'])

            if table_kernel.row_count > 0:
                console.print(table_kernel)

        # === RAMDISK ===
        if ramdisk_info:
            table_ramdisk = Table(title="💾 RAMDISK", border_style="yellow")
            table_ramdisk.add_column("Параметр", style="bold white")
            table_ramdisk.add_column("Значение", style="yellow")

            if ramdisk_info.get('format'):
                table_ramdisk.add_row("Формат", ramdisk_info['format'])
            if ramdisk_info.get('compression'):
                table_ramdisk.add_row("Сжатие", ramdisk_info['compression'])
            if ramdisk_info.get('files'):
                table_ramdisk.add_row("Файлы", "\n".join(ramdisk_info['files'][:5]))

            if table_ramdisk.row_count > 0:
                console.print(table_ramdisk)

        # === CMDLINE ===
        if boot_info and boot_info.get('cmdline'):
            table_cmdline = Table(title="📝 COMMAND LINE", border_style="magenta")
            table_cmdline.add_column("Параметр", style="bold white")
            table_cmdline.add_column("Значение", style="cyan")

            cmdline = boot_info['cmdline']
            if len(cmdline) > 100:
                table_cmdline.add_row("Full", cmdline[:100] + "...")
            else:
                table_cmdline.add_row("Full", cmdline)

            for key in ['cmdline_androidboot.slot_suffix', 'cmdline_androidboot.slot', 'cmdline_skip_override']:
                if boot_info.get(key):
                    table_cmdline.add_row(key.replace('cmdline_', ''), boot_info[key])

            console.print(table_cmdline)

        # === AVB ИНФОРМАЦИЯ ===
        if avb_info:
            table_avb = Table(title="🔒 AVB ИНФОРМАЦИЯ", border_style="red")
            table_avb.add_column("Параметр", style="bold white")
            table_avb.add_column("Значение", style="red")

            if avb_info.get('footer_version'):
                table_avb.add_row("Footer version", avb_info['footer_version'].group(1))
            if avb_info.get('image_size'):
                table_avb.add_row("Image size", format_size(avb_info['image_size'].group(1)))
            if avb_info.get('algorithm'):
                table_avb.add_row("Algorithm", avb_info['algorithm'].group(1))
            if avb_info.get('rollback'):
                table_avb.add_row("Rollback Index", avb_info['rollback'].group(1))
            if avb_info.get('partition_name'):
                table_avb.add_row("Partition", avb_info['partition_name'].group(1))
            if avb_info.get('public_key'):
                pk = avb_info['public_key'].group(1)
                table_avb.add_row("Public Key (SHA1)", f"[dim]{pk[:40]}...[/dim]")

            console.print(table_avb)
        else:
            console.print(Panel(
                "[yellow]⚠️ Образ не содержит AVB футера[/yellow]",
                border_style="yellow"
            ))

        # === HEX ПРЕВЬЮ ===
        hex_table = Table(title="🔢 HEX (первые 64 байта)", border_style="dim cyan")
        hex_table.add_column("Offset")
        hex_table.add_column("Hex")
        hex_table.add_column("ASCII")

        for i in range(0, min(64, size), 16):
            chunk = data[i:i+16]
            hex_str = " ".join(f"{b:02x}" for b in chunk)
            ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            hex_table.add_row(f"0x{i:04x}", hex_str, ascii_str)

        console.print(hex_table)

    else:
        # ANSI Fallback
        print(f"\n  {BOLD}{MAGENTA}🚀 BOOT IMAGE: {image_name}{RESET}")
        print(f"  {'═' * 50}")
        print(f"\n  {BOLD}Размер:{RESET} {GREEN}{format_size(file_size)}{RESET}")

        if boot_info:
            print(f"\n  {BOLD}{CYAN}📋 ЗАГОЛОВОК:{RESET}")
            print(f"  {'─' * 45}")
            print(f"  {BOLD}Kernel:{RESET} {format_size(boot_info['kernel_size'])} @ {boot_info['kernel_addr']}")
            print(f"  {BOLD}Ramdisk:{RESET} {format_size(boot_info['ramdisk_size'])} @ {boot_info['ramdisk_addr']}")
            print(f"  {BOLD}Page size:{RESET} {boot_info['page_size']} bytes")

            if kernel_info.get('linux_version'):
                print(f"\n  {BOLD}Linux:{RESET} {GREEN}{kernel_info['linux_version']}{RESET}")
            if kernel_info.get('compression'):
                print(f"  {BOLD}Сжатие:{RESET} {kernel_info['compression']}")

        if not boot_info:
            print(f"\n  {YELLOW}⚠️ Не является Android boot.img{RESET}")

        print()

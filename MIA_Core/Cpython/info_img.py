# Cpython/info_img.py
# ╔════════════════════════════════════════════════════════════════╗
# ║  Project: MIA Core - Info Image Dispatcher                    ║
# ║  Link: t.me/FrontendVSCode                                    ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                  ║
# ║  lang: python                                                 ║
# ║  [MIA-HASH-01] ΞΩ77Λβ99PPHD8A71                               ║
# ║  build: 3.10.15                                               ║
# ║  files: info_img.py                                           ║
# ╚════════════════════════════════════════════════════════════════╝

import sys
import subprocess
import os
import re
from pathlib import Path

MIATOOL_PATH = Path(__file__).parent.parent / "plugin/mia/miatool.py"

# Цвета ANSI
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
WHITE = '\033[97m'
BOLD = '\033[1m'
RESET = '\033[0m'

# Добавляем папку img в путь для импорта
sys.path.insert(0, str(Path(__file__).parent))


def find_file(filename):
    """Ищет файл: сначала как полный путь, потом в текущей директории"""
    # 1. Проверяем как абсолютный путь
    path = Path(filename)
    if path.exists():
        return path

    # 2. Проверяем относительно текущей директории
    current = Path.cwd() / filename
    if current.exists():
        return current

    # 3. Пробуем только имя файла в текущей директории
    name_only = Path(filename).name
    current_name = Path.cwd() / name_only
    if current_name.exists():
        return current_name

    # 4. Пробуем в папке со скриптом
    script_dir = Path(__file__).parent / name_only
    if script_dir.exists():
        return script_dir

    return None


def get_image_type(image_name):
    """Определяет тип образа по имени файла"""
    name_lower = image_name.lower()

    if "vbmeta_vendor" in name_lower:
        return "vbmeta_vendor"
    elif "vbmeta_system" in name_lower:
        return "vbmeta_system"
    elif "vbmeta" in name_lower:
        return "vbmeta"
    elif "vendor_boot" in name_lower:
        return "vendor_boot"
    elif "product" in name_lower:
        return "product"
    elif "boot" in name_lower:
        return "boot"
    elif "dtbo" in name_lower:
        return "dtbo"
    elif "preloader_raw" in name_lower:
        return "preloader_raw"
    elif "system_ext" in name_lower:
        return "system_ext"
    elif "system_dlkm" in name_lower:
        return "system_dlkm"
    elif "vendor_dlkm" in name_lower:
        return "vendor_dlkm"
    elif "odm_dlkm" in name_lower:
        return "odm_dlkm"
    elif "mi_ext" in name_lower:
        return "mi_ext"
    elif "vendor" in name_lower:
        return "vendor"
    elif "system" in name_lower:
        return "system"
    elif "tee" in name_lower:
        return "tee"
    elif "lk" in name_lower:
        return "lk"
    elif "logo" in name_lower:
        return "logo"
    elif "gz" in name_lower:
        return "gz"
    elif "scp" in name_lower:
        return "scp"
    elif "spmfw" in name_lower:
        return "spmfw"
    elif "sspm" in name_lower:
        return "sspm"
    elif "md1" in name_lower:
        return "md1"
    elif "preloader" in name_lower:
        return "preloader"
    else:
        return "unknown"


def format_size(bytes_size):
    if bytes_size == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def print_line(char='─', length=45):
    print(f"  {char * length}")


def print_section(title, icon=""):
    print(f"\n  {BOLD}{CYAN}{icon} {title}{RESET}")
    print_line('─')


def print_field(name, value, color=WHITE):
    value_str = str(value)
    if len(value_str) > 45:
        print(f"  {BOLD}{name}:{RESET}")
        for line in value_str.split('\n'):
            if line.strip():
                print(f"    {color}{line.strip()}{RESET}")
    else:
        print(f"  {BOLD}{name}:{RESET} {color}{value_str}{RESET}")


def print_simple_info(file_path, image_type):
    """Простой вывод для образов без MIA структуры"""
    print(f"\n  {BOLD}{CYAN}📦 {file_path.name}{RESET}")
    print_line('═', 45)
    print_section("ОСНОВНАЯ ИНФОРМАЦИЯ", "🔐")
    print_field("Тип", image_type.upper(), GREEN)
    print_field("Размер", format_size(file_path.stat().st_size), CYAN)
    print_field("Путь", str(file_path), WHITE)
    print_line('═', 45)
    print()


def parse_miatool_output(output):
    """Парсинг вывода miatool"""
    data = {
        'chain_partitions': [],
        'hash_partitions': [],
        'hashtree_partitions': [],
        'properties': {}
    }

    patterns = {
        'min_libmia': r'Minimum libmia version:\s+(\S+)',
        'algorithm': r'Algorithm:\s+(\S+)',
        'rollback_index': r'Rollback Index:\s+(\d+)',
        'flags': r'Flags:\s+(\d+)',
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            data[key] = match.group(1)

    size_match = re.search(r'Image size:\s+(\d+)\s+bytes', output)
    if size_match:
        data['image_size'] = int(size_match.group(1))

    key_match = re.search(r'Public key \(sha1\):\s+(\S+)', output)
    if key_match:
        data['public_key_sha1'] = key_match.group(1)

    # Chain Partition
    lines = output.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        if 'Chain Partition descriptor:' in line:
            chain = {}
            i += 1
            while i < len(lines) and i < len(lines):
                if 'Partition Name:' in lines[i]:
                    chain['name'] = lines[i].split('Partition Name:')[1].strip()
                elif 'Rollback Index Location:' in lines[i]:
                    chain['rollback_location'] = lines[i].split('Rollback Index Location:')[1].strip()
                i += 1
                if i < len(lines) and 'Chain Partition descriptor:' in lines[i]:
                    break
            if chain:
                data['chain_partitions'].append(chain)
        else:
            i += 1

    # Hash descriptors
    hash_pattern = r"Hash descriptor:\s+Image Size:\s+(\d+)\s+bytes\s+Hash Algorithm:\s+(\S+)\s+Partition Name:\s+(\S+)"
    for match in re.finditer(hash_pattern, output):
        data['hash_partitions'].append({
            'name': match.group(3),
            'size': int(match.group(1)),
            'algorithm': match.group(2)
        })

    # Hashtree descriptors
    hashtree_pattern = r"Hashtree descriptor:.*?Image Size:\s+(\d+)\s+bytes.*?Partition Name:\s+(\S+)"
    for match in re.finditer(hashtree_pattern, output, re.DOTALL):
        data['hashtree_partitions'].append({
            'name': match.group(2),
            'size': int(match.group(1))
        })

    # Properties
    prop_pattern = r"Prop:\s+([^\s]+)\s+->\s+'([^']+)'"
    for match in re.finditer(prop_pattern, output):
        data['properties'][match.group(1)] = match.group(2)

    return data


def print_beautiful_output(data, image_name):
    """Красивый вывод (общий)"""

    if "vbmeta" in image_name.lower():
        image_type = "VBMETA"
    elif "boot" in image_name.lower():
        image_type = "BOOT"
    else:
        image_type = "IMAGE"

    print(f"\n  {BOLD}{CYAN}📦 {image_name}{RESET}")
    print_line('═', 45)

    print_section("ОСНОВНАЯ ИНФОРМАЦИЯ", "🔐")
    print_field("Тип", image_type, GREEN)
    print_field("Алгоритм", data.get('algorithm', 'N/A'), YELLOW)
    if data.get('public_key_sha1'):
        print_field("Ключ", data['public_key_sha1'][:40] + "...", MAGENTA)
    print_field("Размер", format_size(data.get('image_size', 0)), CYAN)
    print_field("Min Libmia", data.get('min_libmia', 'N/A'), WHITE)
    print_field("Rollback", data.get('rollback_index', '0'), YELLOW)
    print_field("Флаги", data.get('flags', '0'), WHITE)

    if data.get('chain_partitions'):
        print_section("ЦЕПОЧКИ ДОВЕРИЯ", "🔗")
        for chain in data['chain_partitions']:
            print(f"  📦 {BOLD}{chain['name']}{RESET}: слот отката {chain['rollback_location']}")

    if data.get('hash_partitions'):
        print_section("ХЕШИРОВАННЫЕ", "📋")
        for h in data['hash_partitions']:
            print(f"  🔒 {BOLD}{h['name']}{RESET}: {format_size(h['size'])} ({h['algorithm']})")

    if data.get('hashtree_partitions'):
        print_section("HASHTREE", "🌳")
        for ht in data['hashtree_partitions']:
            print(f"  🌿 {BOLD}{ht['name']}{RESET}: {format_size(ht['size'])}")

    props = data.get('properties', {})
    android_version = None
    security_patch = None
    fingerprint = None

    for key, value in props.items():
        if 'os_version' in key and '16' in value:
            android_version = "16"
        if 'security_patch' in key:
            security_patch = value
        if 'fingerprint' in key and not fingerprint:
            fingerprint = value

    if android_version or security_patch:
        print_section("ПРОШИВКА", "📱")
        if android_version:
            print_field("Android", android_version, GREEN)
        if security_patch:
            print_field("Патч", security_patch, YELLOW)
        if fingerprint:
            print_field("Fingerprint", fingerprint, CYAN)

    print_line('═', 45)
    print()


def run_miatool_raw(image_path):
    """Сырой вывод miatool"""
    file_path = find_file(image_path)
    if not file_path:
        print(f"❌ Файл не найден: {image_path}")
        return

    cmd = f'python3 {MIATOOL_PATH} info_image --image {file_path}'
    os.system(cmd)


def run_info():
    """Главная функция - диспетчер"""

    if len(sys.argv) < 3:
        print("❌ Использование: mia-core info <image.img>  или  mia-core info -e <image.img>")
        sys.exit(1)

    # Флаг -e (сырой вывод)
    if sys.argv[2] == "-e":
        if len(sys.argv) < 4:
            print("❌ Использование: mia-core info -e <image.img>")
            sys.exit(1)
        run_miatool_raw(sys.argv[3])
        return

    # Красивый вывод
    image_path = sys.argv[2]
    file_path = find_file(image_path)

    if not file_path:
        print(f"❌ Файл не найден: {image_path}")
        print(f"   Пробовал: {image_path}")
        print(f"   Текущая папка: {Path.cwd()}")
        return

    # Определяем тип образа
    image_type = get_image_type(file_path.name)

    print(f"{BLUE}🔍 Определён тип: {image_type}{RESET}")

    # ВСЕ типы с Rich-модулями (используют print_info)
    rich_types = [
        'tee', 'lk', 'product', 'system', 'vendor', 'boot',
        'vbmeta', 'vbmeta_system', 'vbmeta_vendor', 'dtbo',
        'scp', 'gz', 'logo', 'md1', 'mi_ext', 'odm_dlkm',
        'spmfw', 'sspm', 'preloader', 'preloader_raw',
        'system_ext', 'system_dlkm', 'vendor_dlkm', 'vendor_boot'
    ]

    # Пытаемся импортировать специальный модуль из папки img
    try:
        # Добавляем путь к папке img
        img_path = str(Path(__file__).parent / "img")
        if img_path not in sys.path:
            sys.path.insert(0, img_path)

        # Импортируем модуль
        module = __import__(image_type)
        if hasattr(module, "print_info"):
            # Для Rich-модулей пробуем miatool, но если не работает - вызываем без него
            if image_type in rich_types:
                # Пробуем miatool
                try:
                    cmd = [sys.executable, str(MIATOOL_PATH), "info_image", "--image", str(file_path)]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

                    if result.returncode == 0:
                        module.print_info(str(file_path), result.stdout)
                    else:
                        module.print_info(str(file_path), None)
                except Exception as e:
                    # Если miatool упал - вызываем без него
                    print(f"{YELLOW}⚠️ miatool упал: {e}{RESET}")
                    module.print_info(str(file_path), None)
                return
            else:
                # Для остальных - только miatool
                cmd = [sys.executable, str(MIATOOL_PATH), "info_image", "--image", str(file_path)]
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    module.print_info(str(file_path), result.stdout)
                else:
                    print_simple_info(file_path, image_type)
                return
    except ImportError as e:
        print(f"{YELLOW}⚠️ Модуль {image_type} не найден: {e}{RESET}")

    # Если нет специального модуля, пробуем miatool
    cmd = [sys.executable, str(MIATOOL_PATH), "info_image", "--image", str(file_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print_simple_info(file_path, image_type)
        return

    data = parse_miatool_output(result.stdout)
    print_beautiful_output(data, str(file_path))

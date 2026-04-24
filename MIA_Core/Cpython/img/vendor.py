# img/vendor.py
# ╔════════════════════════════════════════════════════════════════╗
# ║  Project: MIA Core - Vendor Image Handler                     ║
# ║  Link: t.me/FrontendVSCode                                    ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                  ║
# ║  lang: python                                                 ║
# ║  [MIA-HASH-01] ΞΩ77Λβ99PPHD8A71                               ║
# ║  build: 3.10.15                                               ║
# ║  files: vendor.py                                             ║
# ╚════════════════════════════════════════════════════════════════╝

import re
import struct
import subprocess
from pathlib import Path

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


def format_size(bytes_size):
    """Форматирование размера"""
    if not bytes_size:
        return "N/A"
    try:
        size = int(bytes_size)
    except Exception:
        return str(bytes_size)

    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"


def extract_strings_from_file(image_path, min_len=6, max_strings=30):
    """Извлечение строк из файла через внешнюю утилиту strings или встроенный парсер"""
    path = Path(image_path)
    if not path.exists():
        return []

    strings_list = []

    # Пробуем внешнюю утилиту strings
    try:
        result = subprocess.run(
            ['strings', '-n', str(min_len), str(path)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            # Фильтруем мусор
            for line in lines:
                line = line.strip()
                if line and not line.isdigit() and len(line) >= min_len:
                    # Пропускаем бинарный мусор
                    if any(ord(c) < 32 and c not in '\t\n\r' for c in line):
                        continue
                    strings_list.append(line)
            return strings_list[:max_strings]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: встроенный парсер (первые 10MB)
    try:
        with open(path, 'rb') as f:
            data = f.read(10 * 1024 * 1024)
        pattern = rb'[\x20-\x7E]{' + str(min_len).encode() + b',}'
        for match in re.findall(pattern, data):
            try:
                s = match.decode('ascii', errors='ignore')
                if s and not s.isdigit() and len(s) >= min_len:
                    strings_list.append(s)
            except Exception:
                pass
    except Exception:
        pass

    # Убираем дубликаты
    seen = set()
    unique = []
    for s in strings_list:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return unique[:max_strings]


def extract_build_props_from_strings(strings):
    """Извлечение build.prop записей из списка строк"""
    props = {}
    for s in strings:
        if '=' in s and not s.startswith(' '):
            parts = s.split('=', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                if key and value and len(key) < 100 and len(value) < 200:
                    # Только правдоподобные ключи
                    if '.' in key or key.startswith('ro.') or key.startswith('persist.'):
                        props[key] = value
    return props


def parse_avb_footer_direct_force(image_path, endian):
    """Принудительное чтение AVB футера с указанным порядком байт"""
    path = Path(image_path)
    if not path.exists():
        return None

    try:
        with open(path, 'rb') as f:
            f.seek(-64, 2)
            footer = f.read(64)

        if footer[:4] not in (b'AVBf', b'AVB0'):
            return None

        end = '>' if endian == 'big' else '<'
        return {
            'magic': footer[:4].decode('ascii'),
            'version_major': struct.unpack(end + 'I', footer[4:8])[0],
            'version_minor': struct.unpack(end + 'I', footer[8:12])[0],
            'vbmeta_offset': struct.unpack(end + 'Q', footer[16:24])[0],
            'vbmeta_size': struct.unpack(end + 'Q', footer[24:32])[0],
            'endian': endian
        }
    except Exception:
        return None


def parse_vbmeta_from_offset(image_path, vbmeta_offset, vbmeta_size, endian='big'):
    """Чтение и парсинг VBMeta структуры по смещению"""
    path = Path(image_path)
    if not path.exists():
        return None

    try:
        with open(path, 'rb') as f:
            f.seek(vbmeta_offset)
            vbmeta_data = f.read(min(vbmeta_size, 65536))

        if vbmeta_data[:4] != b'AVB0':
            return None

        end = '>' if endian == 'big' else '<'

        info = {
            'magic': vbmeta_data[:4].decode('ascii'),
            'required_libavb_version_major': struct.unpack(end + 'I', vbmeta_data[4:8])[0],
            'required_libavb_version_minor': struct.unpack(end + 'I', vbmeta_data[8:12])[0],
            'authentication_data_block_size': struct.unpack(end + 'Q', vbmeta_data[12:20])[0],
            'auxiliary_data_block_size': struct.unpack(end + 'Q', vbmeta_data[20:28])[0],
            'algorithm_type': struct.unpack(end + 'I', vbmeta_data[28:32])[0],
            'hash_offset': struct.unpack(end + 'Q', vbmeta_data[32:40])[0],
            'hash_size': struct.unpack(end + 'Q', vbmeta_data[40:48])[0],
            'signature_offset': struct.unpack(end + 'Q', vbmeta_data[48:56])[0],
            'signature_size': struct.unpack(end + 'Q', vbmeta_data[56:64])[0],
            'public_key_offset': struct.unpack(end + 'Q', vbmeta_data[64:72])[0],
            'public_key_size': struct.unpack(end + 'Q', vbmeta_data[72:80])[0],
            'public_key_metadata_offset': struct.unpack(end + 'Q', vbmeta_data[80:88])[0],
            'public_key_metadata_size': struct.unpack(end + 'Q', vbmeta_data[88:96])[0],
            'descriptors_offset': struct.unpack(end + 'Q', vbmeta_data[96:104])[0],
            'descriptors_size': struct.unpack(end + 'Q', vbmeta_data[104:112])[0],
            'rollback_index': struct.unpack(end + 'Q', vbmeta_data[112:120])[0],
            'flags': struct.unpack(end + 'I', vbmeta_data[120:124])[0],
            'release_string': vbmeta_data[128:176].split(b'\x00')[0].decode('ascii', errors='ignore'),
        }

        alg_map = {
            0: "NONE",
            1: "SHA256_RSA2048",
            2: "SHA256_RSA4096",
            3: "SHA256_RSA8192",
            4: "SHA512_RSA2048",
            5: "SHA512_RSA4096",
            6: "SHA512_RSA8192",
        }
        info['algorithm_name'] = alg_map.get(info['algorithm_type'], f"Unknown ({info['algorithm_type']})")

        descriptors = parse_descriptors(vbmeta_data, info['descriptors_offset'],
                                        info['descriptors_size'], endian)
        info['descriptors'] = descriptors

        return info
    except Exception:
        return None


def parse_descriptors(data, offset, size, endian='big'):
    """Парсинг дескрипторов VBMeta"""
    if offset == 0 or size == 0:
        return []

    descriptors = []
    pos = offset
    end = offset + size
    endian_char = '>' if endian == 'big' else '<'

    while pos < end and pos < len(data):
        if pos + 16 > len(data):
            break

        tag = struct.unpack(endian_char + 'Q', data[pos:pos+8])[0]
        desc_size = struct.unpack(endian_char + 'Q', data[pos+8:pos+16])[0]

        if desc_size == 0 or pos + desc_size > len(data):
            break

        desc_data = data[pos:pos+desc_size]

        tag_names = {
            0: "PROPERTY",
            1: "HASHTREE",
            2: "HASH",
            3: "KERNEL_CMDLINE",
            4: "CHAIN_PARTITION",
        }

        desc_info = {
            'tag': tag_names.get(tag, f"UNKNOWN (0x{tag:016x})"),
            'size': desc_size,
        }

        if tag == 0 and desc_size > 16:          # PROPERTY
            key_len = struct.unpack(endian_char + 'Q', desc_data[16:24])[0]
            value_len = struct.unpack(endian_char + 'Q', desc_data[24:32])[0]
            if 32 + key_len + value_len <= len(desc_data):
                key = desc_data[32:32+key_len].decode('ascii', errors='ignore')
                value = desc_data[32+key_len:32+key_len+value_len].decode('ascii', errors='ignore')
                desc_info['key'] = key
                desc_info['value'] = value

        elif tag == 1 and desc_size >= 120:      # HASHTREE
            desc_info['dm_verity_version'] = struct.unpack(endian_char + 'I', desc_data[16:20])[0]
            desc_info['image_size'] = struct.unpack(endian_char + 'Q', desc_data[20:28])[0]
            desc_info['tree_offset'] = struct.unpack(endian_char + 'Q', desc_data[28:36])[0]
            desc_info['tree_size'] = struct.unpack(endian_char + 'Q', desc_data[36:44])[0]
            desc_info['data_block_size'] = struct.unpack(endian_char + 'I', desc_data[44:48])[0]
            desc_info['hash_block_size'] = struct.unpack(endian_char + 'I', desc_data[48:52])[0]
            desc_info['fec_num_roots'] = struct.unpack(endian_char + 'I', desc_data[52:56])[0]
            desc_info['fec_offset'] = struct.unpack(endian_char + 'Q', desc_data[56:64])[0]
            desc_info['fec_size'] = struct.unpack(endian_char + 'Q', desc_data[64:72])[0]
            desc_info['hash_algorithm'] = desc_data[72:104].split(b'\x00')[0].decode('ascii', errors='ignore')
            desc_info['partition_name_len'] = struct.unpack(endian_char + 'I', desc_data[104:108])[0]
            desc_info['salt_len'] = struct.unpack(endian_char + 'I', desc_data[108:112])[0]
            desc_info['root_digest_len'] = struct.unpack(endian_char + 'I', desc_data[112:116])[0]
            desc_info['flags'] = struct.unpack(endian_char + 'I', desc_data[116:120])[0]
            name_offset = 120
            if name_offset + desc_info['partition_name_len'] <= len(desc_data):
                desc_info['partition_name'] = desc_data[name_offset:name_offset +
                                                        desc_info['partition_name_len']].decode('ascii', errors='ignore')

        elif tag == 4 and desc_size > 16:        # CHAIN_PARTITION
            rollback_loc = struct.unpack(endian_char + 'I', desc_data[16:20])[0]
            part_name_len = struct.unpack(endian_char + 'I', desc_data[20:24])[0]
            public_key_len = struct.unpack(endian_char + 'I', desc_data[24:28])[0]
            desc_info['rollback_index_location'] = rollback_loc
            desc_info['partition_name_len'] = part_name_len
            desc_info['public_key_len'] = public_key_len
            name_offset = 28
            if name_offset + part_name_len <= len(desc_data):
                desc_info['partition_name'] = desc_data[name_offset:name_offset +
                                                        part_name_len].decode('ascii', errors='ignore')

        descriptors.append(desc_info)
        pos += desc_size

    return descriptors


def print_info(image_name, miatool_output):
    """Вывод информации для vendor.img"""

    path = Path(image_name)
    file_size = path.stat().st_size if path.exists() else 0

    if miatool_output is None:
        miatool_output = ""

    # Если miatool_output пустой или не содержит AVB-данных — прямой разбор
    if not miatool_output or "Footer version:" not in miatool_output:
        avb_info_be = parse_avb_footer_direct_force(image_name, 'big')
        avb_info_le = parse_avb_footer_direct_force(image_name, 'little')

        print(f"\n  {BOLD}{MAGENTA}📦 VENDOR ОБРАЗ: {image_name}{RESET}")
        print(f"  {BOLD}{'═' * 55}{RESET}")
        print(f"\n  {BOLD}{CYAN}🔐 ОСНОВНАЯ ИНФОРМАЦИЯ{RESET}")
        print(f"  {BOLD}{'─' * 55}{RESET}")
        print(f"  {BOLD}Размер:{RESET} {GREEN}{format_size(file_size)}{RESET}")

        # Извлекаем строки напрямую
        strings = extract_strings_from_file(image_name, min_len=6, max_strings=50)
        build_props = extract_build_props_from_strings(strings)

        if build_props:
            print(f"\n  {BOLD}{CYAN}📝 BUILD.PROP (извлечено напрямую){RESET}")
            print(f"  {BOLD}{'─' * 55}{RESET}")
            for key, value in list(build_props.items())[:12]:
                if len(value) > 60:
                    value = value[:57] + "..."
                print(f"  {BOLD}{key}:{RESET} {GREEN}{value}{RESET}")

        # Важные строки (fingerprint, security patch и т.д.)
        important_strings = []
        for s in strings:
            if any(k in s.lower() for k in ['fingerprint', 'security_patch', 'os_version', 'build.id', 'build.version']):
                important_strings.append(s)

        if important_strings:
            print(f"\n  {BOLD}{CYAN}📌 ВАЖНЫЕ СТРОКИ{RESET}")
            print(f"  {BOLD}{'─' * 55}{RESET}")
            for s in important_strings[:10]:
                if len(s) > 60:
                    s = s[:57] + "..."
                print(f"  {YELLOW}• {s}{RESET}")

        # Пробуем оба порядка байт для AVB футера
        found_vbmeta = False
        for avb_info in [avb_info_be, avb_info_le]:
            if not avb_info:
                continue

            print(f"\n  {BOLD}{CYAN}📌 AVB FOOTER ({avb_info['endian']}-endian){RESET}")
            print(f"  {BOLD}{'─' * 55}{RESET}")
            print(f"  {BOLD}Magic:{RESET}          {GREEN}{avb_info['magic']}{RESET}")
            print(f"  {BOLD}Version:{RESET}        {avb_info['version_major']}.{avb_info['version_minor']}")
            print(f"  {BOLD}VBMeta offset:{RESET}  {YELLOW}{avb_info['vbmeta_offset']}{RESET}")
            print(f"  {BOLD}VBMeta size:{RESET}    {YELLOW}{avb_info['vbmeta_size']} bytes{RESET}")

            if avb_info['vbmeta_offset'] + avb_info['vbmeta_size'] > file_size:
                print(f"  {RED}⚠️ VBMeta выходит за пределы файла{RESET}")
                continue

            vbmeta_info = parse_vbmeta_from_offset(
                image_name,
                avb_info['vbmeta_offset'],
                avb_info['vbmeta_size'],
                avb_info['endian']
            )

            if vbmeta_info:
                found_vbmeta = True
                print(f"\n  {BOLD}{CYAN}🔐 VBMETA СТРУКТУРА{RESET}")
                print(f"  {BOLD}{'─' * 55}{RESET}")
                print(f"  {BOLD}Algorithm:{RESET}         {GREEN}{vbmeta_info['algorithm_name']}{RESET}")
                print(f"  {BOLD}Rollback Index:{RESET}    {RED}{vbmeta_info['rollback_index']}{RESET}")
                print(f"  {BOLD}Flags:{RESET}             {WHITE}{vbmeta_info['flags']}{RESET}")
                if vbmeta_info.get('release_string'):
                    print(f"  {BOLD}Release String:{RESET}    {CYAN}{vbmeta_info['release_string'][:50]}{RESET}")

                if vbmeta_info.get('descriptors'):
                    print(f"\n  {BOLD}{CYAN}📋 ДЕСКРИПТОРЫ{RESET}")
                    print(f"  {BOLD}{'─' * 55}{RESET}")
                    for desc in vbmeta_info['descriptors'][:15]:
                        if desc['tag'] == 'PROPERTY':
                            print(f"  {GREEN}• PROPERTY:{RESET} {desc.get('key', '?')} = {desc.get('value', '?')[:50]}")
                        elif desc['tag'] == 'CHAIN_PARTITION':
                            print(f"  {YELLOW}• CHAIN:{RESET} {desc.get('partition_name', '?')}")
                        elif desc['tag'] == 'HASHTREE':
                            print(
                                f"  {BLUE}• HASHTREE:{RESET} {desc.get('partition_name', '?')} ({format_size(desc.get('image_size', 0))})")

                print(f"\n  {BOLD}{RED}🔒 ARB (Anti-Rollback){RESET}")
                print(f"  {BOLD}{'─' * 55}{RESET}")
                print(f"  {BOLD}Rollback Index:{RESET}    {RED}{vbmeta_info['rollback_index']}{RESET}")
                print(f"  {BOLD}Внимание:{RESET}          {YELLOW}Откат на версию с меньшим индексом невозможен{RESET}")
                break  # Нашли рабочий — выходим

        if not found_vbmeta:
            print(f"\n  {BOLD}{RED}🔒 ARB (Anti-Rollback){RESET}")
            print(f"  {BOLD}{'─' * 55}{RESET}")
            print(f"  {BOLD}Статус:{RESET}          {YELLOW}Не удалось прочитать VBMeta{RESET}")
            print(f"  {BOLD}Причина:{RESET}         {WHITE}Футер найден, но VBMeta структура повреждена или не по смещению{RESET}")

        print(f"\n  {BOLD}{'═' * 55}{RESET}\n")
        return

    # ========== ПАРСИНГ MIATOOL (если вывод есть) ==========
    # ... (оставь без изменений, как в предыдущей версии)

    # ========== ПАРСИНГ MIATOOL (если вывод есть) ==========
    footer_version = re.search(r'Footer version:\s+(\S+)', miatool_output)
    image_size = re.search(r'Image size:\s+(\d+)\s+bytes', miatool_output)
    original_size = re.search(r'Original image size:\s+(\d+)\s+bytes', miatool_output)
    vbmeta_offset = re.search(r'VBMeta offset:\s+(\d+)', miatool_output)
    vbmeta_size = re.search(r'VBMeta size:\s+(\d+)\s+bytes', miatool_output)

    min_libmia = re.search(r'Minimum libmia version:\s+(\S+)', miatool_output)
    header_block = re.search(r'Header Block:\s+(\d+)\s+bytes', miatool_output)
    auth_block = re.search(r'Authentication Block:\s+(\d+)\s+bytes', miatool_output)
    aux_block = re.search(r'Auxiliary Block:\s+(\d+)\s+bytes', miatool_output)
    algorithm = re.search(r'Algorithm:\s+(\S+)', miatool_output)
    rollback = re.search(r'Rollback Index:\s+(\d+)', miatool_output)
    flags = re.search(r'Flags:\s+(\d+)', miatool_output)
    rollback_loc = re.search(r'Rollback Index Location:\s+(\d+)', miatool_output)
    release_string = re.search(r"Release String:\s+'([^']+)'", miatool_output)

    dm_version = re.search(r'Version of dm-verity:\s+(\d+)', miatool_output)
    tree_offset = re.search(r'Tree Offset:\s+(\d+)', miatool_output)
    tree_size = re.search(r'Tree Size:\s+(\d+)\s+bytes', miatool_output)
    data_block = re.search(r'Data Block Size:\s+(\d+)\s+bytes', miatool_output)
    hash_block = re.search(r'Hash Block Size:\s+(\d+)\s+bytes', miatool_output)
    fec_roots = re.search(r'FEC num roots:\s+(\d+)', miatool_output)
    fec_offset = re.search(r'FEC offset:\s+(\d+)', miatool_output)
    fec_size = re.search(r'FEC size:\s+(\d+)\s+bytes', miatool_output)
    hash_alg = re.search(r'Hash Algorithm:\s+(\S+)', miatool_output)
    partition_name = re.search(r'Partition Name:\s+(\S+)', miatool_output)
    salt = re.search(r'Salt:\s+(\S+)', miatool_output)
    root_digest = re.search(r'Root Digest:\s+(\S+)', miatool_output)

    os_version = re.search(r'com\.android\.build\.vendor\.os_version\s+->\s+\'([^\']+)\'', miatool_output)
    fingerprint = re.search(r'com\.android\.build\.vendor\.fingerprint\s+->\s+\'([^\']+)\'', miatool_output)
    security_patch = re.search(r'com\.android\.build\.vendor\.security_patch\s+->\s+\'([^\']+)\'', miatool_output)

    arb_index = None
    if rollback:
        arb_index = rollback.group(1)

    print(f"\n  {BOLD}{MAGENTA}📦 VENDOR ОБРАЗ: {image_name}{RESET}")
    print(f"  {BOLD}{'═' * 55}{RESET}")

    print(f"\n  {BOLD}{CYAN}🔐 ОСНОВНАЯ ИНФОРМАЦИЯ{RESET}")
    print(f"  {BOLD}{'─' * 55}{RESET}")

    if footer_version:
        print(f"  {BOLD}Версия Footer:{RESET}        {GREEN}{footer_version.group(1)}{RESET}")
    if image_size:
        print(f"  {BOLD}Размер образа:{RESET}         {GREEN}{format_size(image_size.group(1))}{RESET} ({image_size.group(1)} bytes)")
    if original_size:
        print(f"  {BOLD}Оригинальный размер:{RESET}   {GREEN}{format_size(original_size.group(1))}{RESET} ({original_size.group(1)} bytes)")
    if vbmeta_offset:
        print(f"  {BOLD}VBMeta смещение:{RESET}       {YELLOW}{vbmeta_offset.group(1)}{RESET}")
    if vbmeta_size:
        print(f"  {BOLD}VBMeta размер:{RESET}         {YELLOW}{vbmeta_size.group(1)} bytes{RESET}")

    if arb_index:
        print(f"\n  {BOLD}{RED}🔒 ARB (Anti-Rollback) INDEX{RESET}")
        print(f"  {BOLD}{'─' * 55}{RESET}")
        print(f"  {BOLD}Rollback Index:{RESET}        {RED}{arb_index}{RESET}")
        print(f"  {BOLD}Внимание:{RESET}              {YELLOW}Откат на версию с меньшим индексом невозможен{RESET}")

    print(f"\n  {BOLD}{CYAN}📋 ЗАГОЛОВКИ{RESET}")
    print(f"  {BOLD}{'─' * 55}{RESET}")

    if min_libmia:
        print(f"  {BOLD}Min libmia версия:{RESET}     {WHITE}{min_libmia.group(1)}{RESET}")
    if header_block:
        print(f"  {BOLD}Header Block:{RESET}          {WHITE}{header_block.group(1)} bytes{RESET}")
    if auth_block:
        print(f"  {BOLD}Authentication Block:{RESET}  {WHITE}{auth_block.group(1)} bytes{RESET}")
    if aux_block:
        print(f"  {BOLD}Auxiliary Block:{RESET}       {WHITE}{aux_block.group(1)} bytes{RESET}")
    if algorithm:
        algo_color = RED if algorithm.group(1) == "NONE" else GREEN
        print(f"  {BOLD}Алгоритм:{RESET}              {algo_color}{algorithm.group(1)}{RESET}")
    if rollback and not arb_index:
        print(f"  {BOLD}Rollback Index:{RESET}        {RED}{rollback.group(1)}{RESET}")
    if flags:
        print(f"  {BOLD}Флаги:{RESET}                 {WHITE}{flags.group(1)}{RESET}")
    if rollback_loc:
        print(f"  {BOLD}Rollback Index Location:{RESET} {WHITE}{rollback_loc.group(1)}{RESET}")
    if release_string:
        print(f"  {BOLD}Release String:{RESET}        {CYAN}{release_string.group(1)}{RESET}")

    if partition_name:
        print(f"\n  {BOLD}{CYAN}🌳 HASHTREE (DM-VERITY){RESET}")
        print(f"  {BOLD}{'─' * 55}{RESET}")

        if dm_version:
            print(f"  {BOLD}Версия dm-verity:{RESET}     {WHITE}{dm_version.group(1)}{RESET}")
        if partition_name:
            print(f"  {BOLD}Имя раздела:{RESET}          {GREEN}{partition_name.group(1)}{RESET}")
        if hash_alg:
            print(f"  {BOLD}Хеш алгоритм:{RESET}         {YELLOW}{hash_alg.group(1)}{RESET}")
        if image_size:
            print(f"  {BOLD}Размер данных:{RESET}         {GREEN}{format_size(image_size.group(1))}{RESET}")
        if tree_offset:
            print(f"  {BOLD}Смещение дерева:{RESET}       {WHITE}{tree_offset.group(1)}{RESET}")
        if tree_size:
            print(f"  {BOLD}Размер дерева:{RESET}         {GREEN}{format_size(tree_size.group(1))}{RESET}")
        if data_block:
            print(f"  {BOLD}Блок данных:{RESET}           {WHITE}{data_block.group(1)} bytes{RESET}")
        if hash_block:
            print(f"  {BOLD}Блок хешей:{RESET}            {WHITE}{hash_block.group(1)} bytes{RESET}")
        if fec_roots:
            print(f"  {BOLD}FEC корней:{RESET}            {WHITE}{fec_roots.group(1)}{RESET}")
        if fec_offset:
            print(f"  {BOLD}FEC смещение:{RESET}          {WHITE}{fec_offset.group(1)}{RESET}")
        if fec_size:
            print(f"  {BOLD}FEC размер:{RESET}            {GREEN}{format_size(fec_size.group(1))}{RESET}")
        if salt:
            salt_val = salt.group(1)
            if len(salt_val) > 40:
                print(f"  {BOLD}Salt:{RESET}                  {MAGENTA}{salt_val[:40]}...{RESET}")
            else:
                print(f"  {BOLD}Salt:{RESET}                  {MAGENTA}{salt_val}{RESET}")
        if root_digest:
            digest_val = root_digest.group(1)
            if len(digest_val) > 40:
                print(f"  {BOLD}Root Digest:{RESET}            {MAGENTA}{digest_val[:40]}...{RESET}")
            else:
                print(f"  {BOLD}Root Digest:{RESET}            {MAGENTA}{digest_val}{RESET}")

    if os_version or fingerprint or security_patch:
        print(f"\n  {BOLD}{CYAN}📱 СВОЙСТВА ПРОШИВКИ{RESET}")
        print(f"  {BOLD}{'─' * 55}{RESET}")

        if os_version:
            print(f"  {BOLD}Версия Android OS:{RESET}     {GREEN}{os_version.group(1)}{RESET}")
        if security_patch:
            print(f"  {BOLD}Патч безопасности:{RESET}     {YELLOW}{security_patch.group(1)}{RESET}")
        if fingerprint:
            fp = fingerprint.group(1)
            if len(fp) > 50:
                print(f"  {BOLD}Fingerprint:{RESET}")
                for i in range(0, len(fp), 50):
                    print(f"    {CYAN}{fp[i:i+50]}{RESET}")
            else:
                print(f"  {BOLD}Fingerprint:{RESET}        {CYAN}{fp}{RESET}")

    print(f"\n  {BOLD}{'═' * 55}{RESET}\n")

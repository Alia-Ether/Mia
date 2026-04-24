# core/payload_parser.py
import struct
from pathlib import Path
from .ui import info, error, step


class PayloadParser:
    def __init__(self, payload_path: str):
        self.path = Path(payload_path)
        self.metadata = {}

    def parse_metadata(self):
        """Чтение заголовка payload.bin"""
        step(f"Анализ: {self.path.name}")

        with open(self.path, 'rb') as f:
            # Читаем магию "CrAU"
            magic = f.read(4)
            if magic != b'CrAU':
                error("Неверный формат payload.bin")
                return False

            # Версия
            version = struct.unpack('<Q', f.read(8))[0]
            info(f"Версия протокола: {version}")

            # Размер манифеста
            manifest_size = struct.unpack('<Q', f.read(8))[0]
            info(f"Размер манифеста: {manifest_size} байт")

            self.metadata['version'] = version
            self.metadata['manifest_size'] = manifest_size

        return True

    def list_partitions(self):
        """Список разделов в прошивке"""
        # Пока заглушка, потом добавим полный парсинг protobuf
        partitions = ['boot', 'system', 'vendor', 'product', 'vbmeta']
        return partitions

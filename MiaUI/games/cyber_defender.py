# ╔═════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                       ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║
# ║  lang: python                                    ║
# ║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║
# ║  build:3.10.15                                   ║
# ║  files: cyber_defender.py                        ║
# ╚═════════════════════════════╝


import os
import random
import time
import hashlib
from datetime import datetime

VERSION = "1.0.2026"

# Очистка экрана


def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

# Цвета для терминала


class Colors:
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    WHITE = '\033[97m'
    END = '\033[0m'


# БАННЕР ЗАЩИТНИКА
BANNER = f"""
{Colors.BLUE}╔════════════════════════════════════════════════════════════════╗
║                                                                    ║
║     {Colors.CYAN}██████╗███████╗███████╗███████╗███╗   ██╗███████╗{Colors.BLUE}        ║
║     {Colors.CYAN}██╔══██╗██╔════╝██╔════╝██╔════╝████╗  ██║██╔════╝{Colors.BLUE}        ║
║     {Colors.CYAN}██║  ██║█████╗  █████╗  █████╗  ██╔██╗ ██║█████╗  {Colors.BLUE}        ║
║     {Colors.CYAN}██║  ██║██╔══╝  ██╔══╝  ██╔══╝  ██║╚██╗██║██╔══╝  {Colors.BLUE}        ║
║     {Colors.CYAN}██████╔╝███████╗██║     ███████╗██║ ╚████║███████╗{Colors.BLUE}        ║
║     {Colors.CYAN}╚═════╝ ╚══════╝╚═╝     ╚══════╝╚═╝  ╚═══╝╚══════╝{Colors.BLUE}        ║
║                                                                    ║
║              {Colors.GREEN}⚡ ТВОЯ МИССИЯ: ЗАЩИЩАТЬ МИР ⚡{Colors.BLUE}                    ║
║              {Colors.YELLOW}     ОТ ХАКЕРОВ, ВИРУСОВ И УГРОЗ      {Colors.BLUE}           ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝{Colors.END}
"""

# ПРЕДУПРЕЖДЕНИЕ
WARNING = f"""
{Colors.GREEN}╔════════════════════════════════════════════════════════════════╗
║  🛡️🛡️🛡️  ЭТИЧНЫЙ ХАКЕР. ЗАЩИТА, А НЕ НАПАДЕНИЕ.  🛡️🛡️🛡️      ║
╠════════════════════════════════════════════════════════════════╣
║  🔸 Ты — белый хакер (этичный)                                ║
║  🔸 Ты защищаешь системы, а не взламываешь                    ║
║  🔸 Все атаки — симулированные (учебные)                      ║
║  🔸 Это как тренажёр для пожарных — всё по-настоящему,        ║
║  🔸 но огонь ненастоящий                                      ║
║  🔸 Microsoft Security гордилась бы тобой! 🤗                 ║
║                                                                    ║
║  {Colors.YELLOW}░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░{Colors.GREEN}  ║
║  {Colors.YELLOW}░░  ТЫ ЗАЩИТНИК, А НЕ НАРУШИТЕЛЬ. ПОМНИ ОБ ЭТОМ.  ░░{Colors.GREEN}  ║
║  {Colors.YELLOW}░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░{Colors.GREEN}  ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════╝{Colors.END}
"""

# ГЕНЕРАТОР ДАННЫХ ДЛЯ ЗАЩИТЫ


class DefenseGen:
    @staticmethod
    def ip():
        return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

    @staticmethod
    def threat_name():
        threats = [
            "SQL-инъекция", "XSS-атака", "DDoS-атака", "Brute Force",
            "Фишинг", "Ransomware", "Trojan", "Zero-Day", "Man-in-the-Middle",
            "DNS Spoofing", "ARP Poisoning", "Port Scanning"
        ]
        return random.choice(threats)

    @staticmethod
    def severity():
        return random.choice(["Низкая", "Средняя", "Высокая", "Критическая"])

    @staticmethod
    def action():
        actions = [
            "Блокировка IP", "Обновление сигнатур", "Запрос 2FA",
            "Изоляция хоста", "Очистка кеша", "Сброс сессии",
            "Анализ трафика", "Сканирование портов", "Проверка целостности"
        ]
        return random.choice(actions)

    @staticmethod
    def success_message():
        messages = [
            "✅ Атака отражена! Система в безопасности.",
            "✅ Угроза нейтрализована.",
            "✅ Защита сработала идеально.",
            "✅ Хакер заблокирован.",
            "✅ Всё чисто, можем работать дальше.",
            "✅ SIEM подтверждает: инцидент закрыт."
        ]
        return random.choice(messages)

    @staticmethod
    def funny_message():
        return random.choice([
            "🛡️ Хакер заплакал и ушёл",
            "🛡️ Атака разбилась о защиту как об стену",
            "🛡️ Хакер пошёл читать учебник",
            "🛡️ Мы поймали его на IP: 127.0.0.1 (сам себя взламывал)",
            "🛡️ У хакера Windows без антивируса — сам виноват",
            "🛡️ Его пароль был '123456' — даже защищать не пришлось",
            "🛡️ Хакер использовал Kali Linux, но забыл её включить"
        ])

    @staticmethod
    def defense_tip():
        tips = [
            "Используй 2FA везде!",
            "Обновляй софт регулярно",
            "Не открывай подозрительные письма",
            "Сложные пароли — наше всё",
            "Бэкапы спасут твои данные",
            "Антивирус должен быть всегда включён",
            "VPN для публичных сетей"
        ]
        return random.choice(tips)

# ОСНОВНОЙ КЛАСС ЗАЩИТНИКА


class CyberDefender:
    def __init__(self):
        self.gen = DefenseGen
        self.username = "defender"
        self.score = 0
        self.threats_blocked = 0
        self.systems_protected = 0
        self.coffee = 0
        self.level = 1

        self.cmd_map = {
            'scan': self.scan, 'sca': self.scan,
            'monitor': self.monitor, 'mon': self.monitor,
            'defend': self.defend, 'def': self.defend,
            'analyze': self.analyze, 'ana': self.analyze,
            'firewall': self.firewall, 'fw': self.firewall,
            'patch': self.patch,
            'backup': self.backup,
            'report': self.report,
            'train': self.train,
            'coffee': self.coffee_cmd,
            'status': self.status,
            'clear': self.clear,
            'help': self.help,
            'exit': self.exit, '0': self.exit
        }

    def print_header(self):
        now = datetime.now().strftime("%H:%M:%S")
        random.randint(15, 40)
        random.randint(20, 60)
        print(f"{Colors.BLUE}════════════════════════════════════════════════════════════════{Colors.END}")
        print(f"{Colors.CYAN}  🛡️ ЗАЩИТНИК v{VERSION}  |  {now}  |  УРОВЕНЬ {self.level}  |  БЛОКИРОВОК: {self.threats_blocked}{Colors.END}")
        print(f"{Colors.BLUE}════════════════════════════════════════════════════════════════{Colors.END}")

    def progress(self, text: str, steps: int = 5, color=Colors.CYAN):
        print(f"{color}  └─> {text}{Colors.END}")
        for i in range(1, steps + 1):
            bar = '█' * i + '░' * (steps - i)
            percent = i * 100 // steps
            print(f"      [{bar}] {percent:3d}%", end='\r')
            time.sleep(0.15)
        print(f"      {Colors.GREEN}[{'█' * steps}] 100% ГОТОВО{Colors.END}")
        time.sleep(0.2)

    def scan(self, args):
        target = ' '.join(args[1:]) if len(args) > 1 else "локальная сеть"
        print(f"\n{Colors.CYAN}  🔍 СКАНИРОВАНИЕ: {target}{Colors.END}")

        self.progress("Поиск уязвимостей", 6)
        vulns = random.randint(0, 3)
        if vulns > 0:
            print(f"{Colors.YELLOW}      Найдено уязвимостей: {vulns}{Colors.END}")
            for _ in range(vulns):
                print(f"{Colors.YELLOW}      - {self.gen.threat_name()} ({self.gen.severity()}){Colors.END}")
        else:
            print(f"{Colors.GREEN}      Уязвимостей не найдено. Система чиста!{Colors.END}")

        self.progress("Проверка обновлений", 4)
        updates = random.randint(0, 2)
        if updates > 0:
            print(f"{Colors.YELLOW}      Доступно обновлений: {updates}{Colors.END}")
        else:
            print(f"{Colors.GREEN}      Всё обновлено!{Colors.END}")

        print(f"{Colors.GREEN}  ✅ СКАНИРОВАНИЕ ЗАВЕРШЕНО{Colors.END}")
        self.score += 10

    def monitor(self, args):
        print(f"\n{Colors.CYAN}  📡 МОНИТОРИНГ СЕТИ{Colors.END}")

        self.progress("Анализ трафика", 5)
        packets = random.randint(1000, 5000)
        print(f"{Colors.GREEN}      Проанализировано пакетов: {packets}{Colors.END}")

        threats = random.randint(0, 3)
        if threats > 0:
            print(f"{Colors.YELLOW}      Обнаружено угроз: {threats}{Colors.END}")
            for _ in range(threats):
                threat = self.gen.threat_name()
                ip = self.gen.ip()
                print(f"{Colors.YELLOW}      ⚠️  {threat} с IP {ip}{Colors.END}")

                # Автоматическая защита
                self.progress(f"Блокировка {threat}", 3)
                self.threats_blocked += 1
                print(f"{Colors.GREEN}      ✅ Угроза нейтрализована!{Colors.END}")
        else:
            print(f"{Colors.GREEN}      Угроз не обнаружено. Спокойно!{Colors.END}")

        print(f"{Colors.GREEN}  ✅ МОНИТОРИНГ ЗАВЕРШЁН{Colors.END}")
        self.score += 15

    def defend(self, args):
        threat = ' '.join(args[1:]) if len(args) > 1 else "неизвестная атака"
        print(f"\n{Colors.RED}  ⚔️  ОТРАЖЕНИЕ АТАКИ: {threat}{Colors.END}")

        self.progress("Анализ угрозы", 4)
        severity = self.gen.severity()
        print(f"{Colors.YELLOW}      Серьёзность: {severity}{Colors.END}")
        print(f"{Colors.YELLOW}      Источник: {self.gen.ip()}{Colors.END}")

        self.progress("Выбор стратегии защиты", 3)
        action = self.gen.action()
        print(f"{Colors.CYAN}      Действие: {action}{Colors.END}")

        self.progress("Применение контрмер", 5)

        if random.random() > 0.1:  # 90% успеха
            print(f"{Colors.GREEN}      {self.gen.success_message()}{Colors.END}")
            self.threats_blocked += 1
            self.systems_protected += 1
        else:
            print(f"{Colors.YELLOW}      ⚠️ Атака частично отражена, требуется дополнительная защита{Colors.END}")

        print(f"{Colors.GREEN}  ✅ АТАКА ОТРАЖЕНА{Colors.END}")
        self.score += 30

    def analyze(self, args):
        target = ' '.join(args[1:]) if len(args) > 1 else "система"
        print(f"\n{Colors.MAGENTA}  🔬 ГЛУБОКИЙ АНАЛИЗ: {target}{Colors.END}")

        self.progress("Сбор метрик", 4)
        print(f"{Colors.GREEN}      CPU: {random.randint(10, 50)}%{Colors.END}")
        print(f"{Colors.GREEN}      RAM: {random.randint(20, 70)}%{Colors.END}")
        print(f"{Colors.GREEN}      Диск: {random.randint(30, 90)}%{Colors.END}")
        print(f"{Colors.GREEN}      Сеть: {random.randint(1, 100)} Mbps{Colors.END}")

        self.progress("Проверка целостности", 5)
        if random.random() > 0.8:
            print(f"{Colors.YELLOW}      Найдены изменения в системных файлах{Colors.END}")
            self.progress("Восстановление", 3)
            print(f"{Colors.GREEN}      ✅ Файлы восстановлены{Colors.END}")
        else:
            print(f"{Colors.GREEN}      Всё в порядке, изменений нет{Colors.END}")

        self.progress("Проверка логов", 4)
        logs = random.randint(50, 200)
        suspicious = random.randint(0, 5)
        print(f"{Colors.GREEN}      Всего записей: {logs}{Colors.END}")
        if suspicious > 0:
            print(f"{Colors.YELLOW}      Подозрительных записей: {suspicious}{Colors.END}")
        else:
            print(f"{Colors.GREEN}      Логи чистые{Colors.END}")

        print(f"{Colors.GREEN}  ✅ АНАЛИЗ ЗАВЕРШЁН{Colors.END}")
        self.score += 20

    def firewall(self, args):
        print(f"\n{Colors.CYAN}  🔥 НАСТРОЙКА ФАЙРВОЛА{Colors.END}")

        self.progress("Обновление правил", 4)
        rules = random.randint(50, 200)
        print(f"{Colors.GREEN}      Активных правил: {rules}{Colors.END}")

        self.progress("Блокировка подозрительных IP", 5)
        blocked = random.randint(5, 30)
        print(f"{Colors.GREEN}      Заблокировано IP: {blocked}{Colors.END}")
        for _ in range(min(3, blocked)):
            print(f"{Colors.YELLOW}      - {self.gen.ip()}{Colors.END}")

        self.progress("Проверка соединений", 4)
        connections = random.randint(10, 100)
        print(f"{Colors.GREEN}      Активных соединений: {connections}{Colors.END}")

        print(f"{Colors.GREEN}  ✅ ФАЙРВОЛ НАСТРОЕН{Colors.END}")
        self.score += 15

    def patch(self, args):
        target = ' '.join(args[1:]) if len(args) > 1 else "система"
        print(f"\n{Colors.YELLOW}  🔧 УСТАНОВКА ОБНОВЛЕНИЙ: {target}{Colors.END}")

        self.progress("Поиск обновлений", 4)
        patches = random.randint(1, 10)
        print(f"{Colors.GREEN}      Найдено обновлений: {patches}{Colors.END}")

        for i in range(1, min(4, patches + 1)):
            self.progress(f"Установка патча {i}", 3)
            print(f"{Colors.GREEN}      Исправлена уязвимость: {self.gen.threat_name()}{Colors.END}")

        print(f"{Colors.GREEN}  ✅ СИСТЕМА ОБНОВЛЕНА{Colors.END}")
        self.score += 25
        self.systems_protected += 1

    def backup(self, args):
        target = ' '.join(args[1:]) if len(args) > 1 else "данные"
        print(f"\n{Colors.GREEN}  💾 СОЗДАНИЕ БЭКАПА: {target}{Colors.END}")

        self.progress("Подготовка к копированию", 3)
        size = random.randint(10, 500)
        print(f"{Colors.GREEN}      Размер данных: {size} MB{Colors.END}")

        self.progress("Копирование файлов", 5)
        files = random.randint(100, 5000)
        print(f"{Colors.GREEN}      Скопировано файлов: {files}{Colors.END}")

        self.progress("Проверка целостности", 4)
        print(
            f"{Colors.GREEN}      Контрольная сумма: {hashlib.md5(str(time.time()).encode()).hexdigest()[:16]}{Colors.END}")

        print(f"{Colors.GREEN}  ✅ БЭКАП СОЗДАН{Colors.END}")
        self.score += 20

    def report(self, args):
        print(f"\n{Colors.MAGENTA}  📊 ОТЧЁТ ПО БЕЗОПАСНОСТИ{Colors.END}")

        print(f"\n{Colors.CYAN}  ───── СТАТИСТИКА ЗАЩИТЫ ─────{Colors.END}")
        print(f"{Colors.GREEN}      Отражено атак: {self.threats_blocked}{Colors.END}")
        print(f"{Colors.GREEN}      Защищено систем: {self.systems_protected}{Colors.END}")
        print(f"{Colors.GREEN}      Уровень защиты: {min(100, self.threats_blocked * 10)}%{Colors.END}")

        print(f"\n{Colors.CYAN}  ───── ТЕКУЩИЕ УГРОЗЫ ─────{Colors.END}")
        threats_now = random.randint(0, 3)
        if threats_now > 0:
            for _ in range(threats_now):
                print(f"{Colors.YELLOW}      ⚠️  {self.gen.threat_name()} (в обработке){Colors.END}")
        else:
            print(f"{Colors.GREEN}      Угроз нет. Всё спокойно.{Colors.END}")

        print(f"\n{Colors.CYAN}  ───── РЕКОМЕНДАЦИИ ─────{Colors.END}")
        for _ in range(3):
            print(f"{Colors.GREEN}      💡 {self.gen.defense_tip()}{Colors.END}")

        print(f"{Colors.GREEN}  ✅ ОТЧЁТ СФОРМИРОВАН{Colors.END}")
        self.score += 10

    def train(self, args):
        print(f"\n{Colors.YELLOW}  📚 ОБУЧЕНИЕ ПО БЕЗОПАСНОСТИ{Colors.END}")

        self.progress("Изучение новых угроз", 4)
        print(f"{Colors.GREEN}      Изучено: {self.gen.threat_name()}{Colors.END}")

        self.progress("Практика защиты", 5)
        print(f"{Colors.GREEN}      Отработана защита от: {self.gen.threat_name()}{Colors.END}")

        self.progress("Тестирование навыков", 3)
        if random.random() > 0.3:
            print(f"{Colors.GREEN}      Тест пройден! Уровень повышен!{Colors.END}")
            self.level += 1
        else:
            print(f"{Colors.YELLOW}      Тест почти пройден. Попробуй ещё раз.{Colors.END}")

        print(f"{Colors.GREEN}  ✅ ОБУЧЕНИЕ ЗАВЕРШЕНО{Colors.END}")
        self.score += 30

    def coffee_cmd(self, args):
        print(f"\n{Colors.MAGENTA}  >> КОФЕ-БРЕЙК{Colors.END}")
        self.progress("Наливаю кофе", 4)
        self.coffee += 1
        print(f"{Colors.GREEN}      ☕ Кофе #{self.coffee} готов! Пей, защитник.{Colors.END}")
        print(f"{Colors.YELLOW}      {self.gen.funny_message()}{Colors.END}")

    def status(self, args):
        print(f"\n{Colors.MAGENTA}  >> СТАТУС ЗАЩИТНИКА{Colors.END}")
        print(f"{Colors.GREEN}      Имя: {self.username}{Colors.END}")
        print(f"{Colors.GREEN}      Уровень: {self.level}{Colors.END}")
        print(f"{Colors.GREEN}      Очки защиты: {self.score}{Colors.END}")
        print(f"{Colors.GREEN}      Отражено атак: {self.threats_blocked}{Colors.END}")
        print(f"{Colors.GREEN}      Защищено систем: {self.systems_protected}{Colors.END}")
        print(f"{Colors.GREEN}      Выпито кофе: {self.coffee}{Colors.END}")
        print(f"{Colors.GREEN}      Статус: АКТИВЕН{Colors.END}")

    def clear(self, args):
        clear()
        print(BANNER)
        print(WARNING)

    def help(self, args):
        print(f"\n{Colors.BLUE}╔════════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.BLUE}║{Colors.CYAN}              КОМАНДЫ ЭТИЧНОГО ХАКЕРА (ЗАЩИТА)              {Colors.BLUE}║{Colors.END}")
        print(f"{Colors.BLUE}╠════════════════════════════════════════════════════════════════╣{Colors.END}")

        cmds = [
            ("scan [сеть]", "Сканирование уязвимостей"),
            ("monitor", "Мониторинг сети и обнаружение атак"),
            ("defend [атака]", "Отражение активной атаки"),
            ("analyze [система]", "Глубокий анализ системы"),
            ("firewall", "Настройка файрвола"),
            ("patch [система]", "Установка обновлений"),
            ("backup [данные]", "Создание резервной копии"),
            ("report", "Отчёт по безопасности"),
            ("train", "Обучение и повышение уровня"),
            ("coffee", "Кофе-брейк"),
            ("status", "Статус защитника"),
            ("clear", "Очистить экран"),
            ("help", "Эта справка"),
            ("exit/0", "Выход")
        ]

        for cmd, desc in cmds:
            print(f"{Colors.BLUE}║{Colors.GREEN}  {cmd:12} {Colors.WHITE}{desc:<44}{Colors.BLUE}║{Colors.END}")

        print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════════════╝{Colors.END}")
        print(f"{Colors.YELLOW}  🛡️ Ты защищаешь мир. Каждая твоя команда делает его безопаснее!{Colors.END}")

    def exit(self, args):
        print(f"\n{Colors.GREEN}  >> ДО НОВЫХ ВСТРЕЧ, ЗАЩИТНИК!{Colors.END}")
        return False

    def run(self):
        clear()
        print(BANNER)
        print(WARNING)

        # Логин
        print(f"\n{Colors.BLUE}╔════════════════════════════════════════════════════════════════╗{Colors.END}")
        self.username = input(f"{Colors.BLUE}║{Colors.GREEN}  Как тебя зовут, защитник? {Colors.END}").strip()
        if not self.username:
            self.username = "defender"
        print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════════════╝{Colors.END}")

        print(f"\n{Colors.GREEN}  ✅ Привет, {self.username}! Готов защищать мир?{Colors.END}")
        print(f"{Colors.YELLOW}  🛡️ Помни: мы на стороне добра!{Colors.END}\n")

        running = True
        while running:
            try:
                self.print_header()
                cmd_line = input(f"{Colors.CYAN}C:\\Defender\\{self.username}>{Colors.END} ").strip()

                if not cmd_line:
                    continue

                parts = cmd_line.split()
                cmd = parts[0].lower()

                if cmd in ('exit', '0'):
                    if self.exit(parts) is False:
                        break

                elif cmd in self.cmd_map:
                    self.cmd_map[cmd](parts)
                else:
                    print(f"{Colors.RED}  ❌ Неизвестная команда. Попробуй 'help'{Colors.END}")

                print()

            except KeyboardInterrupt:
                print(f"\n{Colors.RED}  >> До свидания!{Colors.END}")
                break

        # Финальный экран
        clear()
        print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.BLUE}║{Colors.GREEN}                                                            {Colors.BLUE}║{Colors.END}")
        print(f"{Colors.BLUE}║{Colors.GREEN}     🎉  ТЫ УСПЕШНО ЗАЩИТИЛ СИСТЕМЫ!  🎉               {Colors.BLUE}║{Colors.END}")
        print(f"{Colors.BLUE}║{Colors.GREEN}                                                            {Colors.BLUE}║{Colors.END}")
        print(f"{Colors.BLUE}║{Colors.YELLOW}     Отражено атак: {self.threats_blocked}                             {Colors.BLUE}║{Colors.END}")
        print(f"{Colors.BLUE}║{Colors.YELLOW}     Защищено систем: {self.systems_protected}                          {Colors.BLUE}║{Colors.END}")
        print(f"{Colors.BLUE}║{Colors.YELLOW}     Выпито кофе: {self.coffee}                                        {Colors.BLUE}║{Colors.END}")
        print(f"{Colors.BLUE}║{Colors.GREEN}                                                            {Colors.BLUE}║{Colors.END}")
        print(f"{Colors.BLUE}║{Colors.CYAN}     Microsoft Security ждёт таких героев, как ты!          {Colors.BLUE}║{Colors.END}")
        print(f"{Colors.BLUE}║{Colors.GREEN}                                                            {Colors.BLUE}║{Colors.END}")
        print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════════════╝{Colors.END}")
        time.sleep(4)

# ========== ЭТО ВАЖНО ==========
# Добавляем функцию, которую вызовет window.py


def main():
    """Запуск игры для вызова из window.py"""
    defender = CyberDefender()
    defender.run()

# Для совместимости со старыми вызовами


def start_game():
    """Альтернативное имя функции"""
    main()


# Если файл запущен напрямую, а не импортирован
if __name__ == "__main__":
    main()

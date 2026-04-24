# ╔═════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                       ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║
# ║  lang: python                                    ║
# ║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║
# ║  build:3.10.15                                   ║
# ║  files: shake.py                                 ║
# ╚═════════════════════════════╝

import curses
import random
import time
import json
from enum import Enum

# ==================== КОНСТАНТЫ ====================
VERSION = "SHAKE-XTREME 10.2.2026"
AUTHOR = "Alia Ether 🌷"
PRICE = "$10,000 REAL 💰"

# Оптимизация производительности
FPS = 30  # Целевой FPS
FRAME_TIME = 1.0 / FPS
TICK_RATE = 0.1  # Скорость движения змейки
MAX_ENTITIES = 50  # Максимум объектов на экране

# Цвета
COLORS = {
    'SNAKE': 1,
    'SNAKE_HEAD': 2,
    'FOOD': 3,
    'FOOD_GOLDEN': 4,
    'FOOD_RAINBOW': 5,
    'POWERUP': 6,
    'WARNING': 7,
    'BORDER': 8,
    'SCORE': 9,
    'GOLD': 10,
    'RAINBOW': 11,
    'GHOST': 12,
    'LASER': 13,
    'MENU_TITLE': 14,
    'MENU_OPTION': 15,
    'MENU_SELECTED': 16,
}

# ==================== ТИПЫ ====================


class FoodType(Enum):
    NORMAL = "🍎"
    SUPER = "🍊"
    GOLDEN = "🍇"
    RAINBOW = "🍒"
    TIME = "🍓"
    SCORE = "🍉"
    SPEED = "🍌"
    SLOW = "🍑"
    INVINCIBLE = "🥝"
    GHOST = "🍍"


class PowerUpType(Enum):
    DOUBLE_POINTS = "2️⃣"
    SLOW_MOTION = "⏱️"
    INVINCIBLE = "✨"
    GHOST_MODE = "👻"
    MAGNET = "🧲"
    EXTRA_LIFE = "❤️"
    SPEED_BOOST = "⚡"
    TIME_FREEZE = "❄️"
    MEGA_SCORE = "💎"
    PORTAL = "🌀"
    LASER = "🔫"
    SHIELD = "🛡️"


class SkinType(Enum):
    CLASSIC = "■"
    MODERN = "●"
    DIAMOND = "◆"
    HEART = "❤️"
    STAR = "⭐"
    DRAGON = "🐉"
    GHOST = "👻"
    RAINBOW = "🌈"

# ==================== ДАННЫЕ ====================


class Snake:
    __slots__ = ('body', 'direction', 'next_direction', 'skin', 'invincible',
                 'ghost_mode', 'double_points', 'speed_boost', 'magnet',
                 'shield', 'laser_charges', 'length', 'effect_end_time')

    def __init__(self, start_y, start_x):
        self.body = [[start_y, start_x], [start_y, start_x-1], [start_y, start_x-2]]
        self.direction = curses.KEY_RIGHT
        self.next_direction = curses.KEY_RIGHT
        self.skin = SkinType.CLASSIC

        # Способности
        self.invincible = False
        self.ghost_mode = False
        self.double_points = False
        self.speed_boost = False
        self.magnet = False
        self.shield = 0
        self.laser_charges = 0
        self.length = 3

        # Время окончания эффектов
        self.effect_end_time = {}

    @property
    def head(self):
        return self.body[0]

    def set_effect(self, effect, duration):
        self.effect_end_time[effect] = time.time() + duration
        setattr(self, effect, True)

    def update_effects(self, current_time):
        expired = []
        for effect, end_time in self.effect_end_time.items():
            if current_time >= end_time:
                setattr(self, effect, False)
                expired.append(effect)
        for effect in expired:
            del self.effect_end_time[effect]


class Food:
    __slots__ = ('y', 'x', 'type', 'value', 'duration', 'created_at')

    def __init__(self, y, x, ftype=FoodType.NORMAL):
        self.y = y
        self.x = x
        self.type = ftype
        self.value = self._get_value()
        self.duration = self._get_duration()
        self.created_at = time.time()

    def _get_value(self):
        return {FoodType.NORMAL: 1, FoodType.SUPER: 3,
                FoodType.GOLDEN: 5, FoodType.RAINBOW: 10,
                FoodType.SCORE: 20}.get(self.type, 1)

    def _get_duration(self):
        return {FoodType.TIME: 5, FoodType.SPEED: 3,
                FoodType.SLOW: 3, FoodType.INVINCIBLE: 5,
                FoodType.GHOST: 5}.get(self.type, 0)

    @property
    def symbol(self):
        symbols = {FoodType.NORMAL: "🍎", FoodType.SUPER: "🍊",
                   FoodType.GOLDEN: "🍇", FoodType.RAINBOW: "🍒",
                   FoodType.TIME: "🍓", FoodType.SCORE: "🍉",
                   FoodType.SPEED: "🍌", FoodType.SLOW: "🍑",
                   FoodType.INVINCIBLE: "🥝", FoodType.GHOST: "🍍"}
        return symbols.get(self.type, "🍎")


class PowerUp:
    __slots__ = ('y', 'x', 'type', 'duration')

    def __init__(self, y, x, ptype=PowerUpType.DOUBLE_POINTS):
        self.y = y
        self.x = x
        self.type = ptype
        self.duration = self._get_duration()

    def _get_duration(self):
        durations = {PowerUpType.DOUBLE_POINTS: 10,
                     PowerUpType.SLOW_MOTION: 5,
                     PowerUpType.INVINCIBLE: 5,
                     PowerUpType.GHOST_MODE: 5,
                     PowerUpType.MAGNET: 8,
                     PowerUpType.SPEED_BOOST: 5,
                     PowerUpType.TIME_FREEZE: 3,
                     PowerUpType.LASER: 3,
                     PowerUpType.SHIELD: 3}
        return durations.get(self.type, 5)

    @property
    def symbol(self):
        symbols = {PowerUpType.DOUBLE_POINTS: "2️⃣",
                   PowerUpType.SLOW_MOTION: "⏱️",
                   PowerUpType.INVINCIBLE: "✨",
                   PowerUpType.GHOST_MODE: "👻",
                   PowerUpType.MAGNET: "🧲",
                   PowerUpType.EXTRA_LIFE: "❤️",
                   PowerUpType.SPEED_BOOST: "⚡",
                   PowerUpType.TIME_FREEZE: "❄️",
                   PowerUpType.MEGA_SCORE: "💎",
                   PowerUpType.PORTAL: "🌀",
                   PowerUpType.LASER: "🔫",
                   PowerUpType.SHIELD: "🛡️"}
        return symbols.get(self.type, "✨")


class Game:
    __slots__ = ('score', 'high_score', 'apples_eaten', 'powerups_collected',
                 'play_time', 'deaths', 'speed_multiplier', 'difficulty',
                 'colors', 'grid', 'infinite_powerups', 'portal_mode',
                 'running', 'obstacles')

    def __init__(self):
        self.score = 0
        self.high_score = self.load_high_score()
        self.apples_eaten = 0
        self.powerups_collected = 0
        self.play_time = 0
        self.deaths = 0

        # Настройки
        self.speed_multiplier = 1.0
        self.difficulty = 1
        self.colors = True
        self.grid = False

        # Режимы
        self.infinite_powerups = False
        self.portal_mode = False
        self.running = True
        self.obstacles = []

    def load_high_score(self):
        try:
            with open("snake_scores.json", "r") as f:
                return json.load(f).get("high_score", 0)
        except Exception:
            return 0

    def save_high_score(self):
        try:
            with open("snake_scores.json", "w") as f:
                json.dump({"high_score": self.high_score}, f)
        except Exception:
            pass

# ==================== МЕНЮ ====================


class Menu:
    def __init__(self, stdscr, snake, game):
        self.stdscr = stdscr
        self.snake = snake
        self.game = game
        self.sh, self.sw = stdscr.getmaxyx()

    def clear(self):
        self.stdscr.clear()
        self.stdscr.refresh()

    def center_text(self, y, text, color=0, bold=False):
        x = self.sw//2 - len(text)//2
        attr = curses.color_pair(color)
        if bold:
            attr |= curses.A_BOLD
        try:
            self.stdscr.addstr(y, x, text, attr)
        except Exception:
            pass

    def get_key(self):
        return self.stdscr.getch()


class MainMenu(Menu):
    def show(self):
        self.stdscr.nodelay(False)
        curses.curs_set(1)

        options = ["▶ Новая игра", "🛒 Магазин", "⚡ Читы", "📊 Статистика", "❌ Выход"]
        current = 0

        while True:
            self.clear()
            self.center_text(2, "🐍 SNAKE XTREME", COLORS['RAINBOW'], True)
            self.center_text(3, f"v{VERSION}", COLORS['GOLD'])

            for i, opt in enumerate(options):
                y = self.sh//2 - 2 + i
                color = COLORS['MENU_SELECTED'] if i == current else COLORS['MENU_OPTION']
                self.center_text(y, opt, color, i == current)

            self.center_text(self.sh-2, "↑/↓ - выбрать | Enter - подтвердить", COLORS['SCORE'])
            self.stdscr.refresh()

            key = self.get_key()
            if key == curses.KEY_UP and current > 0:
                current -= 1
            elif key == curses.KEY_DOWN and current < len(options)-1:
                current += 1
            elif key == ord('\n'):
                return current
            elif key == ord('q'):
                return 4

        curses.curs_set(0)
        self.stdscr.nodelay(True)


class ModMenu(Menu):
    def show(self):
        self.stdscr.nodelay(False)

        mods = [
            ('1', 'Бессмертие', 'invincible', 'bool'),
            ('2', 'Призрак', 'ghost_mode', 'bool'),
            ('3', 'Двойные очки', 'double_points', 'bool'),
            ('4', 'Супер скорость', 'speed_boost', 'bool'),
            ('5', 'Магнит', 'magnet', 'bool'),
            ('6', 'Лазер +3', 'laser_charges', 'add', 3),
            ('7', 'Щит +3', 'shield', 'add', 3),
            ('8', 'Длина +5', None, 'grow'),
            ('9', 'Очистить всё', None, 'clear'),
            ('a', 'Замедлить', 'speed', 'speed', 0.5),
            ('b', 'Ускорить', 'speed', 'speed', 2.0),
            ('c', 'Нормально', 'speed', 'speed', 1.0),
            ('d', '+1000 очков', 'score', 'score', 1000),
            ('e', '∞ бонусы', 'infinite_powerups', 'toggle'),
            ('f', 'Порталы', 'portal_mode', 'toggle'),
        ]

        while True:
            self.clear()
            self.center_text(2, "⚡ ЧИТЫ", COLORS['RAINBOW'], True)

            for i, (key, name, attr, mode, *val) in enumerate(mods):
                y = 4 + i
                if mode == 'bool':
                    status = "✅" if getattr(self.snake, attr) else "❌"
                elif mode == 'toggle':
                    status = "✅" if getattr(self.game, attr) else "❌"
                elif mode == 'add':
                    status = f"{getattr(self.snake, attr)}"
                else:
                    status = "⚡"
                self.center_text(y, f"[{key}] {name}: {status}", COLORS['MENU_OPTION'])

            self.center_text(self.sh-2, "0 - назад | q - выход", COLORS['SCORE'])
            self.stdscr.refresh()

            key = self.get_key()
            if key == ord('0'):
                break
            elif key == ord('q'):
                self.game.running = False
                break
            elif 32 <= key <= 126:
                k = chr(key).lower()
                for key_char, name, attr, mode, *val in mods:
                    if k == key_char:
                        if mode == 'bool':
                            setattr(self.snake, attr, not getattr(self.snake, attr))
                        elif mode == 'toggle':
                            setattr(self.game, attr, not getattr(self.game, attr))
                        elif mode == 'add':
                            setattr(self.snake, attr, getattr(self.snake, attr) + val[0])
                        elif mode == 'grow':
                            for _ in range(5):
                                self.snake.body.append(self.snake.body[-1][:])
                        elif mode == 'clear':
                            self.game.obstacles.clear()
                        elif mode == 'speed':
                            self.game.speed_multiplier = val[0]
                        elif mode == 'score':
                            self.game.score += val[0]
                        break

        self.stdscr.nodelay(True)


class ShopMenu(Menu):
    def show(self):
        self.stdscr.nodelay(False)

        skins = [
            (SkinType.CLASSIC, 0, "■ Классика"),
            (SkinType.MODERN, 100, "● Модерн"),
            (SkinType.DIAMOND, 200, "◆ Бриллиант"),
            (SkinType.HEART, 500, "❤️ Сердце"),
            (SkinType.STAR, 1000, "⭐ Звезда"),
            (SkinType.DRAGON, 2000, "🐉 Дракон"),
            (SkinType.GHOST, 5000, "👻 Призрак"),
            (SkinType.RAINBOW, 10000, "🌈 Радуга"),
        ]

        while True:
            self.clear()
            self.center_text(2, "🛒 МАГАЗИН СКИНОВ", COLORS['GOLD'], True)
            self.center_text(3, f"💰 {self.game.score} очков", COLORS['GOLD'])

            for i, (skin, price, name) in enumerate(skins):
                y = 5 + i
                status = "✅" if self.snake.skin == skin else f"{price}💰"
                color = COLORS['MENU_SELECTED'] if price <= self.game.score and self.snake.skin != skin else COLORS['MENU_OPTION']
                self.center_text(y, f"{i+1}. {name} - {status}", color)

            self.center_text(self.sh-2, "0 - назад", COLORS['SCORE'])
            self.stdscr.refresh()

            try:
                key = self.stdscr.getstr(self.sh-3, self.sw//2-10, 3).decode()
                if key == '0':
                    break

                idx = int(key) - 1
                if 0 <= idx < len(skins):
                    skin, price, name = skins[idx]
                    if price <= self.game.score and self.snake.skin != skin:
                        self.game.score -= price
                        self.snake.skin = skin
                        self.center_text(self.sh-4, f"✅ Куплено!", COLORS['GOLD'])
                        self.stdscr.refresh()
                        time.sleep(1)
            except Exception:
                pass

        self.stdscr.nodelay(True)


class StatsMenu(Menu):
    def show(self):
        self.stdscr.nodelay(False)

        stats = [
            f"🏆 Счёт: {self.game.score}",
            f"⭐ Рекорд: {self.game.high_score}",
            f"🍎 Яблок: {self.game.apples_eaten}",
            f"✨ Бонусов: {self.game.powerups_collected}",
            f"🐍 Длина: {len(self.snake.body)}",
            f"⚡ Скорость: {self.game.speed_multiplier}x",
            f"🛡️ Щит: {self.snake.shield}",
            f"🔫 Лазер: {self.snake.laser_charges}",
        ]

        while True:
            self.clear()
            self.center_text(2, "📊 СТАТИСТИКА", COLORS['GOLD'], True)

            for i, stat in enumerate(stats):
                self.center_text(4 + i, stat, COLORS['MENU_OPTION'])

            self.center_text(self.sh-2, "Нажми любую клавишу", COLORS['SCORE'])
            self.stdscr.refresh()

            if self.get_key() != -1:
                break

        self.stdscr.nodelay(True)

# ==================== ИГРОВАЯ ЛОГИКА ====================


def spawn_entity(sh, sw, snake_body, entity_type='food'):
    max_attempts = 100
    for _ in range(max_attempts):
        y = random.randint(1, sh-2)
        x = random.randint(1, sw-2)
        if [y, x] not in snake_body:
            if entity_type == 'food':
                return Food(y, x)
            elif entity_type == 'powerup':
                return PowerUp(y, x)
    return None


def start_game():
    def main(stdscr):
        # Инициализация цветов
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(COLORS['SNAKE'], curses.COLOR_GREEN, -1)
        curses.init_pair(COLORS['SNAKE_HEAD'], curses.COLOR_YELLOW, -1)
        curses.init_pair(COLORS['FOOD'], curses.COLOR_RED, -1)
        curses.init_pair(COLORS['FOOD_GOLDEN'], curses.COLOR_YELLOW, -1)
        curses.init_pair(COLORS['FOOD_RAINBOW'], curses.COLOR_MAGENTA, -1)
        curses.init_pair(COLORS['POWERUP'], curses.COLOR_MAGENTA, -1)
        curses.init_pair(COLORS['WARNING'], curses.COLOR_RED, -1)
        curses.init_pair(COLORS['BORDER'], curses.COLOR_CYAN, -1)
        curses.init_pair(COLORS['SCORE'], curses.COLOR_YELLOW, -1)
        curses.init_pair(COLORS['GOLD'], curses.COLOR_YELLOW, -1)
        curses.init_pair(COLORS['RAINBOW'], curses.COLOR_MAGENTA, -1)
        curses.init_pair(COLORS['GHOST'], curses.COLOR_WHITE, -1)
        curses.init_pair(COLORS['LASER'], curses.COLOR_CYAN, -1)
        curses.init_pair(COLORS['MENU_TITLE'], curses.COLOR_MAGENTA, -1)
        curses.init_pair(COLORS['MENU_OPTION'], curses.COLOR_WHITE, -1)
        curses.init_pair(COLORS['MENU_SELECTED'], curses.COLOR_YELLOW, -1)

        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.keypad(True)

        sh, sw = stdscr.getmaxyx()

        # Инициализация игры
        game = Game()
        snake = Snake(sh // 2, sw // 4)

        # Объекты
        foods = []
        powerups = []

        # Временные переменные
        last_tick = time.time()
        last_frame = time.time()
        frame_count = 0

        # Главное меню
        main_menu = MainMenu(stdscr, snake, game)

        while game.running:
            current_time = time.time()

            # Обновление эффектов
            snake.update_effects(current_time)
            game.play_time = current_time - last_tick

            # Проверка меню
            key = stdscr.getch()
            if key == ord('0'):
                choice = main_menu.show()
                if choice == 0:  # Новая игра
                    snake = Snake(sh // 2, sw // 4)
                    game.score = 0
                    foods = [spawn_entity(sh, sw, snake.body, 'food')]
                    powerups = []
                elif choice == 1:  # Магазин
                    ShopMenu(stdscr, snake, game).show()
                elif choice == 2:  # Читы
                    ModMenu(stdscr, snake, game).show()
                elif choice == 3:  # Статистика
                    StatsMenu(stdscr, snake, game).show()
                elif choice == 4:  # Выход
                    break

            # Управление змейкой
            if key != -1:
                if (key == curses.KEY_UP and snake.direction != curses.KEY_DOWN) or \
                   (key == curses.KEY_DOWN and snake.direction != curses.KEY_UP) or \
                   (key == curses.KEY_LEFT and snake.direction != curses.KEY_RIGHT) or \
                   (key == curses.KEY_RIGHT and snake.direction != curses.KEY_LEFT):
                    snake.direction = key

            # Игровой тик
            if current_time - last_tick >= TICK_RATE / game.speed_multiplier:
                # Новая голова
                head = snake.head[:]
                if snake.direction == curses.KEY_UP:
                    head[0] -= 1
                elif snake.direction == curses.KEY_DOWN:
                    head[0] += 1
                elif snake.direction == curses.KEY_LEFT:
                    head[1] -= 1
                elif snake.direction == curses.KEY_RIGHT:
                    head[1] += 1

                # Портал режим
                if game.portal_mode:
                    if head[0] <= 0:
                        head[0] = sh-2
                    elif head[0] >= sh-1:
                        head[0] = 1
                    if head[1] <= 0:
                        head[1] = sw-2
                    elif head[1] >= sw-1:
                        head[1] = 1

                # Проверка столкновений
                if not game.portal_mode:
                    if head[0] <= 0 or head[0] >= sh-1 or head[1] <= 0 or head[1] >= sw-1:
                        if not snake.invincible and not snake.ghost_mode:
                            game.deaths += 1
                            break

                if head in snake.body and not snake.ghost_mode and not snake.invincible:
                    game.deaths += 1
                    break

                # Движение
                snake.body.insert(0, head)

                # Проверка еды
                food_eaten = None
                for food in foods:
                    if head[0] == food.y and head[1] == food.x:
                        points = food.value * (2 if snake.double_points else 1)
                        game.score += points
                        game.apples_eaten += 1

                        # Эффекты еды
                        if food.type == FoodType.SUPER:
                            snake.body.append(snake.body[-1][:])
                        elif food.type == FoodType.GOLDEN:
                            game.score += 50
                        elif food.type == FoodType.RAINBOW:
                            game.score += 100
                            for _ in range(3):
                                snake.body.append(snake.body[-1][:])
                        elif food.type == FoodType.TIME:
                            snake.set_effect('slow_game', 5)
                        elif food.type == FoodType.SPEED:
                            snake.set_effect('speed_boost', 3)
                        elif food.type == FoodType.INVINCIBLE:
                            snake.set_effect('invincible', 5)
                        elif food.type == FoodType.GHOST:
                            snake.set_effect('ghost_mode', 5)
                        else:
                            snake.body.append(snake.body[-1][:])

                        food_eaten = food
                        break

                if food_eaten:
                    foods.remove(food_eaten)
                else:
                    snake.body.pop()

                # Проверка бонусов
                for powerup in powerups[:]:
                    if head[0] == powerup.y and head[1] == powerup.x:
                        game.powerups_collected += 1

                        if powerup.type == PowerUpType.DOUBLE_POINTS:
                            snake.set_effect('double_points', 10)
                        elif powerup.type == PowerUpType.SLOW_MOTION:
                            snake.set_effect('slow_game', 5)
                        elif powerup.type == PowerUpType.INVINCIBLE:
                            snake.set_effect('invincible', 5)
                        elif powerup.type == PowerUpType.GHOST_MODE:
                            snake.set_effect('ghost_mode', 5)
                        elif powerup.type == PowerUpType.MAGNET:
                            snake.set_effect('magnet', 8)
                        elif powerup.type == PowerUpType.EXTRA_LIFE:
                            snake.shield += 1
                        elif powerup.type == PowerUpType.SPEED_BOOST:
                            snake.set_effect('speed_boost', 5)
                        elif powerup.type == PowerUpType.MEGA_SCORE:
                            game.score += 500
                        elif powerup.type == PowerUpType.LASER:
                            snake.laser_charges += 3
                        elif powerup.type == PowerUpType.SHIELD:
                            snake.shield += 2

                        powerups.remove(powerup)

                # Лазер
                if snake.laser_charges > 0 and key == ord(' '):
                    snake.laser_charges -= 1
                    # Уничтожение препятствий впереди
                    if snake.direction == curses.KEY_UP:
                        for y in range(head[0]-1, 0, -1):
                            for o in game.obstacles[:]:
                                if o.y == y and abs(o.x - head[1]) < 2:
                                    game.obstacles.remove(o)
                                    game.score += 50
                    elif snake.direction == curses.KEY_DOWN:
                        for y in range(head[0]+1, sh-1):
                            for o in game.obstacles[:]:
                                if o.y == y and abs(o.x - head[1]) < 2:
                                    game.obstacles.remove(o)
                                    game.score += 50

                # Магнит
                if snake.magnet:
                    for food in foods[:3]:
                        if abs(food.y - head[0]) < 3 and abs(food.x - head[1]) < 3:
                            if food.y > head[0]:
                                food.y -= 1
                            elif food.y < head[0]:
                                food.y += 1
                            if food.x > head[1]:
                                food.x -= 1
                            elif food.x < head[1]:
                                food.x += 1

                # Спавн объектов
                if len(foods) < 3 + game.difficulty and random.random() < 0.1:
                    new_food = spawn_entity(sh, sw, snake.body, 'food')
                    if new_food:
                        foods.append(new_food)

                if len(powerups) < game.difficulty and (random.random() < 0.05 or game.infinite_powerups):
                    new_powerup = spawn_entity(sh, sw, snake.body, 'powerup')
                    if new_powerup:
                        powerups.append(new_powerup)

                # Обновление рекорда
                if game.score > game.high_score:
                    game.high_score = game.score

                last_tick = current_time

            # Отрисовка (ограничение по FPS)
            if current_time - last_frame >= FRAME_TIME:
                stdscr.erase()

                # Границы
                if game.colors:
                    stdscr.attron(curses.color_pair(COLORS['BORDER']))
                for i in range(sw):
                    try:
                        stdscr.addch(0, i, '█')
                        stdscr.addch(sh-1, i, '█')
                    except Exception:
                        pass
                for i in range(sh):
                    try:
                        stdscr.addch(i, 0, '█')
                        stdscr.addch(i, sw-1, '█')
                    except Exception:
                        pass
                if game.colors:
                    stdscr.attroff(curses.color_pair(COLORS['BORDER']))

                # Сетка
                if game.grid:
                    for i in range(1, sh-1, 2):
                        for j in range(1, sw-1, 2):
                            try:
                                stdscr.addch(i, j, '·', curses.A_DIM)
                            except Exception:
                                pass

                # Еда
                for food in foods:
                    color = COLORS['FOOD']
                    if food.type == FoodType.GOLDEN:
                        color = COLORS['FOOD_GOLDEN']
                    elif food.type == FoodType.RAINBOW:
                        color = COLORS['FOOD_RAINBOW']
                    try:
                        stdscr.addch(food.y, food.x, food.symbol,
                                     curses.color_pair(color))
                    except Exception:
                        pass

                # Бонусы
                for powerup in powerups:
                    try:
                        stdscr.addch(powerup.y, powerup.x, powerup.symbol,
                                     curses.color_pair(COLORS['POWERUP']))
                    except Exception:
                        pass

                # Препятствия
                for obs in game.obstacles:
                    color = COLORS['WARNING']
                    try:
                        stdscr.addch(obs.y, obs.x, obs.symbol,
                                     curses.color_pair(color))
                    except Exception:
                        pass

                # Змейка
                for i, segment in enumerate(snake.body):
                    color = COLORS['SNAKE_HEAD'] if i == 0 else COLORS['SNAKE']
                    if i == 0:
                        if snake.invincible:
                            color = COLORS['GOLD']
                        elif snake.ghost_mode:
                            color = COLORS['GHOST']
                        elif snake.speed_boost:
                            color = COLORS['LASER']
                    try:
                        stdscr.addch(segment[0], segment[1], snake.skin.value,
                                     curses.color_pair(color) | curses.A_BOLD)
                    except Exception:
                        pass

                # Верхняя панель
                panel = f" 🐍 {game.score}  🏆 {game.high_score}  "
                if snake.double_points:
                    panel += "2️⃣ "
                if snake.invincible:
                    panel += "✨ "
                if snake.ghost_mode:
                    panel += "👻 "
                if snake.magnet:
                    panel += "🧲 "
                if snake.shield:
                    panel += f"🛡️{snake.shield} "
                if snake.laser_charges:
                    panel += f"🔫{snake.laser_charges} "

                try:
                    stdscr.addstr(0, 2, panel[:sw-4], curses.A_REVERSE)
                except Exception:
                    pass

                # Нижняя панель
                help_text = "0-МЕНЮ | ПРОБЕЛ-ЛАЗЕР"
                try:
                    stdscr.addstr(sh-1, sw - len(help_text) - 2, help_text, curses.A_DIM)
                except Exception:
                    pass

                stdscr.refresh()
                last_frame = current_time
                frame_count += 1

        # Сохранение рекорда
        game.save_high_score()

        # Экран смерти
        stdscr.nodelay(False)
        stdscr.clear()
        title = "💀 GAME OVER 💀"
        try:
            stdscr.addstr(sh//2 - 2, sw//2 - len(title)//2, title,
                          curses.A_BOLD | curses.color_pair(COLORS['WARNING']))
            stdscr.addstr(sh//2, sw//2 - 10, f"Счёт: {game.score}", curses.A_BOLD)
            stdscr.addstr(sh//2 + 1, sw//2 - 10, f"Рекорд: {game.high_score}", curses.A_BOLD)
            stdscr.addstr(sh//2 + 3, sw//2 - 10, "Нажми Enter", curses.A_DIM)
        except Exception:
            pass
        stdscr.refresh()
        stdscr.getch()

    curses.wrapper(main)


if __name__ == "__main__":
    print(f"\n{'='*50}")
    print(f"🐍 SNAKE XTREME v{VERSION}")
    print(f"👤 {AUTHOR}")
    print(f"{'='*50}\n")
    time.sleep(1)
    start_game()

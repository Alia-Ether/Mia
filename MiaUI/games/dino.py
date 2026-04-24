

# ╔═════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                       ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║
# ║  lang: python                                    ║
# ║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║
# ║  build:3.10.15                                   ║
# ║  files: dino.py                                  ║
# ╚═════════════════════════════╝

import curses
import random
import time
import signal
import json
from enum import Enum
from dataclasses import dataclass
from typing import List

# ==================== КОНСТАНТЫ ====================
VERSION = "DINO-XTREME 5.0.2026"
AUTHOR = "Alia Ether 🌷"
PRICE = "$5000+ 💰"

# ==================== БЛОКИРОВКА CTRL ====================


def block_ctrl():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTSTP, signal.SIG_IGN)

# ==================== РАЗРЕШЁННЫЕ КЛАВИШИ ====================


def allowed_key(key):
    allowed = [
        ord(" "), ord("c"), ord("C"), ord("m"), ord("M"),
        ord("0"), ord("1"), ord("2"), ord("3"), ord("4"),
        ord("5"), ord("6"), ord("7"), ord("8"), ord("9"),
        curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT,
        ord("p"), ord("P"), ord("r"), ord("R"), ord("s"), ord("S"),
        ord("+"), ord("-"), ord("="), ord("q"), ord("Q"),
        27  # ESC
    ]
    return key in allowed

# ==================== БЕЗОПАСНЫЙ ВЫВОД ====================


def safe_addstr(stdscr, y, x, text, attr=0):
    sh, sw = stdscr.getmaxyx()
    if 0 <= y < sh and 0 <= x < sw:
        try:
            stdscr.addstr(y, x, text[:max(0, sw - x)], attr)
        except Exception:
            pass

# ==================== ТИПЫ ИГРОКОВ ====================


class PlayerType(Enum):
    DINOSAUR = "🦖"
    PTERODACTYL = "🦅"
    TRICERATOPS = "🦏"
    T_REX = "🦖🔥"
    RAPTOR = "🐉"
    DRAGON = "🐲"
    PHOENIX = "🔥🦅"
    UNICORN = "🦄"
    ROBOT = "🤖"
    ALIEN = "👽"

# ==================== ТИПЫ ПРЕПЯТСТВИЙ ====================


class ObstacleType(Enum):
    CACTUS = "🌵"
    ROCK = "🪨"
    TREE = "🌲"
    BIRD = "🐦"
    METEOR = "☄️"
    UFO = "🛸"
    GHOST = "👻"
    LASER = "⚡"
    FIRE = "🔥"
    ICE = "❄️"
    SPIKE = "🔪"
    BOMB = "💣"
    PORTAL = "🌀"

# ==================== ТИПЫ БОНУСОВ ====================


class PowerUpType(Enum):
    SHIELD = "🛡️"
    MAGNET = "🧲"
    DOUBLE_SCORE = "2️⃣"
    SLOW_MO = "⏱️"
    INVINCIBLE = "✨"
    EXTRA_LIFE = "❤️"
    SUPER_JUMP = "⬆️"
    DASH = "💨"
    FREEZE = "❄️"
    TELEPORT = "🌀"
    TIME_STOP = "⏸️"
    MEGA_SCORE = "💎"

# ==================== ДАННЫЕ ИГРОКА ====================


@dataclass
class PlayerData:
    name: str
    high_score: int
    games_played: int
    total_score: int
    achievements: List[str]
    unlocked_skins: List[str]
    unlocked_powerups: List[str]

# ==================== КЛАСС ИГРОКА ====================


class Player:
    def __init__(self, y, x):
        self.x = x
        self.base_y = y
        self.y = float(y)
        self.vy = 0
        self.alive = True
        self.frame = 0
        self.type = PlayerType.DINOSAUR

        # Читы
        self.invincible = False
        self.noclip = False
        self.fly = False
        self.god_mode = False
        self.one_hit_kill = False
        self.infinite_jump = False
        self.super_speed = False
        self.invisible = False

        # Бонусы
        self.shield = 0
        self.double_score = False
        self.slow_mo = False
        self.magnet = False
        self.extra_life = False
        self.dash = False
        self.freeze = False
        self.teleport_ready = True
        self.time_stop = False

        # Статистика
        self.jumps = 0
        self.distance = 0
        self.powerups_collected = 0
        self.obstacles_destroyed = 0
        self.combo = 0
        self.max_combo = 0

        # Скины
        self.unlocked_skins = [PlayerType.DINOSAUR]
        self.current_skin_index = 0

    @property
    def width(self):
        return 2 if self.type != PlayerType.T_REX else 3

    @property
    def symbol(self):
        symbols = {
            PlayerType.DINOSAUR: "🦖",
            PlayerType.PTERODACTYL: "🦅",
            PlayerType.TRICERATOPS: "🦏",
            PlayerType.T_REX: "🦖🔥",
            PlayerType.RAPTOR: "🐉",
            PlayerType.DRAGON: "🐲",
            PlayerType.PHOENIX: "🔥🦅",
            PlayerType.UNICORN: "🦄",
            PlayerType.ROBOT: "🤖",
            PlayerType.ALIEN: "👽"
        }
        return symbols.get(self.type, "🦖")

# ==================== КЛАСС ПРЕПЯТСТВИЯ ====================


class Obstacle:
    def __init__(self, x, y, otype: ObstacleType, length=1, speed=1):
        self.x = x
        self.y = y
        self.type = otype
        self.length = length
        self.speed = speed
        self.health = random.randint(1, 3) if otype in [ObstacleType.ROCK, ObstacleType.TREE] else 1
        self.damage = random.randint(1, 3) if otype in [ObstacleType.METEOR, ObstacleType.LASER] else 1
        self.effect = None

    @property
    def width(self):
        return self.length

    @property
    def symbol(self):
        symbols = {
            ObstacleType.CACTUS: "🌵",
            ObstacleType.ROCK: "🪨",
            ObstacleType.TREE: "🌲",
            ObstacleType.BIRD: "🐦",
            ObstacleType.METEOR: "☄️",
            ObstacleType.UFO: "🛸",
            ObstacleType.GHOST: "👻",
            ObstacleType.LASER: "⚡",
            ObstacleType.FIRE: "🔥",
            ObstacleType.ICE: "❄️",
            ObstacleType.SPIKE: "🔪",
            ObstacleType.BOMB: "💣",
            ObstacleType.PORTAL: "🌀"
        }
        return symbols.get(self.type, "█")

# ==================== КЛАСС БОНУСА ====================


class PowerUp:
    def __init__(self, x, y, ptype: PowerUpType):
        self.x = x
        self.y = y
        self.type = ptype
        self.duration = random.randint(3, 10)

    @property
    def symbol(self):
        symbols = {
            PowerUpType.SHIELD: "🛡️",
            PowerUpType.MAGNET: "🧲",
            PowerUpType.DOUBLE_SCORE: "2️⃣",
            PowerUpType.SLOW_MO: "⏱️",
            PowerUpType.INVINCIBLE: "✨",
            PowerUpType.EXTRA_LIFE: "❤️",
            PowerUpType.SUPER_JUMP: "⬆️",
            PowerUpType.DASH: "💨",
            PowerUpType.FREEZE: "❄️",
            PowerUpType.TELEPORT: "🌀",
            PowerUpType.TIME_STOP: "⏸️",
            PowerUpType.MEGA_SCORE: "💎"
        }
        return symbols.get(self.type, "⭐")

# ==================== КЛАСС ДРОНА ====================


class Drone:
    def __init__(self):
        self.active = False
        self.x = 0
        self.y = 0
        self.bombs = 0

    def deploy(self, player_x, player_y):
        self.active = True
        self.x = player_x + 2
        self.y = player_y - 1
        self.bombs = 3

    def drop_bomb(self):
        if self.bombs > 0:
            self.bombs -= 1
            return True
        return False

# ==================== МОД-МЕНЮ ====================


class ModMenu:
    def __init__(self, player, game):
        self.player = player
        self.game = game
        self.mods = {
            '1': ('Бессмертие', lambda: setattr(player, 'invincible', not player.invincible)),
            '2': ('Сквозь стены', lambda: setattr(player, 'noclip', not player.noclip)),
            '3': ('Полёт', lambda: setattr(player, 'fly', not player.fly)),
            '4': ('Режим Бога', lambda: setattr(player, 'god_mode', not player.god_mode)),
            '5': ('Один удар', lambda: setattr(player, 'one_hit_kill', not player.one_hit_kill)),
            '6': ('Бесконечный прыжок', lambda: setattr(player, 'infinite_jump', not player.infinite_jump)),
            '7': ('Супер скорость', lambda: setattr(player, 'super_speed', not player.super_speed)),
            '8': ('Невидимость', lambda: setattr(player, 'invisible', not player.invisible)),
            '9': ('Макс счёт', lambda: setattr(game, 'score', game.score + 10000)),
            'a': ('Очистить препятствия', game.clear_obstacles),
            'b': ('Добавить жизнь', lambda: setattr(player, 'extra_life', True)),
            'c': ('Супер прыжок', lambda: setattr(player, 'super_jump', not getattr(player, 'super_jump', False))),
            'd': ('Дрон поддержки', lambda: setattr(game, 'drone', Drone())),
            'e': ('Бесконечные бонусы', lambda: setattr(game, 'infinite_powerups', not getattr(game, 'infinite_powerups', False))),
            'f': ('Замедление времени', lambda: setattr(game, 'slow_motion', not getattr(game, 'slow_motion', False))),
        }

    def show(self, stdscr):
        stdscr.nodelay(False)
        curses.curs_set(1)

        while True:
            stdscr.clear()
            sh, sw = stdscr.getmaxyx()

            # Заголовок
            title = " ⚡ ЭКСТРИМАЛЬНОЕ МОД-МЕНЮ ⚡ "
            safe_addstr(stdscr, 1, sw//2 - len(title)//2, title, curses.A_BOLD | curses.color_pair(3))

            # Статус игрока
            status = f"Здоровье: {'∞' if False else '1'} | Скорость: {'МАКС' if False else 'НОРМ'} | Режим: {'ПОЛЁТ' if False else 'ЗЕМЛЯ'}"
            safe_addstr(stdscr, 3, 2, status)

            # Список модов
            y = 5
            safe_addstr(stdscr, y, 2, "═══ ОСНОВНЫЕ МОДЫ ═══", curses.A_BOLD)
            y += 2

            mods_list = [
                ("1", "Бессмертие", False),
                ("2", "Сквозь стены", False),
                ("3", "Полёт", False),
                ("4", "Режим Бога", False),
                ("5", "Один удар", False),
                ("6", "Бесконечный прыжок", False),
                ("7", "Супер скорость", False),
                ("8", "Невидимость", False),
            ]

            for key, name, enabled in mods_list:
                color = curses.color_pair(1) if enabled else 0
                status = "✅" if enabled else "❌"
                safe_addstr(stdscr, y, 4, f"[{key}] {name}: {status}", color)
                y += 1

            y += 1
            safe_addstr(stdscr, y, 2, "═══ ЭКСТРИМАЛЬНЫЕ МОДЫ ═══", curses.A_BOLD)
            y += 2

            extreme_mods = [
                ("9", "+10000 очков"),
                ("a", "Очистить препятствия"),
                ("b", "Добавить жизнь"),
                ("c", "Супер прыжок"),
                ("d", "Активировать дрон"),
                ("e", "Бесконечные бонусы"),
                ("f", "Замедление времени"),
            ]

            for key, name in extreme_mods:
                safe_addstr(stdscr, y, 4, f"[{key}] {name}")
                y += 1

            y += 1
            safe_addstr(stdscr, y, 2, "═══ УПРАВЛЕНИЕ ═══", curses.A_BOLD)
            y += 2
            safe_addstr(stdscr, y, 4, "0 - Назад в игру")
            y += 1
            safe_addstr(stdscr, y, 4, "q - Выход в главное меню")

            # Подсказка
            help_text = "Нажми цифру/букву для активации мода"
            safe_addstr(stdscr, sh-2, sw//2 - len(help_text)//2, help_text, curses.A_DIM)

            stdscr.refresh()
            key = stdscr.getch()

            if key == ord('0'):
                break
            elif key == ord('q'):
                self.game.running = False
                break
            elif chr(key) if 32 <= key <= 126 else None:
                key_char = chr(key).lower()
                if key_char in self.mods:
                    self.mods[key_char][1]()

        stdscr.nodelay(True)
        curses.curs_set(0)

# ==================== МАГАЗИН СКИНОВ ====================


class SkinShop:
    def __init__(self, player, game):
        self.player = player
        self.game = game
        self.skins = [
            (PlayerType.DINOSAUR, 0, "Базовый динозавр"),
            (PlayerType.PTERODACTYL, 500, "Птеродактиль - летает!"),
            (PlayerType.TRICERATOPS, 1000, "Трицератопс - сильный"),
            (PlayerType.T_REX, 2000, "Тираннозавр - огромный!"),
            (PlayerType.RAPTOR, 3000, "Раптор - быстрый"),
            (PlayerType.DRAGON, 5000, "Дракон - огненный"),
            (PlayerType.PHOENIX, 7500, "Феникс - возрождается"),
            (PlayerType.UNICORN, 10000, "Единорог - магический"),
            (PlayerType.ROBOT, 15000, "Робот - лазерный"),
            (PlayerType.ALIEN, 20000, "Пришелец - телепортация"),
        ]

    def show(self, stdscr):
        stdscr.nodelay(False)

        while True:
            stdscr.clear()
            sh, sw = stdscr.getmaxyx()

            # Заголовок
            title = " 🛍️ МАГАЗИН СКИНОВ 🛍️ "
            safe_addstr(stdscr, 1, sw//2 - len(title)//2, title, curses.A_BOLD | curses.color_pair(2))

            # Баланс
            balance = f"💰 Очки: {self.game.score}"
            safe_addstr(stdscr, 3, sw - len(balance) - 2, balance, curses.color_pair(1))

            # Текущий скин
            current = f"Текущий: {self.player.type.value}"
            safe_addstr(stdscr, 3, 2, current)

            # Список скинов
            y = 5
            safe_addstr(stdscr, y, 2, "═" * 50, curses.A_DIM)
            y += 1

            for i, (skin, price, desc) in enumerate(self.skins):
                status = "✅" if skin == self.player.type else "🔒" if price > self.game.score else "💰"
                color = curses.color_pair(1) if price <= self.game.score and skin != self.player.type else 0

                line = f"{i+1}. {skin.value} - {desc} | {price} очков {status}"
                safe_addstr(stdscr, y + i, 4, line, color)

            y += len(self.skins) + 2
            safe_addstr(stdscr, y, 2, "═" * 50, curses.A_DIM)
            y += 1

            safe_addstr(stdscr, y, 4, "Введите номер скина для покупки (0 - назад):")

            stdscr.refresh()

            try:
                key = stdscr.getstr(y+1, 4, 3).decode()
                if key == '0':
                    break

                idx = int(key) - 1
                if 0 <= idx < len(self.skins):
                    skin, price, _ = self.skins[idx]
                    if price <= self.game.score:
                        self.game.score -= price
                        self.player.type = skin
                        if skin not in self.player.unlocked_skins:
                            self.player.unlocked_skins.append(skin)
                        self.game.show_message(stdscr, f"✅ Куплен {skin.value}!")
                    else:
                        self.game.show_message(stdscr, "❌ Недостаточно очков!")
                else:
                    self.game.show_message(stdscr, "❌ Неверный номер!")
            except Exception:
                break

        stdscr.nodelay(True)

# ==================== ГЛАВНЫЙ КЛАСС ИГРЫ ====================


class Game:
    def __init__(self):
        self.score = 0
        self.high_score = self.load_high_score()
        self.difficulty = 1
        self.running = True
        self.paused = False
        self.drone = None
        self.slow_motion = False
        self.infinite_powerups = False
        self.powerups = []
        self.combo_timer = 0
        self.weather_effect = None
        self.day_night_cycle = 0
        self.achievements = []

    def load_high_score(self):
        try:
            with open("dino_scores.json", "r") as f:
                data = json.load(f)
                return data.get("high_score", 0)
        except Exception:
            return 0

    def save_high_score(self):
        try:
            with open("dino_scores.json", "w") as f:
                json.dump({"high_score": self.high_score}, f)
        except Exception:
            pass

    def clear_obstacles(self):
        self.obstacles.clear()

    def show_message(self, stdscr, msg, duration=1):
        sh, sw = stdscr.getmaxyx()
        safe_addstr(stdscr, sh//2, sw//2 - len(msg)//2, msg, curses.A_BOLD)
        stdscr.refresh()
        time.sleep(duration)

# ==================== ОСНОВНАЯ ФУНКЦИЯ ====================


def start_game():
    def main(stdscr):
        block_ctrl()
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        stdscr.nodelay(True)
        stdscr.keypad(True)

        # Цвета
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_RED, -1)
        curses.init_pair(3, curses.COLOR_CYAN, -1)
        curses.init_pair(4, curses.COLOR_YELLOW, -1)
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)
        curses.init_pair(6, curses.COLOR_BLUE, -1)

        sh, sw = stdscr.getmaxyx()

        game = Game()
        player = Player(sh - 4, 5)
        obstacles = []
        powerups = []
        game.obstacles = obstacles
        game.powerups = powerups

        last_spawn_score = 0
        current_delay = 0.05
        speed_level = 0
        frame_count = 0
        combo_counter = 0

        mod_menu = ModMenu(player, game)
        skin_shop = SkinShop(player, game)

        # Главный игровой цикл
        while player.alive and game.running:
            stdscr.erase()
            key = stdscr.getch()

            if key != -1 and not allowed_key(key):
                key = -1

            # Обработка клавиш
            if key == ord('0'):
                game.paused = True
                if not pause_menu(stdscr, game):
                    break

            if key in (ord('c'), ord('C')):
                mod_menu.show(stdscr)

            if key in (ord('s'), ord('S')):
                skin_shop.show(stdscr)

            if key == 27:  # ESC
                if confirm_exit(stdscr):
                    break

            if key == ord('+') or key == ord('='):
                game.difficulty = min(5, game.difficulty + 1)
            if key == ord('-') or key == ord('_'):
                game.difficulty = max(1, game.difficulty - 1)

            if key == ord('q') or key == ord('Q'):
                if confirm_exit(stdscr):
                    break

            # Управление игроком
            if player.fly:
                if key == curses.KEY_UP:
                    player.y -= 1
                if key == curses.KEY_DOWN:
                    player.y += 1
                if key == curses.KEY_LEFT:
                    player.x -= 1
                if key == curses.KEY_RIGHT:
                    player.x += 1
            else:
                if key in (ord(' '), curses.KEY_UP) and (player.y >= player.base_y or player.infinite_jump):
                    player.vy = -1.5
                    player.jumps += 1

                player.y += player.vy
                player.vy += 0.8 * (0.5 if game.slow_motion else 1)

                if player.vy > 2.0:
                    player.vy = 2.0

                if player.y >= player.base_y:
                    player.y = player.base_y
                    player.vy = 0

            # Счёт и скорость
            speed_mult = 2 if player.super_speed else 1
            player.distance += 1 * speed_mult
            game.score += 1 * (2 if player.double_score else 1) * speed_mult

            if game.score > game.high_score:
                game.high_score = game.score

            if game.score // 100 > speed_level:
                speed_level = game.score // 100
                current_delay = max(0.01, 0.05 - speed_level * 0.003 * game.difficulty)

            # Спавн препятствий
            spawn_chance = random.randint(0, 25 // game.difficulty)
            if game.score - last_spawn_score > 20 and spawn_chance == 0:
                if random.random() < 0.3:  # 30% шанс на бонус
                    ptype = random.choice(list(PowerUpType))
                    powerups.append(PowerUp(sw - 2, sh - 5, ptype))
                else:
                    otype = random.choice(list(ObstacleType))
                    length = random.randint(1, 3)
                    if otype in [ObstacleType.BIRD, ObstacleType.GHOST]:
                        y = sh - random.randint(4, 7)
                    else:
                        y = sh - 4
                    obstacles.append(Obstacle(sw - 2, y, otype, length, game.difficulty))
                last_spawn_score = game.score

            # Движение препятствий
            for o in obstacles:
                o.x -= o.speed * (0.5 if game.slow_motion else 1)

            # Движение бонусов
            for p in powerups[:]:
                p.x -= 1
                if p.x < 0:
                    powerups.remove(p)

            # Коллизии с препятствиями
            for o in obstacles[:]:
                if (player.x < o.x + o.width and player.x + player.width > o.x and int(player.y) == o.y):
                    if player.invincible or player.god_mode or player.noclip:
                        if player.one_hit_kill:
                            obstacles.remove(o)
                            player.obstacles_destroyed += 1
                            game.score += 100
                            combo_counter += 1
                            player.max_combo = max(player.max_combo, combo_counter)
                    elif player.shield > 0:
                        player.shield -= 1
                        obstacles.remove(o)
                    elif player.extra_life:
                        player.extra_life = False
                        obstacles.remove(o)
                    else:
                        player.alive = False

                if o.x + o.width < 0:
                    obstacles.remove(o)
                    combo_counter = 0

            # Коллизии с бонусами
            for p in powerups[:]:
                if player.x < p.x + 1 and player.x + player.width > p.x and int(player.y) == p.y:
                    apply_powerup(player, game, p.type)
                    powerups.remove(p)
                    player.powerups_collected += 1
                    game.score += 50

            # Дрон
            if game.drone and game.drone.active:
                if key == ord('b') or key == ord('B'):
                    if game.drone.drop_bomb():
                        for o in obstacles[:]:
                            if abs(o.x - game.drone.x) < 3:
                                obstacles.remove(o)
                                game.score += 50

            # Отрисовка
            frame_count += 1

            # Земля
            ground_pattern = "═" if not game.weather_effect else "≈"
            ground_line = ground_pattern * sw
            safe_addstr(stdscr, sh - 3, 0, ground_line, curses.color_pair(6) if game.weather_effect else 0)

            # Игрок
            if not player.invisible or frame_count % 10 < 5:
                safe_addstr(stdscr, int(player.y), player.x, player.symbol,
                            curses.color_pair(3) if player.invincible else curses.color_pair(1))

            # Препятствия
            for o in obstacles:
                safe_addstr(stdscr, o.y, o.x, o.symbol * o.length, curses.color_pair(2))

            # Бонусы
            for p in powerups:
                if frame_count % 20 < 10:  # Мигание
                    safe_addstr(stdscr, p.y, p.x, p.symbol, curses.color_pair(4))

            # Дрон
            if game.drone and game.drone.active:
                safe_addstr(stdscr, game.drone.y, game.drone.x, "🚁", curses.color_pair(5))

            # Верхняя панель
            panel = f" 🦖 ОЧКИ:{game.score} 🏆 РЕКОРД:{game.high_score} ⚡УРОВЕНЬ:{game.difficulty} 💫КОМБО:{combo_counter} "
            panel += f"🛡️{player.shield} ❤️{'∞' if player.invincible else '1'} "
            if game.drone:
                panel += f"🚁{game.drone.bombs} "
            safe_addstr(stdscr, 0, 0, panel.ljust(sw), curses.A_REVERSE)

            # Нижняя панель
            controls = "C-ЧИТЫ | S-МАГАЗИН | +/- СЛОЖНОСТЬ | ESC-ВЫХОД | 0-ПАУЗА"
            safe_addstr(stdscr, sh-1, sw - len(controls) - 2, controls, curses.A_DIM)

            stdscr.refresh()

            # Задержка
            delay = current_delay * (2 if game.slow_motion else 1)
            time.sleep(delay)

        # Сохранение рекорда
        game.save_high_score()

        # Экран смерти
        show_death_screen(stdscr, player, game)

    curses.wrapper(main)

# ==================== ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ ====================


def apply_powerup(player, game, ptype):
    effects = {
        PowerUpType.SHIELD: lambda: setattr(player, 'shield', player.shield + 3),
        PowerUpType.MAGNET: lambda: setattr(player, 'magnet', True),
        PowerUpType.DOUBLE_SCORE: lambda: setattr(player, 'double_score', True),
        PowerUpType.SLOW_MO: lambda: setattr(game, 'slow_motion', True),
        PowerUpType.INVINCIBLE: lambda: setattr(player, 'invincible', True),
        PowerUpType.EXTRA_LIFE: lambda: setattr(player, 'extra_life', True),
        PowerUpType.SUPER_JUMP: lambda: setattr(player, 'super_jump', True),
        PowerUpType.DASH: lambda: setattr(player, 'dash', True),
        PowerUpType.FREEZE: lambda: [setattr(o, 'speed', 0) for o in game.obstacles],
        PowerUpType.TELEPORT: lambda: setattr(player, 'x', max(5, player.x - 10)),
        PowerUpType.TIME_STOP: lambda: setattr(game, 'slow_motion', True),
        PowerUpType.MEGA_SCORE: lambda: setattr(game, 'score', game.score + 1000),
    }

    if ptype in effects:
        effects[ptype]()

    # Таймеры для временных эффектов
    if ptype in [PowerUpType.INVINCIBLE, PowerUpType.SLOW_MO, PowerUpType.DOUBLE_SCORE]:
        def reset():
            if ptype == PowerUpType.INVINCIBLE:
                player.invincible = False
            elif ptype == PowerUpType.SLOW_MO:
                game.slow_motion = False
            elif ptype == PowerUpType.DOUBLE_SCORE:
                player.double_score = False
        threading.Timer(5.0, reset).start()


def pause_menu(stdscr, game):
    stdscr.nodelay(False)
    while True:
        stdscr.clear()
        sh, sw = stdscr.getmaxyx()

        title = "⏸ ПАУЗА"
        safe_addstr(stdscr, sh//2 - 2, sw//2 - len(title)//2, title, curses.A_BOLD)

        options = [
            "1 - Продолжить",
            "2 - Перезапустить",
            "3 - Главное меню",
            "0 - Выход"
        ]

        for i, opt in enumerate(options):
            safe_addstr(stdscr, sh//2 + i, sw//2 - 12, opt)

        stdscr.refresh()
        key = stdscr.getch()

        if key == ord('1'):
            stdscr.nodelay(True)
            return True
        elif key == ord('2'):
            stdscr.nodelay(True)
            start_game()
            return False
        elif key == ord('3'):
            stdscr.nodelay(True)
            return False
        elif key == ord('0'):
            return False


def confirm_exit(stdscr):
    stdscr.nodelay(False)
    sh, sw = stdscr.getmaxyx()

    msg = "Выйти из игры? (y/n)"
    safe_addstr(stdscr, sh//2, sw//2 - len(msg)//2, msg, curses.A_BOLD)
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key == ord('y') or key == ord('Y'):
            return True
        elif key == ord('n') or key == ord('N'):
            stdscr.nodelay(True)
            return False


def show_death_screen(stdscr, player, game):
    stdscr.nodelay(False)
    sh, sw = stdscr.getmaxyx()

    stats = [
        f"🏆 Итоговый счёт: {game.score}",
        f"⭐ Рекорд: {game.high_score}",
        f"🦖 Прыжков: {player.jumps}",
        f"💫 Макс комбо: {player.max_combo}",
        f"📦 Бонусов: {player.powerups_collected}",
        f"💥 Препятствий уничтожено: {player.obstacles_destroyed}",
        f"📏 Дистанция: {player.distance}",
        "",
        "1 - Играть снова",
        "2 - Главное меню",
        "0 - Выход"
    ]

    while True:
        stdscr.clear()

        title = "💀 GAME OVER 💀"
        safe_addstr(stdscr, sh//2 - 6, sw//2 - len(title)//2, title, curses.A_BOLD | curses.color_pair(2))

        for i, stat in enumerate(stats):
            safe_addstr(stdscr, sh//2 - 4 + i, sw//2 - 15, stat)

        stdscr.refresh()
        key = stdscr.getch()

        if key == ord('1'):
            start_game()
            break
        elif key == ord('2'):
            break
        elif key == ord('0'):
            exit(0)


# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    start_game()

# ╔═════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                       ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║
# ║  lang: python                                    ║
# ║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║
# ║  build:3.10.15                                   ║
# ║  files: maze.py                                  ║
# ╚═════════════════════════════╝

import curses
import random
import time
import json
import os
from enum import Enum

# ==================== КОНСТАНТЫ ====================
VERSION = "MAZE-XTREME 15.0.2026"
AUTHOR = "Alia Ether 🌷"
PRICE = "$15,000 REAL 💰"
SAVE_FILE = "maze_save.json"

FPS = 30
FRAME_TIME = 1.0 / FPS

# Базовые символы
PLAYER_CHARS = ["🧙", "🧝", "🧛", "🧟", "🧚", "🧜", "🧞", "🧌", "🤴", "👸"]
WALL_CHARS = ["█", "▓", "▒", "░"]
FLOOR_CHARS = ["·", "•", "◦", "◊"]
EXIT_CHARS = ["🏁", "🚪", "🔑", "🏆", "👑", "⭐", "🌟", "✨"]
BONUS_CHARS = ["⭐", "💰", "💎", "🍎", "🍒", "🍇"]
TRAP_CHARS = ["💀", "⚡", "🔥", "❄️", "🌀", "💣", "🔪", "🕸️"]
KEY_CHARS = ["🔑", "🗝️", "🔐", "🔒"]
DOOR_CHARS = ["🚪", "🚫", "🔴", "🔵", "🟢"]
TELEPORT_CHARS = ["🌀", "🌪️", "🌈", "⚡", "✨", "💫"]
POWERUP_CHARS = ["⚡", "🛡️", "💊", "🧪", "🔮", "📿", "💍", "👑", "🎁"]
MONSTER_CHARS = ["👾", "👹", "👺", "🤖", "👽", "💀", "👻", "😈", "👿"]

# Цвета
COLORS = {
    'PLAYER': 1, 'WALL': 2, 'FLOOR': 3, 'EXIT': 4, 'BONUS': 5,
    'TRAP': 6, 'KEY': 7, 'DOOR': 8, 'TELEPORT': 9, 'POWERUP': 10,
    'MONSTER': 11, 'GOLD': 12, 'RAINBOW': 13, 'WARNING': 14, 'INFO': 15,
}

# ==================== ТИПЫ КЛЕТОК ====================


class CellType(Enum):
    EMPTY = 0
    WALL = 1
    BONUS = 2
    EXIT = 3
    TELEPORT = 4
    TRAP = 5
    KEY = 6
    DOOR = 7
    POWERUP = 8
    MONSTER = 9
    SECRET = 10

# ==================== ТИПЫ БОНУСОВ ====================


class PowerUpType(Enum):
    INVINCIBLE = "🛡️"
    SUPER_SPEED = "⚡"
    DOUBLE_SCORE = "2️⃣"
    EXTRA_LIFE = "❤️"
    SHIELD = "🛡️"
    GHOST = "👻"

# ==================== ТИПЫ МОНСТРОВ ====================


class MonsterType(Enum):
    GOBLIN = "👾"
    ORC = "👹"
    DEMON = "👺"
    ROBOT = "🤖"
    ALIEN = "👽"
    GHOST = "👻"
    SKELETON = "💀"

# ==================== ТИПЫ ЛОВУШЕК ====================


class TrapType(Enum):
    SPIKE = "🔪"
    FIRE = "🔥"
    ICE = "❄️"
    POISON = "☠️"
    PIT = "🕳️"
    WEB = "🕸️"
    BOMB = "💣"

# ==================== КЛАСС ИГРОКА ====================


class Player:
    def __init__(self, y, x):
        self.y = y
        self.x = x
        self.start_y = y
        self.start_x = x
        self.score = 0
        self.lives = 3
        self.level = 1
        self.keys = 0
        self.teleports_used = 0
        self.max_teleports = 3

        # Способности
        self.invincible = False
        self.super_speed = False
        self.double_score = False
        self.ghost = False
        self.shield = 0

        # Скин
        self.skin_index = 0
        self.skins = PLAYER_CHARS

        # Временные эффекты
        self.effect_timers = {}

        # Статистика
        self.bonuses_collected = 0
        self.monsters_defeated = 0
        self.traps_triggered = 0
        self.secrets_found = 0

        # Настройки
        self.time_enabled = True

    @property
    def skin(self):
        return self.skins[self.skin_index % len(self.skins)]

# ==================== КЛАСС МОНСТРА ====================


class Monster:
    def __init__(self, y, x, level=1):
        self.y = y
        self.x = x
        self.level = level
        self.health = level
        self.speed = 0.5
        self.damage = level
        self.symbol = random.choice(MONSTER_CHARS)

    def move(self, maze, player):
        if random.random() < self.speed:
            # Движение к игроку
            dy = 1 if player.y > self.y else -1 if player.y < self.y else 0
            dx = 1 if player.x > self.x else -1 if player.x < self.x else 0

            if random.random() < 0.7:  # 70% двигаться к игроку
                if abs(dy) > abs(dx):
                    new_y = self.y + dy
                    new_x = self.x
                else:
                    new_y = self.y
                    new_x = self.x + dx
            else:  # 30% случайное движение
                new_y = self.y + random.choice([-1, 0, 1])
                new_x = self.x + random.choice([-1, 0, 1])

            # Проверка на проходимость
            if 0 <= new_y < len(maze) and 0 <= new_x < len(maze[0]):
                if maze[new_y][new_x] not in [CellType.WALL, CellType.DOOR]:
                    self.y = new_y
                    self.x = new_x

# ==================== КЛАСС ЛОВУШКИ ====================


class Trap:
    def __init__(self, y, x, level=1):
        self.y = y
        self.x = x
        self.level = level
        self.active = True
        self.damage = level
        self.visible = True
        self.symbol = random.choice(TRAP_CHARS)

# ==================== КЛАСС ИГРЫ ====================


class Game:
    def __init__(self):
        self.score = 0
        self.high_score = 0
        self.levels_completed = 0
        self.bonuses_collected = 0
        self.monsters_defeated = 0
        self.traps_triggered = 0
        self.deaths = 0
        self.play_time = 0
        self.achievements = []

        # ВАЖНО: Добавляем атрибут running
        self.running = True

        # Настройки
        self.speed_multiplier = 1.0
        self.difficulty = 1
        self.sound = True
        self.colors = True
        self.show_full_map = False

        # Объекты
        self.monsters = []
        self.traps = []

        self.load_score()

    def load_score(self):
        try:
            if os.path.exists(SAVE_FILE):
                with open(SAVE_FILE, 'r') as f:
                    data = json.load(f)
                    self.high_score = data.get('high_score', 0)
        except Exception:
            pass

    def save_score(self):
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except Exception:
            pass

    def show_message(self, stdscr, msg, duration=1):
        sh, sw = stdscr.getmaxyx()
        try:
            stdscr.addstr(sh//2, sw//2 - len(msg)//2, msg, curses.A_BOLD)
            stdscr.refresh()
            time.sleep(duration)
        except Exception:
            pass

# ==================== ФУНКЦИИ ГЕНЕРАЦИИ ЛАБИРИНТА ====================


def generate_maze(sh, sw, level):
    height = sh - 4
    width = sw - 2
    maze = [[CellType.WALL for _ in range(width)] for _ in range(height)]

    # Алгоритм генерации (DFS)
    stack = [(1, 1)]
    maze[1][1] = CellType.EMPTY

    while stack:
        y, x = stack[-1]
        neighbors = []

        # Проверяем соседние клетки через одну
        for dy, dx in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            ny, nx = y + dy, x + dx
            if 1 <= ny < height-1 and 1 <= nx < width-1 and maze[ny][nx] == CellType.WALL:
                neighbors.append((ny, nx))

        if neighbors:
            ny, nx = random.choice(neighbors)
            maze[(y + ny)//2][(x + nx)//2] = CellType.EMPTY
            maze[ny][nx] = CellType.EMPTY
            stack.append((ny, nx))
        else:
            stack.pop()

    # Добавляем бонусы
    bonus_count = level * 3
    for _ in range(bonus_count):
        for _ in range(100):
            by, bx = random.randint(1, height-2), random.randint(1, width-2)
            if maze[by][bx] == CellType.EMPTY:
                maze[by][bx] = CellType.BONUS
                break

    # Добавляем ключи и двери
    door_count = level
    for _ in range(door_count):
        for _ in range(100):
            dy, dx = random.randint(1, height-2), random.randint(1, width-2)
            if maze[dy][dx] == CellType.EMPTY:
                maze[dy][dx] = CellType.DOOR
                break
        for _ in range(100):
            ky, kx = random.randint(1, height-2), random.randint(1, width-2)
            if maze[ky][kx] == CellType.EMPTY:
                maze[ky][kx] = CellType.KEY
                break

    # Добавляем ловушки
    trap_count = level
    for _ in range(trap_count):
        for _ in range(100):
            ty, tx = random.randint(1, height-2), random.randint(1, width-2)
            if maze[ty][tx] == CellType.EMPTY:
                maze[ty][tx] = CellType.TRAP
                break

    # Добавляем монстров
    monster_count = level
    for _ in range(monster_count):
        for _ in range(100):
            my, mx = random.randint(1, height-2), random.randint(1, width-2)
            if maze[my][mx] == CellType.EMPTY:
                maze[my][mx] = CellType.MONSTER
                break

    # Добавляем телепорты
    teleport_count = 2
    for _ in range(teleport_count):
        for _ in range(100):
            t1y, t1x = random.randint(1, height-2), random.randint(1, width-2)
            if maze[t1y][t1x] == CellType.EMPTY:
                maze[t1y][t1x] = CellType.TELEPORT
                break
        for _ in range(100):
            t2y, t2x = random.randint(1, height-2), random.randint(1, width-2)
            if maze[t2y][t2x] == CellType.EMPTY:
                maze[t2y][t2x] = CellType.TELEPORT
                break

    # Добавляем бонусы силы
    powerup_count = level // 2
    for _ in range(powerup_count):
        for _ in range(100):
            py, px = random.randint(1, height-2), random.randint(1, width-2)
            if maze[py][px] == CellType.EMPTY:
                maze[py][px] = CellType.POWERUP
                break

    # Выход
    for _ in range(1000):
        ey, ex = random.randint(1, height-2), random.randint(1, width-2)
        if maze[ey][ex] == CellType.EMPTY:
            maze[ey][ex] = CellType.EXIT
            exit_pos = (ey, ex)
            break
    else:
        exit_pos = (height-2, width-2)
        maze[height-2][width-2] = CellType.EXIT

    return maze, exit_pos


def get_random_empty_cell(maze):
    empty_cells = [(y, x) for y in range(len(maze)) for x in range(len(maze[0]))
                   if maze[y][x] == CellType.EMPTY]
    return empty_cells[0] if empty_cells else (1, 1)

# ==================== МОД-МЕНЮ ====================


class ModMenu:
    def __init__(self, player, game):
        self.player = player
        self.game = game
        self.mods = {
            '1': ('Бессмертие', lambda: setattr(player, 'invincible', not player.invincible)),
            '2': ('Призрак', lambda: setattr(player, 'ghost', not player.ghost)),
            '3': ('Супер скорость', lambda: setattr(player, 'super_speed', not player.super_speed)),
            '4': ('Двойные очки', lambda: setattr(player, 'double_score', not player.double_score)),
            '5': ('+3 жизни', lambda: setattr(player, 'lives', player.lives + 3)),
            '6': ('+1000 очков', lambda: setattr(game, 'score', game.score + 1000)),
            '7': ('Показать карту', lambda: setattr(game, 'show_full_map', not game.show_full_map)),
            '8': ('Замедлить', lambda: setattr(game, 'speed_multiplier', 0.3)),
            '9': ('Нормально', lambda: setattr(game, 'speed_multiplier', 1.0)),
        }

    def show(self, stdscr):
        stdscr.nodelay(False)

        while True:
            stdscr.clear()
            sh, sw = stdscr.getmaxyx()

            title = " ⚡ МОД-МЕНЮ ⚡ "
            x = sw//2 - len(title)//2
            stdscr.addstr(sh//2 - 8, x, title, curses.A_BOLD | curses.color_pair(COLORS['RAINBOW']))

            status = f"❤️ Жизни: {self.player.lives} | 🛡️ Щит: {self.player.shield} | 🔑 Ключи: {self.player.keys}"
            x = sw//2 - len(status)//2
            stdscr.addstr(sh//2 - 6, x, status)

            y = sh//2 - 4
            mods_list = [
                ("1", "Бессмертие", self.player.invincible),
                ("2", "Призрак", self.player.ghost),
                ("3", "Супер скорость", self.player.super_speed),
                ("4", "Двойные очки", self.player.double_score),
                ("5", "+3 жизни", False),
                ("6", "+1000 очков", False),
                ("7", "Показать карту", self.game.show_full_map),
                ("8", "Замедлить", self.game.speed_multiplier < 1),
                ("9", "Нормально", self.game.speed_multiplier == 1),
            ]

            for i, (key, name, enabled) in enumerate(mods_list):
                color = curses.color_pair(COLORS['GOLD']) if enabled else 0
                status = "✅" if enabled else "❌" if isinstance(enabled, bool) else ""
                x = sw//2 - 15
                stdscr.addstr(y + i, x, f"[{key}] {name}: {status}", color)

            x = sw//2 - 15
            stdscr.addstr(sh-4, x, "0 - Назад в игру | q - Выход")

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

# ==================== МЕНЮ ПАУЗЫ ====================


class PauseMenu:
    def __init__(self, player, game):
        self.player = player
        self.game = game
        self.mod_menu = ModMenu(player, game)

    def show(self, stdscr):
        stdscr.nodelay(False)

        while True:
            stdscr.clear()
            sh, sw = stdscr.getmaxyx()

            title = " ⏸️ МЕНЮ ПАУЗЫ ⏸️ "
            x = sw//2 - len(title)//2
            stdscr.addstr(sh//2 - 6, x, title, curses.A_BOLD | curses.color_pair(COLORS['RAINBOW']))

            options = [
                "1 - Продолжить",
                "2 - Моды",
                "3 - Статистика",
                "0 - Выход",
            ]

            for i, opt in enumerate(options):
                x = sw//2 - len(opt)//2
                stdscr.addstr(sh//2 - 3 + i, x, opt, curses.A_BOLD)

            status = f"🎮 Уровень: {self.player.level} | 💰 Очки: {self.game.score} | ❤️ Жизни: {self.player.lives}"
            x = sw//2 - len(status)//2
            stdscr.addstr(sh-3, x, status)

            stdscr.refresh()
            key = stdscr.getch()

            if key == ord('1'):
                stdscr.nodelay(True)
                return True
            elif key == ord('2'):
                self.mod_menu.show(stdscr)
            elif key == ord('3'):
                self.show_stats(stdscr)
            elif key == ord('0'):
                return False

    def show_stats(self, stdscr):
        stdscr.nodelay(False)

        while True:
            stdscr.clear()
            sh, sw = stdscr.getmaxyx()

            title = " 📊 СТАТИСТИКА 📊 "
            x = sw//2 - len(title)//2
            stdscr.addstr(sh//2 - 8, x, title, curses.A_BOLD | curses.color_pair(COLORS['GOLD']))

            stats = [
                f"🏆 Текущий счёт: {self.game.score}",
                f"⭐ Рекорд: {self.game.high_score}",
                f"📊 Уровней пройдено: {self.game.levels_completed}",
                f"💰 Бонусов собрано: {self.game.bonuses_collected}",
                f"👹 Монстров убито: {self.game.monsters_defeated}",
                f"💀 Смертей: {self.game.deaths}",
                f"🔑 Ключей: {self.player.keys}",
                f"❤️ Жизней: {self.player.lives}",
                f"⏱️ Время: {int(self.game.play_time)}с",
            ]

            for i, stat in enumerate(stats):
                x = sw//2 - 20
                stdscr.addstr(sh//2 - 6 + i, x, stat)

            x = sw//2 - 20
            stdscr.addstr(sh-3, x, "Нажмите любую клавишу")

            stdscr.refresh()
            key = stdscr.getch()
            if key != -1:
                break

        stdscr.nodelay(True)

# ==================== ОСНОВНАЯ ФУНКЦИЯ ====================


def start_game():
    def main(stdscr):
        # Инициализация
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        stdscr.nodelay(True)
        stdscr.keypad(True)

        # Цвета
        for i in range(1, 16):
            curses.init_pair(i, curses.COLOR_WHITE, -1)
        curses.init_pair(COLORS['PLAYER'], curses.COLOR_GREEN, -1)
        curses.init_pair(COLORS['WALL'], curses.COLOR_WHITE, -1)
        curses.init_pair(COLORS['EXIT'], curses.COLOR_YELLOW, -1)
        curses.init_pair(COLORS['BONUS'], curses.COLOR_YELLOW, -1)
        curses.init_pair(COLORS['TRAP'], curses.COLOR_RED, -1)
        curses.init_pair(COLORS['KEY'], curses.COLOR_YELLOW, -1)
        curses.init_pair(COLORS['DOOR'], curses.COLOR_RED, -1)
        curses.init_pair(COLORS['TELEPORT'], curses.COLOR_MAGENTA, -1)
        curses.init_pair(COLORS['POWERUP'], curses.COLOR_CYAN, -1)
        curses.init_pair(COLORS['MONSTER'], curses.COLOR_RED, -1)
        curses.init_pair(COLORS['GOLD'], curses.COLOR_YELLOW, -1)
        curses.init_pair(COLORS['RAINBOW'], curses.COLOR_MAGENTA, -1)

        sh, sw = stdscr.getmaxyx()
        if sh < 20 or sw < 40:
            stdscr.addstr(0, 0, "Окно слишком маленькое!")
            stdscr.refresh()
            time.sleep(2)
            return

        # Инициализация игры
        game = Game()
        level = 1
        maze, exit_pos = generate_maze(sh, sw, level)

        # Создаем монстров и ловушки
        monsters = []
        traps = []
        for y in range(len(maze)):
            for x in range(len(maze[0])):
                if maze[y][x] == CellType.MONSTER:
                    monsters.append(Monster(y, x, level))
                elif maze[y][x] == CellType.TRAP:
                    traps.append(Trap(y, x, level))

        game.monsters = monsters
        game.traps = traps

        # Игрок
        player_y, player_x = get_random_empty_cell(maze)
        player = Player(player_y, player_x)
        player.level = level

        # Меню паузы
        pause_menu = PauseMenu(player, game)

        # Временные переменные
        level_start_time = time.time()
        game_start_time = time.time()
        frame_count = 0

        # Словарь символов
        cell_symbols = {
            CellType.WALL: random.choice(WALL_CHARS),
            CellType.EMPTY: random.choice(FLOOR_CHARS),
            CellType.EXIT: random.choice(EXIT_CHARS),
            CellType.BONUS: random.choice(BONUS_CHARS),
            CellType.TRAP: random.choice(TRAP_CHARS),
            CellType.KEY: random.choice(KEY_CHARS),
            CellType.DOOR: random.choice(DOOR_CHARS),
            CellType.TELEPORT: random.choice(TELEPORT_CHARS),
            CellType.POWERUP: random.choice(POWERUP_CHARS),
            CellType.MONSTER: random.choice(MONSTER_CHARS),
        }

        # Главный цикл
        while game.running and player.lives > 0:
            stdscr.erase()
            frame_count += 1
            game.play_time = time.time() - game_start_time

            # Ввод
            key = stdscr.getch()

            # Пауза
            if key == ord('0') or key == ord('p') or key == ord('P'):
                if not pause_menu.show(stdscr):
                    break

            # Телепорт
            if key == ord('t') or key == ord('T'):
                if player.teleports_used < player.max_teleports:
                    # Ищем телепорт
                    teleports = [(y, x) for y in range(len(maze)) for x in range(len(maze[0]))
                                 if maze[y][x] == CellType.TELEPORT and (y, x) != (player.y, player.x)]
                    if teleports:
                        player.y, player.x = random.choice(teleports)
                        player.teleports_used += 1

            # Управление
            dy, dx = 0, 0
            if key == curses.KEY_UP:
                dy = -1
            elif key == curses.KEY_DOWN:
                dy = 1
            elif key == curses.KEY_LEFT:
                dx = -1
            elif key == curses.KEY_RIGHT:
                dx = 1

            new_y = player.y + dy
            new_x = player.x + dx

            if 0 <= new_y < len(maze) and 0 <= new_x < len(maze[0]):
                cell = maze[new_y][new_x]

                # Проверка проходимости
                can_move = True
                if cell == CellType.WALL and not player.ghost:
                    can_move = False
                elif cell == CellType.DOOR and player.keys == 0 and not player.ghost:
                    can_move = False

                if can_move:
                    player.y, player.x = new_y, new_x

                    # Обработка клеток
                    if cell == CellType.BONUS:
                        player.score += 10 * level
                        game.score += 10 * level
                        game.bonuses_collected += 1
                        player.bonuses_collected += 1
                        maze[new_y][new_x] = CellType.EMPTY

                    elif cell == CellType.EXIT:
                        game.score += 100 * level
                        game.levels_completed += 1
                        level += 1
                        player.level = level

                        # Генерация нового уровня
                        maze, exit_pos = generate_maze(sh, sw, level)
                        player.y, player.x = get_random_empty_cell(maze)
                        player.teleports_used = 0

                        # Создание монстров и ловушек
                        monsters.clear()
                        traps.clear()
                        for y in range(len(maze)):
                            for x in range(len(maze[0])):
                                if maze[y][x] == CellType.MONSTER:
                                    monsters.append(Monster(y, x, level))
                                elif maze[y][x] == CellType.TRAP:
                                    traps.append(Trap(y, x, level))
                        game.monsters = monsters
                        game.traps = traps

                        game.show_message(stdscr, f"🏁 УРОВЕНЬ {level}!", 1)

                    elif cell == CellType.TRAP and not player.invincible:
                        player.lives -= 1
                        game.traps_triggered += 1
                        player.traps_triggered += 1
                        maze[new_y][new_x] = CellType.EMPTY
                        if player.lives <= 0:
                            game.deaths += 1
                            player.y, player.x = player.start_y, player.start_x
                            player.lives = 3

                    elif cell == CellType.KEY:
                        player.keys += 1
                        maze[new_y][new_x] = CellType.EMPTY

                    elif cell == CellType.DOOR and player.keys > 0:
                        player.keys -= 1
                        maze[new_y][new_x] = CellType.EMPTY

                    elif cell == CellType.POWERUP:
                        ptype = random.choice(list(PowerUpType))

                        if ptype == PowerUpType.INVINCIBLE:
                            player.invincible = True
                            player.effect_timers['invincible'] = 150
                        elif ptype == PowerUpType.SUPER_SPEED:
                            player.super_speed = True
                            player.effect_timers['super_speed'] = 150
                        elif ptype == PowerUpType.DOUBLE_SCORE:
                            player.double_score = True
                            player.effect_timers['double_score'] = 300
                        elif ptype == PowerUpType.EXTRA_LIFE:
                            player.lives += 1
                        elif ptype == PowerUpType.SHIELD:
                            player.shield += 1

                        maze[new_y][new_x] = CellType.EMPTY

            # Обновление таймеров эффектов
            for effect in list(player.effect_timers.keys()):
                player.effect_timers[effect] -= 1
                if player.effect_timers[effect] <= 0:
                    if effect == 'invincible':
                        player.invincible = False
                    elif effect == 'super_speed':
                        player.super_speed = False
                    elif effect == 'double_score':
                        player.double_score = False
                    del player.effect_timers[effect]

            # Движение монстров
            for monster in monsters[:]:
                monster.move(maze, player)
                if monster.y == player.y and monster.x == player.x and not player.invincible:
                    player.lives -= 1
                    game.monsters_defeated += 1
                    player.monsters_defeated += 1
                    monsters.remove(monster)
                    if player.lives <= 0:
                        game.deaths += 1
                        player.y, player.x = player.start_y, player.start_x
                        player.lives = 3

            # Отрисовка
            for y in range(len(maze)):
                for x in range(len(maze[0])):
                    cell = maze[y][x]
                    if cell != CellType.EMPTY or (game.show_full_map and cell == CellType.WALL):
                        symbol = cell_symbols.get(cell, " ")
                        color_map = {
                            CellType.WALL: COLORS['WALL'],
                            CellType.EXIT: COLORS['EXIT'],
                            CellType.BONUS: COLORS['BONUS'],
                            CellType.TRAP: COLORS['TRAP'],
                            CellType.KEY: COLORS['KEY'],
                            CellType.DOOR: COLORS['DOOR'],
                            CellType.TELEPORT: COLORS['TELEPORT'],
                            CellType.POWERUP: COLORS['POWERUP'],
                        }
                        color = color_map.get(cell, 0)

                        try:
                            stdscr.addstr(y, x, symbol,
                                          curses.color_pair(color) if game.colors and color else 0)
                        except Exception:
                            pass

            # Отрисовка монстров
            for monster in monsters:
                try:
                    stdscr.addstr(monster.y, monster.x, monster.symbol,
                                  curses.color_pair(COLORS['MONSTER']) if game.colors else 0)
                except Exception:
                    pass

            # Отрисовка игрока
            try:
                stdscr.addstr(player.y, player.x, player.skin,
                              curses.color_pair(COLORS['PLAYER']) | curses.A_BOLD if game.colors else curses.A_BOLD)
            except Exception:
                pass

            # Верхняя панель
            time_left = max(0, 60 - int(time.time() - level_start_time)) if player.time_enabled else 999
            panel = f" 🧙 УРОВЕНЬ:{level}  💰 СЧЁТ:{game.score}  ⭐ БОНУСЫ:{game.bonuses_collected}  "
            panel += f"🔑 КЛЮЧИ:{player.keys}  ❤️ ЖИЗНИ:{player.lives}  🌀 ТЕЛЕПОРТЫ:{player.teleports_used}/{player.max_teleports}  "
            panel += f"⏱️ ВРЕМЯ:{time_left if time_left < 60 else '∞'}"

            if player.invincible:
                panel += " 🛡️"
            if player.super_speed:
                panel += " ⚡"
            if player.double_score:
                panel += " 2️⃣"
            if player.ghost:
                panel += " 👻"

            try:
                stdscr.addstr(0, 0, panel[:sw-1], curses.A_REVERSE)
            except Exception:
                pass

            # Нижняя панель
            help_text = "0-ПАУЗА | T-ТЕЛЕПОРТ | P-МЕНЮ"
            try:
                stdscr.addstr(sh-1, sw - len(help_text) - 2, help_text, curses.A_DIM)
            except Exception:
                pass

            stdscr.refresh()

            # Задержка
            delay = 0.05 / (game.speed_multiplier * (2 if player.super_speed else 1))
            time.sleep(delay)

            # Проверка времени
            if player.time_enabled and time.time() - level_start_time > 60:
                player.lives -= 1
                if player.lives <= 0:
                    game.deaths += 1
                    player.y, player.x = player.start_y, player.start_x
                    player.lives = 3
                level_start_time = time.time()

            # Рекорд
            if game.score > game.high_score:
                game.high_score = game.score

        # Game Over
        game.save_score()

        stdscr.nodelay(False)
        stdscr.clear()

        y = sh//2 - 6
        stdscr.addstr(y, sw//2 - 8, "💀 GAME OVER 💀", curses.A_BOLD | curses.color_pair(COLORS['WARNING']))

        stats = [
            f"💰 Счёт: {game.score}",
            f"🏆 Рекорд: {game.high_score}",
            f"📊 Уровни: {game.levels_completed}",
            f"⭐ Бонусы: {game.bonuses_collected}",
            f"👹 Монстры: {game.monsters_defeated}",
            f"⏱️ Время: {int(game.play_time)}с",
        ]

        for i, stat in enumerate(stats):
            stdscr.addstr(y + 2 + i, sw//2 - 10, stat)

        stdscr.addstr(y + 9, sw//2 - 15, "Нажмите R для рестарта или Q для выхода")

        stdscr.refresh()

        while True:
            key = stdscr.getch()
            if key == ord('r') or key == ord('R'):
                main(stdscr)
                break
            elif key == ord('q') or key == ord('Q'):
                break

    curses.wrapper(main)


# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"🏰 MAZE XTREME v{VERSION}")
    print(f"👤 {AUTHOR}")
    print(f"💰 Цена: {PRICE}")
    print(f"{'='*60}\n")
    print("Запуск игры...")
    time.sleep(2)
    start_game()

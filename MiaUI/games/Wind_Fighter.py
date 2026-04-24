# ╔═════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                       ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║
# ║  lang: python                                    ║
# ║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║
# ║  build:3.10.15                                   ║
# ║  files: Wind_Fighter.py                          ║
# ╚═════════════════════════════╝

import curses
import random
import time
import json
import math
import threading
from enum import Enum
from dataclasses import dataclass
from typing import List

# ==================== КОНСТАНТЫ ====================
VERSION = "WIND-FIGHTER XTREME 20.0.2026"
AUTHOR = "Alia Ether 🌷"

# Игрок
PLAYER_CHARS = ['✈✈', '🚁', '🛩️', '🚀', '🛸', '⚡⚡', '🔥🔥', '💫💫', '✨✨', '🌟🌟']

# Пули
BULLET_CHARS = ['||', '··', '··', '==', '>>', '👉', '⚡', '🔥', '💫', '✨']

# Враги
ENEMY_CHARS = ['██', '▲▲', '◆◆', '●●', '◉◉', '▼▼', '★★', '♠♠', '♣♣', '♦♦']
BOSS_CHARS = ['✹✹', '✸✸', '✦✦', '✧✧', '❄❄', '☠☠', '👾👾', '👹👹', '👺👺', '💀💀']

# Бонусы
BONUS_CHARS = ['★', '✚', '$', '❤️', '⚡', '🛡️', '🔫', '💊', '🎁', '👑']

# Оружие
WEAPON_CHARS = {
    'pistol': '🔫',
    'laser': '⚡',
    'shotgun': '🔫🔫',
    'machinegun': '🔫🔫🔫',
    'rocket': '🚀',
    'plasma': '💫',
    'flamethrower': '🔥',
    'freeze': '❄️',
}

# Цвета
COLORS = {
    'PLAYER': 1,
    'BULLET': 2,
    'ENEMY': 3,
    'BOSS1': 4,
    'BOSS2': 5,
    'BOSS3': 6,
    'SCORE': 7,
    'BONUS': 8,
    'BACKGROUND': 9,
    'WARNING': 10,
    'GOLD': 11,
    'RAINBOW': 12,
    'POWERUP': 13,
    'SHIELD': 14,
    'LASER': 15,
}

RAINBOW_COLORS = [curses.COLOR_RED, curses.COLOR_YELLOW, curses.COLOR_GREEN,
                  curses.COLOR_CYAN, curses.COLOR_BLUE, curses.COLOR_MAGENTA]

# ==================== ТИПЫ ВРАГОВ ====================


class EnemyType(Enum):
    BASIC = "BASIC"
    FAST = "FAST"
    TANK = "TANK"
    SHOOTER = "SHOOTER"
    BOMBER = "BOMBER"
    TELEPORTER = "TELEPORTER"
    SPLITTER = "SPLITTER"
    BOSS = "BOSS"

# ==================== ТИПЫ ОРУЖИЯ ====================


class WeaponType(Enum):
    PISTOL = "pistol"
    LASER = "laser"
    SHOTGUN = "shotgun"
    MACHINEGUN = "machinegun"
    ROCKET = "rocket"
    PLASMA = "plasma"
    FLAMETHROWER = "flamethrower"
    FREEZE = "freeze"

# ==================== ТИПЫ БОНУСОВ ====================


class BonusType(Enum):
    SCORE = "score"
    HEAL = "heal"
    SPEED = "speed"
    DAMAGE = "damage"
    SHIELD = "shield"
    WEAPON = "weapon"
    INVINCIBLE = "invincible"
    DOUBLE_SCORE = "double_score"
    EXTRA_LIFE = "extra_life"
    NUKE = "nuke"

# ==================== ТИПЫ УРОВНЕЙ ====================


class LevelType(Enum):
    NORMAL = "normal"
    BOSS = "boss"
    SURVIVAL = "survival"
    TIMED = "timed"
    ENDLESS = "endless"

# ==================== ДАННЫЕ ИГРОКА ====================


@dataclass
class PlayerData:
    name: str
    high_score: int
    levels_completed: int
    games_played: int
    total_score: int
    enemies_killed: int
    bosses_killed: int
    bonuses_collected: int
    deaths: int
    play_time: float
    achievements: List[str]
    unlocked_skins: List[str]
    unlocked_weapons: List[str]
    unlocked_levels: List[int]

# ==================== КЛАСС ИГРОКА ====================


class Player:
    def __init__(self, y, x):
        self.y = y
        self.x = x
        self.base_hp = 15
        self.hp = 15
        self.max_hp = 15
        self.speed = 2
        self.base_speed = 2
        self.damage = 1
        self.base_damage = 1
        self.shield = 0
        self.score = 0
        self.level = 1
        self.experience = 0
        self.exp_needed = 100

        # Оружие
        self.weapon = WeaponType.PISTOL
        self.weapon_level = 1
        self.weapon_cooldown = 0
        self.weapon_timer = 0

        # Способности
        self.invincible = False
        self.double_score = False
        self.freeze_enemies = False
        self.piercing = False
        self.homing = False
        self.multishot = 1
        self.spread = 0

        # Скины
        self.skin_index = 0
        self.skins = PLAYER_CHARS

        # Статистика
        self.enemies_killed = 0
        self.bosses_killed = 0
        self.bonuses_collected = 0
        self.shots_fired = 0
        self.shots_hit = 0

        # Временные эффекты
        self.effects = {}

    @property
    def skin(self):
        return self.skins[self.skin_index % len(self.skins)]

    def level_up(self):
        self.experience -= self.exp_needed
        self.level += 1
        self.exp_needed = int(self.exp_needed * 1.5)
        self.max_hp += 5
        self.hp = self.max_hp
        self.damage += 1
        return True

# ==================== КЛАСС ВРАГА ====================


class Enemy:
    def __init__(self, y, x, etype=EnemyType.BASIC, level=1):
        self.y = y
        self.x = x
        self.type = etype
        self.level = level

        # Базовые характеристики
        if etype == EnemyType.BASIC:
            self.hp = level
            self.max_hp = level
            self.speed = random.randint(4, 6)
            self.damage = 1
            self.points = 10 * level
            self.char = random.choice(ENEMY_CHARS)
            self.color = COLORS['ENEMY']

        elif etype == EnemyType.FAST:
            self.hp = level
            self.max_hp = level
            self.speed = random.randint(2, 3)
            self.damage = 1
            self.points = 15 * level
            self.char = '⚡⚡'
            self.color = COLORS['LASER']

        elif etype == EnemyType.TANK:
            self.hp = level * 3
            self.max_hp = level * 3
            self.speed = random.randint(7, 10)
            self.damage = 2
            self.points = 20 * level
            self.char = '██'
            self.color = COLORS['WARNING']

        elif etype == EnemyType.SHOOTER:
            self.hp = level
            self.max_hp = level
            self.speed = random.randint(5, 7)
            self.damage = 1
            self.points = 25 * level
            self.char = '🔫🔫'
            self.color = COLORS['BOSS2']
            self.shoot_cooldown = 0

        elif etype == EnemyType.BOMBER:
            self.hp = level
            self.max_hp = level
            self.speed = random.randint(5, 7)
            self.damage = 3
            self.points = 30 * level
            self.char = '💣💣'
            self.color = COLORS['WARNING']

        elif etype == EnemyType.TELEPORTER:
            self.hp = level
            self.max_hp = level
            self.speed = random.randint(5, 7)
            self.damage = 1
            self.points = 35 * level
            self.char = '🌀🌀'
            self.color = COLORS['RAINBOW']
            self.teleport_cooldown = 0

        elif etype == EnemyType.SPLITTER:
            self.hp = level * 2
            self.max_hp = level * 2
            self.speed = random.randint(5, 7)
            self.damage = 1
            self.points = 40 * level
            self.char = '◉◉'
            self.color = COLORS['BOSS1']

        elif etype == EnemyType.BOSS:
            self.hp = level * 20
            self.max_hp = level * 20
            self.speed = random.randint(8, 12)
            self.damage = 3
            self.points = 100 * level
            self.char = random.choice(BOSS_CHARS)
            self.color = COLORS['BOSS3']
            self.phase = 1
            self.attack_pattern = 0

        self.move_counter = 0
        self.pattern = random.randint(0, 3)

    def move(self, player, sh, sw):
        self.move_counter += 1

        if self.type == EnemyType.FAST:
            # Быстрое движение к игроку
            if self.move_counter % self.speed == 0:
                if self.y < player.y:
                    self.y += 1
                if self.x < player.x:
                    self.x += 1
                elif self.x > player.x:
                    self.x -= 1

        elif self.type == EnemyType.TANK:
            # Медленное, но направленное движение
            if self.move_counter % self.speed == 0:
                if self.y < player.y:
                    self.y += 1
                if abs(self.x - player.x) > 2:
                    if self.x < player.x:
                        self.x += 1
                    elif self.x > player.x:
                        self.x -= 1

        elif self.type == EnemyType.SHOOTER:
            # Стреляет, но не двигается
            if self.move_counter % 20 == 0:
                self.shoot_cooldown = 3

        elif self.type == EnemyType.BOMBER:
            # Движется вниз с бомбами
            if self.move_counter % self.speed == 0:
                self.y += 1

        elif self.type == EnemyType.TELEPORTER:
            # Телепортируется
            if self.move_counter % 30 == 0:
                self.y = random.randint(1, sh-5)
                self.x = random.randint(5, sw-6)

        elif self.type == EnemyType.SPLITTER:
            # Движется к игроку
            if self.move_counter % self.speed == 0:
                if self.y < player.y:
                    self.y += 1
                if abs(self.x - player.x) > 1:
                    if self.x < player.x:
                        self.x += 1
                    elif self.x > player.x:
                        self.x -= 1

        elif self.type == EnemyType.BOSS:
            # Сложное движение босса
            if self.move_counter % self.speed == 0:
                if self.phase == 1:
                    # Простое движение
                    self.x += math.sin(self.move_counter * 0.1) * 2
                elif self.phase == 2:
                    # Более агрессивное
                    if self.x < player.x:
                        self.x += 2
                    else:
                        self.x -= 2
                elif self.phase == 3:
                    # Очень агрессивное
                    if self.y < player.y:
                        self.y += 2
                    if self.x < player.x:
                        self.x += 2
                    else:
                        self.x -= 2

        else:
            # Обычное движение вниз
            if self.move_counter % self.speed == 0:
                self.y += 1

        # Ограничение границ
        self.y = max(1, min(sh-2, self.y))
        self.x = max(1, min(sw-3, self.x))

# ==================== КЛАСС ПУЛИ ====================


class Bullet:
    def __init__(self, y, x, weapon=WeaponType.PISTOL, damage=1, piercing=False, homing=False):
        self.y = y
        self.x = x
        self.weapon = weapon
        self.damage = damage
        self.piercing = piercing
        self.homing = homing
        self.speed = 2
        self.life = 20
        self.target = None

    @property
    def char(self):
        chars = {
            WeaponType.PISTOL: '||',
            WeaponType.LASER: '··',
            WeaponType.SHOTGUN: '==',
            WeaponType.MACHINEGUN: '>>',
            WeaponType.ROCKET: '🚀',
            WeaponType.PLASMA: '💫',
            WeaponType.FLAMETHROWER: '🔥',
            WeaponType.FREEZE: '❄️',
        }
        return chars.get(self.weapon, '||')

# ==================== КЛАСС БОНУСА ====================


class Bonus:
    def __init__(self, y, x, btype=BonusType.SCORE, value=1):
        self.y = y
        self.x = x
        self.type = btype
        self.value = value
        self.life = 100
        self.char = self._get_char()

    def _get_char(self):
        chars = {
            BonusType.SCORE: '★',
            BonusType.HEAL: '❤️',
            BonusType.SPEED: '⚡',
            BonusType.DAMAGE: '🔫',
            BonusType.SHIELD: '🛡️',
            BonusType.WEAPON: '🎁',
            BonusType.INVINCIBLE: '✨',
            BonusType.DOUBLE_SCORE: '2️⃣',
            BonusType.EXTRA_LIFE: '👑',
            BonusType.NUKE: '💣',
        }
        return chars.get(self.type, '★')

# ==================== МОД-МЕНЮ ====================


class ModMenu:
    def __init__(self, player, game):
        self.player = player
        self.game = game
        self.mods = {
            '1': ('Бессмертие', lambda: setattr(player, 'invincible', not player.invincible)),
            '2': ('Неуязвимость', lambda: setattr(player, 'god_mode', not getattr(player, 'god_mode', False))),
            '3': ('Двойные очки', lambda: setattr(player, 'double_score', not player.double_score)),
            '4': ('Супер скорость', lambda: setattr(player, 'speed', player.speed * 2)),
            '5': ('Макс урон', lambda: setattr(player, 'damage', player.damage * 3)),
            '6': ('Мультивыстрел', lambda: setattr(player, 'multishot', player.multishot + 1)),
            '7': ('Пробивание', lambda: setattr(player, 'piercing', not player.piercing)),
            '8': ('Самонаведение', lambda: setattr(player, 'homing', not player.homing)),
            '9': ('Замедление врагов', lambda: setattr(game, 'enemy_slow', True)),
            'a': ('Очистить врагов', game.clear_enemies),
            'b': ('+1000 очков', lambda: setattr(player, 'score', player.score + 1000)),
            'c': ('+10 жизней', lambda: setattr(player, 'hp', player.hp + 10)),
            'd': ('Следующий уровень', game.next_level),
            'e': ('Ядерный удар', game.nuke),
            'f': ('Бесконечные патроны', lambda: setattr(game, 'infinite_ammo', not getattr(game, 'infinite_ammo', False))),
        }

    def show(self, stdscr):
        stdscr.nodelay(False)
        curses.curs_set(1)

        while True:
            stdscr.clear()
            sh, sw = stdscr.getmaxyx()

            # Заголовок
            title = " ⚡ ЭКСТРИМАЛЬНОЕ МОД-МЕНЮ ⚡ "
            self._center_text(stdscr, sh//2 - 12, title, curses.A_BOLD | curses.color_pair(COLORS['RAINBOW']))

            # Статус
            status = f"❤️ HP: {player.hp}/{player.max_hp} | 🛡️ Щит: {player.shield} | 🔫 Урон: {player.damage} | ⚡ Скорость: {player.speed}"
            self._center_text(stdscr, sh//2 - 10, status)

            # Моды
            y = sh//2 - 8
            mods_list = [
                ("1", "Бессмертие", player.invincible),
                ("2", "Неуязвимость", getattr(player, 'god_mode', False)),
                ("3", "Двойные очки", player.double_score),
                ("4", "Супер скорость", player.speed > player.base_speed),
                ("5", "Макс урон", player.damage > player.base_damage),
                ("6", "Мультивыстрел", player.multishot),
                ("7", "Пробивание", player.piercing),
                ("8", "Самонаведение", player.homing),
                ("9", "Замедление врагов", getattr(game, 'enemy_slow', False)),
                ("a", "Очистить врагов", False),
                ("b", "+1000 очков", False),
                ("c", "+10 жизней", False),
                ("d", "Следующий уровень", False),
                ("e", "Ядерный удар", False),
                ("f", "Бесконечные патроны", getattr(game, 'infinite_ammo', False)),
            ]

            for i, (key, name, enabled) in enumerate(mods_list):
                color = curses.color_pair(COLORS['GOLD']) if enabled else 0
                status = "✅" if enabled else "❌" if isinstance(enabled, bool) else ""
                self._center_text(stdscr, y + i, f"[{key}] {name}: {status}", color)

            # Управление
            self._center_text(stdscr, sh-4, "0 - Назад в игру | q - Выход в меню")

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

    def _center_text(self, stdscr, y, text, attr=0):
        sh, sw = stdscr.getmaxyx()
        x = sw//2 - len(text)//2
        try:
            stdscr.addstr(y, x, text, attr)
        except Exception:
            pass

# ==================== МАГАЗИН СКИНОВ ====================


class SkinShop:
    def __init__(self, player, game):
        self.player = player
        self.game = game
        self.skins = [
            (0, "✈✈ Истребитель", 0),
            (1, "🚁 Вертолёт", 500),
            (2, "🛩️ Самолёт", 1000),
            (3, "🚀 Ракета", 2000),
            (4, "🛸 НЛО", 3000),
            (5, "⚡⚡ Молния", 4000),
            (6, "🔥🔥 Феникс", 5000),
            (7, "💫💫 Комета", 7500),
            (8, "✨✨ Звезда", 10000),
            (9, "🌟🌟 Солнце", 15000),
        ]

    def show(self, stdscr):
        stdscr.nodelay(False)

        while True:
            stdscr.clear()
            sh, sw = stdscr.getmaxyx()

            # Заголовок
            title = " 🛍️ МАГАЗИН СКИНОВ 🛍️ "
            self._center_text(stdscr, 2, title, curses.A_BOLD | curses.color_pair(COLORS['GOLD']))

            # Баланс
            balance = f"💰 Очки: {self.player.score}"
            self._center_text(stdscr, 4, balance, curses.color_pair(COLORS['GOLD']))

            # Текущий скин
            current = f"Текущий: {self.player.skin}"
            self._center_text(stdscr, 5, current)

            # Список скинов
            y = 7
            for i, (idx, name, price) in enumerate(self.skins):
                status = "✅" if idx == self.player.skin_index else "🔒" if price > self.player.score else "💰"
                color = curses.color_pair(
                    COLORS['GOLD']) if price <= self.player.score and idx != self.player.skin_index else 0

                line = f"{i+1}. {name} | {price} очков {status}"
                self._center_text(stdscr, y + i, line, color)

            # Инструкция
            self._center_text(stdscr, sh-4, "Введите номер скина (0 - назад):")

            stdscr.refresh()

            try:
                key = stdscr.getstr(sh-3, sw//2 - 10, 3).decode()
                if key == '0':
                    break

                idx = int(key) - 1
                if 0 <= idx < len(self.skins):
                    skin_idx, name, price = self.skins[idx]
                    if price <= self.player.score:
                        self.player.score -= price
                        self.player.skin_index = skin_idx
                        self.game.show_message(stdscr, f"✅ Куплен {name}!")
                    else:
                        self.game.show_message(stdscr, "❌ Недостаточно очков!")
                else:
                    self.game.show_message(stdscr, "❌ Неверный номер!")
            except Exception:
                break

        stdscr.nodelay(True)

    def _center_text(self, stdscr, y, text, attr=0):
        sh, sw = stdscr.getmaxyx()
        x = sw//2 - len(text)//2
        try:
            stdscr.addstr(y, x, text, attr)
        except Exception:
            pass

# ==================== МЕНЮ ДОСТИЖЕНИЙ ====================


class AchievementMenu:
    def __init__(self, game):
        self.game = game
        self.achievements = [
            ("🏆 Новичок", "Убейте 10 врагов", 10),
            ("🏆 Опытный", "Убейте 50 врагов", 50),
            ("🏆 Профи", "Убейте 100 врагов", 100),
            ("🏆 Мастер", "Убейте 500 врагов", 500),
            ("🏆 Легенда", "Убейте 1000 врагов", 1000),
            ("👑 Охотник на боссов", "Убейте 5 боссов", 5),
            ("👑 Убийца боссов", "Убейте 10 боссов", 10),
            ("👑 Бог боссов", "Убейте 20 боссов", 20),
            ("💰 Коллекционер", "Соберите 50 бонусов", 50),
            ("💰 Богач", "Соберите 100 бонусов", 100),
            ("💰 Миллионер", "Соберите 500 бонусов", 500),
            ("💪 Живучий", "Наберите 10000 очков", 10000),
            ("💪 Бессмертный", "Наберите 50000 очков", 50000),
            ("💪 Легенда", "Наберите 100000 очков", 100000),
            ("⭐ Идеальный", "Пройдите уровень без потерь", 1),
        ]

    def show(self, stdscr):
        stdscr.nodelay(False)

        while True:
            stdscr.clear()
            sh, sw = stdscr.getmaxyx()

            # Заголовок
            title = " 🏆 ДОСТИЖЕНИЯ 🏆 "
            self._center_text(stdscr, 2, title, curses.A_BOLD | curses.color_pair(COLORS['GOLD']))

            # Прогресс
            progress = f"📊 Прогресс: {len(self.game.achievements)}/{len(self.achievements)}"
            self._center_text(stdscr, 4, progress)

            # Список достижений
            y = 6
            for i, (name, desc, req) in enumerate(self.achievements):
                achieved = name in self.game.achievements
                color = curses.color_pair(COLORS['GOLD']) if achieved else 0
                status = "✅" if achieved else "❌"

                # Проверяем выполнение
                if not achieved:
                    if "врагов" in name and self.game.enemies_killed >= req:
                        achieved = True
                        self.game.achievements.append(name)
                    elif "боссов" in name and self.game.bosses_killed >= req:
                        achieved = True
                        self.game.achievements.append(name)
                    elif "бонусов" in name and self.game.bonuses_collected >= req:
                        achieved = True
                        self.game.achievements.append(name)
                    elif "очков" in name and self.game.total_score >= req:
                        achieved = True
                        self.game.achievements.append(name)

                line = f"{status} {name}: {desc}"
                self._center_text(stdscr, y + i, line, color)

            # Инструкция
            self._center_text(stdscr, sh-4, "Нажмите любую клавишу для выхода")

            stdscr.refresh()
            key = stdscr.getch()
            if key != -1:
                break

        stdscr.nodelay(True)

    def _center_text(self, stdscr, y, text, attr=0):
        sh, sw = stdscr.getmaxyx()
        x = sw//2 - len(text)//2
        try:
            stdscr.addstr(y, x, text, attr)
        except Exception:
            pass

# ==================== ГЛАВНОЕ МЕНЮ ПАУЗЫ ====================


class PauseMenu:
    def __init__(self, player, game):
        self.player = player
        self.game = game
        self.mod_menu = ModMenu(player, game)
        self.skin_shop = SkinShop(player, game)
        self.achievement_menu = AchievementMenu(game)

    def show(self, stdscr):
        stdscr.nodelay(False)

        while True:
            stdscr.clear()
            sh, sw = stdscr.getmaxyx()

            # Заголовок
            title = " ⏸️ МЕНЮ ПАУЗЫ ⏸️ "
            self._center_text(stdscr, sh//2 - 10, title, curses.A_BOLD | curses.color_pair(COLORS['RAINBOW']))

            # Опции
            options = [
                "1 - Продолжить игру",
                "2 - Моды (Читы)",
                "3 - Магазин скинов",
                "4 - Достижения",
                "5 - Статистика",
                "6 - Настройки",
                "7 - Смена оружия",
                "0 - Выход в главное меню",
            ]

            for i, opt in enumerate(options):
                y = sh//2 - 7 + i
                self._center_text(stdscr, y, opt, curses.A_BOLD)

            # Текущий статус
            status = f"✈️ Уровень: {player.level} | 💰 Очки: {player.score} | ❤️ HP: {player.hp}/{player.max_hp} | 🔫 {player.weapon.value}"
            self._center_text(stdscr, sh-3, status)

            stdscr.refresh()
            key = stdscr.getch()

            if key == ord('1'):
                stdscr.nodelay(True)
                return True
            elif key == ord('2'):
                self.mod_menu.show(stdscr)
            elif key == ord('3'):
                self.skin_shop.show(stdscr)
            elif key == ord('4'):
                self.achievement_menu.show(stdscr)
            elif key == ord('5'):
                self.show_stats(stdscr)
            elif key == ord('6'):
                self.show_settings(stdscr)
            elif key == ord('7'):
                self.show_weapon_shop(stdscr)
            elif key == ord('0'):
                return False

    def show_stats(self, stdscr):
        stdscr.nodelay(False)

        while True:
            stdscr.clear()
            sh, sw = stdscr.getmaxyx()

            # Заголовок
            title = " 📊 СТАТИСТИКА 📊 "
            self._center_text(stdscr, sh//2 - 10, title, curses.A_BOLD | curses.color_pair(COLORS['GOLD']))

            stats = [
                f"🏆 Текущий счёт: {player.score}",
                f"⭐ Рекорд: {self.game.high_score}",
                f"📊 Уровень: {player.level}",
                f"👹 Врагов убито: {self.game.enemies_killed}",
                f"👑 Боссов убито: {self.game.bosses_killed}",
                f"💰 Бонусов собрано: {self.game.bonuses_collected}",
                f"🎯 Точность: {(player.shots_hit/player.shots_fired*100 if player.shots_fired else 0):.1f}%",
                f"⏱️ Время игры: {int(self.game.play_time)}с",
                f"🏅 Достижений: {len(self.game.achievements)}",
            ]

            for i, stat in enumerate(stats):
                self._center_text(stdscr, sh//2 - 8 + i, stat)

            self._center_text(stdscr, sh-3, "Нажмите любую клавишу для возврата")

            stdscr.refresh()
            key = stdscr.getch()
            if key != -1:
                break

        stdscr.nodelay(True)

    def show_settings(self, stdscr):
        stdscr.nodelay(False)

        while True:
            stdscr.clear()
            sh, sw = stdscr.getmaxyx()

            # Заголовок
            title = " ⚙️ НАСТРОЙКИ ⚙️ "
            self._center_text(stdscr, sh//2 - 6, title, curses.A_BOLD | curses.color_pair(COLORS['RAINBOW']))

            settings = [
                f"1 - Скорость: {self.game.speed_multiplier}x",
                f"2 - Сложность: {self.game.difficulty}",
                f"3 - Звук: {'Вкл' if self.game.sound else 'Выкл'}",
                f"4 - Цвета: {'Вкл' if self.game.colors else 'Выкл'}",
                f"5 - Звёзды: {'Вкл' if self.game.stars else 'Выкл'}",
                f"6 - Частицы: {'Вкл' if self.game.particles else 'Выкл'}",
                "",
                "0 - Назад",
            ]

            for i, setting in enumerate(settings):
                y = sh//2 - 4 + i
                self._center_text(stdscr, y, setting)

            stdscr.refresh()
            key = stdscr.getch()

            if key == ord('1'):
                self.game.speed_multiplier = (self.game.speed_multiplier % 3) + 1
            elif key == ord('2'):
                self.game.difficulty = (self.game.difficulty % 5) + 1
            elif key == ord('3'):
                self.game.sound = not self.game.sound
            elif key == ord('4'):
                self.game.colors = not self.game.colors
            elif key == ord('5'):
                self.game.stars = not self.game.stars
            elif key == ord('6'):
                self.game.particles = not self.game.particles
            elif key == ord('0'):
                break

        stdscr.nodelay(True)

    def show_weapon_shop(self, stdscr):
        stdscr.nodelay(False)

        weapons = [
            (WeaponType.PISTOL, "Пистолет", 0, 1, "Базовое оружие"),
            (WeaponType.LASER, "Лазер", 1000, 2, "Пробивает врагов"),
            (WeaponType.SHOTGUN, "Дробовик", 2000, 3, "3 пули за раз"),
            (WeaponType.MACHINEGUN, "Пулемёт", 3000, 1, "Быстрая стрельба"),
            (WeaponType.ROCKET, "Ракета", 5000, 5, "Большой урон"),
            (WeaponType.PLASMA, "Плазма", 7500, 4, "Замедляет врагов"),
            (WeaponType.FLAMETHROWER, "Огнемёт", 10000, 3, "Горит 3 секунды"),
            (WeaponType.FREEZE, "Заморозка", 15000, 2, "Останавливает врагов"),
        ]

        while True:
            stdscr.clear()
            sh, sw = stdscr.getmaxyx()

            # Заголовок
            title = " 🔫 МАГАЗИН ОРУЖИЯ 🔫 "
            self._center_text(stdscr, 2, title, curses.A_BOLD | curses.color_pair(COLORS['GOLD']))

            # Баланс
            balance = f"💰 Очки: {player.score}"
            self._center_text(stdscr, 4, balance, curses.color_pair(COLORS['GOLD']))

            # Текущее оружие
            current = f"Текущее: {player.weapon.value}"
            self._center_text(stdscr, 5, current)

            # Список оружия
            y = 7
            for i, (wtype, name, price, damage, desc) in enumerate(weapons):
                status = "✅" if wtype == player.weapon else "🔒" if price > player.score else "💰"
                color = curses.color_pair(COLORS['GOLD']) if price <= player.score and wtype != player.weapon else 0

                line = f"{i+1}. {name} - Урон: {damage} | {price} очков {status}"
                self._center_text(stdscr, y + i, line, color)
                self._center_text(stdscr, y + i + 0.5, f"   {desc}", curses.A_DIM)
                y += 1

            # Инструкция
            self._center_text(stdscr, sh-4, "Введите номер оружия (0 - назад):")

            stdscr.refresh()

            try:
                key = stdscr.getstr(sh-3, sw//2 - 10, 3).decode()
                if key == '0':
                    break

                idx = int(key) - 1
                if 0 <= idx < len(weapons):
                    wtype, name, price, damage, desc = weapons[idx]
                    if price <= player.score:
                        player.score -= price
                        player.weapon = wtype
                        player.damage = damage
                        self.game.show_message(stdscr, f"✅ Куплен {name}!")
                    else:
                        self.game.show_message(stdscr, "❌ Недостаточно очков!")
                else:
                    self.game.show_message(stdscr, "❌ Неверный номер!")
            except Exception:
                break

        stdscr.nodelay(True)

    def _center_text(self, stdscr, y, text, attr=0):
        sh, sw = stdscr.getmaxyx()
        x = sw//2 - len(text)//2
        try:
            stdscr.addstr(y, x, text, attr)
        except Exception:
            pass

# ==================== ГЛАВНЫЙ КЛАСС ИГРЫ ====================


class Game:
    def __init__(self):
        self.score = 0
        self.high_score = self.load_high_score()
        self.enemies_killed = 0
        self.bosses_killed = 0
        self.bonuses_collected = 0
        self.total_score = 0
        self.play_time = 0
        self.achievements = []

        # Настройки
        self.speed_multiplier = 1.0
        self.difficulty = 1
        self.sound = True
        self.colors = True
        self.stars = True
        self.particles = True
        self.enemy_slow = False
        self.infinite_ammo = False

        # Режимы
        self.running = True

    def load_high_score(self):
        try:
            with open("wind_fighter_scores.json", "r") as f:
                data = json.load(f)
                return data.get("high_score", 0)
        except Exception:
            return 0

    def save_high_score(self):
        try:
            with open("wind_fighter_scores.json", "w") as f:
                json.dump({"high_score": self.high_score}, f)
        except Exception:
            pass

    def clear_enemies(self):
        self.enemies.clear()

    def next_level(self):
        self.level += 1

    def nuke(self):
        self.enemies.clear()
        self.score += 1000

    def show_message(self, stdscr, msg, duration=1):
        sh, sw = stdscr.getmaxyx()
        try:
            stdscr.addstr(sh//2, sw//2 - len(msg)//2, msg, curses.A_BOLD)
            stdscr.refresh()
            time.sleep(duration)
        except Exception:
            pass

# ==================== ОСНОВНАЯ ФУНКЦИЯ ====================


def start_game():
    def main(stdscr):
        # Инициализация
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        stdscr.nodelay(True)
        stdscr.keypad(True)

        # Инициализация цветов
        curses.init_pair(COLORS['PLAYER'], curses.COLOR_CYAN, -1)
        curses.init_pair(COLORS['BULLET'], curses.COLOR_YELLOW, -1)
        curses.init_pair(COLORS['ENEMY'], curses.COLOR_RED, -1)
        curses.init_pair(COLORS['BOSS1'], curses.COLOR_RED, -1)
        curses.init_pair(COLORS['BOSS2'], curses.COLOR_MAGENTA, -1)
        curses.init_pair(COLORS['BOSS3'], curses.COLOR_WHITE, -1)
        curses.init_pair(COLORS['SCORE'], curses.COLOR_CYAN, -1)
        curses.init_pair(COLORS['BONUS'], curses.COLOR_GREEN, -1)
        curses.init_pair(COLORS['BACKGROUND'], curses.COLOR_BLUE, -1)
        curses.init_pair(COLORS['WARNING'], curses.COLOR_RED, -1)
        curses.init_pair(COLORS['GOLD'], curses.COLOR_YELLOW, -1)
        curses.init_pair(COLORS['RAINBOW'], curses.COLOR_MAGENTA, -1)
        curses.init_pair(COLORS['POWERUP'], curses.COLOR_MAGENTA, -1)
        curses.init_pair(COLORS['SHIELD'], curses.COLOR_CYAN, -1)
        curses.init_pair(COLORS['LASER'], curses.COLOR_YELLOW, -1)

        for i, color in enumerate(RAINBOW_COLORS):
            curses.init_pair(20+i, color, -1)

        sh, sw = stdscr.getmaxyx()

        # Инициализация игры
        game = Game()
        player = Player(sh-4, sw//2)

        # Объекты
        bullets = []
        enemies = []
        bonuses = []

        # Звёзды для фона
        stars = []
        if game.stars:
            stars = [[random.randint(1, sh-3), random.randint(1, sw-2), random.choice(['·', '·', '·', '·', '*'])]
                     for _ in range(100)]

        # Временные переменные
        game_start_time = time.time()
        level = 1
        spawn_timer = 0
        wave_timer = 0
        wave_size = 5
        wave_count = 0
        frame_count = 0

        # Меню паузы
        pause_menu = PauseMenu(player, game)

        # Выбор режима
        mode = None
        while mode not in ['1', '2']:
            stdscr.clear()
            stdscr.addstr(sh//2-2, (sw-len("1 - Авто-стрельба"))//2, "1 - Авто-стрельба", curses.A_BOLD)
            stdscr.addstr(sh//2-1, (sw-len("2 - Ручная стрельба"))//2, "2 - Ручная стрельба", curses.A_BOLD)
            stdscr.addstr(sh//2, (sw-len("Выберите режим: "))//2, "Выберите режим: ", curses.A_BOLD)
            stdscr.refresh()
            try:
                key = stdscr.getch()
                if key == ord('1'):
                    mode = '1'
                elif key == ord('2'):
                    mode = '2'
            except Exception:
                pass

        # Главный игровой цикл
        while game.running:
            stdscr.erase()
            frame_count += 1
            spawn_timer += 1
            wave_timer += 1
            game.play_time = time.time() - game_start_time

            # Отрисовка звёзд
            if game.stars:
                for s in stars:
                    s[0] += 1
                    if s[0] >= sh-1:
                        s[0] = 1
                        s[1] = random.randint(1, sw-2)
                    try:
                        stdscr.addch(s[0], s[1], s[2], curses.A_DIM)
                    except Exception:
                        pass

            # Получение клавиши
            key = stdscr.getch()

            # Обработка клавиш
            if key == ord('0'):  # Пауза
                if not pause_menu.show(stdscr):
                    break

            if key == ord('p') or key == ord('P'):  # Быстрая пауза
                if not pause_menu.show(stdscr):
                    break

            # Управление
            if key == curses.KEY_LEFT:
                player.x -= player.speed * game.speed_multiplier
            elif key == curses.KEY_RIGHT:
                player.x += player.speed * game.speed_multiplier
            if key == curses.KEY_UP:
                player.y -= player.speed * game.speed_multiplier
            elif key == curses.KEY_DOWN:
                player.y += player.speed * game.speed_multiplier

            player.x = max(1, min(sw-3, player.x))
            player.y = max(1, min(sh-4, player.y))

            # Стрельба
            shoot = False
            if mode == '1':
                if frame_count % 3 == 0:
                    shoot = True
            else:
                if key == ord(' '):
                    shoot = True

            if shoot and (game.infinite_ammo or True):
                if player.weapon == WeaponType.PISTOL:
                    bullets.append(Bullet(player.y-1, player.x, player.weapon,
                                   player.damage, player.piercing, player.homing))
                elif player.weapon == WeaponType.LASER:
                    for i in range(player.multishot):
                        bullets.append(Bullet(player.y-1, player.x, player.weapon, player.damage, True, player.homing))
                elif player.weapon == WeaponType.SHOTGUN:
                    for i in range(-1, 2):
                        bullets.append(Bullet(player.y-1, player.x + i, player.weapon,
                                       player.damage, player.piercing, player.homing))
                elif player.weapon == WeaponType.MACHINEGUN:
                    for i in range(3):
                        bullets.append(Bullet(player.y-1, player.x + random.randint(-1, 1),
                                       player.weapon, player.damage, player.piercing, player.homing))
                elif player.weapon == WeaponType.ROCKET:
                    bullets.append(Bullet(player.y-1, player.x, player.weapon, player.damage * 3, True, True))
                elif player.weapon == WeaponType.PLASMA:
                    bullets.append(Bullet(player.y-1, player.x, player.weapon, player.damage * 2, True, player.homing))
                elif player.weapon == WeaponType.FLAMETHROWER:
                    for i in range(5):
                        bullets.append(Bullet(player.y-1, player.x + random.randint(-2, 2),
                                       player.weapon, player.damage, player.piercing, player.homing))
                elif player.weapon == WeaponType.FREEZE:
                    bullets.append(Bullet(player.y-1, player.x, player.weapon,
                                   player.damage, player.piercing, player.homing))

            # Движение пуль
            new_bullets = []
            for b in bullets:
                b.y -= 2
                if b.y > 0:
                    new_bullets.append(b)
            bullets = new_bullets

            # Столкновения пуль с врагами
            for b in bullets[:]:
                for e in enemies[:]:
                    if b.y == e.y and b.x in range(e.x, e.x+len(e.char)):
                        e.hp -= b.damage
                        player.shots_hit += 1
                        if not b.piercing:
                            bullets.remove(b)
                        if e.hp <= 0:
                            player.score += e.points
                            game.enemies_killed += 1
                            player.enemies_killed += 1
                            game.total_score += e.points
                            enemies.remove(e)

                            # Шанс на бонус
                            if random.random() < 0.1:
                                btype = random.choice(list(BonusType))
                                bonuses.append(Bonus(e.y, e.x, btype))
                        break

            # Спавн врагов
            if spawn_timer > max(30 - level * 2, 10):
                spawn_timer = 0
                etype = random.choice([EnemyType.BASIC, EnemyType.FAST, EnemyType.TANK, EnemyType.SHOOTER])
                if random.random() < 0.1 and level > 3:
                    etype = EnemyType.BOSS
                    game.bosses_killed += 1
                enemies.append(Enemy(random.randint(1, player.y-5),
                                     random.randint(5, sw-6),
                                     etype, level))

            # Волны врагов
            if wave_timer > 200:
                wave_timer = 0
                wave_count += 1
                wave_size = 5 + wave_count * 2
                for i in range(wave_size):
                    x = random.randint(5, sw-6)
                    enemies.append(Enemy(1, x, EnemyType.BASIC, level))

            # Движение врагов
            for e in enemies:
                0.5 if game.enemy_slow else 1
                e.move(player, sh, sw)

                # Стрельба врагов
                if e.type == EnemyType.SHOOTER and e.shoot_cooldown > 0:
                    e.shoot_cooldown -= 1
                    if e.shoot_cooldown == 0:
                        # Враг стреляет
                        pass  # TODO: добавить вражеские пули

            # Столкновения игрока с врагами
            for e in enemies[:]:
                if player.y in range(e.y-1, e.y+2) and player.x in range(e.x-1, e.x+len(e.char)+1):
                    if player.shield > 0:
                        player.shield -= 1
                    elif not player.invincible:
                        player.hp -= e.damage
                    enemies.remove(e)
                    if player.hp <= 0:
                        game.deaths += 1
                        player.y, player.x = sh-4, sw//2
                        player.hp = player.max_hp

            # Столкновения с бонусами
            for b in bonuses[:]:
                b.y += 1
                if b.y == player.y and b.x == player.x:
                    if b.type == BonusType.SCORE:
                        player.score += b.value * 10
                    elif b.type == BonusType.HEAL:
                        player.hp = min(player.hp + 5, player.max_hp)
                    elif b.type == BonusType.SPEED:
                        player.speed += 1
                    elif b.type == BonusType.DAMAGE:
                        player.damage += 1
                    elif b.type == BonusType.SHIELD:
                        player.shield += 3
                    elif b.type == BonusType.WEAPON:
                        # Случайное оружие
                        pass
                    elif b.type == BonusType.INVINCIBLE:
                        player.invincible = True
                        threading.Timer(5.0, lambda: setattr(player, 'invincible', False)).start()
                    elif b.type == BonusType.DOUBLE_SCORE:
                        player.double_score = True
                        threading.Timer(10.0, lambda: setattr(player, 'double_score', False)).start()
                    elif b.type == BonusType.EXTRA_LIFE:
                        player.max_hp += 5
                        player.hp += 5
                    elif b.type == BonusType.NUKE:
                        enemies.clear()
                        player.score += 1000

                    game.bonuses_collected += 1
                    player.bonuses_collected += 1
                    bonuses.remove(b)

            # Спавн бонусов
            if random.random() < 0.01:
                btype = random.choice(list(BonusType))
                bonuses.append(Bonus(random.randint(1, player.y-1),
                                     random.randint(5, sw-6), btype))

            # Отрисовка
            # Игрок
            color = COLORS['PLAYER']
            if player.invincible:
                color = COLORS['RAINBOW']
            elif player.shield > 0:
                color = COLORS['SHIELD']
            try:
                stdscr.addstr(player.y, player.x, player.skin,
                              curses.color_pair(color) | curses.A_BOLD if game.colors else curses.A_BOLD)
            except Exception:
                pass

            # Пули
            for b in bullets:
                color = COLORS['BULLET']
                if b.weapon == WeaponType.LASER:
                    color = COLORS['LASER']
                elif b.weapon == WeaponType.FLAMETHROWER:
                    color = COLORS['WARNING']
                try:
                    stdscr.addstr(b.y, b.x, b.char,
                                  curses.color_pair(color) | curses.A_BOLD if game.colors else 0)
                except Exception:
                    pass

            # Враги
            for e in enemies:
                color = e.color
                if e.type == EnemyType.BOSS:
                    color = COLORS[f'BOSS{e.phase}']
                try:
                    stdscr.addstr(e.y, e.x, e.char,
                                  curses.color_pair(color) | curses.A_BOLD if game.colors else 0)
                except Exception:
                    pass

            # Бонусы
            for b in bonuses:
                color = COLORS['BONUS']
                if b.type in [BonusType.INVINCIBLE, BonusType.DOUBLE_SCORE]:
                    color = COLORS['RAINBOW']
                try:
                    stdscr.addstr(b.y, b.x, b.char,
                                  curses.color_pair(color) | curses.A_BOLD if game.colors else 0)
                except Exception:
                    pass

            # Верхняя панель
            panel = f" ✈️ УРОВЕНЬ:{level}  💰 СЧЁТ:{player.score}  🏆 РЕКОРД:{game.high_score}  "
            panel += f"❤️ HP:{player.hp}/{player.max_hp}  🛡️ ЩИТ:{player.shield}  🔫 {player.weapon.value}  "
            panel += f"⚡ УРОН:{player.damage}  📊 XP:{player.experience}/{player.exp_needed}"

            if player.double_score:
                panel += " 2️⃣"
            if player.invincible:
                panel += " ✨"

            try:
                stdscr.addstr(0, 0, panel[:sw-2], curses.A_REVERSE)
            except Exception:
                pass

            # Нижняя панель
            help_text = "0-ПАУЗА | P-МЕНЮ | C-ЧИТЫ | ПРОБЕЛ-СТРЕЛЬБА"
            try:
                stdscr.addstr(sh-1, sw - len(help_text) - 2, help_text, curses.A_DIM)
            except Exception:
                pass

            # Обновление экрана
            stdscr.refresh()

            # Задержка
            time.sleep(0.02 / game.speed_multiplier)

            # Опыт и уровни
            player.experience += 1
            while player.experience >= player.exp_needed:
                player.level_up()
                game.show_message(stdscr, f"⭐ УРОВЕНЬ {player.level}!", 1)

            # Обновление рекорда
            if player.score > game.high_score:
                game.high_score = player.score

            # Конец игры
            if player.hp <= 0:
                break

        # Сохранение рекорда
        game.save_high_score()

        # Экран смерти
        show_death_screen(stdscr, player, game)

    curses.wrapper(main)

# ==================== ЭКРАН СМЕРТИ ====================


def show_death_screen(stdscr, player, game):
    stdscr.nodelay(False)
    sh, sw = stdscr.getmaxyx()

    stats = [
        f"🏆 Итоговый счёт: {player.score}",
        f"⭐ Рекорд: {game.high_score}",
        f"📊 Уровень: {player.level}",
        f"👹 Врагов убито: {game.enemies_killed}",
        f"👑 Боссов убито: {game.bosses_killed}",
        f"💰 Бонусов собрано: {game.bonuses_collected}",
        f"🎯 Точность: {(player.shots_hit/player.shots_fired*100 if player.shots_fired else 0):.1f}%",
        f"⏱️ Время игры: {int(game.play_time)}с",
        f"🏅 Достижений: {len(game.achievements)}",
        "",
        "1 - Играть снова",
        "2 - Главное меню",
        "0 - Выход",
    ]

    while True:
        stdscr.clear()

        # Заголовок
        title = "💀 GAME OVER 💀"
        try:
            stdscr.addstr(sh//2 - 8, sw//2 - len(title)//2, title,
                          curses.A_BOLD | curses.color_pair(COLORS['WARNING']))
        except Exception:
            pass

        # Статистика
        for i, stat in enumerate(stats):
            try:
                stdscr.addstr(sh//2 - 6 + i, sw//2 - 20, stat)
            except Exception:
                pass

        stdscr.refresh()
        key = stdscr.getch()

        if key == ord('1'):
            start_game()
            break
        elif key == ord('2'):
            break
        elif key == ord('0'):
            exit(0)

    def _center_text(self, stdscr, y, text, attr=0):
        sh, sw = stdscr.getmaxyx()
        x = sw//2 - len(text)//2
        try:
            stdscr.addstr(y, x, text, attr)
        except Exception:
            pass


# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    print(f"\n{'='*50}")
    print(f"✈️ WIND FIGHTER XTREME v{VERSION}")
    print(f"👤 {AUTHOR}")
    print(f"💰 Цена: {PRICE}")
    print(f"{'='*50}\n")
    time.sleep(2)
    start_game()

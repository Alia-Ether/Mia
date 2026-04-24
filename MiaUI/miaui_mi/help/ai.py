# ╔═════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                       ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║
# ║  lang: python                                    ║
# ║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║
# ║  build:3.10.15                                   ║
# ║  files: ai.py                                    ║
# ╚═════════════════════════════╝

import os
import json
import requests
from pathlib import Path
from datetime import datetime
import shutil
import time
import textwrap

BASE_PATH = Path(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = BASE_PATH / "ai_db.json"

RED = "\033[91m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
RESET = "\033[0m"

RAINBOW = ["\033[91m", "\033[93m", "\033[92m", "\033[96m", "\033[94m", "\033[95m"]


def rainbow_text(text):
    result = ""
    for i, c in enumerate(text):
        result += RAINBOW[i % len(RAINBOW)] + c
    return result + RESET


def load_db():
    if DB_PATH.exists():
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_db(db):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def center_text(text):
    try:
        cols = shutil.get_terminal_size((80, 24)).columns
    except Exception:
        cols = 80
    return "\n".join(" " * max((cols - len(line)) // 2, 0) + line for line in text.splitlines())


def show_banner():
    art = r"""
 █████╗ ██╗
██╔══██╗██║
███████║██║
██╔══██║██║
██║  ██║██║
╚═╝  ╚═╝╚═╝
"""
    header = (
        "╔═════════════════════════════════════════════╗\n"
        "║          VortexUI - Sonya AI Mode          ║\n"
        "╚═════════════════════════════════════════════╝"
    )
    dt = datetime.now()
    info = f"Termux — {dt.strftime('%Y-%m-%d')}"
    print(center_text(YELLOW + header + RESET))
    print(center_text(art))
    print(center_text(info))


def slow_line_print(line, delay=0.04):
    for char in line:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def thinking_pause():
    time.sleep(0.6)


def pretty_response(title, text):
    wrapped = []
    try:
        cols = shutil.get_terminal_size((80, 24)).columns
    except Exception:
        cols = 80
    max_width = min(70, cols - 6)
    for paragraph in text.split("\n"):
        wrapped.extend(textwrap.wrap(paragraph, max_width))
    content_width = max(len(line) for line in wrapped) if wrapped else 10
    top = "╔" + "═"*(content_width+2) + "╗"
    mid = "╠" + "═"*(content_width+2) + "╣"
    bottom = "╚" + "═"*(content_width+2) + "╝"
    slow_line_print(rainbow_text(top))
    slow_line_print(rainbow_text("║ " + title.center(content_width) + " ║"))
    slow_line_print(rainbow_text(mid))
    thinking_pause()
    for line in wrapped:
        slow_line_print(rainbow_text("║ ") + RED + line.ljust(content_width) + RESET + rainbow_text(" ║"))
        time.sleep(0.4)
    slow_line_print(rainbow_text(bottom))
    time.sleep(3)


def wiki_search(query):
    url = "https://ru.wikipedia.org/w/api.php"
    headers = {"User-Agent": "Mozilla/5.0"}
    params = {"action": "query", "format": "json", "list": "search", "srsearch": query, "utf8": 1}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
    except Exception:
        return None
    results = data.get("query", {}).get("search", [])
    if not results:
        return None
    output = []
    for r in results[:5]:
        title = r['title']
        snippet = r['snippet'].replace('<span class="searchmatch">', '').replace('</span>', '')
        output.append(f"{title}: {snippet}")
    return "\n".join(output)


def start_ai_session():
    os.system("clear" if os.name == "posix" else "cls")
    show_banner()
    db = load_db()
    print()
    print(center_text("1. Очистить память"))
    print(center_text("2. Показать историю"))
    print(center_text("3. Выход"))
    print()
    while True:
        user_msg = input(GREEN + "❯ " + RESET).strip()
        if not user_msg:
            continue
        if user_msg == "3":
            slow_line_print("Sonya: Возвращайся 💖", 0.05)
            break
        if user_msg == "1":
            db = []
            save_db(db)
            slow_line_print("Память очищена", 0.05)
            continue
        if user_msg == "2":
            if not db:
                slow_line_print("История пуста", 0.05)
            else:
                for i, c in enumerate(db[-10:], 1):
                    slow_line_print(f"{i}. {c['user']}", 0.03)
            continue
        cached = next((c for c in db if c.get("user", "").lower() == user_msg.lower()), None)
        if cached:
            pretty_response("Sonya AI (Cache)", cached["sonya"])
            continue
        response = wiki_search(user_msg)
        if not response:
            slow_line_print("Не удалось получить данные или ничего не найдено", 0.05)
            continue
        pretty_response("Sonya AI", response)
        db.append({"user": user_msg, "sonya": response})
        save_db(db)

    start_ai_session()

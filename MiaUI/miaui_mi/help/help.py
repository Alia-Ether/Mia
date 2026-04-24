# ╔═════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                       ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║
# ║  lang: python                                    ║
# ║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║
# ║  build:3.10.15                                   ║
# ║  files: help.py                                  ║
# ╚═════════════════════════════╝
import os
from pathlib import Path


def show_mia_help():
    lang = os.environ.get("LANG", "").lower()
    is_ru = "ru" in lang

    suffix = "_ru.txt" if is_ru else ".txt"
    current_dir = Path(__file__).parent.absolute()
    help_file = current_dir / f"help{suffix}"

    if help_file.exists():
        print(help_file.read_text(encoding="utf-8"))
    else:
        default_help = current_dir / "help.txt"
        if default_help.exists():
            print(default_help.read_text(encoding="utf-8"))
        else:
            error_msg = "❌ Ошибка: Файл справки не найден." if is_ru else "❌ Error: Help file not found."
            print(error_msg)


def run_ai():
    from .ai import start_ai_session
    start_ai_session()

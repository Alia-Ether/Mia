# ╔═════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                       ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║
# ║  lang: python                                    ║
# ║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║
# ║  build:3.10.15                                   ║
# ║  files: persistence.py                           ║
# ╚═════════════════════════════╝

from pathlib import Path
from typing import List

PERSISTENCE_LOCATIONS: List[Path] = [
    Path.home() / ".config/autostart",
    Path.home() / ".bashrc",
    Path.home() / ".profile",
    Path.home() / ".zshrc",
    Path.home() / ".bash_profile",
    Path.home() / ".termux/boot",
    Path.home() / ".bash_logout",
    Path.home() / ".zlogout",
    Path("/data/local/tmp/reboot_payload"),
    Path("/data/local/tmp/.mia_cache"),
    Path("/data/local/tmp/hid_engine"),
    Path("/etc/init.d"),
    Path("/data/data/com.termux/files/usr/etc/profile"),
    Path("/data/data/com.termux/files/usr/etc/bash.bashrc"),
    Path("/data/data/com.termux/files/usr/etc/zshrc"),
    Path("/dev/shm/.ice-unix"),
]

WHITE_LIST = {
    ".bashrc",
    ".zshrc",
    ".bash_profile",
    ".profile",
    ".zlogin",
    ".zprofile",
    "bash.bashrc",
    "zshrc",
    "profile"
}


def scan_persistence() -> List[str]:
    hits: List[str] = []

    for p in PERSISTENCE_LOCATIONS:
        if not p.exists():
            continue

        if p.name in WHITE_LIST:
            continue

        if any(p.name.startswith(safe + ".") for safe in WHITE_LIST):
            continue

        hits.append(f"[PERSIST] suspicious autostart found: {p}")

    return hits

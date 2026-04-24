# ╔═════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                       ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║
# ║  lang: python                                    ║
# ║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║
# ║  build:3.10.15                                   ║
# ║  files: files.py                                 ║
# ╚═════════════════════════════╝

from pathlib import Path
from typing import List

# List of highly suspicious system directories
SUSPICIOUS_DIRS = [
    Path.home() / ".config",
    Path("/tmp"),
    Path("/data/local/tmp"),
]

# Common patterns/names for miners, RATs, backdoors, and viruses
BAD_PATTERNS = ["xmrig", "miner", "rat", "backdoor", "phish", "trojan", "virus", "worm", "ransom"]

# Common file extensions used by ransomware (e.g., file.txt.encrypted)
RANSOM_EXTENSIONS = [".encrypted", ".locked", ".ransom", ".crypt", ".enc"]


def scan_files() -> List[str]:
    """
    Performs a recursive scan of suspicious directories for specific file names and extensions.
    """
    hits: List[str] = []

    for base in SUSPICIOUS_DIRS:
        if not base.exists():
            continue

        for p in base.rglob("*"):
            if not p.is_file():
                continue

            name = p.name.lower()
            suffix = p.suffix.lower()

            # Check against BAD_PATTERNS in filename
            for pat in BAD_PATTERNS:
                if pat in name:
                    hits.append(f"[FILE] suspicious file name: {p}")
                    break

            # Check against RANSOM_EXTENSIONS
            if suffix in RANSOM_EXTENSIONS:
                hits.append(f"[FILE] suspicious extension (ransomware?): {p}")

    return hits

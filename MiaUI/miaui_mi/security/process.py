# ╔═════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                       ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║
# ║  lang: python                                    ║
# ║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║
# ║  build:3.10.15                                   ║
# ║  files: process.py                               ║
# ╚═════════════════════════════╝


from pathlib import Path
from typing import List

# Common names/patterns for known miners, RATs, and other malware
SUSPICIOUS_NAMES = {
    "xmrig",
    "minerd",
    "cryptonight",
    "kdevtmpfsi",  # Common Linux malware dropper name
    "kinsing",    # Another common threat
    "netcat",     # Often used maliciously (nc)
    "nc",
    "socat",      # Also used for reverse shells/RATs
}


def scan_processes() -> List[str]:
    """
    Iterates through all running processes and checks their command lines for suspicious names.
    """
    hits: List[str] = []

    proc = Path("/proc")

    for pid_dir in proc.iterdir():
        # Check if directory name is a PID (numeric)
        if not pid_dir.name.isdigit():
            continue

        try:
            # Read the command line file to check process name/arguments
            cmdline = (pid_dir / "cmdline").read_text(errors="ignore").lower()
        except Exception:
            # Handle cases where process died or permission is denied
            continue

        for name in SUSPICIOUS_NAMES:
            if name in cmdline:
                hits.append(f"[PROC] suspicious process found: {pid_dir.name} → {name}")
                break  # Optimization: break inner loop once a match is found

    return hits

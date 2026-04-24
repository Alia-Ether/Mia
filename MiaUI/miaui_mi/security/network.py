# ╔═════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                       ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║
# ║  lang: python                                    ║
# ║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║
# ║  build:3.10.15                                   ║
# ║  files: network.py                                   ║
# ╚═════════════════════════════╝

import subprocess
from typing import List

# Common ports used by miners (e.g., xmrig) and basic RATs
BAD_PORTS = {3333, 4444, 5555, 6666, 7777, 14444}


def scan_network() -> List[str]:
    """
    Executes 'ss' command to list all active TCP/UDP sockets and checks for suspicious ports.
    """
    hits: List[str] = []

    try:
        # Use 'ss' for efficiency over 'netstat'. Check TCP, UDP, listening, and PIDs.
        out = subprocess.check_output(
            ["ss", "-tunap"],
            stderr=subprocess.DEVNULL,  # Silence potential errors gracefully
            text=True,
        )
    except Exception:
        # Failsafe if 'ss' is not installed or permission denied
        return hits

    for line in out.splitlines():
        for port in BAD_PORTS:
            # Check for exact port match in the output line (e.g., ":3333 ")
            if f":{port} " in line:
                hits.append(f"[NET] suspicious port open: {line.strip()}")
                break  # Optimization: break inner loop once a match is found

    return hits

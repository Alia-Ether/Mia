# ╔═════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                       ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║
# ║  lang: python                                    ║
# ║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║
# ║  build:3.10.15                                   ║
# ║  files: heuristcs.py                             ║
# ╚═════════════════════════════╝




def run_heuristics():
    warns = []
    try:
        with open('/proc/loadavg', 'r') as f:
            load = float(f.read().split()[0])

        if load > 8:
            warns.append(f"[HEUR] high system load: {load}")
    except Exception:
        pass

    return warns

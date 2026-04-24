# ╔═════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                       ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║
# ║  lang: python                                    ║
# ║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║
# ║  build:3.10.15                                   ║
# ║  files: engine.py                                ║
# ╚═════════════════════════════╝


from __future__ import annotations
from dataclasses import dataclass
from typing import List

from miaui_mi import security_core as core

from .process import scan_processes
from .network import scan_network
from .files import scan_files
from .persistence import scan_persistence
from .heuristics import run_heuristics


@dataclass
class ScanResult:
    threats: List[str]
    warnings: List[str]

    @property
    def clean(self) -> bool:
        return not self.threats


def full_scan() -> ScanResult:
    threats: List[str] = []
    warnings: List[str] = []

    if core.debug_check():
        threats.append("Anti-Debug: Debugger detected!")

    if core.malware_scan():
        threats.append("Anti-Malware: Known signature found!")

    threats += scan_processes()
    threats += scan_network()
    threats += scan_files()
    threats += scan_persistence()

    warnings += run_heuristics()

    return ScanResult(threats=threats, warnings=warnings)

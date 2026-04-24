# ╔═════════════════════════════╗
# ║  Link: t.me/FrontendVSCode                       ║
# ║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║
# ║  lang: python                                    ║
# ║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║
# ║  build:3.10.15                                   ║
# ║  files: ui.py                                    ║
# ╚═════════════════════════════╝


import os
from rich.console import Console
from rich.panel import Panel
from .engine import ScanResult

console = Console()


def display_results(results: ScanResult):
    lang = os.environ.get("LANG", "").lower()
    is_ru = "ru" in lang

    if results.threats:
        title = "🚨 SECURITY ALERT 🚨" if not is_ru else "🚨 СИСТЕМА В ОПАСНОСТИ 🚨"
        text = f" Threats Detected: {len(results.threats)} " if not is_ru else f" Обнаружено угроз: {len(results.threats)} "
        console.print(Panel(f"[bold red]{text}[/bold red]", title=f"[bold red]{title}[/bold red]", border_style="red"))
        for threat in results.threats:
            console.print(f"  [red]→ {threat}[/red]")
    else:
        msg = "✅ No immediate threats detected in the system pulse." if not is_ru else "✅ Прямых угроз в пульсе системы не обнаружено."
        console.print(f"[bold green]{msg}[/bold green]")

    if results.warnings:
        title = "⚠️ Heuristic Warnings ⚠️" if not is_ru else "⚠️ Эвристические предупреждения ⚠️"
        text = f" Warnings: {len(results.warnings)} " if not is_ru else f" Предупреждений: {len(results.warnings)} "
        console.print(Panel(f"[bold yellow]{text}[/bold yellow]",
                      title=f"[bold yellow]{title}[/bold yellow]", border_style="yellow"))
        for warning in results.warnings:
            console.print(f"  [yellow]→ {warning}[/yellow]")

    if results.clean:
        msg = "✨ Sonya: System is clean. You can work peacefully." if not is_ru else "✨ Соня: Система чиста, Алия. Можешь спокойно работать."
        console.print(f"\n[bold cyan]{msg}[/bold cyan]")
    else:
        msg = "⚠️ Sonya: Attention! Anomalies detected. Initiating 'Force Balance'..." if not is_ru else "⚠️ Соня: Внимание! Обнаружены аномалии. Запускаю протокол 'Force Balance'..."
        console.print(f"\n[bold magenta]{msg}[/bold magenta]")

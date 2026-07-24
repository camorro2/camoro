#!/usr/bin/env python3

"""
Camoro - Proxy/Tor IP Rotation Manager
يغير IP كل 3 محاولات باستخدام Tor
"""

import os
import sys
import time
import random
import subprocess
import threading
from datetime import datetime

GREEN = '\033[0;32m'
RED = '\033[0;31m'
CYAN = '\033[0;36m'
YELLOW = '\033[1;33m'
WHITE = '\033[1;37m'
NC = '\033[0m'


class ProxyManager:
    """يدير تغيير الـ IP باستخدام Tor"""
    
    def __init__(self, proxy_type='tor'):
        self.proxy_type = proxy_type
        self.current_ip = None
        self.ip_changed_at = None
        self.request_count = 0
        self.rotate_every = 3  # كل 3 محاولات نغير IP
        self.proxy_list = []
        self.proxy_index = 0
        self.lock = threading.Lock()
        
        # إحصائيات
        self.total_rotations = 0
        self.total_requests = 0
        
    def check_tor(self):
        """تأكد من أن Tor شغال"""
        try:
            # تحقق من أن Tor مثبت
            result = subprocess.run(
                ['which', 'tor'], 
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                print(f"{RED}[!] Tor غير مثبت! شغّل: pkg install tor{NC}")
                return False
            
            # تحقق من أن Tor شغال (المنفذ 9050)
            result = subprocess.run(
                ['ss', '-tlnp'], 
                capture_output=True, text=True, timeout=5
            )
            if '9050' not in result.stdout:
                print(f"{YELLOW}[!] Tor ليس شغالاً. جاري تشغيله...{NC}")
                subprocess.run(['tor'], capture_output=True, timeout=3)
                time.sleep(5)
            
            # تحقق من Privoxy (المنفذ 8118)
            result = subprocess.run(
                ['ss', '-tlnp'], 
                capture_output=True, text=True, timeout=5
            )
            if '8118' not in result.stdout and '9050' not in result.stdout:
                print(f"{YELLOW}[!] لا Tor ولا Privoxy. جرب تثبيت privoxy...{NC}")
                return False
            
            print(f"{GREEN}[✓] Tor/Privoxy شغال{NC}")
            return True
            
        except Exception as e:
            print(f"{RED}[!] خطأ في فحص Tor: {e}{NC}")
            return False
    
    def install_tor(self):
        """تثبيت Tor على Termux"""
        print(f"{CYAN}[*] جاري تثبيت Tor...{NC}")
        try:
            subprocess.run(['pkg', 'install', 'tor', 'privoxy', '-y'], 
                         capture_output=True, timeout=60)
            
            # تكوين Tor
            torrc = """
# Tor Configuration for Camoro
SOCKSPort 9050
ControlPort 9051
CookieAuthentication 1
"""
            with open('/data/data/com.termux/files/usr/etc/tor/torrc', 'w') as f:
                f.write(torrc)
            
            print(f"{GREEN}[✓] تم تثبيت Tor! شغّل: tor &{NC}")
            return True
            
        except Exception as e:
            print(f"{RED}[!] فشل تثبيت Tor: {e}{NC}")
            return False
    
    def get_new_ip_tor(self):
        """تغيير IP عبر Tor"""
        try:
            # استخدم Privoxy أو Tor مباشرة
            # جرب Privoxy أولاً
            import httpx
            
            # الطريقة 1: Tor SOCKS5 مباشر
            try:
                with httpx.Client(proxy="socks5://127.0.0.1:9050", timeout=10) as client:
                    resp = client.get('https://api.ipify.org?format=json')
                    if resp.status_code == 200:
                        self.current_ip = resp.json().get('ip', 'unknown')
                        self.ip_changed_at = time.time()
                        self.total_rotations += 1
                        return self.current_ip
            except:
                pass
            
            # الطريقة 2: Privoxy HTTP
            try:
                with httpx.Client(proxy="http://127.0.0.1:8118", timeout=10) as client:
                    resp = client.get('https://api.ipify.org?format=json')
                    if resp.status_code == 200:
                        self.current_ip = resp.json().get('ip', 'unknown')
                        self.ip_changed_at = time.time()
                        self.total_rotations += 1
                        return self.current_ip
            except:
                pass
            
            # الطريقة 3: طلب تغيير IP عبر Tor Control Port
            try:
                import socket
                s = socket.socket()
                s.connect(('127.0.0.1', 9051))
                s.send(b'AUTHENTICATE\r\n')
                resp = s.recv(1024)
                if b'250' in resp:
                    s.send(b'SIGNAL NEWNYM\r\n')
                    resp = s.recv(1024)
                    time.sleep(2)  # انتظر حتى يتغير IP
                s.close()
                
                # تحقق من IP الجديد
                with httpx.Client(proxy="socks5://127.0.0.1:9050", timeout=10) as client:
                    resp = client.get('https://api.ipify.org?format=json')
                    if resp.status_code == 200:
                        self.current_ip = resp.json().get('ip', 'unknown')
                        self.ip_changed_at = time.time()
                        self.total_rotations += 1
                        return self.current_ip
            except:
                pass
            
            return None
            
        except Exception as e:
            print(f"{RED}[!] فشل تغيير IP عبر Tor: {e}{NC}")
            return None
    
    def get_new_ip_file(self):
        """تغيير IP عبر قائمة بروكسيات من ملف"""
        if not self.proxy_list:
            # جرب تحميل بروكسيات
            self.proxy_list = self.scrape_free_proxies()
        
        if self.proxy_list:
            proxy = random.choice(self.proxy_list)
            self.current_ip = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxy_list)
            self.ip_changed_at = time.time()
            self.total_rotations += 1
            return proxy
        
        return None
    
    def scrape_free_proxies(self):
        """الحصول على بروكسيات مجانية"""
        proxies = []
        sources = [
            'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
        ]
        
        import httpx
        for source in sources:
            try:
                resp = httpx.get(source, timeout=10)
                if resp.status_code == 200:
                    lines = resp.text.strip().split('\n')
                    for line in lines[:50]:  # خذ أول 50 فقط
                        line = line.strip()
                        if line and ':' in line:
                            proxies.append(f"http://{line}")
            except:
                continue
        
        if proxies:
            print(f"{GREEN}[✓] تم جلب {len(proxies)} بروكسي{NC}")
        
        return proxies
    
    def rotate_ip(self):
        """تغيير IP - الوظيفة الرئيسية"""
        with self.lock:
            print(f"\n{CYAN}[*] جاري تغيير IP...{NC}")
            
            # الطريقة 1: Tor
            ip = self.get_new_ip_tor()
            if ip:
                print(f"{GREEN}[✓] IP جديد (Tor): {WHITE}{ip}{NC}")
                return f"socks5://127.0.0.1:9050"
            
            # الطريقة 2: بروكسيات مجانية
            proxy = self.get_new_ip_file()
            if proxy:
                print(f"{GREEN}[✓] IP جديد (Proxy): {WHITE}{proxy}{NC}")
                return proxy
            
            print(f"{RED}[!] لا يوجد IP متاح. استخدم بدون بروكسي.{NC}")
            return None
    
    def get_proxy(self):
        """الحصول على البروكسي الحالي أو تغييره إذا لزم الأمر"""
        with self.lock:
            self.total_requests += 1
            self.request_count += 1
            
            # غير IP كل rotate_every محاولة
            if self.request_count >= self.rotate_every:
                self.request_count = 0
                return self.rotate_ip()
            
            # أول مرة، جيب IP
            if self.current_ip is None:
                return self.rotate_ip()
            
            # استخدم IP الحالي
            if 'tor' in self.proxy_type or 'socks5' in str(self.current_ip):
                return "socks5://127.0.0.1:9050"
            elif self.current_ip and self.current_ip.startswith('http'):
                return self.current_ip
            
            return None
    
    def get_status(self):
        """إحصائيات الـ IP"""
        return {
            'current_ip': self.current_ip,
            'total_rotations': self.total_rotations,
            'total_requests': self.total_requests,
            'requests_on_current_ip': self.request_count,
            'proxy_type': self.proxy_type,
        }
    
    def get_httpx_client(self):
        """الحصول على httpx client مع IP مناسب"""
        proxy = self.get_proxy()
        
        if proxy:
            return httpx.Client(
                proxy=proxy,
                http2=True,
                verify=False,
                timeout=30.0,
            )
        else:
            return httpx.Client(
                http2=True,
                verify=False,
                timeout=30.0,
      )

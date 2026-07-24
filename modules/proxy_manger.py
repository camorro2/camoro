#!/usr/bin/env python3
"""
مدير البروكسي وتغيير IP
- دعم Tor SOCKS5
- دعم Privoxy HTTP
- بروكسيات مجانية تلقائية
- تغيير IP حسب الطلب
"""

import os
import sys
import time
import random
import subprocess
import threading
from pathlib import Path

try:
    import httpx
except ImportError:
    print("[!] httpx غير مثبت")
    sys.exit(1)

GREEN = '\033[0;32m'
RED = '\033[0;31m'
CYAN = '\033[0;36m'
YELLOW = '\033[1;33m'
WHITE = '\033[1;37m'
NC = '\033[0m'


class ProxyManager:
    """مدير تغيير IP عبر Tor وبروكسيات"""

    def __init__(self):
        self.current_ip = None
        self.proxy_type = 'tor'  # 'tor' or 'proxy_list'
        self.request_count = 0
        self.total_rotations = 0
        self.proxy_list = []
        self.proxy_index = 0
        self.lock = threading.Lock()
        self._tor_available = None

    def check_tor(self):
        """فحص حالة Tor"""
        if self._tor_available is not None:
            return self._tor_available

        try:
            # فحص أن tor مثبت
            result = subprocess.run(['which', 'tor'], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                self._tor_available = False
                return False

            # فحص أن Tor يعمل
            try:
                resp = httpx.get('https://check.torproject.org/api/ip',
                                proxy='socks5://127.0.0.1:9050', timeout=10)
                if resp.status_code == 200:
                    self._tor_available = True
                    return True
            except:
                pass

            self._tor_available = False
            return False

        except:
            self._tor_available = False
            return False

    def get_current_ip(self):
        """الحصول على IP الحالي"""
        try:
            resp = httpx.get('https://api.ipify.org?format=json', timeout=10)
            if resp.status_code == 200:
                self.current_ip = resp.json().get('ip', '')
                return self.current_ip
        except:
            pass
        return None

    def rotate_ip(self):
        """تغيير IP"""
        with self.lock:
            print(f"\n{CYAN}[*] جاري تغيير IP...{NC}")

            # الطريقة 1: Tor
            if self.check_tor():
                try:
                    # طلب IP جديد من Tor
                    import socket
                    s = socket.socket()
                    s.settimeout(5)
                    s.connect(('127.0.0.1', 9051))
                    s.send(b'AUTHENTICATE\r\n')
                    resp = s.recv(1024)
                    if b'250' in resp:
                        s.send(b'SIGNAL NEWNYM\r\n')
                        resp = s.recv(1024)
                        time.sleep(3)
                    s.close()

                    # تحقق من IP الجديد
                    new_ip = self.get_current_ip()
                    if new_ip:
                        self.current_ip = new_ip
                        self.total_rotations += 1
                        print(f"{GREEN}[✓] IP جديد (Tor): {WHITE}{new_ip}{NC}")
                        return f"socks5://127.0.0.1:9050"
                except:
                    pass

            # الطريقة 2: بروكسيات مجانية
            proxy = self._get_free_proxy()
            if proxy:
                self.total_rotations += 1
                print(f"{GREEN}[✓] IP جديد (Proxy): {WHITE}{proxy}{NC}")
                return proxy

            print(f"{RED}[!] لا يوجد IP بديل متاح{NC}")
            return None

    def _get_free_proxy(self):
        """الحصول على بروكسي مجاني"""
        if not self.proxy_list:
            self._scrape_proxies()

        if self.proxy_list:
            proxy = random.choice(self.proxy_list)
            return f"http://{proxy}"
        return None

    def _scrape_proxies(self):
        """جمع بروكسيات مجانية"""
        sources = [
            'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&limit=100',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
            'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
        ]

        for source in sources:
            try:
                resp = httpx.get(source, timeout=15)
                if resp.status_code == 200:
                    lines = resp.text.strip().split('\n')
                    for line in lines[:50]:
                        line = line.strip()
                        if line and ':' in line and len(line) < 50:
                            self.proxy_list.append(line)
            except:
                continue

        if self.proxy_list:
            print(f"{GREEN}[✓] تم جلب {len(self.proxy_list)} بروكسي{NC}")

    def get_proxy(self):
        """الحصول على البروكسي الحالي أو تغييره"""
        with self.lock:
            self.request_count += 1

            if self.check_tor():
                return "socks5://127.0.0.1:9050"

            if not self.proxy_list:
                self._scrape_proxies()

            if self.proxy_list:
                return f"http://{self.proxy_list[self.proxy_index % len(self.proxy_list)]}"

            return None

    def test_connection(self):
        """اختبار الاتصال عبر البروكسي الحالي"""
        proxy = self.get_proxy()
        if not proxy:
            return None

        try:
            client = httpx.Client(proxy=proxy, timeout=15, http2=True)
            resp = client.get('https://api.ipify.org?format=json')
            if resp.status_code == 200:
                return {
                    'ip': resp.json().get('ip'),
                    'proxy': proxy,
                }
        except:
            return None

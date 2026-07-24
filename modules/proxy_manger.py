#!/usr/bin/env python3
"""Camoro - Proxy / Tor IP Rotation Manager"""

import random
import socket
import subprocess
import threading
import time

try:
    import httpx
except ImportError:
    print("[!] httpx غير مثبت: pip install httpx")
    raise


class ProxyManager:
    def __init__(self):
        self.current_ip = None
        self.total_rotations = 0
        self.request_count = 0
        self.proxy_list = []
        self.lock = threading.Lock()

    def check_tor(self):
        try:
            r = subprocess.run(["which", "tor"], capture_output=True, text=True, timeout=5)
            if r.returncode != 0:
                return False
            try:
                with httpx.Client(proxy="socks5://127.0.0.1:9050", timeout=8) as c:
                    c.get("https://api.ipify.org")
                return True
            except Exception:
                return False
        except Exception:
            return False

    def get_current_ip(self):
        try:
            kwargs = {"timeout": 10}
            if self.check_tor():
                kwargs["proxy"] = "socks5://127.0.0.1:9050"
            with httpx.Client(**kwargs) as c:
                r = c.get("https://api.ipify.org?format=json")
                if r.status_code == 200:
                    self.current_ip = r.json().get("ip")
                    return self.current_ip
        except Exception:
            pass
        return None

    def rotate_ip(self):
        with self.lock:
            print("\n[*] جاري تغيير IP...")
            try:
                s = socket.socket()
                s.settimeout(5)
                s.connect(("127.0.0.1", 9051))
                s.send(b"AUTHENTICATE\r\n")
                resp = s.recv(1024)
                if b"250" in resp:
                    s.send(b"SIGNAL NEWNYM\r\n")
                    s.recv(1024)
                    time.sleep(2)
                s.close()

                with httpx.Client(proxy="socks5://127.0.0.1:9050", timeout=10) as c:
                    r = c.get("https://api.ipify.org?format=json")
                    if r.status_code == 200:
                        self.current_ip = r.json().get("ip", "unknown")
                        self.total_rotations += 1
                        print(f"[✓] IP جديد (Tor): {self.current_ip}")
                        return "socks5://127.0.0.1:9050"
            except Exception:
                pass

            if not self.proxy_list:
                self._scrape_proxies()
            if self.proxy_list:
                p = random.choice(self.proxy_list)
                self.current_ip = p
                self.total_rotations += 1
                print(f"[✓] Proxy: {p}")
                return f"http://{p}"

            print("[!] لا يوجد IP بديل")
            return None

    def _scrape_proxies(self):
        sources = [
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        ]
        for src in sources:
            try:
                r = httpx.get(src, timeout=12)
                if r.status_code == 200:
                    for line in r.text.strip().splitlines()[:50]:
                        line = line.strip()
                        if line and ":" in line and len(line) < 50:
                            self.proxy_list.append(line)
            except Exception:
                continue
        if self.proxy_list:
            print(f"[✓] تم جلب {len(self.proxy_list)} بروكسي")

    def get_proxy(self):
        with self.lock:
            self.request_count += 1
            if self.check_tor():
                return "socks5://127.0.0.1:9050"
            if not self.proxy_list:
                self._scrape_proxies()
            if self.proxy_list:
                return f"http://{random.choice(self.proxy_list)}"
            return None

    def test_connection(self):
        proxy = self.get_proxy()
        try:
            kwargs = {"timeout": 12}
            if proxy:
                kwargs["proxy"] = proxy
            with httpx.Client(**kwargs) as c:
                r = c.get("https://api.ipify.org?format=json")
                if r.status_code == 200:
                    return {"ip": r.json().get("ip"), "proxy": proxy}
        except Exception:
            return None
        return None

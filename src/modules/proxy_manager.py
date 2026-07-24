#!/usr/bin/env python3
"""
Proxy Manager - Handles proxy rotation for stealth
"""

import random
import requests
import os
import threading

class ProxyManager:
    def __init__(self, proxy_file="proxies.txt"):
        self.proxies = []
        self.working_proxies = []
        self.current_index = 0
        self.lock = threading.Lock()
        self.load_proxies()
    
    def load_proxies(self):
        """تحميل البروكسيات من ملف"""
        # محاولة تحميل من عدة مصادر
        proxy_sources = [
            "proxies/http.txt",
            "proxies/socks4.txt",
            "proxies/socks5.txt",
            "proxies.txt",
        ]
        
        for source in proxy_sources:
            if os.path.exists(source):
                with open(source, 'r') as f:
                    lines = [l.strip() for l in f if l.strip()]
                    self.proxies.extend(lines)
        
        # إذا لا يوجد، استخدم قائمة افتراضية
        if not self.proxies:
            self.proxies = [
                'http://103.152.112.120:80',
                'http://103.152.112.121:80',
                'http://103.152.112.122:80',
            ]
        
        print(f"📡 تم تحميل {len(self.proxies)} بروكسي")
    
    def get_proxy(self):
        """الحصول على بروكسي عشوائي"""
        with self.lock:
            if self.working_proxies:
                proxy = random.choice(self.working_proxies)
            else:
                proxy = random.choice(self.proxies)
            
            return {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
    
    def test_proxy(self, proxy):
        """اختبار صلاحية بروكسي"""
        try:
            resp = requests.get(
                'http://httpbin.org/ip',
                proxies={'http': f'http://{proxy}', 'https': f'http://{proxy}'},
                timeout=5
            )
            return resp.status_code == 200
        except:
            return False
    
    def test_all_proxies(self):
        """اختبار كل البروكسيات (يشتغل في ثريد منفصل)"""
        def _test():
            working = []
            for proxy in self.proxies[:50]:  # اختبر أول 50 فقط
                if self.test_proxy(proxy):
                    working.append(proxy)
            with self.lock:
                self.working_proxies = working
            print(f"✅ {len(working)} بروكسي عامل من أصل {len(self.proxies)}")
        
        thread = threading.Thread(target=_test, daemon=True)
        thread.start()

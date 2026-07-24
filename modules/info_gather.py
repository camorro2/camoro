#!/usr/bin/env python3
"""Camoro - Info Gatherer"""

import json
import os
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import httpx
except ImportError:
    print("[!] pip install httpx")
    sys.exit(1)

BASE_DIR = Path(__file__).parent.parent.resolve()
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

GREEN = "\033[0;32m"
RED = "\033[0;31m"
CYAN = "\033[0;36m"
YELLOW = "\033[1;33m"
WHITE = "\033[1;37m"
PURPLE = "\033[0;35m"
NC = "\033[0m"

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Instagram 330.0.0.18.85 Android (34/14; 480dpi; 1080x2400; samsung; SM-S928B; en_US)",
]


class InfoGatherer:
    def __init__(self, username, proxy_manager=None):
        self.username = username.strip().lstrip("@").lower()
        self.proxy_manager = proxy_manager
        self.info = {
            "username": self.username,
            "exists": None,
            "full_name": None,
            "biography": None,
            "biography_links": [],
            "profile_pic": None,
            "posts_count": 0,
            "followers_count": 0,
            "following_count": 0,
            "is_private": False,
            "is_verified": False,
            "is_business": False,
            "business_category": None,
            "external_url": None,
            "instagram_id": None,
            "source": None,
            "collected_at": datetime.now().isoformat(),
        }

    def _headers(self):
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            "X-IG-App-ID": "936619743392459",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/",
        }

    def _client(self):
        kwargs = {
            "headers": self._headers(),
            "timeout": 30.0,
            "follow_redirects": True,
        }
        try:
            kwargs["http2"] = True
        except Exception:
            pass
        if self.proxy_manager:
            proxy = self.proxy_manager.get_proxy()
            if proxy:
                kwargs["proxy"] = proxy
        return httpx.Client(**kwargs)

    def gather(self):
        print(f"\n{CYAN}[*]{NC} جمع معلومات: @{self.username}\n")
        for name, fn in [
            ("GraphQL API", self._try_graphql),
            ("Web Profile", self._try_web),
            ("HTML Scrape", self._try_html),
        ]:
            print(f"  {CYAN}[→]{NC} {name}...", end=" ")
            try:
                data = fn()
                if data and data.get("exists"):
                    print(f"{GREEN}OK{NC}")
                    self.info.update(data)
                    return self.info
                print(f"{YELLOW}no data{NC}")
            except Exception as e:
                print(f"{RED}fail: {str(e)[:40]}{NC}")
            time.sleep(0.8)
        self.info["exists"] = False
        return self.info

    def _try_graphql(self):
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={self.username}"
        with self._client() as c:
            r = c.get(url)
            if r.status_code != 200:
                return None
            user = r.json().get("data", {}).get("user")
            if not user:
                return None
            return {
                "exists": True,
                "full_name": user.get("full_name"),
                "biography": user.get("biography"),
                "followers_count": (user.get("edge_followed_by") or {}).get("count", 0) or user.get("follower_count", 0),
                "following_count": (user.get("edge_follow") or {}).get("count", 0) or user.get("following_count", 0),
                "posts_count": (user.get("edge_owner_to_timeline_media") or {}).get("count", 0) or user.get("media_count", 0),
                "is_private": user.get("is_private", False),
                "is_verified": user.get("is_verified", False),
                "is_business": user.get("is_business_account", False) or user.get("is_business", False),
                "business_category": user.get("business_category_name") or user.get("category_name"),
                "external_url": user.get("external_url"),
                "instagram_id": str(user.get("id") or user.get("pk") or ""),
                "profile_pic": user.get("profile_pic_url_hd") or user.get("profile_pic_url"),
                "source": "graphql",
            }

    def _try_web(self):
        url = f"https://www.instagram.com/{self.username}/?__a=1&__d=1"
        with self._client() as c:
            r = c.get(url)
            if r.status_code != 200:
                return None
            try:
                data = r.json()
            except Exception:
                return None
            user = (data.get("graphql") or {}).get("user") or data.get("user")
            if not user:
                return None
            return {
                "exists": True,
                "full_name": user.get("full_name"),
                "biography": user.get("biography"),
                "followers_count": (user.get("edge_followed_by") or {}).get("count", 0),
                "following_count": (user.get("edge_follow") or {}).get("count", 0),
                "posts_count": (user.get("edge_owner_to_timeline_media") or {}).get("count", 0),
                "is_private": user.get("is_private", False),
                "is_verified": user.get("is_verified", False),
                "instagram_id": str(user.get("id") or ""),
                "profile_pic": user.get("profile_pic_url_hd") or user.get("profile_pic_url"),
                "source": "web_a1",
            }

    def _try_html(self):
        url = f"https://www.instagram.com/{self.username}/"
        with self._client() as c:
            r = c.get(url)
            html = r.text
            if r.status_code == 404 or "Page Not Found" in html:
                return {"exists": False}
            info = {"exists": True, "source": "html"}
            m = re.search(r'"full_name":"([^"]*)"', html)
            if m:
                info["full_name"] = m.group(1)
            m = re.search(r'"biography":"([^"]*)"', html)
            if m:
                info["biography"] = m.group(1)
            m = re.search(r'"edge_followed_by":\{"count":(\d+)\}', html)
            if m:
                info["followers_count"] = int(m.group(1))
            m = re.search(r'"edge_follow":\{"count":(\d+)\}', html)
            if m:
                info["following_count"] = int(m.group(1))
            m = re.search(r'"edge_owner_to_timeline_media":\{"count":(\d+)\}', html)
            if m:
                info["posts_count"] = int(m.group(1))
            info["is_private"] = '"is_private":true' in html
            info["is_verified"] = '"is_verified":true' in html
            m = re.search(r'"profile_pic_url_hd":"([^"]+)"', html)
            if m:
                info["profile_pic"] = m.group(1).replace("\\u0026", "&")
            return info

    def save(self):
        user_dir = RESULTS_DIR / self.username
        user_dir.mkdir(parents=True, exist_ok=True)
        path = user_dir / "info.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.info, f, indent=2, ensure_ascii=False)
        print(f"{GREEN}[✓]{NC} حفظ: {path}")
        return path

    def display(self):
        print(f"\n{PURPLE}════ معلومات الحساب ════{NC}")
        if not self.info.get("exists"):
            print(f"{RED}[!] الحساب غير موجود{NC}")
            return
        rows = [
            ("username", "المستخدم"),
            ("full_name", "الاسم"),
            ("biography", "البايو"),
            ("followers_count", "متابعون"),
            ("following_count", "يتابع"),
            ("posts_count", "منشورات"),
            ("is_private", "خاص"),
            ("is_verified", "موثق"),
            ("instagram_id", "ID"),
            ("source", "المصدر"),
        ]
        for k, label in rows:
            v = self.info.get(k)
            if v is None or v == "" or v is False:
                continue
            if isinstance(v, bool):
                v = "نعم" if v else "لا"
            if isinstance(v, int):
                v = f"{v:,}"
            print(f"  {YELLOW}{label}:{NC} {WHITE}{v}{NC}")
        print()


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--username", "-u", required=True)
    args = p.parse_args()

    proxy = None
    try:
        from modules.proxy_manager import ProxyManager
        proxy = ProxyManager()
    except Exception:
        pass

    g = InfoGatherer(args.username, proxy_manager=proxy)
    data = g.gather()
    if data.get("exists"):
        g.save()
        g.display()
    else:
        print(f"{RED}فشل جمع المعلومات{NC}")
        sys.exit(1)

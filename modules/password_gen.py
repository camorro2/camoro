#!/usr/bin/env python3
"""Camoro - Smart Password Generator"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

C = "\033[0;36m"
G = "\033[0;32m"
Y = "\033[1;33m"
N = "\033[0m"

COMMON = [
    "password", "123456", "12345678", "123456789", "qwerty", "abc123",
    "password1", "iloveyou", "admin", "welcome", "monkey", "dragon",
    "master", "login", "princess", "football", "shadow", "sunshine",
    "trustno1", "batman", "superman", "hello", "freedom", "whatever",
    "qwerty123", "letmein", "starwars", "passw0rd", "instagram", "insta",
    "snapchat", "tiktok", "love", "baby", "angel", "happy", "ahmed",
    "mohamed", "ali", "omar", "sara", "nour", "hassan", "fatima",
]

EXTRA_WORDS = [
    "love", "life", "king", "queen", "star", "moon", "fire", "heart",
    "soul", "cool", "hot", "dark", "light", "gold", "black", "white",
    "red", "blue", "real", "best", "boss", "pro", "vip", "god", "baby",
]


class PasswordGenerator:
    def __init__(self, username: str, info: Dict | None = None) -> None:
        self.username = username.strip().lstrip("@").lower()
        self.info = info or {}
        self.passwords: Set[str] = set()

    def _keywords(self) -> List[str]:
        keys: Set[str] = {self.username}
        fields = [
            "full_name", "real_name", "city", "partner_name", "child_name",
            "pet_name", "hobby", "fav_color", "fav_team", "fav_artist",
            "fav_food", "fav_sport", "keyword", "keyword1", "keyword2", "keyword3",
        ]
        for f in fields:
            val = self.info.get(f)
            if not val:
                continue
            for part in re.split(r"[\s\-_\.]+", str(val)):
                part = part.strip().lower()
                if len(part) >= 2:
                    keys.add(part)
                    keys.add(part.capitalize())
        bio = self.info.get("biography") or ""
        for w in re.findall(r"\w{3,}", str(bio).lower()):
            if w not in {"the", "and", "for", "with", "this", "from", "that", "your"}:
                keys.add(w)
        return list(keys)

    def _suffixes(self) -> List[str]:
        year_now = datetime.now().year
        years = [str(y) for y in range(year_now - 6, year_now + 1)]
        nums = [
            "0", "1", "2", "3", "7", "9", "10", "11", "12", "13", "21", "22",
            "23", "24", "25", "69", "77", "99", "100", "111", "123", "420",
            "777", "000", "007", "1234", "12345", "123456", "1111", "0000",
            "!", "@", "#", "$", "123!", "123@", "!", "@#",
        ]
        extra: List[str] = []
        bd = self.info.get("birthdate") or self.info.get("birthday") or ""
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})", str(bd))
        if m:
            y, mo, d = m.group(1), m.group(2), m.group(3)
            extra += [
                y, y[2:], f"{d}{mo}{y}", f"{d}{mo}{y[2:]}",
                f"{mo}{d}{y}", f"{y}{mo}{d}", f"{d}{mo}", f"{mo}{d}",
            ]
        by = self.info.get("birth_year")
        if by:
            extra += [str(by), str(by)[-2:]]
        if self.info.get("fav_number"):
            extra.append(str(self.info["fav_number"]))
        phone = re.sub(r"\D", "", str(self.info.get("phone_number") or self.info.get("phone_last4") or ""))
        if len(phone) >= 4:
            extra.append(phone[-4:])
        return list(dict.fromkeys(extra + years + nums))

    def generate(self, target_count: int = 20000) -> List[str]:
        print(f"\n{C}[*]{N} توليد كلمات المرور...\n")
        kws = self._keywords()
        sfx = self._suffixes()
        print(f"  {Y}[1/8]{N} كلمات أساسية")
        for k in kws:
            self.passwords.add(k)
            self.passwords.add(k.lower())
            self.passwords.add(k.upper())
            self.passwords.add(k.capitalize())
            for s in sfx[:50]:
                self.passwords.add(f"{k}{s}")
                self.passwords.add(f"{s}{k}")
                self.passwords.add(f"{k}_{s}")
                self.passwords.add(f"{k}.{s}")

        print(f"  {Y}[2/8]{N} دمج الأسماء")
        top = kws[:15]
        for i, a in enumerate(top):
            for b in top[i + 1 :]:
                self.passwords.update(
                    {
                        f"{a}{b}", f"{b}{a}", f"{a}_{b}", f"{a}.{b}",
                        f"{a}-{b}", f"{a[0]}{b}", f"{a}{b[0]}",
                    }
                )

        print(f"  {Y}[3/8]{N} كلمات شائعة")
        self.passwords.update(COMMON)
        for p in COMMON:
            for s in ["1", "12", "123", "!", "2024", "2025", "2026"]:
                self.passwords.add(f"{p}{s}")

        print(f"  {Y}[4/8]{N} تركيبات عاطفية")
        for k in kws[:12]:
            for w in EXTRA_WORDS:
                self.passwords.update({f"{k}{w}", f"{w}{k}", f"{k}_{w}"})

        print(f"  {Y}[5/8]{N} أنماط Instagram")
        u = self.username
        for p in [
            f"insta{u}", f"{u}insta", f"ig_{u}", f"{u}_ig",
            f"gram{u}", f"{u}gram", f"instagram{u}", f"{u}official",
        ]:
            self.passwords.update({p, p + "1", p + "123", p + "!", p.capitalize()})

        print(f"  {Y}[6/8]{N} تكرار وعكس")
        sample = list(self.passwords)[:3000]
        for p in sample:
            if 3 <= len(p) <= 12:
                self.passwords.add(p + p)
                self.passwords.add(p[::-1])

        print(f"  {Y}[7/8]{N} Leet Speak")
        leet_map = str.maketrans({"a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7"})
        base = list(self.passwords)[:6000]
        for p in base:
            lp = p.translate(leet_map)
            if lp != p:
                self.passwords.add(lp)
                self.passwords.add(lp + "!")
            self.passwords.add(p + "!")
            self.passwords.add("!" + p)

        print(f"  {Y}[8/8]{N} تنقية وضبط العدد")
        valid = [
            p.strip()
            for p in self.passwords
            if isinstance(p, str) and 4 <= len(p.strip()) <= 64 and p.strip()
        ]
        valid = list(dict.fromkeys(valid))
        random.shuffle(valid)

        if len(valid) < target_count:
            more: List[str] = []
            for p in valid[:6000]:
                for s in sfx[:25]:
                    more.append(f"{p}{s}")
                    if len(valid) + len(more) >= target_count + 1000:
                        break
                if len(valid) + len(more) >= target_count + 1000:
                    break
            valid.extend(more)
            valid = list(dict.fromkeys(valid))

        random.shuffle(valid)
        valid = valid[:target_count]
        print(f"{G}[✓]{N} تم توليد {len(valid):,} كلمة مرور")
        return valid

    def save(self, passwords: List[str]) -> Path:
        user_dir = RESULTS_DIR / self.username
        user_dir.mkdir(parents=True, exist_ok=True)
        path = user_dir / "passwords.txt"
        path.write_text("\n".join(passwords) + "\n", encoding="utf-8")
        print(f"{G}[✓]{N} حفظ: {path}")
        return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Camoro Password Generator")
    parser.add_argument("-u", "--username", required=True)
    parser.add_argument("-c", "--count", type=int, default=20000)
    args = parser.parse_args()
    info_path = RESULTS_DIR / args.username / "info.json"
    info: Dict = {}
    if info_path.exists():
        info = json.loads(info_path.read_text(encoding="utf-8"))
    else:
        print(f"{Y}[!]{N} لا يوجد info.json — توليد من اسم المستخدم فقط")
        info = {"username": args.username}
    gen = PasswordGenerator(args.username, info)
    pw = gen.generate(args.count)
    gen.save(pw)
    print("\nعينة:")
    for x in pw[:15]:
        print(" •", x)


if __name__ == "__main__":
    main()

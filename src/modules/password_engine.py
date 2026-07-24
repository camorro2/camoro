#!/usr/bin/env python3
"""
Password Engine - Generates intelligent password combinations
"""

import random
import itertools

class PasswordEngine:
    def __init__(self, osint_data):
        self.data = osint_data
        self.passwords = set()
        
        # القواعد الأساسية
        self.symbols = ['!', '@', '#', '$', '%', '&', '*', '.', '_', '-', '~', '?']
        self.numbers = [str(i) for i in range(10)]
        self.years = [str(y) for y in range(1950, 2010)]
        
        # كلمات شائعة عالمية
        self.common_words = [
            'password', '123456', '12345678', 'qwerty', 'abc123', 'monkey',
            'dragon', 'master', 'shadow', 'sunshine', 'princess', 'football',
            'baseball', 'welcome', 'admin', 'letmein', 'passw0rd', 'iloveyou',
            'trustno1', 'hunter', 'ranger', 'orange', 'banana', 'killer',
            'george', 'thomas', 'andrew', 'jessica', 'ashley', 'amanda',
            'joshua', 'matthew', 'daniel', 'andrew', 'jennifer', 'michelle',
            'love', 'hello', 'world', 'secret', 'changeme', 'summer',
            'winter', 'spring', 'autumn', 'flower', 'nature', 'beauty',
        ]
        
        # كلمات عربية شائعة
        self.arabic_words = [
            'مرحبا', 'احبك', 'نور', 'قمر', 'ورد', 'قلب', 'حياة', 'امل',
            'ساره', 'مريم', 'احمد', 'محمد', 'علي', 'عمر', 'خالد', 'نور',
            'baba', 'mama', 'soso', 'lolo', 'dada', 'nana', 'fofo',
            'ahmed', 'mohamed', 'ali', 'omar', 'sara', 'nour', 'laila',
            '123456', '123456789', 'password', 'arabic', 'egypt',
        ]
    
    def generate(self, limit=100000):
        """توليد كلمات المرور"""
        username = self.data.get('username', '')
        full_name = self.data.get('full_name', '')
        bio = self.data.get('biography', '')
        keywords = self.data.get('keywords', [])
        personal = self.data.get('personal_info', {})
        
        first_name = personal.get('first_name', '').lower()
        last_name = personal.get('last_name', '').lower()
        birth_year = personal.get('birth_year', '')
        
        # 1️⃣ من اسم المستخدم
        if username:
            self._add_variations(username)
        
        # 2️⃣ من الاسم الكامل
        if full_name:
            parts = full_name.lower().split()
            for part in parts:
                if len(part) >= 3:
                    self._add_variations(part)
            if len(parts) >= 2:
                self._add_combinations(parts[0], parts[-1])
        
        # 3️⃣ من الاسم الأول والأخير
        if first_name:
            self._add_variations(first_name)
        if last_name:
            self._add_variations(last_name)
        if first_name and last_name:
            self._add_combinations(first_name, last_name)
        
        # 4️⃣ من الكلمات المفتاحية
        for kw in (keywords or []):
            if len(kw) >= 3:
                self._add_variations(kw)
        
        # 5️⃣ تواريخ الميلاد
        if birth_year:
            for month in ['01','02','03','04','05','06','07','08','09','10','11','12']:
                for day in ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']:
                    self.passwords.add(f"{day}{month}{birth_year}")
                    self.passwords.add(f"{birth_year}{month}{day}")
        
        # 6️⃣ كلمات شائعة + أرقام
        for word in self.common_words:
            self._add_variations(word)
        
        for word in self.arabic_words:
            self._add_variations(word)
        
        # 7️⃣ أنماط لوحة المفاتيح
        keyboard_patterns = [
            'qwerty', 'qwerty123', 'qwerty123!', 'qwertyuiop', 'asdfgh',
            'asdfgh123', 'zxcvbn', 'zxcvbnm', '1q2w3e4r', '1q2w3e4r5t',
            'qazwsx', 'qazwsx123', '123qwe', '123qwe!', 'qwe123',
            'passw0rd', 'P@ssw0rd', 'p@ssword', 'Passw0rd!',
        ]
        for pattern in keyboard_patterns:
            self.passwords.add(pattern)
        
        # 8️⃣ توليد عشوائي ذكي
        for _ in range(5000):
            if first_name:
                base = first_name
            elif username:
                base = username[:5]
            else:
                base = random.choice(self.common_words)
            
            num = ''.join(random.choices('0123456789', k=random.randint(2,4)))
            sym = random.choice(self.symbols)
            
            pattern = random.choice([
                f"{base}{num}",
                f"{base}{num}{sym}",
                f"{base.capitalize()}{num}",
                f"{base}{sym}{num}",
            ])
            self.passwords.add(pattern)
        
        # تقليم وإرجاع القائمة
        password_list = list(self.passwords)
        random.shuffle(password_list)
        
        return password_list[:limit]
    
    def _add_variations(self, word):
        """إضافة كل تنويعات كلمة"""
        word = word.lower().strip()
        if len(word) < 3:
            return
        
        # الكلمة كما هي
        self.passwords.add(word)
        self.passwords.add(word.capitalize())
        self.passwords.add(word.upper())
        
        # + أرقام
        for i in range(10):
            self.passwords.add(f"{word}{i}")
        for year in ['2020','2021','2022','2023','2024','2025','2026']:
            self.passwords.add(f"{word}{year}")
            self.passwords.add(f"{word}{year}!")
        
        # + رموز
        for sym in self.symbols[:5]:
            self.passwords.add(f"{word}{sym}")
            self.passwords.add(f"{word}123{sym}")
        
        # Leet speak
        leet = word.replace('a','4').replace('e','3').replace('i','1').replace('o','0').replace('s','5')
        self.passwords.add(leet)
        self.passwords.add(f"{leet}123")
        self.passwords.add(f"{leet}!")
        
        # عكس الكلمة
        self.passwords.add(word[::-1])
        self.passwords.add(f"{word[::-1]}123")
    
    def _add_combinations(self, word1, word2):
        """دمج كلمتين"""
        word1 = word1.lower()
        word2 = word2.lower()
        
        # دمج بسيط
        self.passwords.add(f"{word1}{word2}")
        self.passwords.add(f"{word1}.{word2}")
        self.passwords.add(f"{word1}_{word2}")
        self.passwords.add(f"{word1}{word2}123")
        self.passwords.add(f"{word1}{word2}!")
        
        # دمج مع رموز
        for sym in self.symbols[:3]:
            self.passwords.add(f"{word1}{sym}{word2}")
            self.passwords.add(f"{word1}{sym}{word2}123")

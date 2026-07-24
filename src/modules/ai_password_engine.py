#!/usr/bin/env python3
"""
AI Password Engine - Uses LLM (Groq/OpenAI) to generate intelligent passwords
based on OSINT data. This is the secret weapon.
"""

import json
import time
import random

class AIPasswordEngine:
    """
    يولد كلمات مرور بذكاء اصطناعي حقيقي.
    يحلل معلومات الهدف ويستخدم LLM لتوليد كلمات مرور دقيقة.
    """
    
    def __init__(self, osint_data, config=None):
        self.data = osint_data
        self.config = config or {}
        self.api_key = self.config.get('api_key', '')
        self.provider = self.config.get('ai_provider', 'groq')
        self.model = self.config.get('ai_model', 'llama3-70b-8192')
        self.client = None
        
    def _init_client(self):
        """تهيئة اتصال LLM"""
        if not self.api_key:
            return False
        
        try:
            if self.provider == 'groq':
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
            elif self.provider == 'openai':
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            return True
        except Exception as e:
            print(f"⚠️ فشل اتصال AI: {e}")
            return False
    
    def generate_ai_passwords(self, count=20000):
        """
        🧠 يولد كلمات مرور ذكية باستخدام LLM بناءً على:
        - الاسم الكامل
        - البايو والسيرة
        - الإيميلات المستخرجة
        - الاهتمامات
        - أنماط الكلمات الشائعة
        """
        
        if not self._init_client():
            print("⚠️ مفتاح API غير موجود. استخدام المحرك العادي بدلاً من AI.")
            return []
        
        print("🧠 تشغيل الذكاء الاصطناعي لتوليد كلمات مرور مخصصة...")
        
        # بناء prompt ذكي
        full_name = self.data.get('full_name', 'غير معروف')
        username = self.data.get('username', 'غير معروف')
        bio = self.data.get('biography', 'فارغة')
        emails = ', '.join(self.data.get('emails', [])) or 'لا يوجد'
        keywords = ', '.join(self.data.get('keywords', [])[:10]) or 'لا يوجد'
        personal = self.data.get('personal_info', {})
        first_name = personal.get('first_name', 'غير معروف')
        birth_year = personal.get('birth_year', 'غير معروف')
        
        prompt = f"""You are an AI password cracking expert analyzing a target for AUTHORIZED penetration testing.

TARGET PROFILE:
- Username: {username}
- Full Name: {full_name}
- First Name: {first_name}
- Biography/Bio: {bio[:200]}
- Emails found: {emails}
- Keywords from profile: {keywords}
- Possible birth year: {birth_year}

TASK: Generate {count} realistic password candidates in order of likelihood.
Use your knowledge of human psychology, common password patterns, and the specific details above.

RULES:
- Return ONLY a JSON array of strings. No other text.
- No explanations. No markdown. Just ["pass1","pass2",...]
- Include common patterns: name+year, name+symbol, keyboard patterns, leet speak
- Include Arabic/English combinations if name is Arabic
- Include variations with !, @, #, 123, 2023, 2024, 2025
- Include common weak passwords people actually use
- Include reversed names, capitalized variations
- Include combinations of first+last name with years and symbols
- IMPORTANT: Generate exactly {count} passwords, no duplicates
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a password cracking AI for authorized security testing. Generate password lists based on OSINT data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=8000,
            )
            
            result = response.choices[0].message.content.strip()
            
            # تنظيف النتيجة
            if result.startswith('```json'):
                result = result[7:]
            if result.startswith('```'):
                result = result[3:]
            if result.endswith('```'):
                result = result[:-3]
            
            passwords = json.loads(result)
            
            if isinstance(passwords, list) and len(passwords) > 0:
                print(f"✅ AI-generated {len(passwords)} unique passwords")
                return passwords
            
        except Exception as e:
            print(f"⚠️ خطأ في AI generation: {e}")
        
        return []
    
    def enhance_with_ai(self, existing_passwords, count=10000):
        """تحسين قائمة كلمات المرور الحالية باستخدام AI"""
        
        if not self._init_client():
            return existing_passwords
        
        print("🧠 AI يحلل ويحسّن كلمات المرور...")
        
        sample = existing_passwords[:50]  # عينة للتحليل
        
        prompt = f"""Analyze these sample passwords from an authorized pentest and generate {count} BETTER, more likely passwords:

Sample passwords: {json.dumps(sample)}

TARGET:
- Name: {self.data.get('full_name', 'unknown')}
- Username: {self.data.get('username', 'unknown')}
- Bio: {self.data.get('biography', '')[:100]}

Generate {count} passwords that are MORE INTELLIGENT and more likely to work.
Return ONLY a JSON array. No other text.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
                max_tokens=8000,
            )
            
            result = response.choices[0].message.content.strip()
            if result.startswith('```json'):
                result = result[7:]
            if result.startswith('```'):
                result = result[3:]
            if result.endswith('```'):
                result = result[:-3]
            
            ai_passwords = json.loads(result)
            
            if isinstance(ai_passwords, list):
                # دمج مع القائمة الأصلية
                combined = list(set(existing_passwords + ai_passwords))
                print(f"✅ AI أضاف {len(ai_passwords)} كلمة ذكية جديدة")
                return combined
            
        except Exception as e:
            print(f"⚠️ AI enhancement error: {e}")
        
        return existing_passwords

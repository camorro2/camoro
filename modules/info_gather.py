#!/usr/bin/env python3

"""
Camoro v4 - Information Gathering Engine
يجيب معلومات الحساب + عدد المتابعين
للحسابات العامة والخاصة
"""

import json
import os
import sys
import time
import re
import random
from datetime import datetime

try:
    import httpx
except ImportError:
    print("\033[91m[!] httpx غير مثبت. شغّل: pip install httpx[http2]\033[0m")
    sys.exit(1)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')

GREEN = '\033[0;32m'
RED = '\033[0;31m'
CYAN = '\033[0;36m'
YELLOW = '\033[1;33m'
WHITE = '\033[1;37m'
PURPLE = '\033[0;35m'
NC = '\033[0m'

# الأسرار المهمة
INSTAGRAM_WEB_APP_ID = "936619743392459"
INSTAGRAM_MOBILE_APP_ID = "124024574287414"

USER_AGENTS = [
    'Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.164 Mobile Safari/537.36',
    'Instagram 300.0.0.18.85 Android (34/14; 480dpi; 1080x2400; Samsung; SM-S928B; dm1q; qcom; en_US)',
    'Instagram 301.0.0.20.90 Android (34/14; 420dpi; 1080x2340; Google; Pixel 9; husky; qcom; en_US)',
]


class InfoGatherer:
    """يجيب كل شيء عن الحساب"""
    
    def __init__(self, username, proxy_manager=None):
        self.username = username.strip().lower()
        self.proxy_manager = proxy_manager
        self.client = None
        
    def _get_client(self):
        """الحصول على httpx client (مع بروكسي أو بدون)"""
        if self.proxy_manager:
            return self.proxy_manager.get_httpx_client()
        return httpx.Client(http2=True, verify=False, timeout=30.0)
    
    def _get_headers(self, mobile=False):
        """الهيدرز الصحيحة"""
        app_id = INSTAGRAM_MOBILE_APP_ID if mobile else INSTAGRAM_WEB_APP_ID
        ua = random.choice(USER_AGENTS)
        
        return {
            "User-Agent": ua,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "X-IG-App-ID": app_id,
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://www.instagram.com",
            "Referer": f"https://www.instagram.com/{self.username}/",
            "Connection": "keep-alive",
        }
    
    def gather(self):
        """جمع كل المعلومات الممكنة"""
        
        info = {
            'username': self.username,
            'exists': False,
            'is_private': None,
            'followers_count': None,
            'following_count': None,
            'posts_count': None,
            'full_name': '',
            'biography': '',
            'is_verified': False,
            'is_business': False,
            'profile_pic': '',
            'external_url': '',
            'business_category': '',
            'extracted_at': datetime.now().isoformat(),
            'source': '',
        }
        
        print(f"\n{CYAN}[*] {WHITE}جاري فحص {YELLOW}{self.username}{NC}...")
        
        # =================== الطريقة الأولى: web_profile_info (API) ===================
        print(f"{CYAN}[*] {WHITE}الطريقة 1: API web_profile_info...{NC}")
        
        try:
            self.client = self._get_client()
            
            url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={self.username}"
            headers = self._get_headers()
            
            response = self.client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and 'user' in data['data']:
                    user = data['data']['user']
                    
                    info['exists'] = True
                    info['full_name'] = user.get('full_name', '') or ''
                    info['biography'] = user.get('biography', '') or ''
                    info['followers_count'] = user.get('edge_followed_by', {}).get('count', 0)
                    info['following_count'] = user.get('edge_follow', {}).get('count', 0)
                    info['posts_count'] = user.get('edge_owner_to_timeline_media', {}).get('count', 0)
                    info['is_private'] = user.get('is_private', False)
                    info['is_verified'] = user.get('is_verified', False)
                    info['is_business'] = user.get('is_business_account', False)
                    info['profile_pic'] = user.get('profile_pic_url_hd', '') or ''
                    info['external_url'] = user.get('external_url', '') or ''
                    info['business_category'] = user.get('business_category_name', '') or ''
                    info['source'] = 'web_profile_info_api'
                    
                    # جلب bio links
                    bio_links = user.get('bio_links', [])
                    if bio_links:
                        info['biography_links'] = [
                            link.get('url', '') for link in bio_links if link.get('url')
                        ]
                    
                    # جلب profile_pic_id
                    info['profile_pic_id'] = user.get('profile_pic_id', '')
                    
                    # هل الحساب جديد؟
                    info['is_joined_recently'] = user.get('is_joined_recently', False)
                    
                    # معلومات إضافية
                    info['has_biography_links'] = len(bio_links) > 0
                    info['instagram_id'] = user.get('id', '')
                    
                    print(f"{GREEN}[✓] API نجح! المتابعون: {WHITE}{info['followers_count']:,}{NC}")
                    return info
            
            elif response.status_code == 404:
                print(f"{RED}[!] الحساب غير موجود (404){NC}")
                info['exists'] = False
                return info
            
            elif response.status_code == 403:
                print(f"{YELLOW}[!] ممنوع (403). أجرب طريقة أخرى...{NC}")
            
            else:
                print(f"{YELLOW}[!] استجابة: HTTP {response.status_code}{NC}")
        
        except httpx.TimeoutException:
            print(f"{YELLOW}[!] انتهت المهلة{NC}")
        except Exception as e:
            print(f"{YELLOW}[!] خطأ: {e}{NC}")
        
        # =================== الطريقة الثانية: Mobile API ===================
        print(f"\n{CYAN}[*] {WHITE}الطريقة 2: Mobile API...{NC}")
        time.sleep(1)
        
        try:
            self.client = self._get_client()
            
            headers = self._get_headers(mobile=True)
            response = self.client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and 'user' in data['data']:
                    user = data['data']['user']
                    
                    info['exists'] = True
                    info['full_name'] = user.get('full_name', '') or info['full_name']
                    info['biography'] = user.get('biography', '') or info['biography']
                    info['followers_count'] = user.get('edge_followed_by', {}).get('count', info['followers_count'])
                    info['following_count'] = user.get('edge_follow', {}).get('count', info['following_count'])
                    info['posts_count'] = user.get('edge_owner_to_timeline_media', {}).get('count', info['posts_count'])
                    info['is_private'] = user.get('is_private', info['is_private'])
                    info['is_verified'] = user.get('is_verified', info['is_verified'])
                    info['profile_pic'] = user.get('profile_pic_url_hd', '') or info['profile_pic']
                    info['source'] = 'mobile_api'
                    
                    print(f"{GREEN}[✓] Mobile API نجح!{NC}")
                    return info
        
        except Exception as e:
            print(f"{YELLOW}[!] Mobile API فشل: {e}{NC}")
        
        # =================== الطريقة الثالثة: Instagram GraphQL ===================
        print(f"\n{CYAN}[*] {WHITE}الطريقة 3: GraphQL...{NC}")
        time.sleep(1)
        
        try:
            self.client = self._get_client()
            
            # GraphQL query hash للبروفايل
            query_hash = "56a7068fea504063273cc2120ffd54f3"
            variables = json.dumps({"username": self.username, "first": 1})
            
            url = f"https://www.instagram.com/graphql/query/?query_hash={query_hash}&variables={variables}"
            headers = self._get_headers()
            headers['Referer'] = f"https://www.instagram.com/{self.username}/"
            
            response = self.client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and 'user' in data['data']:
                    user = data['data']['user']
                    
                    info['exists'] = True
                    info['full_name'] = user.get('full_name', '') or info['full_name']
                    info['biography'] = user.get('biography', '') or info['biography']
                    info['followers_count'] = user.get('edge_followed_by', {}).get('count', info['followers_count'])
                    info['following_count'] = user.get('edge_follow', {}).get('count', info['following_count'])
                    info['posts_count'] = user.get('edge_owner_to_timeline_media', {}).get('count', info['posts_count'])
                    info['is_private'] = user.get('is_private', info['is_private'])
                    info['is_verified'] = user.get('is_verified', info['is_verified'])
                    info['source'] = 'graphql'
                    
                    print(f"{GREEN}[✓] GraphQL نجح!{NC}")
                    return info
        
        except Exception as e:
            print(f"{YELLOW}[!] GraphQL فشل: {e}{NC}")
        
        # =================== الطريقة الرابعة: HTML (آخر أمل) ===================
        print(f"\n{CYAN}[*] {WHITE}الطريقة 4: HTML extraction...{NC}")
        time.sleep(1)
        
        try:
            self.client = self._get_client()
            
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
            }
            
            response = self.client.get(
                f"https://www.instagram.com/{self.username}/",
                headers=headers,
                follow_redirects=True
            )
            
            if response.status_code == 200:
                html = response.text
                
                # meta description (فيها عدد المتابعين)
                desc_match = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]+)"', html)
                if desc_match:
                    desc = desc_match.group(1)
                    info['meta_description'] = desc
                    
                    # استخرج الأرقام من الوصف
                    nums = re.findall(r'([\d,]+)\s*(Follower|Following|Post)', desc, re.IGNORECASE)
                    for num, label in nums:
                        clean_num = int(num.replace(',', ''))
                        if 'Follower' in label:
                            info['followers_count'] = clean_num
                        elif 'Following' in label:
                            info['following_count'] = clean_num
                        elif 'Post' in label:
                            info['posts_count'] = clean_num
                
                # og:title للاسم الكامل
                title_match = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"', html)
                if title_match:
                    title = title_match.group(1)
                    name = re.sub(r'\s*\(@[^)]+\)', '', title).strip()
                    info['full_name'] = name
                
                # og:image لصورة البروفايل
                img_match = re.search(r'<meta[^>]*property="og:image"[^>]*content="([^"]+)"', html)
                if img_match:
                    info['profile_pic'] = img_match.group(1)
                
                # هل الحساب موجود؟
                if 'Page Not Found' not in html and 'page not found' not in html.lower():
                    info['exists'] = True
                    info['source'] = 'html_fallback'
                    
                    # هل الحساب خاص؟
                    if 'This Account is Private' in html or 'is private' in html.lower():
                        info['is_private'] = True
                        print(f"{YELLOW}[!] الحساب خاص{NC}")
                    else:
                        info['is_private'] = False
                    
                    print(f"{GREEN}[✓] HTML نجح جزئياً!{NC}")
                    return info
                else:
                    print(f"{RED}[!] الحساب غير موجود{NC}")
                    info['exists'] = False
                    return info
            
            elif response.status_code == 404:
                print(f"{RED}[!] الحساب غير موجود (404){NC}")
                info['exists'] = False
                return info
        
        except Exception as e:
            print(f"{YELLOW}[!] HTML فشل: {e}{NC}")
        
        # =================== إذا كل شيء فشل ===================
        if info['exists'] is None:
            print(f"\n{RED}[!] كل الطرق فشلت في جلب المعلومات{NC}")
        
        return info
    
    def save_info(self, info):
        """حفظ المعلومات إلى ملف"""
        user_dir = os.path.join(RESULTS_DIR, self.username)
        os.makedirs(user_dir, exist_ok=True)
        
        filepath = os.path.join(user_dir, 'info.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        
        print(f"{GREEN}[✓] تم الحفظ: {filepath}{NC}")
        return filepath
    
    def display_info(self, info):
        """عرض المعلومات بشكل جميل"""
        print(f"\n{PURPLE}╔{'═'*55}╗{NC}")
        print(f"{PURPLE}║{' ' * 18}📊 معلومات الحساب{' ' * 18}║{NC}")
        print(f"{PURPLE}╚{'═'*55}╝{NC}")
        
        if not info.get('exists'):
            print(f"\n{RED}[!] الحساب غير موجود{NC}")
            return
        
        rows = [
            ('👤 اسم المستخدم', 'username', True),
            ('📝 الاسم', 'full_name', True),
            ('📖 السيرة', 'biography', True),
            ('📸 المنشورات', 'posts_count', True),
            ('👥 المتابعون', 'followers_count', True),
            ('👣 يتابع', 'following_count', True),
            ('🔒 خاص', 'is_private', True),
            ('✅ موثق', 'is_verified', True),
            ('💼 تجاري', 'is_business', True),
            ('🏷️ التصنيف', 'business_category', True),
            ('🔗 رابط', 'external_url', True),
            ('🆔 ID', 'instagram_id', True),
            ('📡 المصدر', 'source', True),
        ]
        
        for icon, key, show in rows:
            value = info.get(key)
            if value is not None and value != '' and value != 0:
                if isinstance(value, bool):
                    value = '✅ نعم' if value else '❌ لا'
                elif isinstance(value, int) and value > 1000:
                    value = f"{value:,}"
                print(f"  {YELLOW}{icon}:{NC} {WHITE}{value}{NC}")
        
        # روابط البايو
        bio_links = info.get('biography_links', [])
        if bio_links:
            print(f"\n  {YELLOW}🔗 روابط البايو:{NC}")
            for link in bio_links:
                print(f"    {CYAN}→{NC} {link}")
        
        # صورة البروفايل
        if info.get('profile_pic'):
            print(f"\n  {YELLOW}🖼️ صورة البروفايل:{NC}")
            print(f"    {CYAN}→{NC} {info['profile_pic'][:60]}...")
        
        print()


def ask_extra_info(username):
    """سؤال المستخدم عن معلومات إضافية"""
    print(f"\n{YELLOW}╔{'═'*55}╗{NC}")
    print(f"{YELLOW}║{' ' * 10}📝 معلومات إضافية (اختياري - تقوي التخمين){' ' * 8}║{NC}")
    print(f"{YELLOW}╚{'═'*55}╝{NC}")
    print(f"\n{CYAN}[?] {WHITE}هل تريد إضافة معلومات لزيادة قوة التخمين؟ (Y/N): {NC}")
    
    choice = input().strip().lower()
    if choice != 'y':
        return {}
    
    extra = {}
    questions = [
        ('real_name', '👤 الاسم الحقيقي'),
        ('birthday', '🎂 تاريخ الميلاد (YYYY-MM-DD)'),
        ('partner_name', '💑 اسم الشريك/الحبيب'),
        ('child_name', '👶 اسم الطفل'),
        ('pet', '🐾 اسم الحيوان الأليف'),
        ('hobby', '🎯 الهواية المفضلة'),
        ('city', '🏙️ المدينة'),
        ('fav_number', '🔢 الرقم المفضل'),
        ('fav_color', '🎨 اللون المفضل'),
        ('fav_sport', '⚽ الرياضة المفضلة'),
        ('fav_food', '🍕 الأكل المفضل'),
        ('keyword', '🔑 أي كلمة مفتاحية'),
    ]
    
    for key, label in questions:
        val = input(f"  {YELLOW}{label}: {NC}").strip()
        if val:
            extra[key] = val
    
    return extra


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Camoro - Info Gatherer v4')
    parser.add_argument('--username', '-u', required=True, help='Instagram username')
    args = parser.parse_args()
    
    print(f"\n{CYAN}╔{'═'*55}╗{NC}")
    print(f"{CYAN}║{' ' * 12}🔍 CAMORO v4 - INFO GATHERER{' ' * 14}║{NC}")
    print(f"{CYAN}║{' ' * 12}⚡ يعمل في 2026 ✅{' ' * 20}║{NC}")
    print(f"{CYAN}╚{'═'*55}╝{NC}\n")
    
    # Import proxy manager
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    try:
        from modules.proxy_manager import ProxyManager
        proxy_mgr = ProxyManager()
    except ImportError:
        proxy_mgr = None
    
    gatherer = InfoGatherer(args.username, proxy_manager=proxy_mgr)
    info = gatherer.gather()
    
    if info and info.get('exists'):
        gatherer.save_info(info)
        gatherer.display_info(info)
        
        # اسأل عن معلومات إضافية
        extra = ask_extra_info(args.username)
        if extra:
            info.update(extra)
            gatherer.save_info(info)
            print(f"{GREEN}[✓] تم حفظ المعلومات الإضافية{NC}")
        
        sys.exit(0)
    else:
        print(f"\n{RED}╔{'═'*55}╗{NC}")
        print(f"{RED}║{' ' * 15}❌ فشل جلب المعلومات{' ' * 18}║{NC}")
        print(f"{RED}╚{'═'*55}╝{NC}")
        print(f"\n{YELLOW}[*] الأسباب المحتملة:{NC}")
        print(f"  {RED}→{NC} الحساب غير موجود")
        print(f"  {RED}→{NC} مشكلة في الإنترنت")
        print(f"  {RED}→{RED} Instagram يحظر مؤقتاً - انتظر 15 دقيقة")
        sys.exit(1)

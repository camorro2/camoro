#!/usr/bin/env python3
"""
محرك جمع المعلومات الاستخباراتية
يستخرج كل البيانات من حساب Instagram:
- الاسم، البايو، عدد المتابعين، المنشورات
- البريد الإلكتروني (إن وجد)
- روابط الموقع
- صورة البروفايل
- حالة الحساب (عام/خاص، موثق، تجاري)
"""

import json
import os
import re
import sys
import time
import random
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

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

# === ثوابت Instagram ===
INSTAGRAM_URLS = {
    'web_profile': 'https://www.instagram.com/{username}/?__a=1&__d=1',
    'web_profile_v2': 'https://www.instagram.com/{username}/?__a=1',
    'web_profile_embed': 'https://www.instagram.com/{username}/embed/',
    'graphql': 'https://www.instagram.com/api/v1/users/web_profile_info/?username={username}',
    'graphql_hash': 'https://www.instagram.com/graphql/query/?query_hash=...',
}

USER_AGENTS = [
    # Android Chrome
    'Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.165 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.122 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; OnePlus 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.179 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; CPH2581) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.165 Mobile Safari/537.36',
    # iOS Safari
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
    # Desktop
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    # Instagram App UA
    'Instagram 330.0.0.18.85 Android (34/14; 480dpi; 1080x2400; samsung; SM-S928B; dm1q; qcom; en_US; 627901348)',
    'Instagram 331.0.0.20.90 Android (34/14; 420dpi; 1080x2340; Google; Pixel 9 Pro; husky; google/tensor; en_US; 627901348)',
]

class InfoGatherer:
    """
    محرك جمع المعلومات الاستخباراتية
    يستخدم طرق متعددة لاستخراج بيانات الحساب
    """

    def __init__(self, username):
        self.username = username.strip().lower()
        self.info = {
            'username': self.username,
            'exists': None,
            'full_name': None,
            'biography': None,
            'biography_links': [],
            'profile_pic_url': None,
            'profile_pic_url_hd': None,
            'posts_count': 0,
            'followers_count': 0,
            'following_count': 0,
            'is_private': False,
            'is_verified': False,
            'is_business': False,
            'business_category': None,
            'external_url': None,
            'instagram_id': None,
            'highlight_reel_count': 0,
            'has_igtv': False,
            'has_guides': False,
            'pronouns': [],
            'category': None,
            'source': None,
            'collected_at': datetime.now().isoformat(),
            'extra': {}
        }

    def _get_client(self):
        """إنشاء httpx client بعناوين عشوائية"""
        ua = random.choice(USER_AGENTS)
        return httpx.Client(
            http2=True,
            timeout=30.0,
            follow_redirects=True,
            headers={
                'User-Agent': ua,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            },
            cookies={
                'sessionid': '',
                'csrftoken': '',
                'mid': self._generate_mid(),
                'ig_did': self._generate_did(),
            }
        )

    def _generate_mid(self):
        """توليد mid عشوائي"""
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
        return ''.join(random.choice(chars) for _ in range(28))

    def _generate_did(self):
        """توليد device id عشوائي"""
        return ''.join(random.choice('0123456789ABCDEF') for _ in range(32)).upper()

    def _extract_from_html(self, html):
        """استخراج البيانات من HTML"""
        # البحث عن JSON المضمن
        patterns = [
            r'window\.__INITIAL_STATE__\s*=\s*({.*?});</script>',
            r'<script type="application/ld\+json">(.*?)</script>',
            r'"user":({.*?})"logging_page_id"',
            r'"graphql":({.*?})"toast"',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    return self._parse_graphql_data(data)
                except:
                    continue

        # استخراج بواسطة regex مباشر
        info = {}

        # الاسم
        name_match = re.search(r'"full_name":"([^"]+)"', html)
        if name_match:
            info['full_name'] = name_match.group(1)

        # البايو
        bio_match = re.search(r'"biography":"([^"]*)"', html)
        if bio_match:
            info['biography'] = bio_match.group(1)

        # المتابعون
        followers_match = re.search(r'"edge_followed_by":\{"count":(\d+)\}', html)
        if followers_match:
            info['followers_count'] = int(followers_match.group(1))

        # يتابع
        following_match = re.search(r'"edge_follow":\{"count":(\d+)\}', html)
        if following_match:
            info['following_count'] = int(following_match.group(1))

        # المنشورات
        posts_match = re.search(r'"edge_owner_to_timeline_media":\{"count":(\d+)\}', html)
        if posts_match:
            info['posts_count'] = int(posts_match.group(1))

        # هل موثق
        info['is_verified'] = '"is_verified":true' in html

        # هل خاص
        info['is_private'] = '"is_private":true' in html

        # معرف المستخدم
        id_match = re.search(r'"id":"(\d+)"', html)
        if id_match:
            info['instagram_id'] = id_match.group(1)

        # صورة البروفايل
        pic_match = re.search(r'"profile_pic_url_hd":"([^"]+)"', html)
        if pic_match:
            info['profile_pic_url_hd'] = pic_match.group(1)
        else:
            pic_match = re.search(r'"profile_pic_url":"([^"]+)"', html)
            if pic_match:
                info['profile_pic_url'] = pic_match.group(1)

        return info

    def _parse_graphql_data(self, data):
        """تحليل بيانات GraphQL"""
        info = {}

        # البحث في هيكل البيانات المتداخل
        def find_key(obj, key):
            if isinstance(obj, dict):
                if key in obj:
                    return obj[key]
                for v in obj.values():
                    result = find_key(v, key)
                    if result is not None:
                        return result
            elif isinstance(obj, list):
                for item in obj:
                    result = find_key(item, key)
                    if result is not None:
                        return result
            return None

        info['full_name'] = find_key(data, 'full_name')
        info['biography'] = find_key(data, 'biography')
        info['followers_count'] = find_key(data, 'edge_followed_by')
        if isinstance(info['followers_count'], dict):
            info['followers_count'] = info['followers_count'].get('count', 0)

        info['following_count'] = find_key(data, 'edge_follow')
        if isinstance(info['following_count'], dict):
            info['following_count'] = info['following_count'].get('count', 0)

        info['posts_count'] = find_key(data, 'edge_owner_to_timeline_media')
        if isinstance(info['posts_count'], dict):
            info['posts_count'] = info['posts_count'].get('count', 0)

        info['is_private'] = find_key(data, 'is_private') or False
        info['is_verified'] = find_key(data, 'is_verified') or False
        info['is_business'] = find_key(data, 'is_business') or False
        info['instagram_id'] = find_key(data, 'id')

        pic = find_key(data, 'profile_pic_url_hd') or find_key(data, 'profile_pic_url')
        info['profile_pic_url'] = pic

        # روابط البايو
        bio_links_raw = find_key(data, 'bio_links')
        if bio_links_raw:
            info['biography_links'] = [l.get('url', '') for l in bio_links_raw if l.get('url')]

        # رابط خارجي
        info['external_url'] = find_key(data, 'external_url')

        # التصنيف التجاري
        info['business_category'] = find_key(data, 'business_category_name')
        info['category'] = find_key(data, 'category_name')

        return info

    def gather(self):
        """جمع المعلومات بكل الطرق الممكنة"""
        print(f"\n{CYAN}[*] {WHITE}جاري جمع المعلومات عن: {self.username}{NC}\n")

        methods = [
            ('GraphQL API', self._try_graphql_api),
            ('Web Profile ?__a=1', self._try_web_profile),
            ('Web Embed', self._try_embed),
            ('HTML Scraping', self._try_html_scrape),
        ]

        for method_name, method_func in methods:
            print(f"  {CYAN}[→]{NC} {method_name}...", end=' ')
            try:
                result = method_func()
                if result:
                    print(f"{GREEN}✅ نجح{NC}")
                    self.info.update(result)
                    self.info['source'] = method_name
                    self.info['exists'] = True
                    return self.info
                else:
                    print(f"{YELLOW}⚠️  لا بيانات{NC}")
            except Exception as e:
                print(f"{RED}❌ فشل: {str(e)[:40]}{NC}")

            time.sleep(random.uniform(0.5, 1.5))

        # كل الطرق فشلت
        self.info['exists'] = False
        return self.info

    def _try_graphql_api(self):
        """محاولة عبر GraphQL API"""
        client = self._get_client()
        url = f'https://www.instagram.com/api/v1/users/web_profile_info/?username={self.username}'
        client.headers.update({
            'X-IG-App-ID': '936619743392459',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json',
        })

        resp = client.get(url)
        if resp.status_code == 200:
            data = resp.json()
            user = data.get('data', {}).get('user', {})
            if user:
                return self._parse_graphql_data(user)
        return None

    def _try_web_profile(self):
        """محاولة عبر صفحة الويب مع __a=1"""
        client = self._get_client()
        url = f'https://www.instagram.com/{self.username}/?__a=1&__d=1'
        resp = client.get(url)
        if resp.status_code == 200:
            try:
                data = resp.json()
                user = data.get('graphql', {}).get('user', {})
                if user:
                    return {
                        'full_name': user.get('full_name'),
                        'biography': user.get('biography'),
                        'followers_count': user.get('edge_followed_by', {}).get('count', 0),
                        'following_count': user.get('edge_follow', {}).get('count', 0),
                        'posts_count': user.get('edge_owner_to_timeline_media', {}).get('count', 0),
                        'is_private': user.get('is_private', False),
                        'is_verified': user.get('is_verified', False),
                        'is_business': user.get('is_business_account', False),
                        'instagram_id': user.get('id'),
                        'profile_pic_url_hd': user.get('profile_pic_url_hd'),
                        'external_url': user.get('external_url'),
                        'business_category': user.get('business_category_name'),
                        'highlight_reel_count': user.get('highlight_reel_count', 0),
                    }
            except:
                pass
        return None

    def _try_embed(self):
        """محاولة عبر صفحة embed"""
        client = self._get_client()
        url = f'https://www.instagram.com/{self.username}/embed/'
        resp = client.get(url)
        if resp.status_code == 200:
            return self._extract_from_html(resp.text)
        return None

    def _try_html_scrape(self):
        """محاولة عبر كشط HTML مباشر"""
        client = self._get_client()
        url = f'https://www.instagram.com/{self.username}/'
        resp = client.get(url)
        if resp.status_code == 200:
            if 'Page Not Found' not in resp.text:
                return self._extract_from_html(resp.text)
        return None

    def save(self):
        """حفظ المعلومات"""
        user_dir = RESULTS_DIR / self.username
        user_dir.mkdir(parents=True, exist_ok=True)
        filepath = user_dir / 'info.json'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.info, f, indent=2, ensure_ascii=False)
        print(f"\n{GREEN}[✓] تم الحفظ: {filepath}{NC}")

    def display(self):
        """عرض المعلومات"""
        print(f"\n{PURPLE}╔{'═' * 55}╗{NC}")
        print(f"{PURPLE}║{' ' * 15}📊 معلومات الحساب{' ' * 17}║{NC}")
        print(f"{PURPLE}╚{'═' * 55}╝{NC}")

        if not self.info.get('exists'):
            print(f"\n{RED}[!] الحساب غير موجود أو لا يمكن الوصول إليه{NC}")
            return

        rows = [
            ('👤', 'username', 'اسم المستخدم', False),
            ('📝', 'full_name', 'الاسم الكامل', False),
            ('📖', 'biography', 'البايو', False),
            ('🆔', 'instagram_id', 'ID', False),
            ('📸', 'posts_count', 'المنشورات', True),
            ('👥', 'followers_count', 'المتابعون', True),
            ('👣', 'following_count', 'يتابع', True),
            ('🔒', 'is_private', 'خاص', False),
            ('✅', 'is_verified', 'موثق', False),
            ('💼', 'is_business', 'تجاري', False),
            ('🏷️', 'business_category', 'التصنيف', False),
            ('🔗', 'external_url', 'رابط خارجي', False),
            ('📡', 'source', 'المصدر', False),
        ]

        for icon, key, label, is_number in rows:
            val = self.info.get(key)
            if val is not None and val != '' and val != 0 and val != False:
                if isinstance(val, bool):
                    val = f'{GREEN}✅ نعم{NC}' if val else f'{RED}❌ لا{NC}'
                elif isinstance(val, int) and val > 999:
                    val = f'{val:,}'
                print(f"  {YELLOW}{icon} {label}:{NC} {WHITE}{val}{NC}")

        # روابط البايو
        links = self.info.get('biography_links', [])
        if links:
            print(f"\n  {YELLOW}🔗 روابط البايو:{NC}")
            for link in links:
                print(f"     {CYAN}→{NC} {link}")

        print()

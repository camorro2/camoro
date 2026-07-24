#!/usr/bin/env python3
import requests
import re
import json
import time

class OSINTScanner:
    def __init__(self, username):
        self.username = username
        self.data = {}
        self.session = requests.Session()
    
    def scan(self):
        info = self._get_basic_info()
        if not info:
            return None
        self.data.update(info)
        self.data['emails'] = self._extract_emails()
        self.data['phones'] = self._extract_phones()
        self.data['keywords'] = self._extract_keywords()
        self.data['personal'] = self._extract_personal()
        return self.data
    
    def _get_basic_info(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36',
            'Accept': 'application/json',
            'x-ig-app-id': '936619743392459',
        }
        try:
            url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={self.username}"
            r = self.session.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                u = r.json().get('data', {}).get('user', {})
                return {
                    'username': self.username,
                    'full_name': u.get('full_name', ''),
                    'biography': u.get('biography', ''),
                    'follower_count': u.get('edge_followed_by', {}).get('count', 0),
                    'following_count': u.get('edge_follow', {}).get('count', 0),
                    'post_count': u.get('edge_owner_to_timeline_media', {}).get('count', 0),
                    'is_private': u.get('is_private', False),
                    'is_verified': u.get('is_verified', False),
                    'external_url': u.get('external_url', ''),
                    'profile_pic': u.get('profile_pic_url', ''),
                }
        except:
            pass
        
        # محاولة بديلة
        try:
            url2 = f"https://www.instagram.com/{self.username}/"
            r2 = self.session.get(url2, headers=headers, timeout=15)
            if r2.status_code == 200:
                # استخراج الاسم من HTML
                match = re.search(r'<title>([^<]+)\(@', r2.text, re.IGNORECASE)
                name = match.group(1).strip() if match else ''
                return {
                    'username': self.username,
                    'full_name': name,
                    'biography': '',
                    'follower_count': 0,
                    'is_private': True,
                }
        except:
            pass
        
        return None
    
    def _extract_emails(self):
        bio = self.data.get('biography', '')
        return re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', bio)
    
    def _extract_phones(self):
        bio = self.data.get('biography', '')
        return [p.strip() for p in re.findall(r'[\+\d\s\-\(\)]{7,}', bio) if len(p.strip()) >= 7]
    
    def _extract_keywords(self):
        bio = self.data.get('biography', '')
        keywords = set()
        keywords.update(re.findall(r'#(\w+)', bio))
        keywords.update(re.findall(r'@(\w+)', bio))
        keywords.update(re.findall(r'\b[a-zA-Z]{4,}\b', bio))
        keywords.update(re.findall(r'\b[\u0600-\u06FF]{2,}\b', bio))
        return list(keywords)
    
    def _extract_personal(self):
        name = self.data.get('full_name', '')
        parts = name.split()
        info = {}
        if parts:
            info['first_name'] = parts[0]
        if len(parts) > 1:
            info['last_name'] = ' '.join(parts[1:])
        return info

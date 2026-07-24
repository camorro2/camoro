#!/usr/bin/env python3
"""
Report Generator - Saves results in multiple formats
"""

import json
import os
from datetime import datetime

class ReportGenerator:
    def __init__(self, username, output_dir="results"):
        self.username = username
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def save_json(self, data, filename=None):
        """حفظ بتنسيق JSON"""
        if not filename:
            filename = f"{self.output_dir}/{self.username}_report_{int(datetime.now().timestamp())}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def save_txt(self, data, filename=None):
        """حفظ بتنسيق نصي"""
        if not filename:
            filename = f"{self.output_dir}/{self.username}_report.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(f"CamarO Pro - Assessment Report\n")
            f.write(f"Target: {self.username}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            if isinstance(data, dict):
                for key, value in data.items():
                    f.write(f"{key}: {value}\n")
            elif isinstance(data, str):
                f.write(data + "\n")
        
        return filename
    
    def generate_report(self, osint_data, found_password, attempts, elapsed_time):
        """توليد تقرير كامل"""
        report = {
            'target': {
                'username': self.username,
                'full_name': osint_data.get('full_name', ''),
                'biography': osint_data.get('biography', ''),
                'follower_count': osint_data.get('follower_count', 0),
                'following_count': osint_data.get('following_count', 0),
                'is_private': osint_data.get('is_private', False),
                'is_verified': osint_data.get('is_verified', False),
            },
            'result': {
                'password_found': found_password is not None,
                'password': found_password or '',
                'attempts': attempts,
                'time_seconds': round(elapsed_time, 2),
            },
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'tool_version': '3.0.0',
            }
        }
        
        return report

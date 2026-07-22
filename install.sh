#!/bin/bash
# NovaX Installation Script for Termux
# اللون للأكواد
R='\033[91m'
G='\033[92m'
Y='\033[93m'
B='\033[94m'
C='\033[96m'
N='\033[0m'

echo -e "${B}╔══════════════════════════════════════╗"
echo -e "║   Installing NovaX Framework...     ║"
echo -e "╚══════════════════════════════════════╝${N}"

# تحديث الحزم
echo -e "${Y}[*] Updating packages...${N}"
pkg update -y && pkg upgrade -y

# تثبيت الحزم الأساسية
echo -e "${Y}[*] Installing dependencies...${N}"
pkg install -y python python-pip git openssh nmap
pkg install -y rust-bin  # لتسريع المكتبات
pkg install -y clang make cmake libffi libsodium

# تثبيت مكتبات بايثون
echo -e "${Y}[*] Installing Python libraries...${N}"
pip install --upgrade pip
pip install requests==2.31.0
pip install scapy==2.5.0
pip install colorama==0.4.6
pip install pycryptodome==3.20.0
pip install beautifulsoup4==4.12.2
pip install aiohttp==3.9.1

# صلاحيات التنفيذ
chmod +x main.py

echo -e "${G}"
echo "╔══════════════════════════════════════╗"
echo "║   Installation Complete!            ║"
echo "║                                     ║"
echo "║   Run: python main.py               ║"
echo "║   or:  sudo python main.py          ║"
echo "╚══════════════════════════════════════╝"
echo -e "${N}"

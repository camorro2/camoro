#!/bin/bash

# Camorro - Setup Script for Termux
# Author: Your Name
# Version: 1.0

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}"
echo "  ██████╗ █████╗ ███╗   ███╗ ██████╗ ██████╗  ██████╗ "
echo " ██╔════╝██╔══██╗████╗ ████║██╔═══██╗██╔══██╗██╔═══██╗"
echo " ██║     ███████║██╔████╔██║██║   ██║██████╔╝██║   ██║"
echo " ██║     ██╔══██║██║╚██╔╝██║██║   ██║██╔══██╗██║   ██║"
echo " ╚██████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██║  ██║╚██████╔╝"
echo "  ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ "
echo -e "${NC}"
echo -e "${YELLOW}[*] Installing Camorro - Termux Pentest Framework${NC}"
echo ""

# تحديث الحزم
echo -e "${YELLOW}[*] Updating packages...${NC}"
pkg update -y && pkg upgrade -y

# تثبيت المتطلبات الأساسية
echo -e "${YELLOW}[*] Installing core dependencies...${NC}"
pkg install -y python python3 git curl wget openssl \
    nmap fping hydra adb termux-tools termux-api

# تثبيت مكتبات بايثون
echo -e "${YELLOW}[*] Installing Python libraries...${NC}"
pip install colorama requests

# تثبيت Metasploit (اختياري)
echo -e "${YELLOW}[*] Do you want to install Metasploit? (y/n)${NC}"
read -r install_msf
if [[ "$install_msf" == "y" || "$install_msf" == "Y" ]]; then
    echo -e "${YELLOW}[*] Installing Metasploit (this may take a while)...${NC}"
    pkg install -y metasploit
fi

# إنشاء المجلدات
echo -e "${YELLOW}[*] Creating Camorro directories...${NC}"
mkdir -p ~/camorro/{payloads,scans,exploits,sessions}

# منح الصلاحيات للنصوص
chmod +x camorro.py

echo -e "${GREEN}[+] Camorro installed successfully!${NC}"
echo -e "${GREEN}[+] Run: python camorro.py${NC}"

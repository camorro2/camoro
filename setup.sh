#!/bin/bash

# CamarO Pro - Setup Script
# Termux / Linux Auto Installer

Green='\033[0;32m'
Red='\033[0;31m'
Cyan='\033[0;36m'
Yellow='\033[1;33m'
NC='\033[0m'

echo -e "${Cyan}"
echo "  ╔═══════════════════════════════════════╗"
echo "  ║        CamarO Pro - Setup             ║"
echo "  ╚═══════════════════════════════════════╝"
echo -e "${NC}"

# اكتشاف النظام
if [ -f /data/data/com.termux/files/usr/bin/pkg ]; then
    echo -e "${Yellow}[*] تم اكتشاف Termux${NC}"
    PKG_MANAGER="pkg"
    INSTALL_CMD="pkg install -y"
    PYTHON="python"
elif [ -f /usr/bin/apt ]; then
    echo -e "${Yellow}[*] تم اكتشاف Linux (APT)${NC}"
    PKG_MANAGER="apt"
    INSTALL_CMD="sudo apt install -y"
    PYTHON="python3"
else
    echo -e "${Red}[!] نظام غير معروف${NC}"
    exit 1
fi

# تحديث الحزم
echo -e "${Yellow}[*] جاري تحديث الحزم...${NC}"
$INSTALL_CMD python python-pip git curl wget > /dev/null 2>&1

# تثبيت المكتبات
echo -e "${Yellow}[*] جاري تثبيت المكتبات...${NC}"
$PYTHON -m pip install --upgrade pip
$PYTHON -m pip install -r requirements.txt

# إنشاء المجلدات
mkdir -p results proxies wordlists

# تحميل قائمة بروكسيات
echo -e "${Yellow}[*] جاري تحميل بروكسيات...${NC}"
curl -s -o proxies/http.txt "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt" 2>/dev/null
curl -s -o proxies/socks4.txt "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt" 2>/dev/null
curl -s -o proxies/socks5.txt "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt" 2>/dev/null

# تحميل RockYou (اختياري)
echo -e "${Yellow}[*] هل تريد تحميل RockYou wordlist? (y/n)${NC}"
read -r choice
if [ "$choice" = "y" ]; then
    echo -e "${Yellow}[*] جاري تحميل RockYou (قد يستغرق وقتاً)...${NC}"
    wget -q -O wordlists/rockyou.txt.gz "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt" 2>/dev/null
    gunzip -f wordlists/rockyou.txt.gz 2>/dev/null || true
fi

# إعداد الإذن
chmod +x src/main.py

echo -e "\n${Green}✅ تم التثبيت بنجاح!${NC}"
echo -e "${Cyan}لتشغيل الأداة:${NC}"
echo -e "  ${Yellow}cd CamarO-Pro && python src/main.py${NC}"

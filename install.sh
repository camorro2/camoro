#!/bin/bash
# Camoro v5.0 - Installer
# AI-Powered Security Assessment Framework

GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m'

clear
echo -e "${PURPLE}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║                                                      ║"
echo "║     ██████╗ █████╗ ███╗   ███╗ ██████╗ ██████╗  ██████╗ "
echo "║    ██╔════╝██╔══██╗████╗ ████║██╔═══██╗██╔══██╗██╔═══██╗"
echo "║    ██║     ███████║██╔████╔██║██║   ██║██████╔╝██║   ██║"
echo "║    ██║     ██╔══██║██║╚██╔╝██║██║   ██║██╔══██╗██║   ██║"
echo "║    ╚██████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██║  ██║╚██████╔╝"
echo "║     ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝"
echo "║                                                      ║"
echo "║         🔮 v5.0 - AI-Powered Installer               ║"
echo "║                                                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}[*] جاري تثبيت Camoro v5.0...${NC}"
sleep 1

# 1. تحديث الحزم
echo -e "${CYAN}[1/4] تحديث الحزم...${NC}"
pkg update -y && pkg upgrade -y 2>/dev/null || apt update -y && apt upgrade -y 2>/dev/null

# 2. تثبيت الأدوات
echo -e "${CYAN}[2/4] تثبيت الأدوات الأساسية...${NC}"
if command -v pkg &> /dev/null; then
    pkg install -y python python-pip git curl tor privoxy openssl 2>/dev/null
else
    sudo apt install -y python3 python3-pip git curl tor privoxy 2>/dev/null
fi

# 3. تثبيت مكتبات Python
echo -e "${CYAN}[3/4] تثبيت مكتبات Python...${NC}"
pip install --upgrade pip 2>/dev/null
pip install httpx[http2] colorama requests urllib3 certifi 2>/dev/null

# 4. صلاحيات
echo -e "${CYAN}[4/4] ضبط الصلاحيات...${NC}"
chmod +x camoro.sh camoro.py 2>/dev/null

echo -e "\n${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     ✅ CAMORO v5.0 INSTALLED!           ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${YELLOW}📌 للتشغيل:${NC}"
echo -e "  ${CYAN}  python camoro.py${NC}"
echo -e "  ${CYAN}  أو: ./camoro.sh${NC}"
echo ""

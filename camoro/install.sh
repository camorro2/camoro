#!/bin/bash
# ===========================================================================
# CamoroMobile v1.0 — Automated Installation Script
# للتركيب على Termux و Kali Linux و Ubuntu
# ===========================================================================

set -e

# الألوان
R='\033[0;91m'
G='\033[0;92m'
Y='\033[0;93m'
B='\033[0;94m'
M='\033[0;95m'
C='\033[0;96m'
W='\033[0;97m'
BOLD='\033[1m'
DIM='\033[2m'
RST='\033[0m'

# تحقق من النظام
if command -v termux-setup-storage &> /dev/null; then
    OS="termux"
elif [[ "$(uname)" == "Linux" ]]; then
    OS="linux"
else
    OS="other"
fi

# البانر
echo -e "${R}${BOLD}"
cat << "BANNER"
    ╔═══════════════════════════════════════════════════════════╗
    ║    ██████  █████  ███    ███  ██████  ███    ███  █████  ║
    ║   ██      ██   ██ ████  ████ ██    ██ ████  ████ ██   ██ ║
    ║   ██      ███████ ██ ████ ██ ██    ██ ██ ████ ██ ███████ ║
    ║   ██      ██   ██ ██  ██  ██ ██    ██ ██  ██  ██ ██   ██ ║
    ║    ██████ ██   ██ ██      ██  ██████  ██      ██ ██   ██ ║
    ║                                                           ║
    ║         MOBILE PENETRATION TESTING FRAMEWORK              ║
    ║                    Automated Installation                 ║
    ╚═══════════════════════════════════════════════════════════╝
BANNER
echo -e "${RST}"

echo -e "${C}════════════════════════════════════════════════════════${RST}"
echo -e "${C}  CamoroMobile v1.0 — Installation${RST}"
echo -e "${C}  النظام المكتشف: $OS${RST}"
echo -e "${C}════════════════════════════════════════════════════════${RST}"
echo ""

# تحديث الحزم
echo -e "${B}[*] جاري تحديث الحزم...${RST}"
if [[ "$OS" == "termux" ]]; then
    pkg update -y -qq 2>/dev/null
    pkg upgrade -y -qq 2>/dev/null
elif [[ "$OS" == "linux" ]]; then
    if command -v apt &> /dev/null; then
        sudo apt update -qq 2>/dev/null
    fi
fi
echo -e "${G}[✓] تم تحديث الحزم${RST}"

# تثبيت Python والأدوات الأساسية
echo -e "\n${B}[*] جاري تثبيت Python والأدوات...${RST}"

if [[ "$OS" == "termux" ]]; then
    pkg install -y -qq python python-pip git curl wget openssl-tool openjdk-17 2>/dev/null || true
elif [[ "$OS" == "linux" ]]; then
    if command -v apt &> /dev/null; then
        sudo apt install -y -qq python3 python3-pip python3-venv git curl wget default-jdk 2>/dev/null || true
    fi
fi
echo -e "${G}[✓] تم تثبيت Python والأدوات${RST}"

# تثبيت أدوات Android (apktool, aapt, etc.)
echo -e "\n${B}[*] جاري تثبيت أدوات Android...${RST}"

if [[ "$OS" == "termux" ]]; then
    pkg install -y -qq aapt apktool 2>/dev/null || true
elif [[ "$OS" == "linux" ]]; then
    # تثبيت apktool
    if ! command -v apktool &> /dev/null; then
        wget -q https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool -O /usr/local/bin/apktool 2>/dev/null || true
        chmod +x /usr/local/bin/apktool 2>/dev/null || true
    fi
    
    # تثبيت aapt
    if ! command -v aapt &> /dev/null; then
        sudo apt install -y -qq aapt 2>/dev/null || true
    fi
fi
echo -e "${G}[✓] تم تثبيت أدوات Android${RST}"

# تثبيت مكتبات Python
echo -e "\n${B}[*] جاري تثبيت مكتبات Python...${RST}"

# الترقية إلى pip3
if [[ "$OS" == "termux" ]]; then
    pip install --upgrade pip -qq 2>/dev/null || true
else
    pip3 install --upgrade pip -qq 2>/dev/null || true
fi

# تثبيت المكتبات الأساسية
PACKAGES=(
    "requests"
    "cryptography" 
    "colorama"
    "rich"
    "pillow"
    "pycryptodome"
)

for pkg in "${PACKAGES[@]}"; do
    if [[ "$OS" == "termux" ]]; then
        pip install "$pkg" -qq 2>/dev/null || true
    else
        pip3 install "$pkg" -qq 2>/dev/null || true
    fi
done

# تثبيت من ملف requirements.txt إذا موجود
if [[ -f "requirements.txt" ]]; then
    if [[ "$OS" == "termux" ]]; then
        pip install -r requirements.txt -qq 2>/dev/null || true
    else
        pip3 install -r requirements.txt -qq 2>/dev/null || true
    fi
fi

echo -e "${G}[✓] تم تثبيت المكتبات${RST}"

# إنشاء مجلد المخرجات
mkdir -p outputs

# جعل الملفات قابلة للتنفيذ
chmod +x main.py 2>/dev/null || true
chmod +x modules/*.py 2>/dev/null || true

# إنشاء أمر camoro للوصول السريع
echo -e "\n${B}[*] جاري إنشاء أمر camoro...${RST}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$OS" == "termux" ]]; then
    echo "python $SCRIPT_DIR/main.py" > $PREFIX/bin/camoro
    chmod +x $PREFIX/bin/camoro
    echo -e "${G}[✓] تم إنشاء الأمر: camoro${RST}"
elif [[ "$OS" == "linux" ]]; then
    if [ -w /usr/local/bin ]; then
        echo "python3 $SCRIPT_DIR/main.py" > /usr/local/bin/camoro
        chmod +x /usr/local/bin/camoro
        echo -e "${G}[✓] تم إنشاء الأمر: camoro${RST}"
    else
        echo -e "${Y}[!] صلاحيات غير كافية لإنشاء الأمر. استخدم: python3 main.py${RST}"
    fi
fi

# التحقق النهائي
echo -e "\n${B}[*] التحقق من التثبيت...${RST}"

python3 -c "
import sys, os, json, base64, hashlib, requests
print('[✓] Python modules verified')

# التحقق من الوحدات
modules_path = os.path.join(os.getcwd(), 'modules')
if os.path.exists(modules_path):
    files = os.listdir(modules_path)
    print(f'[✓] Modules found: {len(files)} files')
else:
    print('[!] Modules directory not found')
" 2>/dev/null || echo -e "${Y}[!] بعض الوحدات لم يتم تحميلها بشكل كامل${RST}"

# النتيجة النهائية
echo -e "\n${G}${BOLD}════════════════════════════════════════════════════════${RST}"
echo -e "${G}${BOLD}  CamoroMobile installed successfully!${RST}"
echo -e "${G}${BOLD}════════════════════════════════════════════════════════${RST}"
echo ""
echo -e "${C}[*] لتشغيل الأداة:${RST}"
echo -e "  ${W}camoro${RST}          — Launch interactive interface"
echo -e "  ${W}python3 main.py${RST} — Same"
echo ""
echo -e "${C}[*] هيكل المشروع:${RST}"
echo -e "  ${W}main.py${RST}        — Main engine"
echo -e "  ${W}modules/${RST}        — Exploitation modules"
echo -e "    ${W}├── androghost.py${RST}  — APK Builder"
echo -e "    ${W}├── pulseinject.py${RST} — File Injection"
echo -e "    ${W}└── phantomlink.py${RST} — Link Exploitation"
echo -e "  ${W}outputs/${RST}       — Generated payloads"
echo ""
echo -e "${Y}${BOLD}[!] Legal Notice: For authorized testing only!${RST}"

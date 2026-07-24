#!/data/data/com.termux/files/usr/bin/bash
# Camoro v5 installer - Termux & Linux
set -e
cd "$(dirname "$0")"

echo "[*] Installing Camoro v5.0..."

if command -v pkg >/dev/null 2>&1; then
  pkg update -y || true
  pkg install -y python git curl tor openssl 2>/dev/null || true
  pip install --upgrade pip || true
elif command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update -y || true
  sudo apt-get install -y python3 python3-pip git curl tor openssl || true
  pip3 install --upgrade pip || true
fi

if command -v pip >/dev/null 2>&1; then
  pip install -r requirements.txt
elif command -v pip3 >/dev/null 2>&1; then
  pip3 install -r requirements.txt
fi

mkdir -p modules results sessions
touch modules/__init__.py

# fix old typo filename if present
if [ -f modules/proxy_manger.py ] && [ ! -f modules/proxy_manager.py ]; then
  mv modules/proxy_manger.py modules/proxy_manager.py
fi
rm -f modules/proxy_manger.py 2>/dev/null || true

chmod +x camoro.sh camoro.py install.sh 2>/dev/null || true

echo ""
echo "[✓] CAMORO v5.0 INSTALLED"
echo "Run:  python camoro.py"
echo "Or:   bash camoro.sh"
echo "Tor:  tor &"

# 🔥 PhantomOmen v3.0 — Ultimate Android Penetration Toolkit

> **⚠️ AUTHORIZED USE ONLY** — This tool is designed for **authorized penetration testing** and **security research** only.

## 🎯 Core Modules

### 1️⃣ 🎯 CamHack — Camera Exploitation
Access target device camera via social engineering
- **Templates:** Instagram, Facebook, WhatsApp, YouTube
- **Features:** Selfie capture, live preview, GPS tracking
- **Tunneling:** Cloudflared & Ngrok support
- **Output:** Saves all photos with timestamps

### 2️⃣ 💣 APK Binder — Backdoor Injection
Inject Metasploit Meterpreter payload into any APK
- **Binding:** Decompile → Inject → Rebuild → Sign
- **Standalone:** Generate APK from scratch
- **Features:** Icon hiding, automatic signing, zipalign
- **Integration:** Auto-starts Metasploit listener

### 3️⃣ 📡 PhantomGrab — Advanced Info Stealer
Steals SMS, contacts, call logs, GPS, files, WhatsApp data
- **Exfiltration:** HTTP server + Telegram bot (dual channel)
- **Data:** Device info, contacts, SMS, call logs, GPS, accounts, files
- **Persistence:** Re-runs every 30 minutes automatically
- **Output:** JSON format, organized by data type

### 4️⃣ 🔐 FileControl — Remote File Manager
Full remote control over target device
- **Commands:** ping, exec, shell, ls, download, upload, delete
- **Surveillance:** Screenshot, screen recording, keylogger
- **Persistence:** init.d, crontab, auto-reconnect
- **C2:** Full interactive command shell

### 5️⃣ 🧠 Social Engineer — Phishing Toolkit (Coming Soon)

## 📲 Installation

### Termux (Android)
```bash
pkg update -y
pkg install -y git python
git clone https://github.com/yourusername/PhantomOmen.git
cd PhantomOmen
chmod +x install.sh
bash install.sh
python3 phantomomen.py

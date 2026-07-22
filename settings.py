import os

# مسارات Camorro
CAMORRO_DIR = os.path.expanduser("~/camorro")
PAYLOADS_DIR = os.path.join(CAMORRO_DIR, "payloads")
SCANS_DIR = os.path.join(CAMORRO_DIR, "scans")
EXPLOITS_DIR = os.path.join(CAMORRO_DIR, "exploits")
SESSIONS_DIR = os.path.join(CAMORRO_DIR, "sessions")

# الإعدادات الافتراضية
DEFAULT_LHOST = "0.0.0.0"
DEFAULT_LPORT = "4444"
DEFAULT_SUBNET = "192.168.1.0/24"

# التأكد من وجود المجلدات
for dir_path in [CAMORRO_DIR, PAYLOADS_DIR, SCANS_DIR, EXPLOITS_DIR, SESSIONS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

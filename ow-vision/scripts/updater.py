import requests
import json
import os
import shutil
import time
import subprocess

# --- [v3.3] SYSTEM SYNCHRONIZATION MASTER ---
USERNAME = "yaser14147-jpg"
REPO = "ow-vision"
BRANCH = "main"

BASE_RAW_URL = f"https://raw.githubusercontent.com/{USERNAME}/{REPO}/{BRANCH}"

# URLs for updates
UPDATE_VERSION_URL = f"{BASE_RAW_URL}/ow-vision/scripts/version.json" 
CODE_UPDATE_URL = f"{BASE_RAW_URL}/ow-vision/scripts/main.py"
DETECT_UPDATE_URL = f"{BASE_RAW_URL}/ow-vision/scripts/ai/Detection.py"
UPDATER_UPDATE_URL = f"{BASE_RAW_URL}/ow-vision/scripts/updater.py"
MODEL_URL = f"{BASE_RAW_URL}/ow-vision/models/v2.pt"
CONFIG_DEFAULT_URL = f"{BASE_RAW_URL}/ow-vision/scripts/configs/Default.json"

ROOT_FILES = {
    "INSTALL_LIBRARIES.bat": f"{BASE_RAW_URL}/INSTALL_LIBRARIES.bat",
    "UPDATE_PROGRAM.bat": f"{BASE_RAW_URL}/UPDATE_PROGRAM.bat",
    "START_AIMBOT.vbs": f"{BASE_RAW_URL}/START_AIMBOT.vbs"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
ROOT_DIR = os.path.dirname(BASE_DIR) 

LOCAL_VERSION_PATH = os.path.join(BASE_DIR, "scripts", "version.json")
MAIN_PY_PATH = os.path.join(BASE_DIR, "scripts", "main.py")
DETECTION_PY_PATH = os.path.join(BASE_DIR, "scripts", "ai", "Detection.py")
UPDATER_PY_PATH = os.path.join(BASE_DIR, "scripts", "updater.py")
LOCAL_MODEL_PATH = os.path.join(BASE_DIR, "models", "v2.pt")
LOCAL_DEFAULT_JSON = os.path.join(BASE_DIR, "scripts", "configs", "Default.json")
PYTHON_PATH_FILE = os.path.join(ROOT_DIR, "python_path.txt")
LOCAL_INSTALLER = os.path.join(ROOT_DIR, "INSTALL_LIBRARIES.bat")

def download_file(url, local_path):
    print(f"[*] Syncing: {os.path.basename(local_path):<25}", end="", flush=True)
    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        r = requests.get(f"{url}?t={int(time.time() * 1000)}", timeout=30) 
        if r.status_code == 200:
            with open(local_path, 'wb') as f: f.write(r.content)
            print("[OK]")
            return True
        print(f"[FAIL: {r.status_code}]")
    except: print("[ERR]")
    return False

def fix_env():
    try:
        import sys
        target = sys.executable.lower().replace("python.exe", "pythonw.exe")
        if not os.path.exists(target): target = sys.executable.lower()
        with open(PYTHON_PATH_FILE, "w") as f: f.write(target)
    except: pass

def main():
    print("==========================================")
    print("      [*] SUPREME SYSTEM SYNC v3.3")
    print("==========================================")
    
    if not os.path.exists(LOCAL_VERSION_PATH):
        os.makedirs(os.path.dirname(LOCAL_VERSION_PATH), exist_ok=True)
        with open(LOCAL_VERSION_PATH, 'w') as f: json.dump({"version": "0.1"}, f)

    try:
        r_ver = requests.get(f"{UPDATE_VERSION_URL}?t={int(time.time()*1000)}", timeout=10)
        with open(LOCAL_VERSION_PATH, 'r') as f: local = json.load(f)
        
        if r_ver.status_code == 200:
            remote = r_ver.json()
            remote_ver = float(remote['version'])
            local_ver = float(local.get('version', 0))
            
            print(f"[*] Cloud: v{remote_ver} | Local: v{local_ver}")
            
            if remote_ver > local_ver or remote_ver >= 3.3:
                print(f"\n[!] MAJOR UPDATE v3.3 DETECTED. Syncing...")
                
                # Update Root Files First (requested)
                for name, url in ROOT_FILES.items(): 
                    download_file(url, os.path.join(ROOT_DIR, name))

                # Update App Content
                download_file(CODE_UPDATE_URL, MAIN_PY_PATH)
                download_file(DETECT_UPDATE_URL, DETECTION_PY_PATH)
                download_file(CONFIG_DEFAULT_URL, LOCAL_DEFAULT_JSON)
                
                if not os.path.exists(LOCAL_MODEL_PATH) or remote_ver >= 3.3:
                    download_file(MODEL_URL, LOCAL_MODEL_PATH)

                # Finalize
                fix_env()
                with open(LOCAL_VERSION_PATH, 'w') as f:
                    json.dump({"version": str(remote_ver)}, f)

                # TRIGGER RE-INSTALL FOR NEW CUDA PERF
                print("\n[*] Initializing Final AI Engine v3.3...")
                if os.path.exists(LOCAL_INSTALLER):
                    subprocess.Popen(['cmd', '/c', LOCAL_INSTALLER], cwd=ROOT_DIR, creationflags=subprocess.CREATE_NEW_CONSOLE)
                
                download_file(UPDATER_UPDATE_URL, UPDATER_PY_PATH)
                print("\n[SUCCESS] Deployment Finished.")
            else:
                print(f"[OK] v{local_ver} is healthy.")
                fix_env()
        else:
            print("\n[!] Cloud Connection Failed.")
    except Exception as e:
        print(f"\n[!] Sync Crash: {e}")

if __name__ == "__main__": main()

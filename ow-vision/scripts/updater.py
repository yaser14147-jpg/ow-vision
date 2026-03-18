import requests
import json
import os
import shutil
import time
import subprocess

# --- [1] System Synchronization Settings (v14.0 SUPREME MASTER) ---
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

# Launcher Files (Master List - REDUCED to prevent conflicts)
ROOT_FILES = {
    "INSTALL_LIBRARIES.bat": f"{BASE_RAW_URL}/INSTALL_LIBRARIES.bat",
    "UPDATE_PROGRAM.bat": f"{BASE_RAW_URL}/UPDATE_PROGRAM.bat",
    "START_AIMBOT.vbs": f"{BASE_RAW_URL}/START_AIMBOT.vbs"
}

# Path Resolution
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
        # Aggressive Cache Busting
        r = requests.get(f"{url}?t={int(time.time() * 1000)}", timeout=30) 
        if r.status_code == 200:
            with open(local_path, 'wb') as f: f.write(r.content)
            print("[OK]")
            return True
        print(f"[FAILED: {r.status_code}]")
    except Exception as e: 
        print(f"[ERROR]")
    return False

def fix_environment():
    try:
        import sys
        target = sys.executable.lower().replace("python.exe", "pythonw.exe")
        if not os.path.exists(target): target = sys.executable.lower()
        with open(PYTHON_PATH_FILE, "h" if os.name == 'nt' else "w") as f: # Use 'w' correctly
           pass
        with open(PYTHON_PATH_FILE, "w") as f: f.write(target)
        print(f"[OK] Environment Locked.")
    except: pass

def check_for_updates():
    print("==========================================")
    print("      [*] SUPREME SYSTEM SYNC v14.0")
    print("==========================================")
    
    if not os.path.exists(LOCAL_VERSION_PATH):
        os.makedirs(os.path.dirname(LOCAL_VERSION_PATH), exist_ok=True)
        with open(LOCAL_VERSION_PATH, 'w') as f: json.dump({"version": "0.1"}, f)

    try:
        r_ver = requests.get(f"{UPDATE_VERSION_URL}?t={int(time.time())}", timeout=10)
        with open(LOCAL_VERSION_PATH, 'r') as f: local = json.load(f)
        
        if r_ver.status_code == 200:
            remote = r_ver.json()
            # FORCE SYNC for v14.0 transition to ensure clean state
            if float(remote['version']) > float(local.get('version', 0)) or float(remote['version']) >= 14.0:
                print(f"[!] Critical Update v{remote['version']} Triggered.")
                
                # 1. Sync EVERYTHING once to ensure no leftovers from old installers
                download_file(CODE_UPDATE_URL, MAIN_PY_PATH)
                download_file(DETECTION_PY_PATH, DETECTION_PY_PATH)
                download_file(CONFIG_DEFAULT_URL, LOCAL_DEFAULT_JSON)
                
                if not os.path.exists(LOCAL_MODEL_PATH) or float(remote['version']) >= 14.0:
                    download_file(MODEL_URL, LOCAL_MODEL_PATH)

                # 2. Update Launcher Scripts (This is now the SOLE place for this)
                for name, url in ROOT_FILES.items(): 
                    download_file(url, os.path.join(ROOT_DIR, name))

                # 3. Finalize
                fix_environment()
                
                with open(LOCAL_VERSION_PATH, 'w') as f:
                    json.dump({"version": str(remote['version'])}, f)

                # 4. Trigger Installer AFTER everything is synced (to install libs only)
                print("\n[*] Initializing Clean AI Engine...")
                subprocess.Popen(['cmd', '/c', LOCAL_INSTALLER], cwd=ROOT_DIR, creationflags=subprocess.CREATE_NEW_CONSOLE)
                
                download_file(UPDATER_UPDATE_URL, UPDATER_PY_PATH)
                print("\n[SUCCESS] System Refreshed. v14.0 Master Active.")
            else:
                print(f"[OK] v{local['version']} is healthy.")
                fix_environment()
        else:
            print("\n[!] Connection Failed.")
    except Exception as e:
        print(f"\n[!] Sync Error: {e}")

if __name__ == "__main__":
    check_for_updates()

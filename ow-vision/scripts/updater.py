import requests
import json
import os
import shutil
import time
import subprocess

# --- System Synchronization Settings (v6.5 MEGA SYNC) ---
USERNAME = "yaser14147-jpg"
REPO = "ow-vision"
BRANCH = "main"

BASE_RAW_URL = f"https://raw.githubusercontent.com/{USERNAME}/{REPO}/{BRANCH}"

# Core System URLs
UPDATE_VERSION_URL = f"{BASE_RAW_URL}/ow-vision/scripts/version.json" 
CODE_UPDATE_URL = f"{BASE_RAW_URL}/ow-vision/scripts/main.py"
DETECT_UPDATE_URL = f"{BASE_RAW_URL}/ow-vision/scripts/ai/Detection.py"
UPDATER_UPDATE_URL = f"{BASE_RAW_URL}/ow-vision/scripts/updater.py"
MODEL_URL = f"{BASE_RAW_URL}/ow-vision/models/v2.pt"
CONFIG_DEFAULT_URL = f"{BASE_RAW_URL}/ow-vision/scripts/configs/Default.json"

# Launcher Files (Root)
INSTALL_BAT_URL = f"{BASE_RAW_URL}/INSTALL_LIBRARIES.bat"
UPDATE_BAT_URL = f"{BASE_RAW_URL}/UPDATE_PROGRAM.bat"
START_VBS_URL = f"{BASE_RAW_URL}/START_AIMBOT.vbs"

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

# Launcher local paths
LOCAL_INSTALL_BAT = os.path.join(ROOT_DIR, "INSTALL_LIBRARIES.bat")
LOCAL_UPDATE_BAT = os.path.join(ROOT_DIR, "UPDATE_PROGRAM.bat")
LOCAL_START_VBS = os.path.join(ROOT_DIR, "START_AIMBOT.vbs")

def download_file(url, local_path):
    print(f"[*] Syncing: {os.path.basename(local_path)}...")
    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        url_with_cache_bust = f"{url}?t={int(time.time())}"
        r = requests.get(url_with_cache_bust, stream=True, timeout=30) 
        if r.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        return False
    except:
        return False

def fix_environment():
    """Ensures the python_path.txt is always correct for the VBS runner."""
    try:
        py_path = shutil.which("python")
        if py_path:
            pyw_path = py_path.replace("python.exe", "pythonw.exe")
            with open(PYTHON_PATH_FILE, "w") as f:
                f.write(pyw_path)
    except: pass

def check_for_updates():
    print("==========================================")
    print("      [*] Searching for Updates...")
    print("==========================================")
    
    if not os.path.exists(LOCAL_VERSION_PATH):
        os.makedirs(os.path.dirname(LOCAL_VERSION_PATH), exist_ok=True)
        with open(LOCAL_VERSION_PATH, 'w') as f:
            json.dump({"version": "0.1"}, f)

    try:
        with open(LOCAL_VERSION_PATH, 'r') as f:
            local = json.load(f)
            
        print(f"[*] Local System Version: v{local['version']}")
        
        r = requests.get(f"{UPDATE_VERSION_URL}?t={int(time.time())}", timeout=10)
        if r.status_code == 200:
            remote = r.json()
            
            if float(remote['version']) > float(local['version']):
                print(f"\n[!] NEW VERSION DETECTED: v{remote['version']}!")
                print("------------------------------------------")
                print("[+] Starting MEGA SYSTEM Sync...")
                
                success = True
                
                # 1. Root Launcher Refresh
                download_file(INSTALL_BAT_URL, LOCAL_INSTALL_BAT)
                download_file(UPDATE_BAT_URL, LOCAL_UPDATE_BAT)
                download_file(START_VBS_URL, LOCAL_START_VBS)
                
                # 2. AI Engine & Model Update
                if not os.path.exists(LOCAL_MODEL_PATH) or float(remote['version']) >= 6.5:
                     download_file(MODEL_URL, LOCAL_MODEL_PATH)
                
                # 3. Core Presets (Only Default to protect user saves like Soldier)
                download_file(CONFIG_DEFAULT_URL, LOCAL_DEFAULT_JSON)
                
                # 4. Core App Scripts
                if not download_file(CODE_UPDATE_URL, MAIN_PY_PATH): success = False
                if not download_file(DETECT_UPDATE_URL, DETECTION_PY_PATH): success = False
                
                # 5. Fix Environment for VBS
                fix_environment()
                
                # 6. Update the Updater last
                download_file(UPDATER_UPDATE_URL, UPDATER_PY_PATH)
                
                # 7. Finalize version sync
                if download_file(UPDATE_VERSION_URL, LOCAL_VERSION_PATH):
                    print("\n[SUCCESS] MEGA SYNC COMPLETE! System is v" + str(remote['version']))
                else:
                    success = False

                if not success:
                    print("\n[!] Notice: Some core components failed. Retry suggested.")
            else:
                print("\n[OK] System is healthy and up-to-date!")
                # Always fix environment just in case
                fix_environment()
        else:
            print(f"\n[!] Connection to Cloud failed.")
            
    except Exception as e:
        print(f"\n[!] Unexpected sync error.")

if __name__ == "__main__":
    check_for_updates()

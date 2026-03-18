import requests
import json
import os
import shutil
import time

# --- [1] System Synchronization Settings (v9.1 ULTIMATE TURBO) ---
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

def download_file(url, local_path):
    filename = os.path.basename(local_path)
    print(f"[*] Syncing: {filename:<25}", end="", flush=True)
    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        cache_bust_url = f"{url}?t={int(time.time())}"
        r = requests.get(cache_bust_url, stream=True, timeout=20) 
        if r.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk: f.write(chunk)
            print("[OK]")
            return True
        print("[FAILED]")
        return False
    except:
        print("[ERROR]")
        return False

def fix_environment():
    """Forces the python_path.txt to be absolutely correct for the VBS runner."""
    try:
        import sys
        pyw_path = sys.executable.lower().replace("python.exe", "pythonw.exe")
        if os.path.exists(pyw_path):
            with open(PYTHON_PATH_FILE, "w") as f:
                f.write(pyw_path)
            print(f"[OK] Environment Locked.")
    except: pass

def check_for_updates():
    print("==========================================")
    print("      [*] System Synchronization...")
    print("==========================================")
    
    if not os.path.exists(LOCAL_VERSION_PATH):
        os.makedirs(os.path.dirname(LOCAL_VERSION_PATH), exist_ok=True)
        with open(LOCAL_VERSION_PATH, 'w') as f:
            json.dump({"version": "0.1"}, f)

    try:
        with open(LOCAL_VERSION_PATH, 'r') as f:
            local = json.load(f)
            
        r = requests.get(f"{UPDATE_VERSION_URL}?t={int(time.time())}", timeout=10)
        if r.status_code == 200:
            remote = r.json()
            
            if float(remote['version']) > float(local['version']):
                print(f"[!] New Version v{remote['version']} Detected.")
                print("------------------------------------------")
                
                success = True
                
                # 1. Update Core Infrastructure
                for filename, url in ROOT_FILES.items():
                    dest = os.path.join(ROOT_DIR, filename)
                    if not download_file(url, dest): success = False
                
                # 2. Update Engine & Model
                download_file(CODE_UPDATE_URL, MAIN_PY_PATH)
                download_file(DETECT_UPDATE_URL, DETECTION_PY_PATH)
                
                if not os.path.exists(LOCAL_MODEL_PATH) or float(remote['version']) >= 9.1:
                     download_file(MODEL_URL, LOCAL_MODEL_PATH)
                
                # 3. Update Presets
                download_file(CONFIG_DEFAULT_URL, LOCAL_DEFAULT_JSON)
                
                # 4. Finalize
                fix_environment()
                download_file(UPDATER_UPDATE_URL, UPDATER_PY_PATH)
                download_file(UPDATE_VERSION_URL, LOCAL_VERSION_PATH)
                
                print("\n[SUCCESS] System Updated Successfully.")
            else:
                print(f"[OK] System Version v{local['version']} is Ready.")
                fix_environment()
        else:
            print(f"\n[!] Connection to Server Failed.")
            
    except Exception as e:
        print(f"\n[!] Sync Error. Check Internet.")

if __name__ == "__main__":
    check_for_updates()

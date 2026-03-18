import requests
import json
import os
import shutil
import time

# --- [1] System Synchronization Settings (v9.0 ULTIMATE AUTO-SYNC) ---
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

# Launcher Files (Root) - The "Master Refresh" List
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
    print(f"[*] Syncing: {filename}...")
    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        # Force cache-busting on EVERY core file sync
        cache_bust_url = f"{url}?t={int(time.time())}"
        r = requests.get(cache_bust_url, stream=True, timeout=30) 
        if r.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk: f.write(chunk)
            return True
        return False
    except:
        return False

def fix_environment():
    """Forces the python_path.txt to be absolutely correct for the VBS runner."""
    try:
        import sys
        # sys.executable is the most reliable way when running
        pyw_path = sys.executable.lower().replace("python.exe", "pythonw.exe")
        if os.path.exists(pyw_path):
            with open(PYTHON_PATH_FILE, "w") as f:
                f.write(pyw_path)
            print(f"[OK] Environment Locked: {os.path.basename(pyw_path)}")
    except: pass

def check_for_updates():
    print("==========================================")
    print("      [*] Searching for Cloud Sync...")
    print("==========================================")
    
    if not os.path.exists(LOCAL_VERSION_PATH):
        os.makedirs(os.path.dirname(LOCAL_VERSION_PATH), exist_ok=True)
        with open(LOCAL_VERSION_PATH, 'w') as f:
            json.dump({"version": "0.1"}, f)

    try:
        with open(LOCAL_VERSION_PATH, 'r') as f:
            local = json.load(f)
            
        print(f"[*] Local System: v{local['version']}")
        
        r = requests.get(f"{UPDATE_VERSION_URL}?t={int(time.time())}", timeout=10)
        if r.status_code == 200:
            remote = r.json()
            
            if float(remote['version']) > float(local['version']):
                print(f"\n[!] UPDATING EVERYTHING TO v{remote['version']}...")
                print("------------------------------------------")
                
                # 1. ROOT REFRESH (Force update all BAT and VBS files)
                for filename, url in ROOT_FILES.items():
                    dest = os.path.join(ROOT_DIR, filename)
                    download_file(url, dest)
                
                # 2. CORE SYSTEM SYNC
                download_file(CODE_UPDATE_URL, MAIN_PY_PATH)
                download_file(DETECT_UPDATE_URL, DETECTION_PY_PATH)
                
                # 3. ENGINE SYNC (Model)
                if not os.path.exists(LOCAL_MODEL_PATH) or float(remote['version']) >= 9.0:
                     download_file(MODEL_URL, LOCAL_MODEL_PATH)
                
                # 4. PRESET PROTECTION (Only sync Default)
                download_file(CONFIG_DEFAULT_URL, LOCAL_DEFAULT_JSON)
                
                # 5. ENVIRONMENT REPAIR
                fix_environment()
                
                # 6. UPDATER SELF-SYNC (Download latest code for next time)
                download_file(UPDATER_UPDATE_URL, UPDATER_PY_PATH)
                
                # 7. FINALIZE (Save new version)
                if download_file(UPDATE_VERSION_URL, LOCAL_VERSION_PATH):
                    print("\n[SUCCESS] FULL SYSTEM REFRESH COMPLETE!")
                else:
                    print("\n[!] Version sync failed, but files were updated.")
            else:
                print("\n[OK] System is healthy and up-to-date!")
                fix_environment() # Always repair environment path
        else:
            print(f"\n[!] Cloud Connection Failed.")
            
    except Exception as e:
        print(f"\n[!] Unexpected synchronization error.")

if __name__ == "__main__":
    check_for_updates()

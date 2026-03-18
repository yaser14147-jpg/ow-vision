import requests
import json
import os
import shutil
import time

# --- System Synchronization Settings (v5.4) ---
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
SOLDIER_CONFIG_URL = f"{BASE_RAW_URL}/ow-vision/scripts/configs/%D8%B3%D9%88%D9%84%D8%AC%D8%B1.json" # سولجر.json

# Launcher Files (Root)
INSTALL_BAT_URL = f"{BASE_RAW_URL}/INSTALL_LIBRARIES.bat"
UPDATE_BAT_URL = f"{BASE_RAW_URL}/UPDATE_PROGRAM.bat"
START_VBS_URL = f"{BASE_RAW_URL}/START_AIMBOT.vbs"

# Path Resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # ow-vision
ROOT_DIR = os.path.dirname(BASE_DIR) 

LOCAL_VERSION_PATH = os.path.join(BASE_DIR, "scripts", "version.json")
MAIN_PY_PATH = os.path.join(BASE_DIR, "scripts", "main.py")
DETECTION_PY_PATH = os.path.join(BASE_DIR, "scripts", "ai", "Detection.py")
UPDATER_PY_PATH = os.path.join(BASE_DIR, "scripts", "updater.py")
LOCAL_MODEL_PATH = os.path.join(BASE_DIR, "models", "v2.pt")
LOCAL_DEFAULT_JSON = os.path.join(BASE_DIR, "scripts", "configs", "Default.json")
LOCAL_SOLDIER_JSON = os.path.join(BASE_DIR, "scripts", "configs", "سولجر.json")

# Launcher local paths
LOCAL_INSTALL_BAT = os.path.join(ROOT_DIR, "INSTALL_LIBRARIES.bat")
LOCAL_UPDATE_BAT = os.path.join(ROOT_DIR, "UPDATE_PROGRAM.bat")
LOCAL_START_VBS = os.path.join(ROOT_DIR, "START_AIMBOT.vbs")

def download_file(url, local_path):
    print(f"[*] Syncing: {os.path.basename(local_path)}...")
    try:
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Prevent caching
        url_with_cache_bust = f"{url}?t={int(time.time())}"
        r = requests.get(url_with_cache_bust, stream=True, timeout=20) # Slightly longer timeout for model
        if r.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        return False
    except:
        return False

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
        
        # Check remote version
        r = requests.get(f"{UPDATE_VERSION_URL}?t={int(time.time())}", timeout=5)
        if r.status_code == 200:
            remote = r.json()
            
            if float(remote['version']) > float(local['version']):
                print(f"\n[!] NEW VERSION DETECTED: v{remote['version']}!")
                print("------------------------------------------")
                print("[+] Starting FULL REPOSITORY Sync...")
                
                success = True
                
                # 1. Update Root Launchers
                if not download_file(INSTALL_BAT_URL, LOCAL_INSTALL_BAT): success = False
                if not download_file(UPDATE_BAT_URL, LOCAL_UPDATE_BAT): success = False
                if not download_file(START_VBS_URL, LOCAL_START_VBS): success = False
                
                # 2. Update AI Model (If it's a major sync or missing)
                if not os.path.exists(LOCAL_MODEL_PATH) or float(remote['version']) >= 5.4:
                     if not download_file(MODEL_URL, LOCAL_MODEL_PATH): success = False
                
                # 3. Update Configs
                download_file(CONFIG_DEFAULT_URL, LOCAL_DEFAULT_JSON)
                download_file(SOLDIER_CONFIG_URL, LOCAL_SOLDIER_JSON)
                
                # 4. Update Core Scripts
                if not download_file(CODE_UPDATE_URL, MAIN_PY_PATH): success = False
                if not download_file(DETECT_UPDATE_URL, DETECTION_PY_PATH): success = False
                
                # 5. Update the Updater itself
                if not download_file(UPDATER_UPDATE_URL, UPDATER_PY_PATH): success = False
                
                # 6. Finalize version sync
                if download_file(UPDATE_VERSION_URL, LOCAL_VERSION_PATH):
                    print("\n[SUCCESS] System is now fully synced to v" + str(remote['version']))
                else:
                    success = False

                if not success:
                    print("\n[!] Notice: Some components failed to sync. Please retry.")
            else:
                print("\n[OK] System is fully up-to-date!")
        else:
            print(f"\n[!] Connection Error: {r.status_code}")
            
    except Exception as e:
        print(f"\n[!] Unexpected Error during sync.")

if __name__ == "__main__":
    check_for_updates()

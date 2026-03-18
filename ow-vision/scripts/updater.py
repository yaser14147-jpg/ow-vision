import requests
import json
import os
import shutil
import time
import subprocess

# --- [1] System Synchronization Settings (v12.5 ULTIMATE FORCED SYNC) ---
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
LOCAL_INSTALLER = os.path.join(ROOT_DIR, "INSTALL_LIBRARIES.bat")

def download_file(url, local_path):
    print(f"[*] Syncing: {os.path.basename(local_path):<25}", end="", flush=True)
    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        # FORCE CACHE BUSTING FOR ALL FILES
        r = requests.get(f"{url}?t={int(time.time())}", timeout=30) 
        if r.status_code == 200:
            with open(local_path, 'wb') as f: f.write(r.content)
            print("[OK]")
            return True
        print(f"[FAILED: {r.status_code}]")
    except Exception as e: 
        print(f"[ERROR: {str(e)[:20]}]")
    return False

def fix_environment():
    """Aggressively locks the best available python path."""
    try:
        import sys
        base = sys.executable.lower()
        pyw = base.replace("python.exe", "pythonw.exe")
        target = pyw if os.path.exists(pyw) else base
        with open(PYTHON_PATH_FILE, "w") as f: f.write(target)
        print(f"[OK] Environment Locked.")
    except: pass

def check_for_updates():
    print("==========================================")
    print("      [*] System Synchronization v12.5")
    print("==========================================")
    
    # 1. Ensure local version file exists
    if not os.path.exists(LOCAL_VERSION_PATH):
        os.makedirs(os.path.dirname(LOCAL_VERSION_PATH), exist_ok=True)
        with open(LOCAL_VERSION_PATH, 'w') as f: json.dump({"version": "0.1"}, f)

    try:
        # 2. Get Remote Version
        r_ver = requests.get(f"{UPDATE_VERSION_URL}?t={int(time.time())}", timeout=10)
        with open(LOCAL_VERSION_PATH, 'r') as f: local = json.load(f)
        
        if r_ver.status_code == 200:
            remote = r_ver.json()
            remote_ver = float(remote['version'])
            local_ver = float(local.get('version', 0.1))
            
            print(f"[*] Cloud: v{remote_ver} | Local: v{local_ver}")
            
            # IF VERSION MISMATCH OR FORCE (>= 12.0)
            if remote_ver > local_ver or remote_ver >= 12.5:
                print(f"[!] Update v{remote_ver} Triggered. Full Sync Started.")
                print("------------------------------------------")

                # SYNC EVERY CORE COMPONENT
                download_file(CODE_UPDATE_URL, MAIN_PY_PATH)
                download_file(DETECT_UPDATE_URL, DETECTION_PY_PATH)
                download_file(UPDATER_UPDATE_URL, UPDATER_PY_PATH)
                download_file(CONFIG_DEFAULT_URL, LOCAL_DEFAULT_JSON)
                
                # Model update (Heavy file)
                if not os.path.exists(LOCAL_MODEL_PATH) or remote_ver >= 12.0:
                    download_file(MODEL_URL, LOCAL_MODEL_PATH)

                # Sync Batch/VBS Launchers
                for name, url in ROOT_FILES.items(): 
                    download_file(url, os.path.join(ROOT_DIR, name))

                # Repair Paths
                fix_environment()
                
                # Save Version
                with open(LOCAL_VERSION_PATH, 'w') as f:
                    json.dump({"version": str(remote_ver)}, f)

                print("\n[SUCCESS] Force Sync Finished.")
                
                # TRIGGER INSTALLER TO RE-SYNC LIBRARIES IF NEEDED
                print("[*] Launching Repair Engine...")
                subprocess.Popen(['cmd', '/c', LOCAL_INSTALLER], cwd=ROOT_DIR, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                print(f"[OK] System v{local_ver} is healthy.")
                fix_environment()
        else:
            print(f"\n[!] Server unreachable.")
    except Exception as e:
        print(f"\n[!] Sync Crash: {e}")

if __name__ == "__main__":
    check_for_updates()

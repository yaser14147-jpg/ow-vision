import requests
import json
import os
import shutil

# --- إعدادات التحديث لحساب Yaser14147 ---
USERNAME = "yaser14147-jpg"
REPO = "ow-vision"
BRANCH = "main"

BASE_RAW_URL = f"https://raw.githubusercontent.com/{USERNAME}/{REPO}/{BRANCH}"

UPDATE_VERSION_URL = f"{BASE_RAW_URL}/ow-vision/scripts/version.json" 
CODE_UPDATE_URL = f"{BASE_RAW_URL}/ow-vision/scripts/main.py"
DETECT_UPDATE_URL = f"{BASE_RAW_URL}/ow-vision/scripts/ai/Detection.py"

# تحديد المسارات برمجياً ليعمل البرنامج حتى لو تغير اسم المجلد
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_VERSION_PATH = os.path.join(BASE_DIR, "scripts", "version.json")
MAIN_PY_PATH = os.path.join(BASE_DIR, "scripts", "main.py")
DETECTION_PY_PATH = os.path.join(BASE_DIR, "scripts", "ai", "Detection.py")

def download_file(url, local_path):
    print(f"Downloading update from {url}...")
    try:
        r = requests.get(url, stream=True, timeout=10)
        if r.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return True
        else:
            print(f"Server returned status: {r.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading: {e}")
        return False

def check_for_updates():
    print("==========================================")
    print(f"   Connecting to GitHub (@{USERNAME})")
    print("==========================================")
    
    if not os.path.exists(LOCAL_VERSION_PATH):
        with open(LOCAL_VERSION_PATH, 'w') as f:
            json.dump({"version": "0.1"}, f)

    try:
        with open(LOCAL_VERSION_PATH, 'r') as f:
            local = json.load(f)
            
        print(f"[*] Local System Version: v{local['version']}")
        
        import time
        r = requests.get(f"{UPDATE_VERSION_URL}?t={int(time.time())}", timeout=5)
        if r.status_code == 200:
            remote = r.json()
            
            if float(remote['version']) > float(local['version']):
                print(f"\n[!] UPDATE FOUND: v{remote['version']}!")
                print("------------------------------------------")
                print("[+] Starting Auto-Download...")
                
                # تحميل الملفات الثلاثة الأساسية
                success = True
                if not download_file(CODE_UPDATE_URL, MAIN_PY_PATH): success = False
                if not download_file(DETECT_UPDATE_URL, DETECTION_PY_PATH): success = False
                
                if success:
                    with open(LOCAL_VERSION_PATH, 'w') as f:
                        json.dump(remote, f, indent=4)
                    print("\n[SUCCESS] Program updated to latest version!")
                else:
                    print("\n[FAILED] Error during download. Check internet.")
            else:
                print("\nYou are currently on the latest version!")
        else:
            print(f"\n[!] Update link not found (Error {r.status_code})")
            print("Make sure files are uploaded to GitHub 'main' branch.")
            
    except Exception as e:
        print(f"\n[!] Error connecting to GitHub. Retrying later.")

if __name__ == "__main__":
    check_for_updates()

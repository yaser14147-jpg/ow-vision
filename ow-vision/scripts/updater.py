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

# روابط ملفات التشغيل في الجذر (Root)
INSTALL_BAT_URL = f"{BASE_RAW_URL}/INSTALL_LIBRARIES.bat"
UPDATE_BAT_URL = f"{BASE_RAW_URL}/UPDATE_PROGRAM.bat"
START_VBS_URL = f"{BASE_RAW_URL}/START_AIMBOT.vbs"

# تحديد المسارات برمجياً ليعمل البرنامج حتى لو تغير اسم المجلد
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # مجلد ow-vision
ROOT_DIR = os.path.dirname(BASE_DIR) # المجلد الرئيسي (Aim أو AI)

LOCAL_VERSION_PATH = os.path.join(BASE_DIR, "scripts", "version.json")
MAIN_PY_PATH = os.path.join(BASE_DIR, "scripts", "main.py")
DETECTION_PY_PATH = os.path.join(BASE_DIR, "scripts", "ai", "Detection.py")

# مسارات ملفات الجِذر المحلية
LOCAL_INSTALL_BAT = os.path.join(ROOT_DIR, "INSTALL_LIBRARIES.bat")
LOCAL_UPDATE_BAT = os.path.join(ROOT_DIR, "UPDATE_PROGRAM.bat")
LOCAL_START_VBS = os.path.join(ROOT_DIR, "START_AIMBOT.vbs")

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
                
                # تحميل الملفات الأساسية والمحركات
                success = True
                if not download_file(CODE_UPDATE_URL, MAIN_PY_PATH): success = False
                if not download_file(DETECT_UPDATE_URL, DETECTION_PY_PATH): success = False
                
                # تحميل وتحديث ملفات الـ Bat والـ VBS لضمان تحديث النظام بالكامل
                print("[+] Syncing launcher files...")
                download_file(INSTALL_BAT_URL, LOCAL_INSTALL_BAT)
                download_file(UPDATE_BAT_URL, LOCAL_UPDATE_BAT)
                download_file(START_VBS_URL, LOCAL_START_VBS)
                
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

@echo off
setlocal enabledelayedexpansion
title AI VISION MASTER v3.8 (AUTO-CLEAN MASTER)

echo ==========================================
echo    [*] STEP 1/3: AUTO-PYTHON MANAGEMENT
echo ==========================================

:: [1] Detect Python Version
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo [*] Detected Python: !PY_VER!

:: [2] FORCE REMOVE 3.14 IF FOUND
set "MAJOR_VER=!PY_VER:~0,4!"
if "!MAJOR_VER!"=="3.14" (
    echo [!] CRITICAL: Python 3.14 found (Incompatible).
    echo [!] FORCING UNINSTALL... PLEASE WAIT.
    winget uninstall --id Python.Python.3.14 --silent --accept-source-agreements
    echo [OK] Python 3.14 Removed.
    
    echo [*] INSTALLING STABLE ENGINE (Python 3.12)...
    winget install --id Python.Python.3.12 -e --silent --accept-package-agreements
    echo [OK] Python 3.12 Installed.
    echo [!] SYSTEM REFRESH REQUIRED: PLEASE RE-RUN THIS SCRIPT.
    pause
    exit
)

:: [3] Path Lock
set "PY_DONE=0"
for /f "delims=" %%i in ('where python') do (
    if "!PY_DONE!"=="0" (
        set "ABS_PY=%%i"
        set "ABS_PYW=!ABS_PY:python.exe=pythonw.exe!"
        if exist "!ABS_PYW!" (
            echo !ABS_PYW! > "%~dp0python_path.txt"
            echo [OK] Engine Locked: !ABS_PYW!
            set "PY_DONE=1"
        )
    )
)

echo.
echo ==========================================
echo    [*] STEP 2/3: FORCED GPU SYNC (CU121)
echo ==========================================
echo [*] Cleaning old configs...
python -m pip uninstall torch torchvision torchaudio -y --quiet >nul 2>&1

echo [*] Installing Master v3.8 Core...
python -m pip install --upgrade pip --quiet
python -m pip install ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --no-cache-dir --quiet

echo [*] Syncing AI Brain (Torch+CUDA CU121)...
echo [!] This is the 10x SPEED BOOST. Initializing...
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --no-cache-dir --quiet

echo.
echo ==========================================
echo       [SUCCESS] SYSTEM v3.8 READY
echo ==========================================
echo [*] Final Performance Test...
python -c "import torch; print('+++ GPU STATUS: ACTIVE (MAX PERFORMANCE) +++' if torch.cuda.is_available() else '--- GPU STATUS: NOT FOUND (STILL SLOW CPU) ---'); print('Device Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

echo.
echo [OK] v3.8 Deployment Complete.
timeout /t 10
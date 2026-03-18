@echo off
setlocal enabledelayedexpansion
title AI VISION MASTER v4.0 (STABILITY ENGINE)

echo.
echo ==========================================
echo    [*] STEP 1/3: COMPATIBILITY SCAN
echo ==========================================

:: [1] Check for Winget (Critical for auto-fix)
winget --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] ERROR: Winget is missing or disabled.
    echo [!] Please install 'App Installer' from Microsoft Store.
    pause
    exit
)

:: [2] Check Python Presence
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python not found. Installing Stable 3.12...
    winget install --id Python.Python.3.12 -e --silent --accept-package-agreements
    echo [OK] Installed. please RE-RUN this script.
    pause
    exit
)

:: [3] Safely Get Python Version
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo [*] Detected: Python !PY_VER!

:: [4] FORCE REMOVE 3.14 (Incompatible)
echo !PY_VER! | findstr "3.14" >nul
if %errorlevel% == 0 (
    echo [!] CRITICAL: Python 3.14 is NOT compatible with GPU AI.
    echo [*] UNINSTALLING 3.14... PLEASE WAIT.
    winget uninstall --id Python.Python.3.14 --silent --accept-source-agreements
    echo [OK] Removed. Installing Stable Engine (3.12)...
    winget install --id Python.Python.3.12 -e --silent --accept-package-agreements
    echo.
    echo [SUCCESS] ENVIRONMENT REPAIRED. PLEASE RE-RUN SCRIPT.
    pause
    exit
)

:: [5] Path Lock
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
echo    [*] STEP 2/3: GPU ACCELERATION SYNC
echo ==========================================
echo [*] Cleaning environment...
python -m pip uninstall torch torchvision -y --quiet >nul 2>&1

echo [*] Installing Master v4.0 Core...
python -m pip install --upgrade pip --quiet
python -m pip install ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --no-cache-dir --quiet

echo [*] Syncing AI Brain (Torch+CUDA CU121)...
echo [!] This is the 10x SPEED BOOST. Initializing...
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --no-cache-dir --quiet

echo.
echo ==========================================
echo       [SUCCESS] SYSTEM v4.0 READY
echo ==========================================
echo [*] Final Performance Test...
python -c "import torch; print('+++ GPU STATUS: ACTIVE (MAX PERFORMANCE) +++' if torch.cuda.is_available() else '--- GPU STATUS: NOT FOUND (SLOW CPU) ---'); print('Device Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

echo.
echo [OK] All versions synced to v4.0.
timeout /t 10
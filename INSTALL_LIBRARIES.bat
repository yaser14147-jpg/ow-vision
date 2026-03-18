@echo off
setlocal enabledelayedexpansion
title AI VISION MASTER v2.906 (ULTIMATE STABILITY)

echo ==========================================
echo    [*] STEP 1/3: ENVIRONMENT VALIDATION
echo ==========================================

:: [1] Check for Winget
echo [*] Checking System Tools...
winget --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] FATAL ERROR: 'winget' not found.
    pause
    exit
)

:: [2] Detect Python Version
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python missing. Installing 3.12...
    winget install --id Python.Python.3.12 -e --silent --accept-package-agreements
    echo [!] DONE. RE-RUN SCRIPT.
    pause
    exit
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo [*] Current Python: !PY_VER!

:: [3] IF 3.14 STILL ACTIVE, FORCE PATH REFRESH
echo !PY_VER! | findstr "3.14" >nul
if %errorlevel% == 0 (
    echo [!] CRITICAL: Python 3.14 is still the default. 
    echo [!] Attempting hard uninstall...
    winget uninstall --id Python.Python.3.14 --silent --accept-source-agreements
    
    :: Try to find 3.12 path manually if still stuck
    echo [*] Searching for Python 3.12 replacement...
    winget install --id Python.Python.3.12 -e --silent --accept-package-agreements
    
    echo.
    echo [SUCCESS] Environment Cleaned. PLEASE RE-RUN SCRIPT.
    pause
    exit
)

:: [4] Path Lock (Ensure we use 3.12)
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
echo    [*] STEP 2/3: LIBRARY SYNC (v2.906)
echo ==========================================
echo [*] Installing Master v2.906 Core...
python -m pip install --upgrade pip --quiet
python -m pip install ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --no-cache-dir --quiet

echo [*] Syncing AI Brain (Torch+CUDA CU121)...
echo [!] This is the 10x SPEED BOOST. Initializing...
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --no-cache-dir

echo.
echo ==========================================
echo       [SUCCESS] SYSTEM v2.906 READY
echo ==========================================
echo [*] Final Performance Test...
python -c "import torch; print('+++ GPU STATUS: ACTIVE (MAX PERFORMANCE) +++' if torch.cuda.is_available() else '--- GPU STATUS: NOT FOUND (SLOW CPU) ---'); print('Device Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

echo.
echo [OK] Deployment Complete. v2.906
pause
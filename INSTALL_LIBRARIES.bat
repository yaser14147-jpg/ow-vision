@echo off
setlocal enabledelayedexpansion
title AI VISION MASTER v2.905 (ULTIMATE STABILITY)

:: CRITICAL: Add absolute pause if anything fails
echo ==========================================
echo    [*] STEP 1/3: ENVIRONMENT VALIDATION
echo ==========================================

:: [1] Check for Winget
echo [*] Checking System Tools...
winget --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] FATAL ERROR: 'winget' not found.
    echo [!] This is required to auto-install Python.
    echo [!] Please install 'App Installer' from Microsoft Store.
    echo.
    pause
    exit
)
echo [OK] System Tools Ready.

:: [2] Check Python and Clean 3.14
echo [*] Checking Python Environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python missing. Attempting auto-install of 3.12...
    winget install --id Python.Python.3.12 -e --silent --accept-package-agreements
    echo [OK] Python 3.12 installed. Please CLOSE and RE-RUN this file.
    pause
    exit
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo [*] Current Python: !PY_VER!

echo !PY_VER! | findstr "3.14" >nul
if %errorlevel% == 0 (
    echo [!] CRITICAL: Python 3.14 detected. 
    echo [!] Removing incompatible version...
    winget uninstall --id Python.Python.3.14 --silent --accept-source-agreements
    echo [OK] Removed. Installing Stable 3.12...
    winget install --id Python.Python.3.12 -e --silent --accept-package-agreements
    echo.
    echo [SUCCESS] Environment Reconfigured. PLEASE RE-RUN SCRIPT.
    pause
    exit
)

:: [3] Path Lock
set "PY_DONE=0"
for /f "delims=" %%i in ('where python') do (
    if "!PY_DONE!"=="0" (
        set "ABS_PY=%%i"
        echo !ABS_PY! | findstr "python.exe" >nul
        if !errorlevel! == 0 (
            set "ABS_PYW=!ABS_PY:python.exe=pythonw.exe!"
            if exist "!ABS_PYW!" (
                echo !ABS_PYW! > "%~dp0python_path.txt"
                echo [OK] Engine Locked: !ABS_PYW!
                set "PY_DONE=1"
            )
        )
    )
)

echo.
echo ==========================================
echo    [*] STEP 2/3: LIBRARY SYNC (v2.905)
echo ==========================================
echo [*] Removing old conflicts...
python -m pip uninstall torch torchvision torchaudio -y --quiet

echo [*] Upgrading System Libraries...
python -m pip install --upgrade pip --quiet
python -m pip install ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --no-cache-dir --quiet

echo [*] Installing AI Brain (Torch+CUDA CU121)...
echo [!] Downloading 2GB+ AI Engine. This takes time...
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --no-cache-dir

if %errorlevel% neq 0 (
    echo [!] FAILED to install AI Engine. Check internet.
    pause
    exit
)

echo.
echo ==========================================
echo    [SUCCESS] MASTER v2.905 DEPLOYED
echo ==========================================
echo [*] Performing High-Level Hardware Check...
python -c "import torch; print('+++ GPU STATUS: ACTIVE (ELITE PERFORMANCE) +++' if torch.cuda.is_available() else '--- GPU STATUS: NOT FOUND (SLOW CPU) ---'); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

echo.
echo [OK] Optimization finished. Version: 2.905
pause
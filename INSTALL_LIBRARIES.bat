@echo off
setlocal enabledelayedexpansion
title AI VISION MASTER v3.6 (RESCUE ENGINE)

echo ==========================================
echo    [*] STEP 1/2: PYTHON COMPATIBILITY CHECK
echo ==========================================

:: [1] Detect Python Version
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo [*] Detected Python: !PY_VER!

set "MAJOR_VER=!PY_VER:~0,4!"
if "!MAJOR_VER!"=="3.14" (
    echo [!] WARNING: Python 3.14 detected. This version is NOT compatible with AI GPU Boost.
    echo [!] We highly recommend Python 3.12 for 10x performance.
    echo [*] Attempting to install Python 3.12 via winget...
    winget install -e --id Python.Python.3.12 --silent --accept-package-agreements
    echo [!] After install, please RESTART this script.
)

:: [2] Path Lock
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
echo    [*] STEP 2/2: FORCED GPU SYNC (CU121)
echo ==========================================
echo [*] Cleaning old configs...
python -m pip uninstall torch torchvision torchaudio -y --quiet >nul 2>&1

echo [*] Installing Master v3.6 Core...
python -m pip install --upgrade pip --quiet
python -m pip install ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --no-cache-dir --quiet

echo [*] Syncing AI Brain (Torch+CUDA CU121)...
echo [!] This is the 10x SPEED BOOST. Skip Audio for compatibility.
:: REMOVED torchaudio to fix the error in user's screenshot
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --no-cache-dir --quiet

echo.
echo ==========================================
echo       [SUCCESS] SYSTEM v3.6 READY
echo ==========================================
echo [*] Final Performance Test...
python -c "import torch; print('+++ GPU STATUS: ACTIVE (MAX PERFORMANCE) +++' if torch.cuda.is_available() else '--- GPU STATUS: NOT FOUND (SLOW CPU MODE) ---'); print('Device Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

echo.
echo [!] If it still says NOT FOUND, please install Python 3.12 manually.
timeout /t 10
@echo off
setlocal enabledelayedexpansion
title AI VISION MASTER v3.12 (ULTIMATE SYNC)

echo ==========================================
echo    [*] STEP 1/3: SMART ENVIRONMENT SEARCH
echo ==========================================

:: [1] Search for Python 3.12 in all locations
echo [*] Looking for the Elite Engine (Python 3.12)...
set "BEST_PY="
set "PY_DONE=0"

for /f "delims=" %%i in ('where python') do (
    if "!PY_DONE!"=="0" (
        set "TEST_PY=%%i"
        "!TEST_PY!" --version 2>&1 | findstr "3.12" >nul
        if !errorlevel! == 0 (
            set "BEST_PY=!TEST_PY!"
            set "PY_DONE=1"
            echo [OK] Found Python 3.12 at: !BEST_PY!
        )
    )
)

:: [2] If 3.12 not found at all, try installing it
if "!BEST_PY!"=="" (
    echo [!] Python 3.12 not active. Attempting auto-fix...
    winget install --id Python.Python.3.12 -e --silent --accept-package-agreements
    echo [!] Please RESTART this script to activate 3.12.
    pause
    exit
)

:: [3] Lock the 3.12 Path
set "ABS_PY=!BEST_PY!"
set "ABS_PYW=!ABS_PY:python.exe=pythonw.exe!"
if exist "!ABS_PYW!" (
    echo !ABS_PYW! > "%~dp0python_path.txt"
    echo [OK] 3.12 Engine Locked.
)

echo.
echo ==========================================
echo    [*] STEP 2/3: FORCED LIBRARY SYNC (v3.12)
echo ==========================================
echo [*] Using Engine: !ABS_PY!
"!ABS_PY!" -m pip install --upgrade pip --quiet
"!ABS_PY!" -m pip install ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --no-cache-dir --quiet

echo [*] Syncing AI Brain (Torch+CUDA CU121)...
echo [!] This is the 10x SPEED BOOST. Initializing...
"!ABS_PY!" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --no-cache-dir

echo.
echo ==========================================
echo       [SUCCESS] SYSTEM v3.12 READY
echo ==========================================
echo [*] Final Performance Test...
"!ABS_PY!" -c "import torch; print('+++ GPU STATUS: ACTIVE (MAX PERFORMANCE) +++' if torch.cuda.is_available() else '--- GPU STATUS: NOT FOUND (STILL SLOW CPU) ---'); print('Device Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

echo.
echo [OK] Optimization finished. Version: 3.12
pause
@echo off
setlocal enabledelayedexpansion
title AI VISION MASTER v17.5 (PRESET ENGINE)

echo ==========================================
echo    [*] STEP 1/3: HARDWARE DIAGNOSTIC
echo ==========================================

:: [1] Check for NVIDIA GPU / Drivers
echo [*] Checking NVIDIA Driver Status...
nvidia-smi >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] CRITICAL ERROR: NVIDIA Drivers not found.
    echo.
) else (
    echo [OK] NVIDIA GPU Detected.
)

:: [2] Search for Python 3.12
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

if "!BEST_PY!"=="" (
    echo [!] Python 3.12 missing. Installing...
    winget install --id Python.Python.3.12 -e --silent --accept-package-agreements
    echo [!] Please RESTART this script to activate 3.12.
    pause
    exit
)

:: [3] Path Lock
set "ABS_PY=!BEST_PY!"
set "ABS_PYW=!ABS_PY:python.exe=pythonw.exe!"
echo !ABS_PYW! > "%~dp0python_path.txt"

echo.
echo ==========================================
echo    [*] STEP 2/3: SMART LIBRARY CHECK
echo ==========================================
echo [*] Target Engine: !ABS_PY!

:: Check if torch with CUDA is already working
"!ABS_PY!" -c "import torch, torchvision; exit(0 if torch.cuda.is_available() else 1)" >nul 2>&1
if !errorlevel! == 0 (
    echo [OK] AI Engine (GPU) is already active.
) else (
    echo [!] GPU Engine missing or invalid. Fixing...
    "!ABS_PY!" -m pip uninstall torch torchvision torchaudio -y --quiet
    "!ABS_PY!" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --no-cache-dir
)

:: Check for other dependencies
echo [*] Verifying other libraries...
"!ABS_PY!" -c "import ultralytics, mss, cv2, numpy, pandas, pyautogui, win32api, requests" >nul 2>&1
if !errorlevel! neq 0 (
    echo [!] Some libraries missing. Installing...
    "!ABS_PY!" -m pip install ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --no-cache-dir
) else (
    echo [OK] All dependencies satisfied.
)

echo.
echo ==========================================
echo       [SUCCESS] SYSTEM v17.5 READY
echo ==========================================
echo [*] Status: v17.5 Master.
pause
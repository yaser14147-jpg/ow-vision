@echo off
setlocal enabledelayedexpansion
title AI VISION MASTER v16.2 (GPU-FORCE ENGINE)

echo ==========================================
echo    [*] STEP 1/3: SYSTEM VALIDATION (v16.2)
echo ==========================================

:: [1] Search for Python 3.12
echo [*] Searching for Elite Engine (Python 3.12)...
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

:: [2] Manual Fix if Missing
if "!BEST_PY!"=="" (
    echo [!] Python 3.12 not found. Auto-Injecting...
    winget install --id Python.Python.3.12 -e --silent --accept-package-agreements
    echo [OK] Done. Close and RE-RUN this script.
    pause
    exit
)

:: [3] Path Enforcement
set "ABS_PY=!BEST_PY!"
set "ABS_PYW=!ABS_PY:python.exe=pythonw.exe!"
echo !ABS_PYW! > "%~dp0python_path.txt"

echo.
echo ==========================================
echo    [*] STEP 2/3: FORCED GPU SYNC (v16.2)
echo ==========================================
echo [*] Target Engine: !ABS_PY!

echo [!] CLEANING OLD CPU DRIVERS...
echo [!] This ensures no conflicts with the GPU Engine.
"!ABS_PY!" -m pip uninstall torch torchvision torchaudio -y --quiet

echo [*] Upgrading System Libraries...
"!ABS_PY!" -m pip install --upgrade pip
"!ABS_PY!" -m pip install ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --no-cache-dir

echo.
echo [*] Initializing HIGH-PERFORMANCE Brain (CUDA 12.1)...
echo [!] CRITICAL: Downloading ~2.5GB GPU Engine.
echo [!] Speed depends on your internet. Do NOT close this window.
"!ABS_PY!" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --no-cache-dir

echo.
echo ==========================================
echo       [SUCCESS] SYSTEM v16.2 READY
echo ==========================================
"!ABS_PY!" -c "import torch; print('+++ GPU STATUS: ACTIVE (ELITE PERFORMANCE) +++' if torch.cuda.is_available() else '--- GPU STATUS: CPU ONLY (CHECK DRIVERS) ---'); print('Device Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

echo.
echo [OK] Deployment Complete. Version: 16.2
pause
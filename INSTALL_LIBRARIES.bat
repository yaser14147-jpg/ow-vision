@echo off
setlocal enabledelayedexpansion
title AI VISION MASTER v16.3 (GPU-DOMINANCE)

echo ==========================================
echo    [*] STEP 1/3: HARDWARE DIAGNOSTIC
echo ==========================================

:: [1] Check for NVIDIA GPU / Drivers
echo [*] Checking NVIDIA Driver Status...
nvidia-smi >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] CRITICAL ERROR: NVIDIA Drivers not found.
    echo [!] Your GPU is invisible to the AI.
    echo [!] Download/Update Drivers from: https://www.nvidia.com/Download/index.aspx
    echo.
    pause
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
    echo [OK] Done. RE-RUN this script.
    pause
    exit
)

:: [3] Path Lock
set "ABS_PY=!BEST_PY!"
set "ABS_PYW=!ABS_PY:python.exe=pythonw.exe!"
echo !ABS_PYW! > "%~dp0python_path.txt"

echo.
echo ==========================================
echo    [*] STEP 2/3: FORCED GPU OVERRIDE (v16.3)
echo ==========================================
echo [*] Target Engine: !ABS_PY!

echo [!] PURGING OLD DRIVERS... (NUCLEAR CLEAN)
"!ABS_PY!" -m pip uninstall torch torchvision torchaudio -y --quiet

echo [*] Installing Core Components...
"!ABS_PY!" -m pip install ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --no-cache-dir --quiet

echo.
echo [*] Injecting High-Performance GPU Engine (CUDA 12.1)...
echo [!] This is a 2.5GB mandatory download. 
echo [!] If this doesn't fix it, your NVIDIA drivers ARE OUTDATED.
"!ABS_PY!" -m pip install --force-reinstall torch torchvision --index-url https://download.pytorch.org/whl/cu121 --no-cache-dir

echo.
echo ==========================================
echo       [SUCCESS] SYSTEM v16.3 READY
echo ==========================================
echo [*] Verifying GPU Dominance...
"!ABS_PY!" -c "import torch; print('+++ GPU STATUS: ACTIVE (ULTIMATE PERFORMANCE) +++' if torch.cuda.is_available() else '--- GPU STATUS: CPU ONLY (DRIVERS OUTDATED) ---'); print('Device Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

echo.
echo [OK] Deployment v16.3 Complete.
pause
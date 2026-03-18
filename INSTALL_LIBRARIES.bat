@echo off
setlocal enabledelayedexpansion
title AI VISION MASTER v16.0 (SUPREME FORCE)

echo ==========================================
echo    [*] STEP 1/3: SYSTEM VALIDATION (v16.0)
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
echo    [*] STEP 2/3: FORCED SYNC (v16.0)
echo ==========================================
echo [*] Target Engine: !ABS_PY!
"!ABS_PY!" -m pip install --upgrade pip --quiet
"!ABS_PY!" -m pip install ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --no-cache-dir --quiet

echo [*] Initializing GPU AI Brain (CUDA)...
"!ABS_PY!" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --no-cache-dir

echo.
echo ==========================================
echo       [SUCCESS] SYSTEM v16.0 READY
echo ==========================================
"!ABS_PY!" -c "import torch; print('+++ GPU STATUS: ACTIVE +++' if torch.cuda.is_available() else '--- GPU STATUS: CPU ONLY ---'); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

echo.
echo [OK] All components unified at v16.0.
pause
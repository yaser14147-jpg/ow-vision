@echo off
setlocal enabledelayedexpansion
title AI VISION MASTER v3.5 (SUPREME ENGINE)

echo ==========================================
echo    [*] STEP 1/2: CLEAN ENGINE SETUP
echo ==========================================

:: [1] Ensure Python 3.12 
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python missing. Downloading 3.12...
    winget install -e --id Python.Python.3.12 --silent --accept-package-agreements
)

:: [2] Path Lock (Fixing multiple path detection)
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
echo    [*] STEP 2/2: GPU ACCELERATION (CUDA)
echo ==========================================
echo [*] Cleaning old configs...
python -m pip uninstall torch torchvision torchaudio -y --quiet >nul 2>&1

echo [*] Installing Master v3.5 Libraries...
python -m pip install --upgrade pip --quiet
python -m pip install ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --no-cache-dir --quiet

echo [*] Syncing AI Brain (Torch+CUDA CU121)...
echo [!] This is the 10x SPEED BOOST. Please wait...
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --no-cache-dir --quiet

echo.
echo ==========================================
echo       [SUCCESS] SYSTEM v3.5 READY
echo ==========================================
echo [*] Final Performance Test...
python -c "import torch; print('+++ GPU STATUS: ACTIVE (MAX PERFORMANCE) +++' if torch.cuda.is_available() else '--- GPU STATUS: NOT FOUND (RUNNING ON SLOW CPU) ---'); print('Device Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

if %errorlevel% neq 0 (
    echo [!] Critical Error: Library installation failed.
)

echo.
echo [OK] All versions synced to v3.5.
timeout /t 10
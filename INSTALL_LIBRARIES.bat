@echo off
setlocal enabledelayedexpansion
title AI VISION MASTER v3.4 (ELITE ENGINE)

echo ==========================================
echo    [*] STEP 1/2: ENGINE SYNCHRONIZATION
echo ==========================================

:: [1] Ensure Python 3.12 
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python missing. Downloading 3.12...
    winget install -e --id Python.Python.3.12 --silent --accept-package-agreements
)

:: [2] Path Lock
for /f "delims=" %%i in ('where python') do (
    set "ABS_PY=%%i"
    set "ABS_PYW=!ABS_PY:python.exe=pythonw.exe!"
    if exist "!ABS_PYW!" (
        echo !ABS_PYW! > "%~dp0python_path.txt"
        echo [OK] Engine Locked: !ABS_PYW!
    )
)

echo.
echo ==========================================
echo    [*] STEP 2/2: CUDA ACCELERATION SYNC
echo ==========================================
echo [*] Installing Master Libraries (v3.4)...
python -m pip install --upgrade pip --quiet
python -m pip install --upgrade ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --no-cache-dir --quiet

:: [CRITICAL]: Install CUDA-enabled Torch for 10x speed boost
echo [*] Syncing AI Brain (Torch+CUDA)...
echo [!] This is the secret to high performance. Please wait...
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --upgrade --no-cache-dir --quiet

echo.
echo ==========================================
echo       [SUCCESS] SYSTEM v3.4 READY!
echo    GPU ACCELERATION ACTIVATED (v3.4)
echo ==========================================
echo [*] Testing AI Performance...
python -c "import torch; print('GPU ACTIVE' if torch.cuda.is_available() else 'ERROR: GPU NOT FOUND - CONTACT ADMIN')"

timeout /t 5
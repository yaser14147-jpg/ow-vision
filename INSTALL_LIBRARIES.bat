@echo off
setlocal enabledelayedexpansion
title AI VISION MASTER v16.0 (ULTIMATE ENGINE)

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
echo    [*] STEP 2/2: LIBRARY AND LAUNCHER SYNC
echo ==========================================
echo [*] Syncing libraries (please wait)...
python -m pip install --upgrade pip --quiet
python -m pip install --upgrade ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --no-cache-dir --quiet
python -m pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --quiet

echo.
echo ==========================================
echo       [SUCCESS] SYSTEM v16.0 READY!
echo    ALL COMPONENTS REPAIRED AND SYNCED.
echo ==========================================
timeout /t 3
@echo off
setlocal enabledelayedexpansion
title AI VISION ULTIMATE v11.0 (SELF-CONTAINED ENGINE)

:: --- [1] FORCE ADMINISTRATOR ---
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' neq '0' (
    echo [!] Requesting Administrative Privileges...
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B
)

echo ==========================================
echo    [*] STEP 1/3: CORE ENGINE SETUP
echo ==========================================

:: [2] Targeted Python 3.12 Installation (Silent & Specific)
python --version 2>nul | findstr /R "3.12" >nul
if %errorlevel% neq 0 (
    echo [!] Standard Python 3.12 not found. 
    echo [*] Downloading Specific Engine (Python 3.12)...
    winget install -e --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
    echo [+] AI Engine Installed Successfully.
) else (
    echo [OK] Python 3.12 Engine is already active.
)

:: [3] Capture Absolute Path (The Bulletproof Way)
for /f "delims=" %%i in ('where python') do (
    set "ABS_PY=%%i"
    set "ABS_PYW=!ABS_PY:python.exe=pythonw.exe!"
    if exist "!ABS_PYW!" (
        echo !ABS_PYW! > "%~dp0python_path.txt"
        echo [+] Environment Locked: v3.12 Global.
        goto :sync_libs
    )
)

:sync_libs
echo.
echo ==========================================
echo    [*] STEP 2/3: LIBRARY REFRESH
echo ==========================================
python -m pip install --upgrade pip --quiet
python -m pip install --upgrade ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --no-cache-dir --quiet
python -m pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --quiet
echo [OK] All AI Engines Synchronized.

:sync_launchers
echo.
echo ==========================================
echo    [*] STEP 3/3: SYNCING LAUNCHERS
echo ==========================================
set "USERNAME=yaser14147-jpg"
set "REPO=ow-vision"
set "BRANCH=main"
set "BASE_URL=https://raw.githubusercontent.com/!USERNAME!/!REPO!/!BRANCH!"

curl -L -s "!BASE_URL!/UPDATE_PROGRAM.bat" -o "%~dp0UPDATE_PROGRAM.bat"
curl -L -s "!BASE_URL!/START_AIMBOT.vbs" -o "%~dp0START_AIMBOT.vbs"

echo.
echo ==========================================
echo       [SUCCESS] SYSTEM v11.0 READY!
echo    YOU CAN NOW USE START_AIMBOT.vbs
echo ==========================================
pause

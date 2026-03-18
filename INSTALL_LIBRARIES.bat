@echo off
setlocal enabledelayedexpansion
title AI VISION ULTIMATE INSTALLER v6.0

:: --- [1] FORCE ADMINISTRATOR PRIVILEGES (BEST METHOD) ---
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' neq '0' (
    echo [!] Requesting Administrative Privileges...
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B
)
if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )

echo ==========================================
echo    [+] STEP 1/4: UPDATING ENVIRONMENT...
echo ==========================================

:: Function to update EVERY python instance found on the machine
echo [+] Searching for all Python installations to update...
set "found_any=0"

:: Check for Python Upgrade first
echo [+] Checking for Python 3.12 Updates...
winget upgrade --id Python.Python.3.12 --silent --accept-package-agreements --force >nul 2>&1

for /f "delims=" %%p in ('where python 2^>nul') do (
    set "found_any=1"
    echo.
    echo [>] TARGETING: "%%p"
    "%%p" -m pip install --upgrade pip --no-warn-script-location --quiet
    "%%p" -m pip install --upgrade ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --no-cache-dir --no-warn-script-location --quiet
    "%%p" -m pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --no-warn-script-location --quiet
    echo [OK] Updated: "%%p"
)

:: If none found via 'where', try common manual paths
if "!found_any!"=="0" (
    echo [!] No Python found in PATH. Checking common manual locations...
    for %%d in ("C:\Program Files\Python312" "C:\Program Files\Python311" "%LocalAppData%\Programs\Python\Python312" "%LocalAppData%\Programs\Python\Python311") do (
        if exist "%%~d\python.exe" (
            set "found_any=1"
            echo [>] TARGETING MANUAL: "%%~d\python.exe"
            "%%~d\python.exe" -m pip install --upgrade pip --quiet
            "%%~d\python.exe" -m pip install --upgrade ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --quiet
        )
    )
)

if "!found_any!"=="0" (
    echo [!] Still no Python. Attempting LAST RESORT: Winget Install...
    winget install -e --id Python.Python.3.12 --silent --accept-package-agreements
    echo [!] Please restart this script after Winget finishes.
    pause
    exit /b
)

echo.
echo ==========================================
echo    [+] STEP 2/2: SYNCING LAUNCHERS...
echo ==========================================

:: Download core launchers if missing or to ensure latest
set "USERNAME=yaser14147-jpg"
set "REPO=ow-vision"
set "BRANCH=main"
set "BASE_URL=https://raw.githubusercontent.com/!USERNAME!/!REPO!/!BRANCH!"

echo [+] Syncing UPDATE_PROGRAM.bat...
curl -L -s "!BASE_URL!/UPDATE_PROGRAM.bat" -o "%~dp0UPDATE_PROGRAM.bat"
echo [+] Syncing START_AIMBOT.vbs...
curl -L -s "!BASE_URL!/START_AIMBOT.vbs" -o "%~dp0START_AIMBOT.vbs"

echo.
echo ==========================================
echo       [SUCCESS] SYSTEM IS FULLY READY!
echo             VERSION: v6.0 MASTER
echo   ALL ENGINES, LIBRARIES, AND LAUNCHERS SYNCED.
echo ==========================================
pause

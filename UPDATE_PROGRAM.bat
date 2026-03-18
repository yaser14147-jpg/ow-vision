@echo off
setlocal enabledelayedexpansion
title AI VISION TURBO SYNC v6.5

echo ==========================================
echo    [*] Searching for System Updates...
echo ==========================================

:: 1. Force update the updater script first (to ensure clean UI)
set "USERNAME=yaser14147-jpg"
set "REPO=ow-vision"
set "BRANCH=main"
set "UPDATER_URL=https://raw.githubusercontent.com/!USERNAME!/!REPO!/!BRANCH!/ow-vision/scripts/updater.py"
set "LOCAL_UPDATER=%~dp0ow-vision\scripts\updater.py"

echo [+] Refreshing Sync Engine...
:: Use curl with cache busting
set /a "ts=%time:~0,2%%time:~3,2%%time:~6,2%"
curl -L -s "!UPDATER_URL!?t=!ts!" -o "!LOCAL_UPDATER!"

:: 2. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] ERROR: Python is not installed.
    echo [!] Please run INSTALL_LIBRARIES.bat first!
    pause
    exit
)

:: 3. Run the now-updated updater
python "!LOCAL_UPDATER!"

echo.
echo ==========================================
echo [OK] Synchronization Complete.
echo ==========================================
timeout /t 2

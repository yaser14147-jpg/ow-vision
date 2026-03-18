@echo off
setlocal enabledelayedexpansion
title AI VISION MASTER UPDATE v10.0 (ULTIMATE REPAIR)

echo ==========================================
echo    [*] Searching for System Updates...
echo ==========================================

set "USERNAME=yaser14147-jpg"
set "REPO=ow-vision"
set "BRANCH=main"
set "UPDATER_URL=https://raw.githubusercontent.com/%USERNAME%/%REPO%/%BRANCH%/ow-vision/scripts/updater.py"
set "LOCAL_UPDATER=%~dp0ow-vision\scripts\updater.py"

echo [+] Refreshing Sync Engine...
:: Cache bust with milliseconds if possible
set /a "ts=%time:~0,2%%time:~3,2%%time:~6,2%"
curl -L -s "!UPDATER_URL!?t=!ts!" -o "!LOCAL_UPDATER!"

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python missing. Run INSTALL_LIBRARIES.bat first.
    pause
    exit
)

python "!LOCAL_UPDATER!"

echo.
echo ==========================================
echo [OK] Synchronization Complete (v10.0)
echo ==========================================
pause

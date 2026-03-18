@echo off
setlocal enabledelayedexpansion
title AI VISION MASTER UPDATE v2.904 (SUPREME SYNC)

echo ==========================================
echo    [*] SEARCHING FOR SYSTEM UPDATES...
echo ==========================================

set "USERNAME=yaser14147-jpg"
set "REPO=ow-vision"
set "BRANCH=main"
set "UPDATER_URL=https://raw.githubusercontent.com/%USERNAME%/%REPO%/%BRANCH%/ow-vision/scripts/updater.py"
set "LOCAL_UPDATER=%~dp0ow-vision\scripts\updater.py"

:: [1] Ensure requests is installed (The #1 reason for updater failure)
python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo [+] Preparing first-time sync engine...
    python -m pip install requests --quiet
)

echo [+] Refreshing Sync Engine (v2.904)...
:: Better cache bust using %RANDOM% to avoid space-in-time errors
curl -L -s "!UPDATER_URL!?t=%RANDOM%" -o "!LOCAL_UPDATER!"

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python missing. Run INSTALL_LIBRARIES.bat first.
    pause
    exit
)

:: [2] Execute Master Updater
python "!LOCAL_UPDATER!"

echo.
echo ==========================================
echo [OK] Synchronization Complete (v2.904)
echo ==========================================
pause

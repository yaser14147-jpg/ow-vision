@echo off
setlocal enabledelayedexpansion
title AI VISION MASTER UPDATE v16.0 (SUPREME FORCE)

echo ==========================================
echo    [*] SEARCHING FOR SYSTEM UPDATES...
echo ==========================================

set "USERNAME=yaser14147-jpg"
set "REPO=ow-vision"
set "BRANCH=main"
set "UPDATER_URL=https://raw.githubusercontent.com/%USERNAME%/%REPO%/%BRANCH%/ow-vision/scripts/updater.py"
set "LOCAL_UPDATER=%~dp0ow-vision\scripts\updater.py"

:: [1] Ensure requests is installed
python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo [+] Preparing first-time sync engine...
    python -m pip install requests --quiet
)

echo [+] Refreshing Sync Engine (v16.0 FORCE)...
:: AGGRESSIVE CACHE BUSTING
set "nonce=%date:~-4%%date:~4,2%%date:~7,2%%time:~0,2%%time:~3,2%%time:~6,2%%time:~9,2%"
set "nonce=%nonce: =0%"
curl -L -s "!UPDATER_URL!?nocache=!nonce!" -o "!LOCAL_UPDATER!"

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
echo [OK] Synchronization Complete (v16.0)
echo ==========================================
pause

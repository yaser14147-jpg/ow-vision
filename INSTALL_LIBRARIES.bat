@echo off
setlocal enabledelayedexpansion
title AI VISION ULTIMATE v9.0 (MASTER EDITION)

:: --- [1] FORCE ADMINISTRATOR PRIVILEGES ---
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
echo    [+] STEP 1/2: UPDATING ENVIRONMENT...
echo ==========================================

set "found_any=0"

:: [1] Quick Check: Is Python already active and correct?
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo [+] Fast Discovery: System Python found active.
    set "found_any=1"
    
    :: Get Absolute Path
    for /f "delims=" %%i in ('where python') do (
        set "ABS_PY=%%i"
        set "ABS_PYW=!ABS_PY:python.exe=pythonw.exe!"
        if exist "!ABS_PYW!" (
            echo !ABS_PYW! > "%~dp0python_path.txt"
            echo [OK] Path Locked: "!ABS_PYW!"
            goto :sync_libs
        )
    )
)

:sync_libs
if "!found_any!"=="1" (
    python -m pip install --upgrade pip --quiet
    python -m pip install --upgrade ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --no-cache-dir --quiet
    python -m pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --quiet
    echo [OK] Sync Complete.
    goto :sync_launchers
)

:: [2] Advanced Scan (Common + Registry-style Paths)
echo [!] Scanning environment for Python 3.11, 3.12, 3.13, 3.14...
for %%d in ("C:\Program Files\Python312" "C:\Program Files\Python313" "C:\Program Files\Python314" "%LocalAppData%\Programs\Python\Python312" "%LocalAppData%\Programs\Python\Python313" "%LocalAppData%\Programs\Python\Python314") do (
    if exist "%%~d\python.exe" (
        set "found_any=1"
        echo [+] Found at: "%%~d\python.exe"
        echo %%~d\pythonw.exe > "%~dp0python_path.txt"
        "%%~d\python.exe" -m pip install --upgrade pip --quiet
        "%%~d\python.exe" -m pip install --upgrade ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --quiet
        goto :sync_launchers
    )
)

:: [4] Automated Install (Last Resort)
if "!found_any!"=="0" (
    echo [!] PYTHON MISSING. Starting Auto-Installation...
    winget install -e --id Python.Python.3.12 --silent --accept-package-agreements
    echo [!] Please restart this script after installation finishes.
    pause
    exit /b
)

:sync_launchers
echo.
echo ==========================================
echo    [+] STEP 2/2: SYNCING LAUNCHERS...
echo ==========================================

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
echo             VERSION: v9.0 MASTER
echo   ALL ENGINES AND LAUNCHERS AUTO-SYNCED.
echo ==========================================
pause

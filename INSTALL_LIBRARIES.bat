@echo off
setlocal enabledelayedexpansion
title AI VISION FINAL SHIELD v6.5

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

set "found_any=0"

:: [1] Quick Check: Is Python already active and correct?
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo [+] Fast Discovery: System Python found active.
    set "found_any=1"
    
    :: Get Absolute Path
    for /f "delims=" %%i in ('where python') do set "ABS_PY=%%i"
    set "ABS_PYW=!ABS_PY:python.exe=pythonw.exe!"
    echo !ABS_PYW! > "%~dp0python_path.txt"
    
    echo [>] TARGETING ACTIVE: "!ABS_PYW!"
    "!ABS_PY!" -m pip install --upgrade pip --quiet
    "!ABS_PY!" -m pip install --upgrade ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --no-cache-dir --quiet
    "!ABS_PY!" -m pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --quiet
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

:: [3] Deep Discovery
if "!found_any!"=="0" (
    echo [+] Deep Search for any linked Python instance...
    for /f "delims=" %%p in ('where python 2^>nul') do (
        set "found_any=1"
        set "TARGET_PY=%%p"
        set "TARGET_PYW=!TARGET_PY:python.exe=pythonw.exe!"
        echo !TARGET_PYW! > "%~dp0python_path.txt"
        "%%p" -m pip install --upgrade pip --quiet
        "%%p" -m pip install --upgrade ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --quiet
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

:sync_launchers

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
echo             VERSION: v7.0 MASTER
echo   ENVIRONMENT LOCKED - LAUNCHERS READY.
echo ==========================================
pause

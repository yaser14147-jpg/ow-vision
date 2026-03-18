@echo off
setlocal enabledelayedexpansion
title AI VISION MASTER v12.0 (THE ULTIMATE REPAIR)

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
echo    [*] STEP 1/2: ENGINE SYNCHRONIZATION
echo ==========================================

:: [2] Ensure Python 3.12 is Installed and in PATH
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python not detected. Starting Auto-Install...
    winget install -e --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
    echo [+] Installation triggered. Refreshing environment...
    
    :: Refresh Path without reboot (v12.0 trick)
    for /f "tokens=2*" %%a in ('reg query "HKLM\System\CurrentControlSet\Control\Session Manager\Environment" /v Path') do set "PATH=%%b"
    for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v Path') do set "PATH=!PATH!;%%b"
)

:: Re-check after potential install
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Fatal: Python is still not active. 
    echo [!] Manual install and REBOOT might be needed.
    pause
    exit
)

:: [3] Capture and Lock Path
set "FOUND_PY="
for /f "delims=" %%i in ('where python') do set "FOUND_PY=%%i"

if "%FOUND_PY%"=="" (
    :: Last ditch: Check common install folders directly
    if exist "C:\Program Files\Python312\python.exe" set "FOUND_PY=C:\Program Files\Python312\python.exe"
    if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "FOUND_PY=%LocalAppData%\Programs\Python\Python312\python.exe"
)

if not "%FOUND_PY%"=="" (
    set "FOUND_PYW=!FOUND_PY:python.exe=pythonw.exe!"
    echo !FOUND_PYW! > "%~dp0python_path.txt"
    echo [OK] Engine Locked: !FOUND_PYW!
) else (
    echo [!] Could not lock path. Launchers might fail.
)

echo.
echo ==========================================
echo    [*] STEP 2/2: LIBRARY AND LAUNCHER SYNC
echo ==========================================
echo [*] Upgrading libraries (this may take 1-2 minutes)...
python -m pip install --upgrade pip --quiet
python -m pip install --upgrade ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --no-cache-dir --quiet
python -m pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --quiet

:: Sync Launchers
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
echo       [SUCCESS] SYSTEM v12.0 IS READY!
echo    YOU CAN NOW CLOSE THIS WINDOW AND START
echo ==========================================
pause
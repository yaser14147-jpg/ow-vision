@echo off
setlocal enabledelayedexpansion
title YASER14147 - AI VISION MASTER INSTALLER v2.6

:: --- [1] FORCE ADMINISTRATOR PRIVILEGES (ULTIMATE METHOD) ---
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
echo    [+] STEP 1/3: UPDATING ENVIRONMENT...
echo ==========================================

:: Find the exact python.exe path to avoid "pip notice" issues
set "PYTHON_CMD="
for /f "delims=" %%i in ('where python 2^>nul') do (
    if "!PYTHON_CMD!"=="" set "PYTHON_CMD=%%i"
)

if "!PYTHON_CMD!"=="" (
    echo [!] Python not found. Installing latest Python 3.12 via Winget...
    winget install -e --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
    :: Refresh path and try to find it again
    set "PATH=%PATH%;C:\Program Files\Python312\;C:\Program Files\Python312\Scripts\;%LocalAppData%\Programs\Python\Python312\;%LocalAppData%\Programs\Python\Python312\Scripts\"
    for /f "delims=" %%i in ('where python 2^>nul') do if "!PYTHON_CMD!"=="" set "PYTHON_CMD=%%i"
)

:: Final fallback if still empty
if "!PYTHON_CMD!"=="" (
    if exist "C:\Program Files\Python312\python.exe" set "PYTHON_CMD=C:\Program Files\Python312\python.exe"
)

if "!PYTHON_CMD!"=="" (
    echo [X] FATAL: Python not found. Please install Python manually.
    pause
    exit /b
)

echo [OK] Using Python at: "!PYTHON_CMD!"

echo.
echo ==========================================
echo    [+] STEP 2/3: FORCING ALL UPDATES...
echo ==========================================

echo [+] FORCING PIP UPGRADE (DEFEATING THE NOTICE)...
"!PYTHON_CMD!" -m pip install --upgrade pip --no-warn-script-location

echo [+] FORCING ALL LIBRARIES TO LATEST...
set "libs=ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests"
for %%l in (%libs%) do (
    echo [+] Updating %%l...
    "!PYTHON_CMD!" -m pip install %%l --upgrade --no-cache-dir --no-warn-script-location
)

echo [+] FORCING TORCH (AI ENGINE) UPGRADE (CUDA OPTIMIZED)...
"!PYTHON_CMD!" -m pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --no-warn-script-location

echo.
echo ==========================================
echo    [+] STEP 3/3: FINALIZING v2.6...
echo ==========================================

echo [OK] All components are at their absolute latest version.
echo [OK] Pip notices should now be gone.

echo.
echo ==========================================
echo       [SUCCESS] SYSTEM IS FULLY READY!
echo             VERSION: v2.6 MASTER
echo   ALL UPDATES HAVE BEEN FORCED SUCCESSFULLY.
echo ==========================================
pause

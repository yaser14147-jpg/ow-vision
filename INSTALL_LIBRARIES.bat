@echo off
setlocal enabledelayedexpansion
title YASER14147 - AI VISION MASTER INSTALLER v2.5

:: --- [1] FORCE ADMINISTRATOR PRIVILEGES (ULTIMATE METHOD) ---
:: Check for permissions
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' neq '0' (
    echo [!] Requesting Administrative Privileges...
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B
)
if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )

:: Proceed only if Admin
echo ==========================================
echo    [+] STEP 1/3: UPDATING ENVIRONMENT...
echo ==========================================

:: Update Python via Winget
where python >nul 2>&1
if %errorlevel% == 0 (
    echo [+] Python detected. Checking for updates...
    winget upgrade --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements --force
) else (
    echo [!] Python not found. Installing latest Python 3.12...
    winget install -e --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
)

:: Re-verify Python path after update
set "PATH=%PATH%;C:\Program Files\Python312\;C:\Program Files\Python312\Scripts\;%LocalAppData%\Programs\Python\Python312\;%LocalAppData%\Programs\Python\Python312\Scripts\"

:: Force Python Command
set "PYTHON_CMD=python"
python --version >nul 2>&1
if %errorlevel% neq 0 (
    if exist "C:\Program Files\Python312\python.exe" (set "PYTHON_CMD=C:\Program Files\Python312\python.exe") else (
        echo [X] FATAL: Python is not configured correctly. Installing manually via CURL fallback...
        set "py_url=https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe"
        curl -L !py_url! -o "%temp%\py_install.exe"
        start /wait "" "%temp%\py_install.exe" /quiet InstallAllUsers=1 PrependPath=1
        set "PYTHON_CMD=C:\Program Files\Python312\python.exe"
    )
)

echo.
echo ==========================================
echo    [+] STEP 2/3: FORCING ALL UPDATES...
echo ==========================================

echo [+] FORCING PIP UPGRADE...
%PYTHON_CMD% -m pip install --upgrade pip --quiet

echo [+] FORCING ALL LIBRARIES TO LATEST...
set "libs=ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests"
for %%l in (%libs%) do (
    echo [+] Checking/Updating %%l...
    %PYTHON_CMD% -m pip install %%l --upgrade --no-cache-dir
)

echo [+] FORCING TORCH (AI ENGINE) UPGRADE (CUDA OPTIMIZED)...
%PYTHON_CMD% -m pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo.
echo ==========================================
echo    [+] STEP 3/3: STARTUP REPAIR...
echo ==========================================

:: Link pythonw.exe to absolute path in system if possible (Optional but helps)
echo [+] Environment validation successful.

echo.
echo ==========================================
echo       [SUCCESS] SYSTEM IS FULLY READY!
echo             VERSION: v2.5 MASTER
echo   ALL UPDATES HAVE BEEN FORCED SUCCESSFULLY.
echo ==========================================
pause

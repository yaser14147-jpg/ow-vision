@echo off
setlocal enabledelayedexpansion
title YASER14147 - AI VISION ULTIMATE INSTALLER v2.4

:: --- [1] FORCE ADMINISTRATOR PRIVILEGES ---
:: This block will restart the script as Admin if not already elevated
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] Requesting Admin privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo ==========================================
echo    [+] STEP 1/3: PREPARING ENVIRONMENT...
echo ==========================================

:: Function to check if python is working
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python not found. Installing via Winget...
    winget install -e --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
    
    if %errorlevel% neq 0 (
        echo [!] Winget failed or not available. Using Manual CURL...
        set "py_url=https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe"
        set "py_exe=%temp%\python_installer.exe"
        curl -L !py_url! -o "!py_exe!"
        if exist "!py_exe!" (
            echo [+] Installing Python Silently...
            start /wait "" "!py_exe!" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
            del "!py_exe!"
        )
    )
    :: Force update PATH for current session
    set "PATH=%PATH%;C:\Program Files\Python312\;C:\Program Files\Python312\Scripts\;%LocalAppData%\Programs\Python\Python312\;%LocalAppData%\Programs\Python\Python312\Scripts\"
)

:: Re-verify Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python installation failed or not found in PATH.
    echo [!] Trying to find python.exe manually...
    if exist "C:\Program Files\Python312\python.exe" (set "PYTHON_CMD=C:\Program Files\Python312\python.exe") else (
        echo [X] FATAL ERROR: Please install Python 3.12 manually from python.org
        pause
        exit /b
    )
) else (
    set "PYTHON_CMD=python"
)

echo.
echo ==========================================
echo    [+] STEP 2/3: FORCING UPDATES...
echo ==========================================

echo [+] Upgrading PIP to latest version...
%PYTHON_CMD% -m pip install --upgrade pip --quiet

echo [+] Installing/Upgrading all libraries...
:: Ensuring all libs are the absolute latest
set "libs=ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests"
%PYTHON_CMD% -m pip install --upgrade %libs%

echo [+] Optimizing AI Engine (PyTorch with CUDA)...
%PYTHON_CMD% -m pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo.
echo ==========================================
echo    [+] STEP 3/3: FINAL VERIFICATION...
echo ==========================================

echo [+] Detecting pythonw.exe path...
for /f "delims=" %%i in ('where pythonw 2^>nul') do set "PYW_PATH=%%i"
if "%PYW_PATH%"=="" (
    :: Fallback for manual install
    if exist "C:\Program Files\Python312\pythonw.exe" (set "PYW_PATH=C:\Program Files\Python312\pythonw.exe")
)

if not "%PYW_PATH%"=="" (
    echo [OK] Python Executive found: %PYW_PATH%
) else (
    echo [!] WARNING: pythonw.exe not found in PATH. START_AIMBOT.vbs might fail.
)

echo.
echo ==========================================
echo       [SUCCESS] SYSTEM IS FULLY READY!
echo             VERSION: v2.4
echo   Now try running START_AIMBOT.vbs
echo ==========================================
pause

@echo off
setlocal enabledelayedexpansion
title AI VISION MASTER v14.0 (ENGINE ONLY)

:: --- [1] FORCE ADMINISTRATOR ---
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' neq '0' (
    echo [!] Requesting Administrative Privileges...
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B
)

echo ==========================================
echo    [*] STEP 1/2: PYTHON ENGINE SETUP
echo ==========================================

:: [2] Targeted Python 3.12 Check/Install
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python missing. Downloading 3.12...
    winget install -e --id Python.Python.3.12 --silent --accept-package-agreements
)

:: Re-verify
python --version >nul 2>&1
if %errorlevel% neq 0 ( echo [!] Restart needed after install. & pause & exit )

:: [3] Record Path (For Launcher Use)
for /f "delims=" %%i in ('where python') do (
    set "ABS_PY=%%i"
    set "ABS_PYW=!ABS_PY:python.exe=pythonw.exe!"
    if exist "!ABS_PYW!" (
        echo !ABS_PYW! > "%~dp0python_path.txt"
        echo [OK] Engine Locked: !ABS_PYW!
    )
)

echo.
echo ==========================================
echo    [*] STEP 2/2: LIBRARY SYNCHRONIZATION
echo ==========================================
echo [*] Installing Master AI Libraries...
python -m pip install --upgrade pip --quiet
python -m pip install --upgrade ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests --no-cache-dir --quiet
python -m pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --quiet

echo.
echo ==========================================
echo       [SUCCESS] ENGINE v14.0 READY!
echo    (ALL LAUNCHERS MANAGED BY UPDATER)
echo ==========================================
timeout /t 3
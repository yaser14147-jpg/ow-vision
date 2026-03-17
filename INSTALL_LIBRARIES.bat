@echo off
title OVERWATCH-AI INSTALLER
echo ==========================================
echo    [+] 1/3: Checking Python Installation...
echo ==========================================
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] ERROR: Python is not installed. 
    echo Please install Python 3.10 or newer from python.org
    pause
    exit
)

echo [OK] Python is ready.
echo.
echo ==========================================
echo    [+] 2/3: Upgrading Pip Manager...
echo ==========================================
python -m pip install --upgrade pip

echo.
echo ==========================================
echo    [+] 3/3: Installing Aimbot Libraries...
echo    (This may take a few minutes...)
echo ==========================================
python -m pip install ultralytics mss opencv-python numpy pyautogui pywin32 dxcam torch torchvision torchaudio requests --extra-index-url https://download.pytorch.org/whl/cu121

echo.
echo ==========================================
echo       [SUCCESS] SETUP COMPLETED!
echo   You can now run START_AIMBOT.vbs
echo ==========================================
pause

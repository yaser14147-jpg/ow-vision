@echo off
title YASER14147 - SMART INSTALLER
echo ==========================================
echo    [+] 1/3: CHECKING PYTHON ENVIRONMENT...
echo ==========================================

:: فحص هل بايثون موجود؟
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] PYTHON NOT FOUND! 
    echo [!] Attempting to download and install Python automatically...
    
    :: تحميل مثبت بايثون الصامت (نسخة 3.12 مستقرة)
    set "py_url=https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe"
    set "py_exe=%temp%\python_installer.exe"
    
    echo [+] Downloading Python installer via curl...
    curl -L %py_url% -o %py_exe%
    
    if exist "%py_exe%" (
        echo [+] Installing Python silently... Please wait...
        echo [+] (This will add Python to your system PATH automatically)
        start /wait "" "%py_exe%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
        echo [OK] Python installation finished!
        
        :: محاولة تحديث الـ PATH للجلسة الحالية
        set "PATH=%PATH%;C:\Program Files\Python312\;C:\Program Files\Python312\Scripts\"
    ) else (
        echo [X] FAILED TO DOWNLOAD PYTHON. Please install it manually from python.org
        pause
        exit
    )
) else (
    echo [OK] Python is already installed.
)

echo.
echo ==========================================
echo    [+] 2/3: REPAIRING & UPGRADING PIP...
echo ==========================================
python -m ensurepip --default-pip >nul 2>&1
python -m pip install --upgrade pip

echo.
echo ==========================================
echo    [+] 3/3: INSTALLING MISSING LIBRARIES...
echo ==========================================
:: قائمة المكتبات المطلوبة
set "libs=ultralytics mss opencv-python numpy pyautogui pywin32 dxcam torch torchvision torchaudio requests"

echo [+] Checking each library and installing if missing...
python -m pip install %libs% --extra-index-url https://download.pytorch.org/whl/cu121

echo.
echo ==========================================
echo       [SUCCESS] SYSTEM IS FULLY READY!
echo   You can now run START_AIMBOT.vbs
echo ==========================================
pause

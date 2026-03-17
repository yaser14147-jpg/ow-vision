@echo off
setlocal enabledelayedexpansion
title YASER14147 - AI VISION SMART INSTALLER v2.3

:: Check for Administrative Privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [+] Running with Administrator privileges.
) else (
    echo [!] Please run this script as Administrator for a successful installation.
    pause
    exit /b
)

echo ==========================================
echo    [+] STEP 1/3: CHECKING PYTHON...
echo ==========================================

:: Function to check if python is in PATH
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python not found in PATH.
    echo [!] Attempting to install Python via winget...
    
    winget install -e --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
    
    if %errorlevel% neq 0 (
        echo [!] Winget failed. Downloading Python installer manually...
        set "py_url=https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe"
        set "py_exe=%temp%\python_installer.exe"
        curl -L !py_url! -o "!py_exe!"
        
        if exist "!py_exe!" (
            echo [+] Installing Python... This may take a few minutes.
            start /wait "" "!py_exe!" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
            del "!py_exe!"
            echo [OK] Python installation finished.
            
            :: Refresh PATH for the current session
            set "PATH=%PATH%;C:\Program Files\Python312\;C:\Program Files\Python312\Scripts\;%LocalAppData%\Programs\Python\Python312\;%LocalAppData%\Programs\Python\Python312\Scripts\"
        ) else (
            echo [X] FAILED TO DOWNLOAD PYTHON. Please install it manually from python.org
            pause
            exit /b
        )
    )
) else (
    echo [OK] Python is already installed.
)

:: Re-verify python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python is installed but not responding to 'python' command.
    echo [!] Trying 'py' command...
    py --version >nul 2>&1
    if %errorlevel% == 0 (
        set "PYTHON_CMD=py"
    ) else (
        echo [X] Could not find a working Python command. Please restart your PC and try again.
        pause
        exit /b
    )
) else (
    set "PYTHON_CMD=python"
)

echo.
echo ==========================================
echo    [+] STEP 2/3: CHECKING LIBRARIES...
echo ==========================================

echo [+] Updating PIP...
%PYTHON_CMD% -m pip install --upgrade pip

echo [+] Installing Required Libraries (This may take time, please wait)...
:: List: ultralytics (AI), mss (Screenshot), opencv (Vision), numpy (Math), pandas (Data), pyautogui (Mouse/Control), pywin32 (Windows API), torch/torchvision (AI Engine)
set "libs=ultralytics mss opencv-python numpy pandas pyautogui pywin32 requests"

%PYTHON_CMD% -m pip install %libs%

:: Special install for PyTorch with CUDA support for better FPS
echo [+] Optimizing AI Performance (Installing Torch with CUDA support)...
%PYTHON_CMD% -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo.
echo ==========================================
echo    [+] STEP 3/3: FINALIZING...
echo ==========================================

echo [+] Verifying installation...
for %%l in (%libs%) do (
    %PYTHON_CMD% -c "import %%l" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [OK] %%l is ready.
    ) else (
        echo [!] %%l failed to load. Attempting re-install...
        %PYTHON_CMD% -m pip install %%l
    )
)

echo.
echo ==========================================
echo       [SUCCESS] SYSTEM IS FULLY READY!
echo             VERSION: v2.3
echo   You can now run START_AIMBOT.vbs
echo ==========================================
pause

@echo off
title OVERWATCH-AI SMART UPDATER
echo ==========================================
echo    [*] Checking System Environment...
echo ==========================================

:: 1. فحص بايثون أولاً قبل أي شيء
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python is missing! Redirecting to Installer...
    timeout /t 2 >nul
    call "INSTALL_LIBRARIES.bat"
    
    :: فحص مرة أخرى بعد محاولة التثبيت
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [X] Critical Error: Python could not be installed. 
        pause
        exit
    )
)

:: 2. إذا بايثون موجود، نبدأ التحديث الآن
echo [+] Python found. Checking for updates...
echo ==========================================
python "%~dp0ow-vision\scripts\updater.py"
echo ==========================================
echo.
echo Process Complete.
pause

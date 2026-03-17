@echo off
title OVERWATCH-AI UPDATER
echo ==========================================
echo    [*] Checking for Latest Version...
echo ==========================================

:: فحص سريع لوجود بايثون فقط
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] ERROR: Python is not installed.
    echo [!] Please run INSTALL_LIBRARIES.bat first!
    pause
    exit
)

:: تشغيل كود التحديث
python "%~dp0ow-vision\scripts\updater.py"

echo ==========================================
echo.
echo Process Complete.
pause

@echo off
title Smart Helmet AI - Debug Mode
echo =========================================
echo   Smart Helmet AI : REPAIR & START
echo =========================================
echo.

echo [1/4] Cleaning up existing sessions...
taskkill /F /IM python.exe /T 2>nul
echo [2/4] Checking Python...
python --version
if %errorlevel% neq 0 (
    echo [CRITICAL ERROR] Python is NOT installed or not not valid.
    echo Please install Python 3.10+ from https://python.org
    pause
    exit
)

echo.
echo [2/3] Force Installing Dependencies...
echo Please wait, this may take a minute...
python -m pip install --upgrade pip
python -m pip install flask opencv-python ultralytics numpy
if %errorlevel% neq 0 (
    echo [WARNING] Some libraries might have failed to install.
    echo Attempting to run anyway...
)

echo.
echo =========================================
echo   STARTING SERVER ON PORT 5001
echo   Please wait for "Running on http://..."
echo =========================================
echo.
echo [3/3] Launching App...
start http://127.0.0.1:5001
python backend/app.py

echo.
echo [SERVER STOPPED]
echo If you see an error above, please take a screenshot.
pause

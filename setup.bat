@echo off
REM Ticketmaster Monitor Setup for Windows (Selenium version)

echo ========================================
echo Ticketmaster Monitor Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed
echo.
echo ========================================
echo Setup complete!
echo.
echo NOTE: You also need Chrome and ChromeDriver installed.
echo Download ChromeDriver from: https://chromedriver.chromium.org/
echo.
echo To start monitoring, run:
echo   python ticketmaster_selenium.py
echo.
echo The script will run in this window and show status updates.
echo Press Ctrl+C to stop monitoring.
echo ========================================
echo.
pause

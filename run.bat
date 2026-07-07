@echo off
SETLOCAL EnableDelayedExpansion

echo ==========================================
echo    KL Project - Starter Script
echo ==========================================

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

:: Define virtual environment directory
set VENV_DIR=.venv

:: Create virtual environment if it doesn't exist
if not exist "%VENV_DIR%" (
    echo [INFO] Creating virtual environment...
    python -m venv %VENV_DIR%
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate virtual environment and install dependencies
echo [INFO] Activating virtual environment and checking dependencies...
call %VENV_DIR%\Scripts\activate
python -m pip install --upgrade pip >nul
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

:: Start the Flask server in a new window
echo [INFO] Starting Flask server...
start "KL Project - Flask Server" cmd /k "call %VENV_DIR%\Scripts\activate && python app.py"

:: Wait a moment for the server to initialize
timeout /t 3 /nobreak >nul

:: Open the browser
echo [INFO] Opening the application in your browser...
start http://127.0.0.1:5000

echo ==========================================
echo    Project is running!
echo    Server window is open in background.
echo ==========================================
pause

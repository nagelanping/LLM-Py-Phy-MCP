@echo off
REM ============================================
REM LLM-Py-Phy-MCP Windows Setup Script
REM ============================================

echo ========================================
echo LLM-Py-Phy-MCP Windows Setup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or later from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Python found:
python --version
echo.

REM Create virtual environment
echo [2/3] Creating virtual environment...
if exist "venv\" (
    echo Virtual environment already exists. Removing old one...
    rmdir /s /q venv
)

python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created successfully.
echo.

REM Activate virtual environment and install dependencies
echo [3/3] Installing dependencies...
call venv\Scripts\activate.bat

python -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERROR] Failed to upgrade pip
    pause
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Virtual environment: venv\Scripts\python.exe
echo.
echo Next steps:
echo 1. Update config.json with correct paths
echo 2. Add the configuration to your MCP client
echo 3. Restart your MCP client
echo.
pause

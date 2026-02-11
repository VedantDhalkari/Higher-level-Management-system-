@echo off
title Boutique Management System Launcher
color 0A

echo ===================================================
echo      BOUTIQUE MANAGEMENT SYSTEM - LAUNCHER
echo ===================================================
echo.

echo [1/4] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.10+ from python.org
    pause
    exit /b
)

if not exist "venv" (
    echo [2/4] Creating virtual environment "venv"...
    python -m venv venv
) else (
    echo [2/4] Using existing virtual environment...
)

echo Activating virtual environment...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Warning: venv activation script not found. Using system python.
)

echo.
echo [3/4] Checking dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    color 0C
    echo Error installing dependencies!
    pause
    exit /b
)

echo.
echo [4/4] Launching application...
echo.
python main.py

if %errorlevel% neq 0 (
    color 0C
    echo.
    echo Application exited with error code %errorlevel%
    echo Please check the error message above.
    pause
) else (
    echo Application closed successfully.
)

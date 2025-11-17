@echo off
REM Quick Start Script for RTL-SDR Detection System on Windows
REM Run this file by double-clicking or from Command Prompt

REM Change to the directory where this script is located
cd /d "%~dp0"

echo ========================================
echo RTL-SDR Detection System - Quick Start
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Create necessary directories
if not exist "data" mkdir data
if not exist "models" mkdir models
if not exist "backups" mkdir backups

echo [OK] Directories created
echo.

REM Check if .env exists
if not exist ".env" (
    echo [INFO] Creating .env file from template...
    copy .env.example .env
    echo [INFO] Please edit .env file to configure your settings
)

echo.
echo Building Docker images...
echo This may take a few minutes on first run...
echo.

docker-compose build

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo [OK] Build complete!
echo.
echo Starting containers...
echo.

docker-compose up -d

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start containers!
    pause
    exit /b 1
)

echo.
echo ========================================
echo RTL-SDR Detection System is running!
echo ========================================
echo.
echo Web Dashboard: http://localhost:5000
echo.
echo Important: To use your RTL-SDR device, you need to attach it to WSL:
echo   1. Open PowerShell as Administrator
echo   2. Run: usbipd wsl list
echo   3. Find your RTL-SDR device (usually "Realtek RTL2838")
echo   4. Run: usbipd wsl attach --busid [BUSID] --auto-attach
echo.
echo Useful commands:
echo   - View logs:      docker-compose logs -f
echo   - Stop system:    docker-compose down
echo   - Restart system: docker-compose restart
echo.
echo For more options, use: docker-manage.ps1 [command]
echo.

REM Try to open browser
timeout /t 3 /nobreak >nul
start http://localhost:5000

pause

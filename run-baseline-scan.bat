@echo off
REM Run baseline scan in Docker container
REM This can be run independently anytime

cd /d "%~dp0"

echo ==========================================
echo RTL-SDR Baseline Scan (Docker)
echo ==========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop first.
    pause
    exit /b 1
)

echo Starting baseline scan in Docker container...
echo Press Ctrl+C anytime to stop and save progress
echo.
echo ==========================================
echo.

REM Build image if needed
docker-compose build rtl-sdr-listener >nul 2>&1

REM Stop any running listener containers to free the USB device
docker-compose stop rtl-sdr-listener rtl-sdr-ml-listener >nul 2>&1

REM Run baseline scan in a temporary container
docker-compose run --rm rtl-sdr-listener python collect_baseline.py

echo.
echo ==========================================
echo Baseline scan completed!
echo Results saved to baseline.json
echo ==========================================
echo.
pause

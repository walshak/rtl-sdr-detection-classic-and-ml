@echo off
REM ========================================
REM RTL-SDR Detection System - Stop Script
REM ========================================
SETLOCAL EnableDelayedExpansion

REM Change to the directory where this script is located
cd /d "%~dp0"

echo.
echo ==========================================
echo Stopping RTL-SDR Detection System...
echo ==========================================
echo.

docker-compose down

if not errorlevel 1 (
    echo.
    echo [OK] System stopped successfully
    echo.
) else (
    echo.
    echo [WARN] System may not have been running
    echo.
)

REM Optional: Detach USB device from WSL2
where usbipd >nul 2>&1
if not errorlevel 1 (
    set "BUSID="
    for /f "tokens=1" %%a in ('usbipd list ^| findstr /i "Attached.*RTL"') do set "BUSID=%%a"
    
    if defined BUSID (
        echo Detaching RTL-SDR from WSL2...
        usbipd detach --busid !BUSID!
        echo [OK] Device detached
    )
)

echo.
pause

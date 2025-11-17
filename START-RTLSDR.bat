@echo off
REM ========================================
REM RTL-SDR Detection System - One-Click Launcher
REM ========================================
SETLOCAL EnableDelayedExpansion

REM Change to the directory where this script is located
cd /d "%~dp0"

echo.
echo ==========================================
echo RTL-SDR Detection System - Starting...
echo ==========================================
echo.

REM Check if running as Administrator
net session >nul 2>&1
if errorlevel 1 (
    echo [ERROR] This script requires Administrator privileges!
    echo Right-click this file and select "Run as Administrator"
    echo.
    pause
    exit /b 1
)

echo [1/7] Updating code from Git...

REM Check if git is available
where git >nul 2>&1
if not errorlevel 1 (
    REM Update main repository
    if exist ".git" (
        echo [INFO] Updating main repository...
        git pull origin master
        if not errorlevel 1 (
            echo [OK] Main repository updated
        ) else (
            echo [WARN] Could not update main repository
            echo [INFO] Continuing with existing code...
        )
    ) else (
        echo [INFO] Not a git repository, skipping main update
    )
    
    REM Update AeroShield repository
    if exist "AeroShield\.git" (
        echo [INFO] Updating AeroShield frontend...
        cd AeroShield
        git pull origin master
        if not errorlevel 1 (
            echo [OK] AeroShield updated
        ) else (
            echo [WARN] Could not update AeroShield
            echo [INFO] Continuing with existing code...
        )
        cd ..
    ) else (
        echo [INFO] AeroShield not a git repository, skipping update
    )
) else (
    echo [INFO] Git not installed, skipping updates
)

echo.
echo [2/7] Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not in PATH
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Starting Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo Waiting for Docker to start ^(this may take 30-60 seconds^)...
    
    REM Wait for Docker to be ready
    set /a counter=0
    :waitloop
    timeout /t 5 /nobreak >nul
    docker info >nul 2>&1
    if not errorlevel 1 goto dockerready
    set /a counter+=1
    if !counter! lss 24 (
        echo Still waiting... ^(!counter!/24^)
        goto waitloop
    )
    echo [ERROR] Docker did not start in time. Please start Docker Desktop manually.
    pause
    exit /b 1
)

:dockerready
echo [OK] Docker is running

echo.
echo [3/7] Checking RTL-SDR Device...

REM Try to find and attach RTL-SDR device to WSL
where usbipd >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Found usbipd-win, attempting to attach RTL-SDR to WSL...
    
    REM Find RTL-SDR device BUSID - try multiple identifiers
    set "BUSID="
    
    REM Try VID:PID 0bda:2838 (Realtek RTL2838)
    for /f "tokens=1" %%a in ('usbipd list ^| findstr /i "0bda:2838"') do set "BUSID=%%a"
    
    REM If not found, try common device names
    if not defined BUSID (
        for /f "tokens=1" %%a in ('usbipd list ^| findstr /i "RTL2838"') do set "BUSID=%%a"
    )
    if not defined BUSID (
        for /f "tokens=1" %%a in ('usbipd list ^| findstr /i "Bulk-In"') do set "BUSID=%%a"
    )
    if not defined BUSID (
        for /f "tokens=1" %%a in ('usbipd list ^| findstr /i "RTL"') do set "BUSID=%%a"
    )
    
    if defined BUSID (
        echo [INFO] Found RTL-SDR at bus !BUSID!
        
        REM First, unbind if already bound to ensure clean state
        echo [INFO] Ensuring clean device state...
        usbipd unbind --busid !BUSID! >nul 2>&1
        
        REM Detach if already attached
        usbipd detach --busid !BUSID! >nul 2>&1
        timeout /t 2 /nobreak >nul
        
        REM Bind the device for WSL access
        echo [INFO] Binding device for WSL access...
        usbipd bind --busid !BUSID!
        if not errorlevel 1 (
            echo [OK] Device bound successfully
        ) else (
            echo [ERROR] Failed to bind device
            echo Please ensure you have Administrator privileges
            pause
            exit /b 1
        )
        
        REM Attach to WSL2 (without --auto-attach to avoid blocking)
        echo [INFO] Attaching to WSL2...
        start /B "" cmd /c "usbipd attach --wsl --busid !BUSID! 2>nul"
        
        REM Wait a moment for attachment to complete
        timeout /t 3 /nobreak >nul
        
        REM Verify device is attached by checking WSL
        wsl lsusb 2>nul | findstr /i "Realtek" >nul
        if not errorlevel 1 (
            echo [OK] RTL-SDR attached to WSL2
        ) else (
            echo [WARN] Device attachment may still be in progress
            echo [INFO] Continuing with startup...
        )
    ) else (
        echo [WARN] RTL-SDR device not found via usbipd
        echo.
        echo Please check:
        echo   1. RTL-SDR device is plugged in
        echo   2. Run: usbipd list
        echo   3. Look for VID:PID 0bda:2838 or "Bulk-In" device
        echo.
        echo [INFO] Will try to use native Windows device access
        pause
    )
) else (
    echo [WARN] usbipd-win not installed
    echo [INFO] Install from: https://github.com/dorssel/usbipd-win/releases
    echo [INFO] Will try to use native Windows device access
)

echo.
echo [4/7] Checking project files...
if not exist "docker-compose.yml" (
    echo [ERROR] docker-compose.yml not found!
    echo Please run this file from the RTL-SDR project directory
    pause
    exit /b 1
)
echo [OK] Project files found

echo.
echo [5/7] Checking configuration...
if not exist ".env" (
    echo [INFO] Creating .env from .env.example...
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [OK] .env created
    ) else (
        echo [WARN] No .env.example found, using defaults
    )
) else (
    echo [OK] .env exists
)

REM Ensure data directories exist
if not exist "data" mkdir data
if not exist "models" mkdir models
if not exist "backups" mkdir backups
echo [OK] Directories ready

echo.
echo ==========================================
echo OPTIONAL: Baseline Scan
echo ==========================================
echo.
echo Would you like to run a baseline scan now?
echo This will scan all configured frequencies to establish
echo a baseline for signal detection. You can skip anytime
echo by pressing Ctrl+C during the scan.
echo.
echo Current baseline: 
if exist "baseline.json" (
    echo   baseline.json exists ^(will be updated^)
) else (
    echo   No baseline.json found ^(will be created^)
)
echo.
choice /C YN /N /M "Run baseline scan now? (Y/N): "
if errorlevel 2 goto skip_baseline
if errorlevel 1 (
    echo.
    echo Starting baseline scan in Docker container...
    echo ==========================================
    echo.
    
    REM Build the image first
    docker-compose build rtl-sdr-listener >nul 2>&1
    
    REM Run baseline scan in a temporary container (not the main listener)
    docker-compose run --rm rtl-sdr-listener python collect_baseline.py
    
    echo.
    echo ==========================================
    echo Baseline scan completed
    echo ==========================================
    timeout /t 2 /nobreak >nul
)

:skip_baseline
echo.
echo [6/7] Starting Docker containers...
docker-compose down >nul 2>&1
docker-compose up -d

if errorlevel 1 (
    echo [ERROR] Failed to start containers
    echo.
    echo Troubleshooting steps:
    echo 1. Check Docker Desktop is running
    echo 2. Check for error messages above
    echo 3. Try: docker-compose logs
    echo.
    pause
    exit /b 1
)

echo [OK] Containers started

echo.
echo [7/7] Waiting for system to be ready...
timeout /t 8 /nobreak >nul

REM Check if services are responding
curl -s http://localhost:3000 >nul 2>&1
if not errorlevel 1 (
    echo [OK] AeroShield dashboard is ready!
) else (
    echo [WARN] Dashboard may still be starting...
    echo       Give it a few more seconds after the browser opens
)

echo.
echo ==========================================
echo SUCCESS! System is running
echo ==========================================
echo.
echo AeroShield Dashboard:  http://localhost:3000
echo API Backend:           http://localhost:5000
echo.
echo The RTL-SDR listener is running in the background
echo detecting and logging signals automatically.
echo.
echo Press Ctrl+C in the command window below to see live logs,
echo or just minimize it to keep running in the background.
echo.
echo To stop the system, run: STOP-RTLSDR.bat
echo.
echo Opening AeroShield dashboard in browser...
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo ==========================================
echo LIVE LOGS (Press Ctrl+C to exit logs)
echo ==========================================
echo.

REM Show live logs
docker-compose logs -f --tail=20 rtl-sdr-listener

REM If user exits logs, ask if they want to stop
echo.
choice /C YN /M "Do you want to stop the RTL-SDR system"
if errorlevel 2 goto end
if errorlevel 1 (
    echo Stopping system...
    docker-compose down
    echo System stopped.
)

:end
pause

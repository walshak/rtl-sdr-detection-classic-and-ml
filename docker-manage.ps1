# RTL-SDR Docker Management Script for Windows
# Run this script from PowerShell: .\docker-manage.ps1 [command]

param(
    [Parameter(Position=0)]
    [ValidateSet("build", "start", "stop", "restart", "logs", "status", "clean", "attach-usb", "shell", "backup")]
    [string]$Command = "status"
)

$ErrorActionPreference = "Stop"

Write-Host "🛰️  RTL-SDR Detection System - Docker Manager" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

function Build-Containers {
    Write-Host "📦 Building Docker images..." -ForegroundColor Yellow
    docker-compose build
    Write-Host "✅ Build complete!" -ForegroundColor Green
}

function Start-Containers {
    Write-Host "🚀 Starting containers..." -ForegroundColor Yellow
    docker-compose up -d
    Write-Host "✅ Containers started!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Dashboard: http://localhost:5000" -ForegroundColor Cyan
    Write-Host "📋 View logs: .\docker-manage.ps1 logs" -ForegroundColor Gray
}

function Stop-Containers {
    Write-Host "🛑 Stopping containers..." -ForegroundColor Yellow
    docker-compose down
    Write-Host "✅ Containers stopped!" -ForegroundColor Green
}

function Restart-Containers {
    Write-Host "🔄 Restarting containers..." -ForegroundColor Yellow
    docker-compose restart
    Write-Host "✅ Containers restarted!" -ForegroundColor Green
}

function Show-Logs {
    Write-Host "📋 Showing logs (Ctrl+C to exit)..." -ForegroundColor Yellow
    docker-compose logs -f
}

function Show-Status {
    Write-Host "📊 Container Status:" -ForegroundColor Yellow
    docker-compose ps
    Write-Host ""
    Write-Host "💾 Disk Usage:" -ForegroundColor Yellow
    docker system df
}

function Clean-System {
    Write-Host "🧹 Cleaning Docker system..." -ForegroundColor Yellow
    $confirm = Read-Host "This will remove stopped containers and unused images. Continue? (y/n)"
    if ($confirm -eq 'y') {
        docker-compose down
        docker system prune -f
        Write-Host "✅ Cleanup complete!" -ForegroundColor Green
    } else {
        Write-Host "❌ Cleanup cancelled" -ForegroundColor Red
    }
}

function Attach-USB {
    Write-Host "🔌 USB Device Management" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Available USB devices:" -ForegroundColor Cyan
    usbipd wsl list
    Write-Host ""
    Write-Host "To attach RTL-SDR device, find the BUSID and run:" -ForegroundColor Gray
    Write-Host "  usbipd wsl attach --busid <BUSID> --auto-attach" -ForegroundColor White
    Write-Host ""
    $attach = Read-Host "Enter BUSID to attach (or press Enter to skip)"
    if ($attach) {
        Write-Host "Attaching device $attach..." -ForegroundColor Yellow
        usbipd wsl attach --busid $attach --auto-attach
        Write-Host "✅ Device attached!" -ForegroundColor Green
    }
}

function Open-Shell {
    Write-Host "🐚 Opening shell in rtl-sdr-web container..." -ForegroundColor Yellow
    docker-compose exec rtl-sdr-web /bin/bash
}

function Backup-Data {
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupPath = ".\backups\backup-$timestamp.tar.gz"
    
    Write-Host "💾 Creating backup..." -ForegroundColor Yellow
    
    # Create backups directory if it doesn't exist
    if (-not (Test-Path ".\backups")) {
        New-Item -ItemType Directory -Path ".\backups" | Out-Null
    }
    
    # Create backup using docker
    docker run --rm -v "${PWD}/data:/data" -v "${PWD}/backups:/backup" alpine tar czf "/backup/backup-$timestamp.tar.gz" /data
    
    Write-Host "✅ Backup created: $backupPath" -ForegroundColor Green
}

# Execute command
switch ($Command) {
    "build" { Build-Containers }
    "start" { Start-Containers }
    "stop" { Stop-Containers }
    "restart" { Restart-Containers }
    "logs" { Show-Logs }
    "status" { Show-Status }
    "clean" { Clean-System }
    "attach-usb" { Attach-USB }
    "shell" { Open-Shell }
    "backup" { Backup-Data }
    default { 
        Write-Host "Usage: .\docker-manage.ps1 [command]" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Commands:" -ForegroundColor Cyan
        Write-Host "  build       - Build Docker images" -ForegroundColor White
        Write-Host "  start       - Start all containers" -ForegroundColor White
        Write-Host "  stop        - Stop all containers" -ForegroundColor White
        Write-Host "  restart     - Restart containers" -ForegroundColor White
        Write-Host "  logs        - Show container logs" -ForegroundColor White
        Write-Host "  status      - Show container status" -ForegroundColor White
        Write-Host "  clean       - Clean up Docker system" -ForegroundColor White
        Write-Host "  attach-usb  - Attach RTL-SDR USB device" -ForegroundColor White
        Write-Host "  shell       - Open shell in container" -ForegroundColor White
        Write-Host "  backup      - Backup database files" -ForegroundColor White
    }
}

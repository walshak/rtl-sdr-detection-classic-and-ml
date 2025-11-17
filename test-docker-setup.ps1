# Docker Setup Test Script
# Run this to verify your Docker environment is ready

param(
    [switch]$Quick
)

Write-Host "RTL-SDR Docker Environment Test" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# Test 1: Docker Desktop
Write-Host "1. Checking Docker Desktop..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "   [OK] Docker installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "   [FAIL] Docker not found! Please install Docker Desktop." -ForegroundColor Red
    Write-Host "      Download from: https://www.docker.com/products/docker-desktop/" -ForegroundColor Gray
    $allPassed = $false
}

# Test 2: Docker running
Write-Host "2. Checking Docker daemon..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "   [OK] Docker daemon is running" -ForegroundColor Green
} catch {
    Write-Host "   [FAIL] Docker daemon not running! Please start Docker Desktop." -ForegroundColor Red
    $allPassed = $false
}

# Test 3: Docker Compose
Write-Host "3. Checking Docker Compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version
    Write-Host "   [OK] Docker Compose installed: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "   [FAIL] Docker Compose not found!" -ForegroundColor Red
    $allPassed = $false
}

# Test 4: WSL 2
Write-Host "4. Checking WSL 2..." -ForegroundColor Yellow
try {
    $wslStatus = wsl --status 2>&1
    if ($wslStatus -match "Default Version: 2") {
        Write-Host "   [OK] WSL 2 is active" -ForegroundColor Green
    } else {
        Write-Host "   [WARN] WSL 2 might not be the default version" -ForegroundColor Yellow
        Write-Host "      Run: wsl --set-default-version 2" -ForegroundColor Gray
    }
} catch {
    Write-Host "   [WARN] Could not verify WSL 2 status" -ForegroundColor Yellow
}

# Test 5: USBIPD
Write-Host "5. Checking usbipd-win (for USB device access)..." -ForegroundColor Yellow
try {
    $usbipd = Get-Command usbipd -ErrorAction Stop
    Write-Host "   [OK] usbipd-win installed" -ForegroundColor Green
    
    if (-not $Quick) {
        Write-Host "   USB Devices:" -ForegroundColor Cyan
        usbipd wsl list
    }
} catch {
    Write-Host "   [WARN] usbipd-win not found (optional but recommended)" -ForegroundColor Yellow
    Write-Host "      Download from: https://github.com/dorssel/usbipd-win/releases" -ForegroundColor Gray
}

# Test 6: Required files
Write-Host "6. Checking project files..." -ForegroundColor Yellow
$requiredFiles = @(
    "Dockerfile",
    "docker-compose.yml",
    "docker-entrypoint.sh",
    "requirements.txt",
    "api.py",
    "listen.py"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "   [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "   [FAIL] $file missing!" -ForegroundColor Red
        $missingFiles += $file
        $allPassed = $false
    }
}

# Test 7: Directory structure
Write-Host "7. Checking directory structure..." -ForegroundColor Yellow
$directories = @("templates")
foreach ($dir in $directories) {
    if (Test-Path $dir) {
        Write-Host "   [OK] $dir/ exists" -ForegroundColor Green
    } else {
        Write-Host "   [FAIL] $dir/ missing!" -ForegroundColor Red
        $allPassed = $false
    }
}

# Create optional directories
$optionalDirs = @("data", "models", "backups")
foreach ($dir in $optionalDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "   [OK] Created $dir/" -ForegroundColor Green
    } else {
        Write-Host "   [OK] $dir/ exists" -ForegroundColor Green
    }
}

# Test 8: Environment file
Write-Host "8. Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "   [OK] .env file exists" -ForegroundColor Green
} else {
    if (Test-Path ".env.example") {
        Write-Host "   [WARN] .env not found, creating from .env.example" -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "   [OK] .env created - please review and customize" -ForegroundColor Green
    } else {
        Write-Host "   [WARN] No .env file (optional)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan

if ($allPassed) {
    Write-Host "[SUCCESS] All critical tests passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You're ready to start! Run:" -ForegroundColor Cyan
    Write-Host "   .\docker-manage.ps1 start" -ForegroundColor White
    Write-Host ""
    Write-Host "Or for a quick start:" -ForegroundColor Cyan
    Write-Host "   .\quickstart.bat" -ForegroundColor White
} else {
    Write-Host "[FAILED] Some tests failed! Please resolve issues above." -ForegroundColor Red
    Write-Host ""
    Write-Host "Common fixes:" -ForegroundColor Yellow
    Write-Host "  1. Install Docker Desktop if missing" -ForegroundColor White
    Write-Host "  2. Start Docker Desktop" -ForegroundColor White
    Write-Host "  3. Enable WSL 2 integration in Docker settings" -ForegroundColor White
}

Write-Host ""

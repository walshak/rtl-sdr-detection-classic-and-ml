# RTL-SDR Detection System - Package for Deployment
# Run this to create a deployment package for your client

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RTL-SDR Deployment Package Creator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "[ERROR] docker-compose.yml not found!" -ForegroundColor Red
    Write-Host "Please run this script from the RTL-SDR project directory" -ForegroundColor Yellow
    pause
    exit 1
}

# Package name with timestamp
$timestamp = Get-Date -Format "yyyy-MM-dd-HHmm"
$packageName = "rtl-sdr-detection-$timestamp"
$packagePath = ".\$packageName"
$zipFile = "$packageName.zip"

Write-Host "[1/5] Creating package directory..." -ForegroundColor Yellow
if (Test-Path $packagePath) {
    Remove-Item $packagePath -Recurse -Force
}
New-Item -ItemType Directory -Path $packagePath | Out-Null

Write-Host "[2/5] Copying essential files..." -ForegroundColor Yellow

# Essential files
$files = @(
    "START-RTLSDR.bat",
    "STOP-RTLSDR.bat",
    "migrate-databases.bat",
    "docker-compose.yml",
    "Dockerfile",
    "docker-entrypoint.sh",
    ".env.example",
    "requirements.txt",
    "baseline.json",
    "README-CLIENT.md",
    "USB-SETUP-GUIDE.md"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Copy-Item $file $packagePath\ -Force
        Write-Host "  + $file" -ForegroundColor Green
    } else {
        Write-Host "  - $file (missing)" -ForegroundColor Yellow
    }
}

# Python files
Write-Host "[3/5] Copying Python files..." -ForegroundColor Yellow
$pyFiles = Get-ChildItem -Filter "*.py" -File
foreach ($file in $pyFiles) {
    Copy-Item $file.FullName $packagePath\ -Force
    Write-Host "  + $($file.Name)" -ForegroundColor Green
}

# Templates directory
Write-Host "[4/5] Copying templates..." -ForegroundColor Yellow
if (Test-Path "templates") {
    Copy-Item "templates" $packagePath\ -Recurse -Force
    Write-Host "  + templates/" -ForegroundColor Green
}

# AeroShield frontend
Write-Host "Copying AeroShield frontend..." -ForegroundColor Yellow
if (Test-Path "AeroShield") {
    # Copy AeroShield but exclude node_modules and .next
    robocopy "AeroShield" "$packagePath\AeroShield" /E /XD node_modules .next .git .husky /XF "*.log" /NFL /NDL /NJH /NJS | Out-Null
    Write-Host "  + AeroShield/" -ForegroundColor Green
}

# Create empty directories
Write-Host "[5/5] Creating empty directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "$packagePath\data" -Force | Out-Null
New-Item -ItemType Directory -Path "$packagePath\models" -Force | Out-Null
New-Item -ItemType Directory -Path "$packagePath\backups" -Force | Out-Null
Write-Host "  + data/" -ForegroundColor Green
Write-Host "  + models/" -ForegroundColor Green
Write-Host "  + backups/" -ForegroundColor Green

# Create a quick start PDF-friendly text file
Write-Host ""
Write-Host "Creating QUICK-START.txt..." -ForegroundColor Yellow
@"
========================================
RTL-SDR DETECTION SYSTEM - QUICK START
========================================

PREREQUISITES (Install Once):
1. Docker Desktop: https://www.docker.com/products/docker-desktop/
2. usbipd-win: https://github.com/dorssel/usbipd-win/releases
3. RTL-SDR Drivers (if needed): https://zadig.akeo.ie/

FIRST RUN:
1. Extract this ZIP file to C:\RTL-SDR\
2. Plug in RTL-SDR USB device
3. Right-click START-RTLSDR.bat
4. Select "Run as Administrator"
5. Wait for dashboard to open automatically

DASHBOARD URL:
http://localhost:5000

TO STOP:
Run STOP-RTLSDR.bat (as Administrator)

IMPORTANT:
- Always run as Administrator
- USB device must be re-attached after each Windows restart
- START-RTLSDR.bat handles this automatically

For detailed instructions, see README-CLIENT.md

========================================
"@ | Out-File "$packagePath\QUICK-START.txt" -Encoding UTF8

# Compress to ZIP
Write-Host ""
Write-Host "Creating ZIP file..." -ForegroundColor Yellow
if (Test-Path $zipFile) {
    Remove-Item $zipFile -Force
}

Compress-Archive -Path $packagePath -DestinationPath $zipFile -CompressionLevel Optimal

# Calculate size
$zipSize = [math]::Round((Get-Item $zipFile).Length / 1MB, 2)

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "SUCCESS! Package created:" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "File: $zipFile" -ForegroundColor Cyan
Write-Host "Size: $zipSize MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "Package contents:" -ForegroundColor Yellow
Write-Host "  - START-RTLSDR.bat (main launcher)" -ForegroundColor White
Write-Host "  - STOP-RTLSDR.bat (stop script)" -ForegroundColor White
Write-Host "  - AeroShield/ (Next.js frontend)" -ForegroundColor White
Write-Host "  - All Python source files" -ForegroundColor White
Write-Host "  - Docker configuration" -ForegroundColor White
Write-Host "  - Templates & baseline data" -ForegroundColor White
Write-Host "  - README-CLIENT.md (full documentation)" -ForegroundColor White
Write-Host "  - USB-SETUP-GUIDE.md (USB troubleshooting)" -ForegroundColor White
Write-Host "  - QUICK-START.txt (simple instructions)" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Send $zipFile to your client" -ForegroundColor White
Write-Host "2. Client extracts and runs START-RTLSDR.bat as Admin" -ForegroundColor White
Write-Host "3. That's it!" -ForegroundColor White
Write-Host ""

# Cleanup temp directory
Remove-Item $packagePath -Recurse -Force

Write-Host "Temporary files cleaned up." -ForegroundColor Gray
Write-Host ""
pause

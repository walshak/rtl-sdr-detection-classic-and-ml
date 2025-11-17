# RTL-SDR Detection System - Docker Deployment Guide

## 🐳 Docker Setup for Windows 11

This guide will help you run the RTL-SDR Detection System in Docker containers on Windows 11.

### Prerequisites

1. **Docker Desktop for Windows**
   - Download and install from: https://www.docker.com/products/docker-desktop/
   - Enable WSL 2 backend (recommended)
   - Ensure Docker is running

2. **USB/IP for Windows** (for RTL-SDR USB access in containers)
   - Download usbipd-win from: https://github.com/dorssel/usbipd-win/releases
   - Install the MSI package

3. **RTL-SDR Drivers**
   - Install Zadig (https://zadig.akeo.ie/)
   - Replace RTL-SDR driver with WinUSB driver

### Quick Start

#### Option 1: Using Docker Compose (Recommended)

```powershell
# 1. Build and start all services
docker-compose up -d

# 2. View logs
docker-compose logs -f

# 3. Stop services
docker-compose down

# 4. Start with ML support
docker-compose --profile ml up -d
```

#### Option 2: Using Docker CLI

```powershell
# Build the image
docker build -t rtl-sdr-detection .

# Run the web dashboard
docker run -d `
  --name rtl-sdr-dashboard `
  -p 5000:5000 `
  -v ${PWD}/data:/app/data `
  -v ${PWD}/models:/app/models `
  --privileged `
  rtl-sdr-detection

# Run the listener
docker run -d `
  --name rtl-sdr-listener `
  -v ${PWD}/data:/app/data `
  --privileged `
  rtl-sdr-detection python listen.py
```

### USB Device Access on Windows

To access your RTL-SDR device from Docker containers on Windows:

#### Step 1: List USB Devices
```powershell
usbipd wsl list
```

#### Step 2: Attach RTL-SDR Device
```powershell
# Find your RTL-SDR device (usually "Realtek RTL2838")
# Replace <BUSID> with the actual bus ID (e.g., 2-4)
usbipd wsl attach --busid <BUSID> --auto-attach
```

#### Step 3: Verify Device in WSL
```powershell
# Enter WSL
wsl

# Check if device is visible
lsusb | grep Realtek

# Test RTL-SDR
rtl_test
```

### Container Services

The system includes three main services:

1. **rtl-sdr-web** (Port 5000)
   - Web dashboard and API
   - Access at: http://localhost:5000

2. **rtl-sdr-listener**
   - Continuous signal monitoring
   - Writes to detections.db

3. **rtl-sdr-ml-listener** (Optional)
   - ML-enhanced detection
   - Only starts with `--profile ml` flag

### Volume Mounts

- `./data` - Database files and persistent data
- `./models` - ML models (if using ML features)
- `./baseline.json` - Signal baseline configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Key variables:
- `RTL_SDR_DEVICE` - Device index (default: 0)
- `DEVICE_LABEL` - Identifier for this device
- `DEVICE_LAT` / `DEVICE_LONG` - GPS coordinates
- `SCAN_INTERVAL` - Seconds between scans
- `THRESHOLD_DB` - Detection threshold

### Common Commands

```powershell
# View running containers
docker-compose ps

# View logs for specific service
docker-compose logs -f rtl-sdr-web

# Restart a service
docker-compose restart rtl-sdr-listener

# Execute command in container
docker-compose exec rtl-sdr-web python scan.py

# Stop and remove all containers
docker-compose down -v

# Rebuild after code changes
docker-compose build --no-cache
docker-compose up -d
```

### Troubleshooting

#### Issue: No RTL-SDR device detected

**Solution 1: Check USB attachment**
```powershell
usbipd wsl list
# Ensure device is attached to WSL
```

**Solution 2: Verify in container**
```powershell
docker-compose exec rtl-sdr-web rtl_test
```

#### Issue: Permission denied on USB device

**Solution:**
```powershell
# Run with privileged mode (already in docker-compose.yml)
docker run --privileged ...
```

#### Issue: Port 5000 already in use

**Solution:**
```yaml
# Edit docker-compose.yml
ports:
  - "8080:5000"  # Use port 8080 instead
```

#### Issue: Container can't write to database

**Solution:**
```powershell
# Create data directory with proper permissions
mkdir data
docker-compose down
docker-compose up -d
```

### Performance Tips

1. **Use WSL 2 Backend**
   - Faster file I/O
   - Better USB device support

2. **Limit Log Size**
   ```yaml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

3. **Resource Limits**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 2G
   ```

### Production Deployment

For production use:

1. **Use specific image tags**
   ```yaml
   image: rtl-sdr-detection:v1.0
   ```

2. **Enable health checks**
   ```yaml
   healthcheck:
     test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
     interval: 30s
     timeout: 10s
     retries: 3
   ```

3. **Use Docker secrets for sensitive data**
   ```yaml
   secrets:
     - db_password
   ```

4. **Set up automatic backups**
   ```powershell
   # Backup script
   docker run --rm -v rtl-sdr-data:/data -v ${PWD}/backups:/backup 
     alpine tar czf /backup/backup-$(date +%Y%m%d).tar.gz /data
   ```

### Building for Different Architectures

```powershell
# For ARM devices (Raspberry Pi)
docker buildx build --platform linux/arm64 -t rtl-sdr-detection:arm64 .

# Multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 
  -t rtl-sdr-detection:latest .
```

### Updating the System

```powershell
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d

# Clean up old images
docker image prune -a
```

### Monitoring

```powershell
# Container stats
docker stats

# Resource usage
docker-compose top

# System-wide info
docker system df
```

### Security Considerations

1. **Don't expose to internet without authentication**
2. **Use environment variables for sensitive data**
3. **Regularly update base images**
4. **Run security scans**
   ```powershell
   docker scan rtl-sdr-detection
   ```

### Getting Help

- Check logs: `docker-compose logs -f`
- Enter container: `docker-compose exec rtl-sdr-web bash`
- Test RTL-SDR: `docker-compose exec rtl-sdr-web rtl_test`

### Cleanup

```powershell
# Stop all containers
docker-compose down

# Remove all data (caution!)
docker-compose down -v

# Remove images
docker rmi rtl-sdr-detection

# Full cleanup
docker system prune -a --volumes
```

## 📝 Notes for Windows 11

- Docker Desktop must be running
- WSL 2 integration must be enabled
- USB device attachment requires usbipd-win
- Use PowerShell (not CMD) for better compatibility
- File paths in Windows use backslashes, but Docker uses forward slashes

## 🚀 Next Steps

1. Start the containers: `docker-compose up -d`
2. Attach USB device: `usbipd wsl attach --busid <BUSID>`
3. Open dashboard: http://localhost:5000
4. Monitor logs: `docker-compose logs -f`

Happy signal hunting! 🛰️

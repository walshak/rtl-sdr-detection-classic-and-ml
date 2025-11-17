# 🐳 RTL-SDR Detection System - Docker Edition

A containerized RTL-SDR signal detection and analysis system with web dashboard, optimized for Windows 11.

## 🚀 Quick Start (Windows 11)

### Prerequisites
1. **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
2. **usbipd-win** - [Download here](https://github.com/dorssel/usbipd-win/releases) (for USB device access)
3. **RTL-SDR Device** with drivers installed

### One-Click Start
Simply double-click `quickstart.bat` and follow the prompts!

Or use PowerShell:
```powershell
.\docker-manage.ps1 start
```

### Manual Start
```powershell
# Build containers
docker-compose build

# Start system
docker-compose up -d

# View logs
docker-compose logs -f
```

## 📊 Access the Dashboard
Once running, open your browser to: **http://localhost:5000**

## 🔌 Connecting Your RTL-SDR Device

### On Windows with WSL 2:

1. **List USB devices:**
   ```powershell
   usbipd wsl list
   ```

2. **Attach your RTL-SDR:**
   ```powershell
   # Replace 2-4 with your actual BUSID
   usbipd wsl attach --busid 2-4 --auto-attach
   ```

3. **Verify device:**
   ```powershell
   docker-compose exec rtl-sdr-web rtl_test
   ```

## 📦 What's Included

### Services
- **rtl-sdr-web** (`:5000`) - Web dashboard and REST API
- **rtl-sdr-listener** - Continuous signal monitoring
- **rtl-sdr-ml-listener** - ML-enhanced detection (optional)

### Features
- ✅ Real-time signal detection
- ✅ Interactive web dashboard
- ✅ Signal classification
- ✅ Historical data analysis
- ✅ Multiple device support
- ✅ Automated baseline collection
- ✅ Machine learning integration (optional)

## 🛠️ Management Commands

Using PowerShell script:
```powershell
.\docker-manage.ps1 [command]
```

Available commands:
- `build` - Build Docker images
- `start` - Start all services
- `stop` - Stop all services
- `restart` - Restart services
- `logs` - View logs
- `status` - Show container status
- `attach-usb` - Attach USB device
- `shell` - Open shell in container
- `backup` - Backup database
- `clean` - Clean up Docker system

## 📁 Directory Structure

```
rtl-classic/
├── Dockerfile              # Container image definition
├── docker-compose.yml      # Multi-container orchestration
├── docker-entrypoint.sh    # Container startup script
├── docker-manage.ps1       # Management script (PowerShell)
├── quickstart.bat          # One-click launcher
├── .dockerignore           # Files to exclude from image
├── .env.example            # Environment template
├── data/                   # Persistent data (mounted)
│   ├── detections.db
│   └── ml_detections.db
├── models/                 # ML models (mounted)
└── backups/               # Database backups
```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
# Device Configuration
DEVICE_LABEL=DEVICE_1
DEVICE_LAT=40.7128
DEVICE_LONG=-74.0060

# SDR Settings
RTL_SDR_DEVICE=0
SAMPLE_RATE=2048000
SCAN_INTERVAL=10
THRESHOLD_DB=10

# Flask Settings
FLASK_ENV=production
```

### Docker Compose Profiles

Run specific services:

```powershell
# Standard monitoring only
docker-compose up -d

# Include ML features
docker-compose --profile ml up -d
```

## 🔧 Troubleshooting

### Container won't start
```powershell
# Check Docker is running
docker info

# View container logs
docker-compose logs rtl-sdr-web
```

### Can't detect RTL-SDR device
```powershell
# Verify USB attachment
usbipd wsl list

# Check device in container
docker-compose exec rtl-sdr-web lsusb
docker-compose exec rtl-sdr-web rtl_test
```

### Port 5000 already in use
Edit `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Use port 8080 instead
```

### Database errors
```powershell
# Reinitialize database
docker-compose exec rtl-sdr-web python init_db.py
```

## 📊 Monitoring

### View logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f rtl-sdr-listener
```

### Resource usage
```powershell
docker stats
```

### Health status
```powershell
docker-compose ps
```

Check health endpoint:
```powershell
curl http://localhost:5000/health
```

## 💾 Backup & Restore

### Backup
```powershell
.\docker-manage.ps1 backup
```

Or manually:
```powershell
docker run --rm -v rtl-classic_data:/data -v ${PWD}/backups:/backup `
  alpine tar czf /backup/backup-$(Get-Date -Format yyyyMMdd).tar.gz /data
```

### Restore
```powershell
docker run --rm -v rtl-classic_data:/data -v ${PWD}/backups:/backup `
  alpine tar xzf /backup/backup-YYYYMMDD.tar.gz -C /
```

## 🔄 Updating

```powershell
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🐛 Development Mode

For development with live code reloading:

```yaml
# docker-compose.override.yml
services:
  rtl-sdr-web:
    volumes:
      - .:/app
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
```

Then start with:
```powershell
docker-compose up
```

## 🌐 Remote Access

To access from other devices on your network:

1. Find your IP address:
   ```powershell
   ipconfig
   ```

2. Access from remote device:
   ```
   http://[YOUR_IP]:5000
   ```

3. **Security Warning:** Consider using a reverse proxy with authentication for production use.

## 📈 Performance Tuning

### Limit resources
```yaml
services:
  rtl-sdr-web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

### Optimize for production
```yaml
environment:
  - FLASK_ENV=production
  - PYTHONOPTIMIZE=1
```

## 🔒 Security

- ⚠️ Default setup is for local use only
- Change default ports for production
- Use environment variables for secrets
- Don't expose to internet without authentication
- Keep Docker and images updated

## 📚 Additional Documentation

- [Full Docker Guide](DOCKER_GUIDE.md) - Comprehensive Docker documentation
- [ML System Guide](ML_SYSTEM_GUIDE.md) - Machine learning features
- [README.md](README.md) - Main project documentation

## 🆘 Getting Help

1. Check logs: `docker-compose logs -f`
2. Test device: `docker-compose exec rtl-sdr-web rtl_test`
3. Open shell: `docker-compose exec rtl-sdr-web bash`
4. Check health: `curl http://localhost:5000/health`

## 📝 Notes

- First build takes 5-10 minutes
- USB device must be attached before starting listener
- Data persists in mounted volumes
- Containers restart automatically unless stopped

## 🎯 Next Steps

1. ✅ Start containers: `.\docker-manage.ps1 start`
2. ✅ Attach USB: `.\docker-manage.ps1 attach-usb`
3. ✅ Open dashboard: http://localhost:5000
4. ✅ Collect baseline: `docker-compose exec rtl-sdr-web python collect_baseline.py`
5. ✅ Start listening: Containers auto-start listener

Happy signal hunting! 🛰️📡

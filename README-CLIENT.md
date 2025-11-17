# RTL-SDR Detection System - Client Deployment Guide

## 📦 For the Client

### **One-Click Operation**

1. **Plug in your RTL-SDR device** to a USB port
2. **Right-click** `START-RTLSDR.bat`
3. **Select** "Run as Administrator"
4. **Wait** for the system to start (30-60 seconds)
5. **Browser will open** automatically to http://localhost:5000

That's it! The system will:
- ✅ Check if Docker is running (start it if needed)
- ✅ Attach your RTL-SDR device to WSL2 (if usbipd is installed)
- ✅ Start all containers
- ✅ Open the dashboard in your browser
- ✅ Show live detection logs

### **To Stop**

Simply run `STOP-RTLSDR.bat` (also as Administrator)

---

## 🔧 Prerequisites (One-Time Setup)

The client needs these installed **once** before first use:

### 1. **Docker Desktop** (Required)
- Download: https://www.docker.com/products/docker-desktop/
- Install with WSL2 backend enabled
- Restart computer after installation

### 2. **WSL2** (Usually included with Docker Desktop)
- If not installed, run in PowerShell (Admin):
  ```powershell
  wsl --install
  ```

### 3. **usbipd-win** (Optional but Recommended)
- Download: https://github.com/dorssel/usbipd-win/releases
- Or install via winget:
  ```powershell
  winget install --interactive --exact dorssel.usbipd-win
  ```
- This allows Docker containers to access the USB RTL-SDR device

### 4. **RTL-SDR Drivers** (If device not recognized)
- Download Zadig: https://zadig.akeo.ie/
- Plug in RTL-SDR device
- Run Zadig and install WinUSB driver for "Bulk-In, Interface"

---

## 📁 What to Send to Client

Package these files/folders:

```
rtl-sdr-detection/
├── START-RTLSDR.bat          ⭐ Main launcher
├── STOP-RTLSDR.bat            ⭐ Stop script
├── docker-compose.yml
├── Dockerfile
├── docker-entrypoint.sh
├── .env.example
├── requirements.txt
├── baseline.json
├── *.py (all Python files)
├── templates/
│   └── dashboard.html
├── data/ (empty folder)
├── models/ (empty folder)
└── README-CLIENT.md          ⭐ This file
```

### **As a ZIP File:**
1. Compress the entire folder to `rtl-sdr-detection.zip`
2. Include a PDF version of this README
3. Send to client

---

## 🚀 First Run Instructions for Client

### **Step-by-Step:**

1. **Extract ZIP** to any location (e.g., `C:\RTL-SDR\`)

2. **Install Prerequisites** (one-time):
   - Docker Desktop
   - usbipd-win (optional)
   - RTL-SDR drivers (if needed)

3. **Plug in RTL-SDR** USB device

4. **Run START-RTLSDR.bat**:
   - Right-click → "Run as Administrator"
   - Wait for setup to complete
   - Dashboard opens automatically

5. **View Dashboard**:
   - URL: http://localhost:3000 (AeroShield Frontend)
   - API Backend: http://localhost:5000
   - Login and view real-time RF signal detections

---

## ⚙️ Configuration (Optional)

Edit `.env` file to customize:

```env
# Device index (0 or 1, system will auto-detect)
RTL_SDR_DEVICE=0

# Device identification
DEVICE_LABEL=DEVICE_1
DEVICE_LAT=0.0
DEVICE_LONG=0.0

# Scan settings
SCAN_INTERVAL=10
THRESHOLD_DB=10
```

---

## 🔍 Troubleshooting

### **Docker won't start**
- Open Docker Desktop manually
- Check if virtualization is enabled in BIOS
- Restart computer

### **Device not found**
- Check USB connection
- Run `rtl_test` in command prompt
- Reinstall drivers with Zadig

### **USB binding fails (usbipd)**
The START script will automatically try to bind and attach the device. If it fails:
1. Open PowerShell as Administrator
2. Run: `usbipd list`
3. Note the BUSID of your RTL-SDR
4. Run: `usbipd bind --busid X-Y` (replace X-Y with your BUSID)
5. Run: `usbipd attach --wsl --busid X-Y`

### **Port 3000 already in use**
Another application is using port 3000. Either:
- Stop the other application
- Edit `docker-compose.yml` and change `"3000:3000"` to `"3001:3000"` under aeroshield-frontend
- Access at http://localhost:3001 instead

### **Port 5000 already in use**
Another application is using port 5000. Either:
- Stop the other application
- Edit `docker-compose.yml` and change `"5000:5000"` to `"5001:5000"`
- Access at http://localhost:5001 instead

### **System slow or unresponsive**
- Close unnecessary applications
- Check Docker Desktop resource limits (Settings → Resources)
- Increase memory allocation to 4GB minimum

---

## 📊 What to Expect

### **Normal Operation:**
- Dashboard shows device selection screen
- After selecting device, charts populate with data
- Detection logs scroll in console window
- Database grows in `data/detections.db`

### **Performance:**
- First startup: 2-3 minutes (building containers)
- Subsequent startups: 10-30 seconds
- Detection rate: 10-30 signals per scan
- Memory usage: ~2-4GB
- CPU usage: 10-30%

### **Data Storage:**
All data is stored locally in:
- `data/detections.db` - Detection database
- `data/detections_ml.db` - ML database (if used)
- `models/` - Trained models (if ML enabled)

---

## 🔄 USB Device After Restart

**IMPORTANT:** USB device binding does NOT persist after restart!

After every Windows restart:
1. The RTL-SDR USB device needs to be re-bound and re-attached to WSL2
2. The START-RTLSDR.bat script handles this automatically
3. If it fails, manually run:
   ```powershell
   usbipd list
   usbipd bind --busid X-Y
   usbipd attach --wsl --busid X-Y
   ```

### **Auto-Attach on Startup (Optional):**

Create a scheduled task to auto-bind and attach on boot:

1. Open Task Scheduler
2. Create Basic Task → "Attach RTL-SDR"
3. Trigger: "When computer starts"
4. Action: "Start a program"
5. Program: `powershell.exe`
6. Arguments: `-Command "Start-Sleep 30; usbipd bind --busid X-Y; Start-Sleep 2; usbipd attach --wsl --busid X-Y"`
7. Check "Run with highest privileges"

*(Replace X-Y with your device's BUSID from `usbipd list`)*

---

## 📞 Support

If issues persist:
1. Run `docker-compose logs` to see error messages
2. Check Docker Desktop is using WSL2 backend
3. Verify RTL-SDR works with `rtl_test` command
4. Contact support with screenshots of any errors

---

## 🛡️ Security Note

- The system runs on localhost only (not accessible from internet)
- All data stored locally
- No external connections except for signal detection
- Docker containers isolated from host system

---

## 📝 Quick Reference

| Action | Command |
|--------|---------|
| Start System | Run `START-RTLSDR.bat` as Admin |
| Stop System | Run `STOP-RTLSDR.bat` as Admin |
| View Logs | `docker-compose logs -f` |
| Restart | `STOP-RTLSDR.bat` then `START-RTLSDR.bat` |
| Update Code | Replace files, then restart |
| AeroShield Dashboard | http://localhost:3000 |
| API Backend | http://localhost:5000 |
| Check Device | `rtl_test` in cmd |
| List USB Devices | `usbipd list` in PowerShell (Admin) |
| Bind USB Device | `usbipd bind --busid X-Y` |
| Attach USB Device | `usbipd attach --wsl --busid X-Y` |

---

**System Version:** 2.0
**Last Updated:** November 2025

# USB RTL-SDR Access in Docker on Windows

## The Problem

Docker containers on Windows cannot directly access USB devices like they can on Linux. You have two main options:

## Option 1: Run Natively on Windows (Recommended for Windows 11)

Instead of using Docker for the listener service, run it natively on Windows where USB access is straightforward:

### Setup:
```powershell
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Set device index (if needed)
$env:RTL_SDR_DEVICE=0

# 3. Run the listener
python listen.py

# 4. Run the API in Docker (for dashboard)
docker-compose up rtl-sdr-web
```

### Hybrid Approach (Best of Both Worlds):
```yaml
# In docker-compose.yml, comment out the listener service
# services:
#   rtl-sdr-listener:
#     ...  # Comment this out
```

Then run:
```powershell
# Terminal 1: Dashboard in Docker
docker-compose up rtl-sdr-web

# Terminal 2: Listener on Windows
python listen.py
```

## Option 2: Use WSL2 + usbipd-win (Advanced)

This method forwards USB devices from Windows to WSL2, then to Docker.

### Prerequisites:
1. **WSL2** must be installed and set as default
2. **Docker Desktop** with WSL2 backend enabled
3. **usbipd-win** installed on Windows

### Installation:

#### 1. Install usbipd-win (Windows side)
```powershell
# Download from: https://github.com/dorssel/usbipd-win/releases
# Or use winget:
winget install --interactive --exact dorssel.usbipd-win
```

#### 2. Install usbipd tools (WSL2 side)
```bash
# In WSL2 terminal
sudo apt update
sudo apt install linux-tools-generic hwdata
sudo update-alternatives --install /usr/local/bin/usbip usbip /usr/lib/linux-tools/*-generic/usbip 20
```

#### 3. Attach RTL-SDR to WSL2
```powershell
# On Windows (as Administrator):

# List USB devices
usbipd wsl list

# Find your RTL-SDR (look for "Bulk-In, Interface (DVB-T/DAB/FM)" or "RTL2838")
# Note the BUSID (e.g., 2-4)

# Attach to WSL2
usbipd wsl attach --busid 2-4

# To detach later:
usbipd wsl detach --busid 2-4
```

#### 4. Verify in WSL2
```bash
# In WSL2:
lsusb | grep Realtek

# Should show something like:
# Bus 001 Device 002: ID 0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T
```

#### 5. Run Docker Compose
```powershell
# The USB device is now available to Docker containers in WSL2
docker-compose up
```

### Auto-attach Script (Windows)

Create `attach-rtlsdr.ps1`:
```powershell
# Run as Administrator
$busid = (usbipd wsl list | Select-String "RTL" | ForEach-Object { ($_ -split '\s+')[0] })
if ($busid) {
    Write-Host "Attaching RTL-SDR at bus $busid to WSL2..."
    usbipd wsl attach --busid $busid
    Write-Host "✓ RTL-SDR attached. You can now run docker-compose up"
} else {
    Write-Host "✗ RTL-SDR device not found. Is it plugged in?"
}
```

## Option 3: VirtualHere USB Server (Commercial)

VirtualHere can share USB devices over network to Docker containers.

1. Install VirtualHere USB Server on Windows (free for one device)
2. Connect from Docker container using VirtualHere client
3. More info: https://www.virtualhere.com/

## Troubleshooting

### Device Not Found
```bash
# Check if device is visible in WSL2
lsusb

# Check RTL-SDR specifically
rtl_test

# Check permissions
ls -la /dev/bus/usb/
```

### Permission Denied
```bash
# In WSL2, add udev rules
sudo nano /etc/udev/rules.d/rtl-sdr.rules

# Add this line:
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", MODE="0666"

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Device Disconnects
Windows may put USB devices to sleep. Disable USB selective suspend:
```powershell
# Run as Administrator
powercfg /setacvalueindex scheme_current 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0
powercfg /setactive scheme_current
```

## Recommended Configuration

For **Windows 11 users**, I recommend the **hybrid approach**:

1. ✅ Dashboard/API in Docker (easy to manage, web interface)
2. ✅ Listener running natively on Windows (direct USB access)
3. ✅ Both share the same database via volume mount

This gives you:
- Easy USB device access (native Windows)
- Portable web dashboard (Docker)
- No complex USB forwarding needed
- Better performance for SDR processing

### Quick Start (Hybrid):
```powershell
# 1. Start just the dashboard
docker-compose up rtl-sdr-web -d

# 2. Run listener natively
$env:RTL_SDR_DEVICE=0
python listen.py

# 3. Access dashboard at http://localhost:5000
```

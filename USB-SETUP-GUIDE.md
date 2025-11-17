# USB Device Setup Guide - usbipd-win 5.0+

## Overview

Starting with **usbipd-win 5.0**, USB device sharing requires a **two-step process**:

1. **BIND** - Share the device for WSL access (requires admin, once per boot)
2. **ATTACH** - Actually attach the shared device to WSL (requires admin)

## Quick Commands

### List all USB devices
```powershell
usbipd list
```

Output example:
```
BUSID  VID:PID    DEVICE                                          STATE
1-3    0bda:2838  Realtek Semiconductor Corp. RTL2838 DVB-T       Not shared
4-2    046d:c52b  Logitech USB Input Device                       Not shared
```

### Bind device (share for WSL)
```powershell
usbipd bind --busid 1-3
```

This makes the device **Shared** (available for WSL to use).

### Attach device to WSL
```powershell
usbipd attach --wsl --busid 1-3
```

This actually attaches the device to WSL. Status changes to **Attached**.

### Verify in WSL
```bash
# Inside WSL or Docker container
lsusb
```

Should show:
```
Bus 001 Device 002: ID 0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T
```

### Detach device
```powershell
usbipd detach --busid 1-3
```

Returns device to Windows. Status changes back to **Shared**.

## Important Notes

### ⚠️ Binding Does NOT Persist
After a Windows reboot:
- **Bind status** is lost - you must run `usbipd bind` again
- **Attach status** is lost - you must run `usbipd attach` again

### ✅ START-RTLSDR.bat Handles This
The `START-RTLSDR.bat` script automatically:
1. Finds your RTL-SDR device
2. Binds it (shares for WSL)
3. Attaches it to WSL
4. Starts containers

### 🔄 Auto-Attach on Boot (Optional)

Create a Windows scheduled task:

**Task Settings:**
- Name: `RTL-SDR USB Auto-Attach`
- Trigger: `At system startup`
- Action: Start a program
  - Program: `powershell.exe`
  - Arguments: `-WindowStyle Hidden -Command "Start-Sleep -Seconds 30; usbipd bind --busid 1-3; Start-Sleep -Seconds 2; usbipd attach --wsl --busid 1-3"`
- Run with highest privileges: ✅ Checked
- Run whether user is logged on or not: ✅ Checked

**Replace `1-3` with your actual Bus ID!**

## Troubleshooting

### Device shows "Not shared"
Run bind command:
```powershell
usbipd bind --busid 1-3
```

### Device shows "Shared" but not "Attached"
Run attach command:
```powershell
usbipd attach --wsl --busid 1-3
```

### "Access denied" error
- You must run PowerShell as Administrator
- Right-click PowerShell → "Run as Administrator"

### Device not visible in Docker
Ensure WSL is running before attaching:
```powershell
# Start a WSL session first
wsl echo "WSL is running"

# Then attach
usbipd attach --wsl --busid 1-3
```

### Multiple RTL-SDR devices
Each device needs its own bind and attach:
```powershell
usbipd bind --busid 1-3
usbipd attach --wsl --busid 1-3

usbipd bind --busid 2-4
usbipd attach --wsl --busid 2-4
```

## Command History (Old vs New)

| Old Command (pre-5.0) | New Command (5.0+) |
|----------------------|-------------------|
| `usbipd wsl list` | `usbipd list` |
| `usbipd wsl attach --busid X-Y` | `usbipd bind --busid X-Y` then `usbipd attach --wsl --busid X-Y` |
| `usbipd wsl detach --busid X-Y` | `usbipd detach --busid X-Y` |

## Additional Resources

- Official Documentation: https://github.com/dorssel/usbipd-win/wiki
- Download Latest: https://github.com/dorssel/usbipd-win/releases
- Microsoft Guide: https://learn.microsoft.com/en-us/windows/wsl/connect-usb

---

**Last Updated:** November 2025  
**usbipd-win version:** 5.0.0+

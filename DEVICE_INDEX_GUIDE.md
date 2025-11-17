# RTL-SDR Device Index Configuration

## Quick Start

The system now automatically detects and uses your RTL-SDR device, whether it's on index 0 or 1.

### Auto-Detection Script

Run this to automatically detect and configure your device:

```bash
python detect_rtlsdr.py
```

This will:
- Test device indices 0-3
- Display which devices are found
- Automatically update your `.env` file with the correct index

### Manual Configuration

#### Option 1: Environment Variable (Recommended)

Edit the `.env` file:
```bash
RTL_SDR_DEVICE=0   # Use 0 or 1 depending on your device
```

#### Option 2: Set at Runtime (Windows)

```powershell
$env:RTL_SDR_DEVICE=0
python listen.py
```

```cmd
set RTL_SDR_DEVICE=0
python listen.py
```

#### Option 3: Docker Environment

In `docker-compose.yml`:
```yaml
environment:
  - RTL_SDR_DEVICE=0
```

Or via command line:
```bash
docker run -e RTL_SDR_DEVICE=0 rtl-sdr-detection
```

## How It Works

All Python scripts now:

1. **Read from environment**: Check `RTL_SDR_DEVICE` environment variable (default: 0)
2. **Try specified index**: Attempt to open device at that index
3. **Auto-fallback**: If it fails, try the alternate index (0→1 or 1→0)
4. **Report status**: Print which device index is being used

## Troubleshooting

### Device Not Found

```bash
# Run detection utility
python detect_rtlsdr.py

# Check if device is visible
rtl_test

# On Linux, check USB devices
lsusb | grep RTL
```

### Wrong Device Index

If the auto-detection picks the wrong device:

1. Run `detect_rtlsdr.py` to see all available devices
2. Set `RTL_SDR_DEVICE` to your preferred index
3. The system will no longer try the fallback

### Multiple Devices

If you have multiple RTL-SDR devices:

- Device 0: First device plugged in
- Device 1: Second device plugged in
- Device 2+: Additional devices

Set different `DEVICE_LABEL` values for each device to track them separately.

## Files Updated

The following files now support flexible device indexing:

- ✅ `listen.py` - Main detection script
- ✅ `scan.py` - Frequency scanner
- ✅ `ml_listen.py` - ML-based detection
- ✅ `ml_data_collection.py` - ML training data collection
- ✅ `collect_baseline.py` - Baseline collection
- ✅ `detect_rtlsdr.py` - Device detection utility (NEW)

## Docker Usage

The Docker container respects the `RTL_SDR_DEVICE` environment variable:

```bash
# Using docker-compose (edit docker-compose.yml first)
docker-compose up -d

# Or override at runtime
docker-compose run -e RTL_SDR_DEVICE=1 rtl-sdr-detection python listen.py

# With docker run
docker run -e RTL_SDR_DEVICE=1 --device=/dev/bus/usb rtl-sdr-detection
```

## Best Practices

1. **Run detection first**: Always run `detect_rtlsdr.py` on a new system
2. **Document your setup**: Note which physical USB port corresponds to which index
3. **Use .env file**: Keep configuration in `.env` for consistency
4. **Test after changes**: Verify device access after configuration changes

## Advanced: USB Port Mapping

On Linux/WSL2, you can see USB device details:

```bash
# List USB devices with bus/port info
lsusb -t

# Find RTL-SDR devices
rtl_test -t
```

On Windows with WSL2:

```powershell
# List USB devices (requires usbipd-win)
usbipd wsl list

# Attach to WSL2
usbipd wsl attach --busid X-Y
```

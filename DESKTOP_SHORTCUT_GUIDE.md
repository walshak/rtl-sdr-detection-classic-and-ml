# DESKTOP SHORTCUT SETUP GUIDE

## Creating a Desktop Shortcut

1. **Navigate to the RTL-SDR project folder**
   - Usually `C:\Users\[YourName]\Desktop\rtl-classic\`

2. **Find the START-RTLSDR.bat file**
   - Right-click on `START-RTLSDR.bat`
   - Select "Create shortcut"

3. **Move the shortcut to your Desktop**
   - Drag the new shortcut to your Desktop

4. **Set to always run as Administrator**
   - Right-click the Desktop shortcut
   - Select "Properties"
   - Click "Advanced..." button
   - Check "Run as administrator"
   - Click "OK" then "OK" again

## Using the Shortcut

Simply **double-click** the desktop shortcut! It will:
- ✅ Automatically run as Administrator (after you confirm UAC)
- ✅ Change to the correct project directory
- ✅ Start Docker if not running
- ✅ Attach the RTL-SDR device to WSL
- ✅ Start all containers
- ✅ Open the dashboard in your browser

## Stopping the System

Create another shortcut for `STOP-RTLSDR.bat` using the same steps above.

## Troubleshooting

### "docker-compose.yml not found"
- **FIXED!** The scripts now automatically change to their own directory
- This should not happen anymore

### "Access Denied" or UAC prompt every time
- This is normal! The scripts need Administrator privileges to:
  - Manage Docker containers
  - Attach USB devices to WSL
  - Access system resources

### Shortcut doesn't work
1. Verify the shortcut's "Target" field points to the correct file:
   - Right-click shortcut → Properties
   - Target should be: `C:\Users\[YourName]\Desktop\rtl-classic\START-RTLSDR.bat`
2. Make sure "Start in" field is empty or points to the same directory
3. Verify "Run as administrator" is checked in Advanced settings

### System doesn't start
1. Check Docker Desktop is installed and running
2. Try running the .bat file directly from File Explorer first
3. Check the command window for error messages
4. See `USB-SETUP-GUIDE.md` for USB device issues

## What's Running?

Once started, you'll have:
- 🐋 Docker containers (backend, frontend, database)
- 📡 RTL-SDR device attached to WSL
- 🌐 Web dashboard at http://localhost:3000
- 🔌 API server at http://localhost:5000

## Pro Tips

- **First run takes longer** - Docker needs to build images (5-10 minutes)
- **Subsequent runs are fast** - Usually under 30 seconds
- **Leave the command window open** - It shows live logs
- **Minimize, don't close** - Closing stops the system
- **Use STOP-RTLSDR.bat** - Cleanly shuts down everything

## Need Help?

See the full documentation:
- `README-CLIENT.md` - Complete user guide
- `USB-SETUP-GUIDE.md` - USB troubleshooting
- `DOCKER_GUIDE.md` - Docker details

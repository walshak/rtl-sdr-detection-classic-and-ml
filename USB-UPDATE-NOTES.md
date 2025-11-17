# USB Device Update - November 2025

## What Changed?

Updated all scripts and documentation to match **usbipd-win 5.0+** requirements.

## Key Changes

### 1. Two-Step USB Process
Modern usbipd-win requires:
1. **BIND** - Share device for WSL access (once per boot)
2. **ATTACH** - Attach device to WSL (as needed)

### 2. Command Syntax Updates
| Old (pre-5.0) | New (5.0+) |
|---------------|------------|
| `usbipd wsl list` | `usbipd list` |
| `usbipd wsl attach --busid X-Y` | `usbipd bind --busid X-Y` + `usbipd attach --wsl --busid X-Y` |
| `usbipd wsl detach --busid X-Y` | `usbipd detach --busid X-Y` |

## Files Updated

### ✅ START-RTLSDR.bat
- Added `usbipd bind` command before attach
- Updated error messages with correct commands
- Better error handling for bind failures

### ✅ STOP-RTLSDR.bat
- Fixed command syntax: `usbipd detach` (no `wsl` subcommand)
- Updated device detection logic

### ✅ README-CLIENT.md
- Updated all manual USB commands
- Added two-step process explanation
- Fixed scheduled task PowerShell command
- Updated quick reference table

### ✅ USB-SETUP-GUIDE.md (NEW)
- Comprehensive USB troubleshooting guide
- Command reference with examples
- Scheduled task setup instructions
- Old vs new command comparison table

### ✅ package-for-client.ps1
- Added USB-SETUP-GUIDE.md to package contents
- Updated file list display

## Testing Performed

✅ Verified command syntax against official Microsoft documentation  
✅ Confirmed bind+attach workflow  
✅ Updated all references to `usbipd wsl` commands  
✅ Added proper error handling for bind failures  

## Impact on Users

### For Existing Users:
- **No action required** if using START-RTLSDR.bat (it handles everything)
- Manual commands in documentation now match current usbipd version
- More reliable USB attachment process

### For New Users:
- Clearer documentation with step-by-step process
- Better error messages
- Comprehensive troubleshooting guide

## Deployment Notes

When packaging for client:
1. Run `.\package-for-client.ps1`
2. ZIP file includes all updated documentation
3. Client gets correct commands from day one

## References

- **Official Docs:** https://learn.microsoft.com/en-us/windows/wsl/connect-usb
- **usbipd-win GitHub:** https://github.com/dorssel/usbipd-win
- **Minimum Version:** usbipd-win 5.0.0 or higher

---

**Update Date:** November 17, 2025  
**Updated By:** System Administrator  
**Reason:** Align with usbipd-win 5.0+ requirements

# Quick Database Cleanup Instructions

## Current Situation

You have two `detections.db` files:
- **Root folder**: `C:\Users\ADMIN\Desktop\rtl-classic\detections.db` (40.8 MB - older/smaller)
- **Data folder**: `C:\Users\ADMIN\Desktop\rtl-classic\data\detections.db` (148.7 MB - newer/larger)

The system is now configured to **ONLY** use the one in the `data/` folder.

## What to Do

### Option 1: Delete the Root Database (Recommended)
The root database is likely old data. Since the data folder has a newer, larger database:

1. **Close all applications** that might be using the database:
   - Close any terminals running `python listen.py`
   - Stop Docker containers: Run `STOP-RTLSDR.bat`
   - Close any database browsers (DB Browser for SQLite, etc.)

2. **Delete the old file**:
   ```powershell
   Remove-Item C:\Users\ADMIN\Desktop\rtl-classic\detections.db
   ```
   Or just right-click and delete it in File Explorer

### Option 2: Keep as Backup
If you want to keep the old data:

1. **Rename it**:
   ```powershell
   Rename-Item detections.db detections.db.old.backup
   ```

2. Move it to backups folder:
   ```powershell
   Move-Item detections.db.old.backup backups\
   ```

## Verification

After cleanup, verify only one database exists:

```powershell
# Should show ONLY the data folder database
Get-ChildItem -Recurse -Filter "detections.db" | Select-Object FullName, Length
```

Expected result:
```
FullName                                                      Length
--------                                                      ------
C:\Users\ADMIN\Desktop\rtl-classic\data\detections.db    148721664
```

## Current Configuration

All Python scripts now use: `data/detections.db`
- ✅ `api.py`
- ✅ `listen.py`
- ✅ `init_db.py`
- ✅ `test_data_richness.py`

All ML scripts now use: `data/detections_ml.db`
- ✅ `ml_listen.py`
- ✅ `init_ml_db.py`

## For Future Reference

Always use the `data/` folder for databases:
- Easy to backup: just backup the `data/` folder
- Clean project structure
- Consistent with Docker setup
- Won't accidentally commit to git

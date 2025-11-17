# Database Location Update

## What Changed

All database files now use the `data/` folder instead of the root directory. This keeps your project organized and makes it easier to backup and manage data files.

## File Changes

### Updated Files:
- `api.py` - Now uses `data/detections.db`
- `listen.py` - Now uses `data/detections.db`
- `ml_listen.py` - Now uses `data/detections_ml.db`
- `init_db.py` - Creates database in `data/` folder
- `init_ml_db.py` - Creates ML database in `data/` folder
- `test_data_richness.py` - Reads from `data/detections.db`

### New Files:
- `migrate_db_to_data.py` - Python script to migrate existing databases
- `migrate-databases.bat` - Batch file to run the migration
- `START-RTLSDR.bat` - Now includes `cd /d "%~dp0"` to work from shortcuts
- `STOP-RTLSDR.bat` - Now includes `cd /d "%~dp0"` to work from shortcuts
- `quickstart.bat` - Now includes `cd /d "%~dp0"` to work from shortcuts

## For Existing Installations

If you have existing database files in the root directory, run the migration:

```batch
migrate-databases.bat
```

Or run the Python script directly:

```powershell
python migrate_db_to_data.py
```

The script will:
1. Find any `detections.db` or `detections_ml.db` files in the root
2. Move them to the `data/` folder
3. Handle conflicts if databases exist in both locations
4. Create backups as needed

## For New Installations

Nothing special needed! The `data/` folder will be created automatically when you first run the system.

## Desktop Shortcut Fix

All batch scripts now change to their own directory before running, so they work correctly when:
- Run from a desktop shortcut
- Run from Windows Explorer
- Run from any directory in Command Prompt
- Run with "Run as Administrator"

This means your client can simply:
1. Create a desktop shortcut to `START-RTLSDR.bat`
2. Right-click and select "Run as Administrator"
3. Everything works!

## Benefits

- ✅ Better organization - all data files in one place
- ✅ Easier backups - just backup the `data/` folder
- ✅ Cleaner root directory
- ✅ Works with desktop shortcuts
- ✅ Consistent with Docker container setup
- ✅ Prevents accidental commits of database files (add `data/*.db` to `.gitignore`)

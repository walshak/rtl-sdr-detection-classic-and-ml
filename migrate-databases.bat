@echo off
REM Migrate database files from root to data folder
cd /d "%~dp0"

echo ==========================================
echo Database Migration to data/ folder
echo ==========================================
echo.
echo This will move any existing database files from
echo the root directory to the data/ folder.
echo.

python migrate_db_to_data.py

if errorlevel 1 (
    echo.
    echo [ERROR] Migration failed
    pause
    exit /b 1
)

echo.
echo Migration complete!
echo.
pause

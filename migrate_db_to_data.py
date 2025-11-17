#!/usr/bin/env python3
"""
Migrate existing database files from root to data folder.
Run this once to move any existing databases to the correct location.
"""

import os
import shutil

def migrate_databases():
    """Move databases from root to data folder."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')
    
    # Ensure data directory exists
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created data directory: {data_dir}")
    
    # List of database files to migrate
    db_files = [
        'detections.db',
        'detections_ml.db'
    ]
    
    migrated = []
    skipped = []
    
    for db_file in db_files:
        root_path = os.path.join(script_dir, db_file)
        data_path = os.path.join(data_dir, db_file)
        
        # Check if database exists in root
        if os.path.exists(root_path):
            # Check if database already exists in data folder
            if os.path.exists(data_path):
                # Ask user what to do
                print(f"\n{db_file} exists in both locations:")
                print(f"  Root: {root_path} ({os.path.getsize(root_path):,} bytes)")
                print(f"  Data: {data_path} ({os.path.getsize(data_path):,} bytes)")
                
                choice = input("Keep (r)oot, (d)ata, or (b)ackup root and use data? [b]: ").lower() or 'b'
                
                if choice == 'r':
                    # Move root to data, overwriting
                    shutil.move(root_path, data_path)
                    print(f"✓ Moved {db_file} from root to data (overwritten)")
                    migrated.append(db_file)
                elif choice == 'd':
                    # Keep data, backup root
                    backup_path = os.path.join(script_dir, 'backups', f"{db_file}.root.backup")
                    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                    shutil.move(root_path, backup_path)
                    print(f"✓ Backed up root {db_file} to: {backup_path}")
                    skipped.append(db_file)
                else:  # 'b' or default
                    # Backup root, keep data
                    backup_path = os.path.join(script_dir, 'backups', f"{db_file}.root.backup")
                    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                    try:
                        shutil.copy2(root_path, backup_path)
                        os.remove(root_path)
                        print(f"✓ Backed up root {db_file} to: {backup_path}")
                        skipped.append(db_file)
                    except PermissionError:
                        print(f"✗ Cannot move {db_file} - file is in use")
                        print(f"  Please close any applications using the database and try again")
                        print(f"  Or manually delete: {root_path}")
                        skipped.append(db_file)
            else:
                # Simply move to data folder
                shutil.move(root_path, data_path)
                print(f"✓ Moved {db_file} from root to data folder")
                migrated.append(db_file)
        else:
            # Check if already in data folder
            if os.path.exists(data_path):
                print(f"✓ {db_file} already in data folder")
                skipped.append(db_file)
            else:
                print(f"○ {db_file} not found (will be created on first run)")
    
    # Summary
    print("\n" + "="*50)
    print("MIGRATION SUMMARY")
    print("="*50)
    if migrated:
        print(f"Migrated: {', '.join(migrated)}")
    if skipped:
        print(f"Already in place: {', '.join(skipped)}")
    print(f"\nAll databases are now configured to use: {data_dir}")
    print("="*50)

if __name__ == "__main__":
    print("="*50)
    print("DATABASE MIGRATION TO data/ FOLDER")
    print("="*50)
    print("This will move database files from the root directory")
    print("to the data/ folder to maintain better organization.")
    print()
    
    migrate_databases()
    
    print("\nMigration complete! You can now run your applications.")
    input("\nPress Enter to exit...")

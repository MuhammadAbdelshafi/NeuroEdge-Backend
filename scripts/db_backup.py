import os
import subprocess
import argparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def get_db_url():
    """Retrieve database URL from environment or prompt user."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        db_url = input("Enter Postgres DATABASE_URL (e.g. postgresql://user:pass@host:port/db): ")
    return db_url

def backup_db():
    db_url = get_db_url()
    if not db_url:
        print("Database URL is required.")
        return

    # Create backups directory if it doesn't exist
    os.makedirs("backups", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/db_backup_{timestamp}.sql"
    
    # Run pg_dump
    print(f"Creating backup from {db_url}...")
    try:
        # We use pg_dump which needs to be installed on the system running this script
        subprocess.run(
            ["pg_dump", "-d", db_url, "-f", backup_file, "--no-owner", "--no-acl"],
            check=True
        )
        print(f"✅ Backup created successfully: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Backup failed: {e}")
    except FileNotFoundError:
        print("❌ pg_dump not found in system PATH. Please install PostgreSQL client tools.")

def restore_db():
    db_url = get_db_url()
    if not db_url:
        print("Database URL is required.")
        return

    # List available backups
    if not os.path.exists("backups"):
        print("No backups directory found.")
        return
        
    backups = [f for f in os.listdir("backups") if f.endswith(".sql")]
    if not backups:
        print("No backup files found in 'backups' directory.")
        return
        
    print("Available backups:")
    for i, file in enumerate(backups):
        print(f"{i+1}. {file}")
        
    idx = int(input("Select backup number to restore: ")) - 1
    if idx < 0 or idx >= len(backups):
        print("Invalid selection.")
        return
        
    backup_file = os.path.join("backups", backups[idx])
    
    confirm = input(f"Are you sure you want to restore {backup_file} to {db_url}? This may overwrite existing data. (y/N): ")
    if confirm.lower() != 'y':
        print("Restore cancelled.")
        return
        
    print(f"Restoring from {backup_file}...")
    try:
        subprocess.run(
            ["psql", "-d", db_url, "-f", backup_file],
            check=True
        )
        print("✅ Restore completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Restore failed: {e}")
    except FileNotFoundError:
        print("❌ psql not found in system PATH. Please install PostgreSQL client tools.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Database Backup/Restore Utility")
    parser.add_argument("action", choices=["backup", "restore"], help="Action to perform")
    
    args = parser.parse_args()
    
    if args.action == "backup":
        backup_db()
    elif args.action == "restore":
        restore_db()

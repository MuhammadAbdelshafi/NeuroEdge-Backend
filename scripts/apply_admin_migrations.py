import sqlite3
import os

DB_PATH = "user_service.db"

def run_migration():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found. Skipping migration (will be created by app).")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Migrating Database for Admin Module...")

    # 1. Add columns to users table
    try:
        # Check if login_count exists
        cursor.execute("SELECT login_count FROM users LIMIT 1")
        print("Column 'login_count' already exists.")
    except sqlite3.OperationalError:
        print("Adding 'login_count' to users...")
        cursor.execute("ALTER TABLE users ADD COLUMN login_count INTEGER DEFAULT 0")

    try:
        # Check if role exists
        cursor.execute("SELECT role FROM users LIMIT 1")
        print("Column 'role' already exists.")
    except sqlite3.OperationalError:
        print("Adding 'role' to users...")
        cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'user'")

    try:
        # Check if last_active_at exists
        cursor.execute("SELECT last_active_at FROM users LIMIT 1")
        print("Column 'last_active_at' already exists.")
    except sqlite3.OperationalError:
        print("Adding 'last_active_at' to users...")
        cursor.execute("ALTER TABLE users ADD COLUMN last_active_at TIMESTAMP")


    # 2. Create job_runs table
    print("Creating 'job_runs' table if not exists...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_runs (
        id VARCHAR PRIMARY KEY,
        job_name VARCHAR NOT NULL,
        status VARCHAR NOT NULL,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        finished_at TIMESTAMP,
        duration_sec FLOAT,
        items_processed INTEGER DEFAULT 0,
        error_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
    print("Migration Complete! ✅")

if __name__ == "__main__":
    run_migration()

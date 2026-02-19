import sqlite3
import os

db_path = "user_service.db"

if not os.path.exists(db_path):
    print(f"Database file {db_path} not found.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get columns info for 'users' table
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    
    print("Columns in 'users' table:")
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
        
    conn.close()

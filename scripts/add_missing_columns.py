import sqlite3
import os

db_path = "user_service.db"

if not os.path.exists(db_path):
    print(f"Database file {db_path} not found.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List of columns to add and their types
    new_columns = [
        ("age", "INTEGER"),
        ("nationality", "VARCHAR"),
        ("place_of_work", "VARCHAR"),
        ("years_of_experience", "INTEGER"),
        ("degree", "VARCHAR"),
        ("linkedin_profile", "VARCHAR")
    ]
    
    for col_name, col_type in new_columns:
        try:
            print(f"Adding column {col_name}...")
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            print(f"Successfully added {col_name}.")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"Column {col_name} already exists.")
            else:
                print(f"Error adding {col_name}: {e}")
                
    conn.commit()
    conn.close()
    print("Database schema update complete.")

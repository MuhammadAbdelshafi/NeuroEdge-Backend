import sqlite3
import os

DB_PATH = "user_service.db"

def add_column(cursor, table_name, column_name, column_type):
    try:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        print(f"Added column {column_name} to {table_name}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"Column {column_name} already exists in {table_name}")
        else:
            print(f"Error adding {column_name}: {e}")

def update_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Add classification columns
    add_column(cursor, "papers", "subspecialties", "TEXT") # JSON stored as TEXT in SQLite
    add_column(cursor, "papers", "research_type", "TEXT")
    add_column(cursor, "papers", "classification_confidence", "REAL")
    add_column(cursor, "papers", "classification_status", "TEXT DEFAULT 'pending'")

    conn.commit()
    conn.close()
    print("Schema update completed.")

if __name__ == "__main__":
    update_schema()

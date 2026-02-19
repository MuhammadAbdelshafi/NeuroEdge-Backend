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

def create_summary_table(cursor):
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paper_summaries (
                id VARCHAR PRIMARY KEY,
                paper_id VARCHAR NOT NULL UNIQUE,
                objective TEXT,
                methods TEXT,
                results TEXT,
                conclusion TEXT,
                clinical_relevance TEXT,
                key_points TEXT,  -- JSON stored as text
                model_used VARCHAR,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(paper_id) REFERENCES papers(id)
            )
        """)
        print("Created table paper_summaries")
    except sqlite3.OperationalError as e:
        print(f"Error creating table paper_summaries: {e}")

def update_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Add summarization status to papers
    add_column(cursor, "papers", "summarization_status", "TEXT DEFAULT 'pending'")
    
    # Create Summaries Table
    create_summary_table(cursor)

    conn.commit()
    conn.close()
    print("Schema update for summarization completed.")

if __name__ == "__main__":
    update_schema()

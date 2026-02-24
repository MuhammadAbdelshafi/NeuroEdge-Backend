import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "db", "users.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE new_papers RENAME TO papers")
    cursor.execute("CREATE UNIQUE INDEX ix_papers_doi ON papers (doi)")
    cursor.execute("CREATE UNIQUE INDEX ix_papers_pubmed_id ON papers (pubmed_id)")
    conn.commit()
    print("Table renamed successfully.")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()

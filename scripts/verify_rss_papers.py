import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "users.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

rows = cursor.execute("SELECT journal, title, pubmed_id FROM papers WHERE pubmed_id IS NULL limit 5").fetchall()
print(f"Found {len(rows)} RSS papers without PMIDs in the database:")
for r in rows:
    print(r)
    
count = cursor.execute("SELECT count(*) FROM papers").fetchone()[0]
print(f"Total papers in database: {count}")
    
conn.close()

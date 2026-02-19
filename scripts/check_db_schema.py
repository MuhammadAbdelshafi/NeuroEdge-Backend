import sqlite3

def check_schema():
    conn = sqlite3.connect('user_service.db')
    cursor = conn.cursor()
    
    print("--- Table Info: paper_summaries ---")
    cursor.execute("PRAGMA table_info(paper_summaries)")
    columns = cursor.fetchall()
    for col in columns:
        print(col)
        
    conn.close()

if __name__ == "__main__":
    check_schema()

import sqlite3

def count_pending_classification():
    conn = sqlite3.connect('user_service.db')
    cursor = conn.cursor()
    
    query = "SELECT COUNT(*) FROM papers WHERE classification_status IS NULL OR classification_status = 'pending'"
    cursor.execute(query)
    count = cursor.fetchone()[0]
    
    print(f"Total pending classification: {count}")
    conn.close()

if __name__ == "__main__":
    count_pending_classification()

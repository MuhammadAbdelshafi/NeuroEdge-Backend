import sqlite3

def check_counts():
    conn = sqlite3.connect('user_service.db')
    cursor = conn.cursor()
    
    print("--- Summarization Status Counts ---")
    cursor.execute("SELECT summarization_status, COUNT(*) FROM papers GROUP BY summarization_status")
    results = cursor.fetchall()
    for status, count in results:
        print(f"Status: {status} | Count: {count}")
        
    conn.close()

if __name__ == "__main__":
    check_counts()

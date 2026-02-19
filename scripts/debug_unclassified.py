import sqlite3
import sys

def check_unclassified():
    conn = sqlite3.connect('user_service.db')
    cursor = conn.cursor()
    
    print("--- Checking Unclassified Papers for 'The Lancet Neurology' ---")
    query = """
    SELECT id, title, classification_status, length(ifnull(abstract, '')) 
    FROM papers 
    WHERE journal = 'The Lancet Neurology' 
      AND (classification_status IS NULL OR classification_status != 'completed')
    LIMIT 5
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if not results:
        print("No unclassified papers found for this journal (unexpected based on stats).")
    
    for row in results:
        print(f"ID: {row[0]}")
        print(f"Title: {row[1]}")
        print(f"Status: {row[2]}")
        print(f"Abstract Length: {row[3]}")
        print("-" * 20)
        
    conn.close()

if __name__ == "__main__":
    check_unclassified()

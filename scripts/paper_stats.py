import sys
import os
import sqlite3

# Add the parent directory to sys.path
sys.path.append(".")

def generate_stats():
    conn = sqlite3.connect('user_service.db')
    cursor = conn.cursor()
    
    query = """
    SELECT 
        journal,
        COUNT(*) as total_fetched,
        SUM(CASE WHEN classification_status = 'completed' THEN 1 ELSE 0 END) as total_classified,
        SUM(CASE WHEN summarization_status = 'completed' THEN 1 ELSE 0 END) as total_summarized
    FROM papers
    WHERE journal IS NOT NULL
    GROUP BY journal
    ORDER BY total_fetched DESC
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    headers = ["Journal Name", "Fetched", "Classified", "Summarized"]
    
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in results:
        # journal name can be None
        widths[0] = max(widths[0], len(str(row[0] or "")))
        widths[1] = max(widths[1], len(str(row[1])))
        widths[2] = max(widths[2], len(str(row[2])))
        widths[3] = max(widths[3], len(str(row[3])))
        
    # Formatting string
    fmt = f"{{:<{widths[0]}}} | {{:>{widths[1]}}} | {{:>{widths[2]}}} | {{:>{widths[3]}}}"
    
    print("-" * (sum(widths) + 3*3))
    print(fmt.format(*headers))
    print("-" * (sum(widths) + 3*3))
    
    for row in results:
        print(fmt.format(str(row[0] or "Unknown"), row[1], row[2], row[3]))
        
    conn.close()

if __name__ == "__main__":
    generate_stats()

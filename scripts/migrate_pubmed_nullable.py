import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "db", "users.db")
    print(f"Migrating {db_path}...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # SQLite has limited ALTER TABLE support. 
    # To remove the NOT NULL constraint on pubmed_id, we need a pragma workaround or direct table recreation.
    # Fortunately, SQLite allows renaming and selecting.
    
    try:
        # Create new table
        cursor.execute('''
        CREATE TABLE new_papers (
            id VARCHAR NOT NULL, 
            doi VARCHAR, 
            pubmed_id VARCHAR, 
            title VARCHAR NOT NULL, 
            authors JSON, 
            journal VARCHAR, 
            publication_date DATETIME, 
            abstract TEXT, 
            full_text_link VARCHAR, 
            subspecialties JSON, 
            research_type VARCHAR, 
            classification_confidence FLOAT, 
            classification_status VARCHAR, 
            summarization_status VARCHAR, 
            fetch_status VARCHAR(10), 
            created_at DATETIME, 
            updated_at DATETIME, 
            PRIMARY KEY (id)
        )
        ''')
        
        # Copy data
        cursor.execute('INSERT INTO new_papers SELECT * FROM papers')
        
        # Drop old
        cursor.execute('DROP TABLE papers')
        
        # Rename new
        cursor.execute('ALTER TABLE new_papers RENAME TO papers')
        
        # Recreate indexes
        cursor.execute('CREATE UNIQUE INDEX ix_papers_doi ON papers (doi)')
        cursor.execute('CREATE UNIQUE INDEX ix_papers_pubmed_id ON papers (pubmed_id)')
        
        conn.commit()
        print("Migration to make pubmed_id nullable successful.")
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

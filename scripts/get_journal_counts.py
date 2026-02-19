
import sys
import os
from sqlalchemy import func

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models.paper import Paper
from app.db.models.summary import PaperSummary # Import to avoid mapper errors

def count_papers():
    db = SessionLocal()
    try:
        results = db.query(Paper.journal, func.count(Paper.id)).group_by(Paper.journal).order_by(func.count(Paper.id).desc()).all()
        
        print(f"\n{'Journal Name':<60} | {'Count'}")
        print("-" * 70)
        total = 0
        for journal, count in results:
            print(f"{journal:<60} | {count}")
            total += count
            
        print("-" * 70)
        print(f"{'Total Papers':<60} | {total}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    count_papers()

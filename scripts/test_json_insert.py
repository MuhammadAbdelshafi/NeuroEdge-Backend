import sys
import os

# Add the parent directory to sys.path
sys.path.append(".")

from app.db.session import SessionLocal
from app.db.base import Base
from app.db.models.summary import PaperSummary
from app.db.models.paper import Paper
import uuid

def test_insert():
    db = SessionLocal()
    try:
        # Create a dummy paper first (or find one)
        paper = db.query(Paper).first()
        if not paper:
            print("No paper found.")
            return

        print(f"Using paper: {paper.id}")
        
        # Check if summary exists
        existing = db.query(PaperSummary).filter(PaperSummary.paper_id == paper.id).first()
        if existing:
            print("Summary exists, deleting for test...")
            db.delete(existing)
            db.commit()

        # Try to insert simple JSON
        print("Inserting summary with simple list...")
        s1 = PaperSummary(
            paper_id=paper.id,
            key_points=["Point 1", "Point 2"],
            model_used="test"
        )
        db.add(s1)
        db.commit()
        print("Success: Simple list inserted.")
        
        # Cleanup
        db.delete(s1)
        db.commit()
        
        # Try to insert the complex list structure seen in logs
        print("Inserting summary with complex list...")
        complex_points = ["[", '{"point": "value"}', "]"] 
        s2 = PaperSummary(
            paper_id=paper.id,
            key_points=complex_points,
            model_used="test"
        )
        db.add(s2)
        db.commit()
        print("Success: Complex list inserted.")
        
        # Cleanup
        db.delete(s2)
        db.commit()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_insert()

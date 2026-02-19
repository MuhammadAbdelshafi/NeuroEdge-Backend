import sys
import os

# Add the parent directory to sys.path to allow importing app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models.paper import Paper
from app.db.models.summary import PaperSummary
from app.db.models.user import User
from sqlalchemy import func

def check_data():
    db = SessionLocal()
    try:
        # Check Users
        user_count = db.query(User).count()
        print(f"Total Users: {user_count}")
        if user_count > 0:
            first_user = db.query(User).first()
            print(f"Sample User: {first_user.email}, Subspecialties: {first_user.subspecialties}")

        # Check Papers
        paper_count = db.query(Paper).count()
        print(f"Total Papers: {paper_count}")

        # Check Classification Status
        classified_count = db.query(Paper).filter(Paper.classification_status == 'completed').count()
        print(f"Classified Papers: {classified_count}")
        
        # Check Summarization Status
        summarized_count = db.query(Paper).filter(Paper.summarization_status == 'completed').count()
        print(f"Summarized Papers: {summarized_count}")

        # Check Pending Status
        pending_summary_count = db.query(Paper).filter(Paper.summarization_status == 'pending').count()
        print(f"Pending Summary Papers: {pending_summary_count}")

        if paper_count > 0 and classified_count == 0:
            print("\nWARNING: Papers exist but none are classified. The feed might be empty if filters are strict.")
        
        if paper_count == 0:
            print("\nWARNING: No papers found in the database. You need to run the fetcher first.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_data()

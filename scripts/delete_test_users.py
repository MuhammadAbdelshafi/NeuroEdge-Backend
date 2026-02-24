import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.paper import Paper
from app.db.models.summary import PaperSummary

def delete_test_users():
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.role != 'admin').all()
        count = len(users)
        for user in users:
            db.delete(user)
        db.commit()
        print(f"Successfully deleted {count} non-admin users.")
        
        remaining = db.query(User).count()
        print(f"Total users remaining in DB: {remaining}")
    except Exception as e:
        print(f"Error deleting users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    delete_test_users()

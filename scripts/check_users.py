import sys
sys.path.append(".")
from app.db.session import SessionLocal
from app.db.models.user import User

def check_users():
    db = SessionLocal()
    users = db.query(User).all()
    print(f"Found {len(users)} users.")
    for u in users:
        print(f"User: {u.email}, ID: {u.id}")
    db.close()

if __name__ == "__main__":
    check_users()


import sys
import os

# Add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.paper import Paper # Needed for relationship mapping
from app.db.models.summary import PaperSummary # Needed for relationship mapping

def list_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Found {len(users)} users:")
        print("-" * 60)
        print(f"{'ID':<5} | {'Email':<30} | {'Role':<10} | {'Password Hash (First 20 chars)'}")
        print("-" * 60)
        for user in users:
            # Convert UUID to string and slice it for display
            uid_str = str(user.id)
            pw_display = user.password_hash[:20] + "..." if user.password_hash else "None"
            print(f"{uid_str[:5]:<5} | {user.email:<30} | {user.role:<10} | {pw_display}")
    except Exception as e:
        print(f"Error fetching users: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import io
    # Capture output to file
    with open("users_list.txt", "w") as f:
        sys.stdout = f
        list_users()
        sys.stdout = sys.__stdout__
    # Also print to console
    list_users()

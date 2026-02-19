import sys
import os

# Add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.paper import Paper # Needed for relationship mapping
from app.db.models.summary import PaperSummary # Needed for relationship mapping
from app.core.auth.password_hasher import PasswordHasher

def create_admin(email, password):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"User {email} exists. Updating role to 'admin' and resetting password...")
            user.role = "admin"
            user.password_hash = PasswordHasher.get_password_hash(password)
            db.commit()
            print("Successfully updated user role and password.")
        else:
            print(f"User {email} not found. Creating new admin...")
            user = User(
                email=email,
                password_hash=PasswordHasher.get_password_hash(password),
                full_name="System Admin",
                role="admin",
                is_active=True,
                email_verified=True
            )
            db.add(user)
            db.commit()
            print("Successfully created admin user.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_admin.py <email> <password>")
    else:
        create_admin(sys.argv[1], sys.argv[2])

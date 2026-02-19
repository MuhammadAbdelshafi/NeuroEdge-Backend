import sys
import os

# Add the parent directory to sys.path
sys.path.append(".")

from app.db.session import engine
from app.db.base import Base
# Import models to ensure they are registered with Base
from app.db.models.user import User
from app.db.models.paper import Paper
from app.db.models.favorites import user_favorites

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    init_db()

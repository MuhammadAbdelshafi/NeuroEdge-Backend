import os
import sys

# Add application root to PATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import engine, SessionLocal
from app.db.base import Base
# Import all models to ensure they are registered with Base.metadata
import app.db.models.paper
import app.db.models.user
import app.db.models.user_profile
import app.db.models.summary
import app.modules.analytics.models

def reset_db():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Recreating tables with current models...")
    Base.metadata.create_all(bind=engine)
    print("Database reset complete.")

if __name__ == "__main__":
    reset_db()

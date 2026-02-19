import sys
import os

# Add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.session import engine
from app.modules.analytics.models import UserEvent

def update_schema():
    print("Creating analytics tables...")
    UserEvent.metadata.create_all(bind=engine)
    print("Analytics tables created successfully.")

if __name__ == "__main__":
    update_schema()

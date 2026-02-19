import logging
import sys
import datetime

# Allow importing from parent directory
sys.path.append(".")

from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.paper import Paper
from app.modules.feed.service import FeedService
from app.modules.feed.jobs.notification_job import run_weekly_notification_job
# Import PaperSummary to Ensure Registry
from app.db.models.summary import PaperSummary

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_feed():
    print("Starting Debug Feed Service...")
    db = SessionLocal()
    try:
        # 1. Create a dummy user or get existing
        user = db.query(User).filter(User.email == "test@example.com").first()
        if not user:
            print("Creating test user...")
            from app.core.security import get_password_hash
            user = User(
                email="test@example.com",
                password_hash=get_password_hash("password"),
                full_name="Test User",
                is_active=True,
                email_verified=True, # Important for notification job
                email_frequency="weekly",
                subspecialties=["Stroke", "Epilepsy"], # Example preferences
                research_types=["Clinical Trial"]
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            print(f"Using existing test user: {user.email}")
            # Ensure preferences are set
            user.email_verified = True # FORCE UPDATE
            user.subspecialties = ["Stroke", "Epilepsy"]
            user.research_types = ["Clinical Trial"]
            user.email_frequency = "weekly"
            # Reset last notification date to force email
            user.last_notification_date = datetime.datetime.utcnow() - datetime.timedelta(days=10)
            db.commit()

        # 1.5 Create a Dummy Matching Paper
        paper_id = "test-paper-feed-001"
        existing_paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not existing_paper:
            print("Creating dummy paper for feed test...")
            dummy_paper = Paper(
                id=paper_id,
                title="New Stroke Clinical Trial",
                pubmed_id="12345678",
                publication_date=datetime.datetime.utcnow(),
                subspecialties=["Stroke"],
                research_type="Clinical Trial",
                summarization_status="completed",
                journal="Neurology Journal"
            )
            # Create a dummy summary
            summary = PaperSummary(
                paper_id=paper_id,
                objective="Test Objective",
                methods="Test Methods",
                results="Test Results",
                conclusion="Test Conclusion",
                key_points=["Point 1", "Point 2"]
            )
            db.add(dummy_paper)
            db.commit()
            db.add(summary)
            db.commit()

        # 2. Test Feed Service directly
        print("\n--- Testing FeedService.get_feed() ---")
        service = FeedService(db)
        result = service.get_feed(user, page=1, page_size=5)
        print(f"Found {result['total']} papers matching preferences.")
        for p in result['papers']:
            print(f"- {p.title} ({p.publication_date}) [Sub: {p.subspecialties}]")

        # 3. Test Notification Job
        print("\n--- Testing Notification Job ---")
        # Check user state
        u = db.query(User).filter(User.email == "test@example.com").first()
        print(f"DEBUG: User {u.email} - Verified: {u.email_verified}, Frequency: {u.email_frequency}")
        
        # This should trigger the console email because we reset the date
        run_weekly_notification_job()
            
    except Exception as e:
        logger.error(f"Error during debug feed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("\nDebug Feed Finished.")

if __name__ == "__main__":
    debug_feed()

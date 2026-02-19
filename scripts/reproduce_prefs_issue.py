import sys
import logging

# Allow importing from parent directory
sys.path.append(".")

from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.paper import Paper
from app.modules.feed.service import FeedService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_feed_preferences():
    db = SessionLocal()
    try:
        # 1. Get a test user (or the first user)
        user = db.query(User).first()
        if not user:
            logger.error("No user found to test with.")
            return

        logger.info(f"Testing with User: {user.email}")
        service = FeedService(db)

        # 2. Set Preferences: Filter for "Stroke" only
        logger.info("--- Step 1: Setting User Preferences to 'Stroke' ---")
        service.update_preferences(
            user=user,
            subspecialties=["Stroke"],
            research_types=[], # Empty means all? Or none? Let's assume broad for now
            email_frequency="daily"
        )
        
        # 3. Fetch Feed WITHOUT explicit params (should use user prefs)
        logger.info("--- Step 2: Fetching Feed (No Params) ---")
        result = service.get_feed(user=user, page=1, page_size=100)
        papers = result["papers"]
        
        stroke_count = 0
        non_stroke_count = 0
        
        for p in papers:
            if p.subspecialties and "Stroke" in p.subspecialties:
                stroke_count += 1
            else:
                non_stroke_count += 1
                logger.warning(f"Found non-Stroke paper: {p.title} | Subs: {p.subspecialties}")

        logger.info(f"Result: {stroke_count} Stroke papers, {non_stroke_count} Non-Stroke papers.")
        
        if non_stroke_count > 0:
            logger.error("TEST FAILED: Non-matching papers found in feed!")
        else:
            logger.info("TEST PASSED: Only matching papers found.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_feed_preferences()

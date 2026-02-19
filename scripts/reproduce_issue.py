import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.db.base import Base

# EXPLICITLY IMPORT ALL MODELS TO REGISTER THEM
from app.db.models.user import User
from app.db.models.summary import PaperSummary
from app.db.models.paper import Paper
# Add other models if necessary, but these seem to be the core ones involved in FeedService

from app.modules.feed.service import FeedService

def reproduce():
    db = SessionLocal()
    try:
        # TEST: Check if models are registered
        # print("Registered Mappers:", Base.registry.mappers)

        # 1. Get a user
        user = db.query(User).first()
        if not user:
            print("No user found in DB.")
            return

        print(f"User found: {user.email}")
        print(f"User Subspecialties: {user.subspecialties}")
        print(f"User Research Types: {user.research_types}")

        # 2. Check Lancet Papers metadata
        lancet_papers = db.query(Paper).filter(Paper.journal == "The Lancet Neurology").all()
        print(f"\nTotal Lancet Papers in DB: {len(lancet_papers)}")
        
        if not lancet_papers:
            print("No Lancet papers found to analyze.")
            return

        print("--- Sample Lancet Paper Subspecialties & Status & Type ---")
        for p in lancet_papers[:5]:
            print(f"Title: {p.title[:20]}... | Subs: {p.subspecialties} | Status: {p.summarization_status} | Type: {p.research_type}")

        # 3. Simulate Feed Service Logic
        service = FeedService(db)
        
        # Scenario A: User Profile + Lancet (What happens in Dashboard if no filters selected manually)
        print("\n--- Scenario A: User Profile + Lancet Filter ---")
        print("Calling service.get_feed(user, journals=['The Lancet Neurology'])")
        result_a = service.get_feed(user, journals=["The Lancet Neurology"])
        print(f"Papers returned: {len(result_a['papers'])}")
        
        # Scenario B: Explicitly requesting a subspecialty that Lancet papers HAVE
        # Find a common subspecialty
        common_sub = None
        for p in lancet_papers:
            if p.subspecialties and len(p.subspecialties) > 0:
                common_sub = p.subspecialties[0]
                break
        
        if common_sub:
            print(f"\n--- Scenario B: Matching Subspecialty ({common_sub}) + Lancet ---")
            result_b = service.get_feed(user, subspecialties=[common_sub], journals=["The Lancet Neurology"])
            print(f"Papers returned: {len(result_b['papers'])}")
        else:
            print("\nCould not find a common subspecialty in Lancet papers to test Scenario B.")

        # Scenario C: Empty Subspecialties (Simulate 'Select All' or 'No Preference' if possible)
        # Note: FeedService defaults to user.subspecialties if list is empty.
        print("\n--- Scenario C: Trying to override subspecialties with empty list ---")
        # This will likely default back to user profile due to: target_subs = subspecialties if subspecialties else user.subspecialties
        result_c = service.get_feed(user, subspecialties=[], journals=["The Lancet Neurology"])
        print(f"Papers returned (passing empty list): {len(result_c['papers'])}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    reproduce()

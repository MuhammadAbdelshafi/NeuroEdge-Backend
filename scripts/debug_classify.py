import logging
from app.db.session import SessionLocal
from app.modules.classification.service import PaperClassificationService
from app.db.models.paper import Paper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_classify():
    print("Starting Debug Classification...")
    db = SessionLocal()
    try:
        service = PaperClassificationService(db)
        
        # 1. Check for pending papers
        pending_count = db.query(Paper).filter(
            (Paper.classification_status == None) | (Paper.classification_status == 'pending')
        ).count()
        print(f"Pending papers before run: {pending_count}")
        
        # 2. Run Classification
        service.classify_all_pending(batch_size=10)
        
        # 3. Verify Results
        classified_papers = db.query(Paper).filter(Paper.classification_status == 'completed').limit(5).all()
        print("\n--- Classification Results (Sample) ---")
        for p in classified_papers:
            print(f"\nTitle: {p.title}")
            print(f"Subspecialties: {p.subspecialties}")
            print(f"Research Type: {p.research_type}")
            print(f"Confidence: {p.classification_confidence}")
            
    except Exception as e:
        logger.error(f"Error during debug classification: {e}")
    finally:
        db.close()
        print("\nDebug Classification Finished.")

if __name__ == "__main__":
    debug_classify()

import sys
import os
import time

# Add the parent directory to sys.path
sys.path.append(".")

from app.db.session import SessionLocal
from app.db.models.paper import Paper
from app.modules.classification.service import PaperClassificationService
from app.modules.summarization.service import SummarizationService

def process_backlog(batch_size=10):
    print(f"Starting batch processing for {batch_size} papers...")
    db = SessionLocal()
    try:
        # 1. Classification
        print("--- Running Classification ---")
        classifier_service = PaperClassificationService(db)
        
        while True:
            # Check if there are pending papers
            pending_count = db.query(Paper).filter(
                (Paper.classification_status == None) | (Paper.classification_status == 'pending')
            ).count()
            
            if pending_count == 0:
                print("All papers classified.")
                break
                
            print(f"Pending classifications: {pending_count}. Processing batch of {batch_size*5}...")
            classifier_service.classify_all_pending(batch_size=batch_size*5) # Larger batch for classification
            
        # 2. Summarization
        print("\n--- Running Summarization (Single Batch) ---")
        summarizer_service = SummarizationService(db)
        summarizer_service.summarize_next_batch(batch_size=batch_size)

        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("Batch processing finished.")

if __name__ == "__main__":
    # You can change batch size here
    process_backlog(batch_size=10)

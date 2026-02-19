import sys
import logging
import time

# Allow importing from parent directory
sys.path.append(".")

from app.db.session import SessionLocal
from app.db.models.paper import Paper
from app.db.models.summary import PaperSummary
from app.modules.summarization.service import SummarizationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_and_reprocess():
    db = SessionLocal()
    try:
        logger.info("Starting summary reset process...")
        
        # 1. Get all papers that have an abstract
        papers = db.query(Paper).filter(Paper.abstract.isnot(None), Paper.abstract != "").all()
        logger.info(f"Found {len(papers)} papers with abstracts to reset.")

        # 2. Reset Status and Delete Summaries
        count = 0
        for paper in papers:
            # Delete existing summary if it exists
            # We explicitly query to ensure we have the object to delete if relationship fetch is lazy
            if paper.summary:
                db.delete(paper.summary)
            
            # Reset status
            paper.summarization_status = "pending"
            count += 1
        
        db.commit()
        logger.info(f"Reset {count} papers. Status set to 'pending' and existing summaries deleted.")
        
        # 3. Reprocess Immediately
        logger.info("Starting immediate reprocessing...")
        service = SummarizationService(db)
        
        success = 0
        failed = 0
        
        for paper in papers:
            try:
                # Add a small delay to avoid hitting rate limits too hard if using API
                time.sleep(1) 
                service.summarize_paper(paper)
                success += 1
                logger.info(f"[{success}/{len(papers)}] Processed {paper.id}")
            except Exception as e:
                failed += 1
                logger.error(f"Failed to summarize paper {paper.id}: {e}")
        
        logger.info(f"Reprocessing complete. Success: {success}, Failed: {failed}")
                
    except Exception as e:
        logger.error(f"An error occurred during reset: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_and_reprocess()

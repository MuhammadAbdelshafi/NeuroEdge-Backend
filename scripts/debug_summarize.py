import logging
import sys
import argparse

# Allow importing from parent directory
sys.path.append(".")

from app.db.session import SessionLocal
from app.db.models.paper import Paper
from app.modules.summarization.service import SummarizationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_summarize(paper_id=None, limit=1):
    print("Starting Debug Summarization...")
    db = SessionLocal()
    try:
        service = SummarizationService(db)
        
        if paper_id:
            paper = db.query(Paper).filter(Paper.id == paper_id).first()
            if not paper:
                print(f"Paper {paper_id} not found.")
                return
            print(f"Summarizing specific paper: {paper.title}")
            summary = service.summarize_paper(paper)
        else:
            # Find a paper to summarize that DOES NOT have a summary yet
            paper = db.query(Paper).filter(
                (Paper.summarization_status == "pending") | (Paper.summarization_status == None),
                Paper.abstract.isnot(None),
                Paper.abstract != ""
            ).first()
            
            if not paper:
                print("No papers with abstracts found in DB.")
                return
                
            print(f"Summarizing random paper: {paper.title}")
            summary = service.summarize_paper(paper)
            
        print("\n--- Summary Result ---")
        print(f"Objective: {summary.objective}")
        print(f"Methods: {summary.methods}")
        print(f"Results: {summary.results}")
        print(f"Conclusion: {summary.conclusion}")
        print(f"Clinical Relevance: {summary.clinical_relevance}")
        print(f"Key Points: {summary.key_points}")
            
    except Exception as e:
        logger.error(f"Error during debug summarization: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("\nDebug Summarization Finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=str, help="Paper ID to summarize")
    args = parser.parse_args()
    
    debug_summarize(paper_id=args.id)

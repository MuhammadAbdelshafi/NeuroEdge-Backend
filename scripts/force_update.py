import logging
import sys
import asyncio
from app.db.session import SessionLocal

# Allow importing from parent directory
sys.path.append(".")

from app.modules.papers.jobs.fetch_job import run_fetch_job
from app.modules.classification.jobs.classification_job import run_classification_job
from app.modules.summarization.jobs.summarization_job import run_summarization_job

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def force_update():
    print("Starting Force Update...")
    
    print("\n1. Fetching Papers from PubMed (Last 2 days)...")
    # Note: run_fetch_job might need arguments or defaults. 
    # Assuming it fetches recent papers by default or we might need to tweak it.
    try:
        run_fetch_job() 
        print("Fetch Complete.")
    except Exception as e:
        print(f"Fetch Failed: {e}")

    print("\n2. Classifying Papers...")
    try:
        run_classification_job()
        print("Classification Complete.")
    except Exception as e:
        print(f"Classification Failed: {e}")

    print("\n3. Summarizing Papers (This might take a while)...")
    try:
        run_summarization_job()
        print("Summarization Complete.")
    except Exception as e:
        print(f"Summarization Failed: {e}")
        
    print("\nSystem Update Finished! You can now log in to the Frontend.")

if __name__ == "__main__":
    force_update()

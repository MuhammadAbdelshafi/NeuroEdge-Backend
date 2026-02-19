import logging
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.paper import Paper
from app.db.models.summary import PaperSummary # Fix relationship error
from app.modules.papers.fetchers.pubmed_fetcher import PubMedFetcher
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_dates():
    db = SessionLocal()
    try:
        papers = db.query(Paper).filter(Paper.pubmed_id.isnot(None)).all()
        logger.info(f"Found {len(papers)} papers to check.")
        
        # Group by 100
        batch_size = 100
        fetcher = PubMedFetcher(journal_list=[]) # Dummy list
        
        for i in range(0, len(papers), batch_size):
            batch = papers[i:i+batch_size]
            pmids = [p.pubmed_id for p in batch]
            
            logger.info(f"Fetching batch {i}-{i+len(batch)}...")
            fetched_data = fetcher.fetch_papers_by_ids(pmids)
            
            # Create a map for quick lookup
            fetched_map = {p['pubmed_id']: p for p in fetched_data}
            
            updated_count = 0
            for p in batch:
                if p.pubmed_id in fetched_map:
                    new_date = fetched_map[p.pubmed_id].get('publication_date')
                    if new_date and new_date != p.publication_date:
                        # Check if new date is not 1 Jan 2026 (unless it really is)
                        # Actually, if the fetcher sends 1 Jan 2026, it means it couldn't find other info.
                        # But we updated the fetcher!
                        
                        # Only update if different
                        if p.publication_date and p.publication_date.date() == new_date.date():
                             continue
                             
                        p.publication_date = new_date
                        updated_count += 1
            
            db.commit()
            logger.info(f"Updated {updated_count} papers in this batch.")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_dates()

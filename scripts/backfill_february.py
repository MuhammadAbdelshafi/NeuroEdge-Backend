import logging
import sys
import os
from datetime import datetime

# Add the parent directory to sys.path to allow importing from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.modules.papers.fetchers.pubmed_fetcher import PubMedFetcher
from app.modules.papers.deduplicator import Deduplicator
from app.db.repositories.paper_repo import PaperRepository, FetchLogRepository
from app.modules.papers.jobs.fetch_job import JOURNAL_LIST

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_backfill():
    logger.info("Starting Paper Backfill Job (Feb 1, 2026 - Today)...")
    db = SessionLocal()
    
    start_date = datetime(2026, 2, 1)
    end_date = datetime.now()
    
    try:
        fetcher = PubMedFetcher(journal_list=JOURNAL_LIST, start_date=start_date, end_date=end_date)
        deduplicator = Deduplicator(db)
        repo = PaperRepository(db)
        log_repo = FetchLogRepository(db)
        
        total_new = 0
        
        for journal in JOURNAL_LIST:
            try:
                papers = fetcher.fetch_journal(journal)
                new_papers_count = 0
                
                for paper_data in papers:
                    if deduplicator.is_new(paper_data):
                        repo.create({
                            "pubmed_id": paper_data['pubmed_id'],
                            "doi": paper_data.get('doi'),
                            "title": paper_data['title'],
                            "abstract": paper_data.get('abstract'),
                            "authors": paper_data.get('authors'),
                            "journal": journal,
                            "publication_date": paper_data.get('publication_date'),
                            "full_text_link": paper_data.get('full_text_link'),
                            "fetch_status": "pending"
                        })
                        new_papers_count += 1
                        total_new += 1
                
                log_repo.create_log(journal, "success", new_papers_count)
                logger.info(f"Journal {journal}: {new_papers_count} new papers ingested.")
                
            except Exception as e:
                logger.error(f"Failed to process journal {journal}: {e}")
                log_repo.create_log(journal, "failure", 0, str(e))
                
        logger.info(f"Backfill complete. Total new papers added: {total_new}")
        
    except Exception as e:
        logger.critical(f"Critical error in Backfill Job: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_backfill()

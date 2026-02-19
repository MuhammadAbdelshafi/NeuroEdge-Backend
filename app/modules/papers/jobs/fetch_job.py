import logging
from app.db.session import SessionLocal
from app.modules.papers.fetchers.pubmed_fetcher import PubMedFetcher
from app.modules.papers.deduplicator import Deduplicator
from app.modules.papers.publisher import PaperPublisher
from app.db.repositories.paper_repo import PaperRepository, FetchLogRepository

logger = logging.getLogger(__name__)

import json
import os

# Configurable Journal List (Loaded from config/journals.json)
def load_journals():
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))), "config", "journals.json")
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load journals.json: {e}")
        return []

from app.modules.admin.job_logging import log_job_run, JobName

JOURNAL_LIST = load_journals()

@log_job_run(JobName.FETCH.value)
def run_fetch_job():
    """
    Main job function:
    1. Iterates journals
    2. Fetches papers
    3. Deduplicates
    4. Stores
    5. Publishes event
    6. Logs
    """
    logger.info("Starting Paper Fetch Job...")
    db = SessionLocal()
    
    try:
        fetcher = PubMedFetcher(journal_list=JOURNAL_LIST)
        deduplicator = Deduplicator(db)
        repo = PaperRepository(db)
        log_repo = FetchLogRepository(db)
        publisher = PaperPublisher()
        
        # We process journal by journal to log granularity
        for journal in JOURNAL_LIST:
            try:
                papers = fetcher.fetch_journal(journal)
                new_papers_count = 0
                
                for paper_data in papers:
                    if deduplicator.is_new(paper_data):
                        # Save to DB
                        saved_paper = repo.create({
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
                        
                        # Publish Event
                        publisher.push_new_paper(saved_paper.id, saved_paper.title)
                        new_papers_count += 1
                
                # Log Success
                log_repo.create_log(journal, "success", new_papers_count)
                logger.info(f"Journal {journal}: {new_papers_count} new papers ingested.")
                
            except Exception as e:
                # Log Failure
                logger.error(f"Failed to process journal {journal}: {e}")
                log_repo.create_log(journal, "failure", 0, str(e))
                
    except Exception as e:
        logger.critical(f"Critical error in Fetch Job: {e}")
    finally:
        db.close()
        logger.info("Paper Fetch Job Finished.")

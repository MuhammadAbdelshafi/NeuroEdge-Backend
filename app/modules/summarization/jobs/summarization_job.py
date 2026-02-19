import logging
from app.db.session import SessionLocal
from app.modules.summarization.service import SummarizationService

from app.modules.admin.job_logging import log_job_run, JobName

logger = logging.getLogger(__name__)

@log_job_run(JobName.SUMMARIZE.value)
def run_summarization_job():
    """
    Job to summarize pending papers.
    """
    logger.info("Starting Paper Summarization Job...")
    db = SessionLocal()
    
    try:
        service = SummarizationService(db)
        # Process small batch to respect rate limits
        service.summarize_next_batch(batch_size=5)
        
    except Exception as e:
        logger.error(f"Error in Summarization Job: {e}")
    finally:
        db.close()
        logger.info("Paper Summarization Job Finished.")

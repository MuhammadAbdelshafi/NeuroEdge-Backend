import logging
from app.db.session import SessionLocal
from app.modules.classification.service import PaperClassificationService

from app.modules.admin.job_logging import log_job_run, JobName

logger = logging.getLogger(__name__)

@log_job_run(JobName.CLASSIFY.value)
def run_classification_job():
    """
    Job to classify pending papers.
    """
    logger.info("Starting Paper Classification Job...")
    db = SessionLocal()
    
    try:
        service = PaperClassificationService(db)
        # Classify pending papers
        service.classify_all_pending(batch_size=100) # Processing batch
        
    except Exception as e:
        logger.error(f"Error in Classification Job: {e}")
    finally:
        db.close()
        logger.info("Paper Classification Job Finished.")

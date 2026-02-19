import functools
import logging
import time
import traceback
from datetime import datetime
from app.db.session import SessionLocal
from app.db.models.job import JobRun, JobStatus

logger = logging.getLogger(__name__)


from enum import Enum

class JobName(Enum):
    FETCH = "fetch_papers"
    SUMMARIZE = "generate_summaries"
    CLASSIFY = "classify_papers"
    NOTIFY = "send_notifications"
    CLEANUP = "cleanup"

def log_job_run(job_name: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            db = SessionLocal()
            job_run = JobRun(
                job_name=job_name,
                status=JobStatus.RUNNING.value,
                started_at=datetime.utcnow()
            )
            db.add(job_run)
            db.commit()
            db.refresh(job_run)
            
            start_time = time.time()
            items_processed = 0
            
            try:
                # Execute the actual job
                # If the job returns a count, use it. Otherwise 0.
                result = func(*args, **kwargs)
                if isinstance(result, int):
                    items_processed = result
                
                duration = time.time() - start_time
                
                job_run.status = JobStatus.SUCCESS.value
                job_run.finished_at = datetime.utcnow()
                job_run.duration_sec = duration
                job_run.items_processed = items_processed
                
                db.commit()
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                error_msg = str(e)
                tb = traceback.format_exc()
                
                logger.error(f"Job {job_name} failed: {error_msg}")
                logger.error(tb)
                
                job_run.status = JobStatus.FAILED.value
                job_run.finished_at = datetime.utcnow()
                job_run.duration_sec = duration
                job_run.error_message = f"{error_msg}\n{tb}"
                
                db.commit()
                raise e
            finally:
                db.close()
                
        return wrapper
    return decorator

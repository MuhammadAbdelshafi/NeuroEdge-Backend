from apscheduler.schedulers.background import BackgroundScheduler
from app.modules.papers.jobs.fetch_job import run_fetch_job
from app.modules.classification.jobs.classification_job import run_classification_job
from app.modules.summarization.jobs.summarization_job import run_summarization_job
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def start_scheduler():
    if not scheduler.running:
        # Run Fetch Job Daily at 2:00 AM
        scheduler.add_job(run_fetch_job, 'cron', hour=2, minute=0, id='fetch_papers_daily')
        
        # Run classification job every hour
        scheduler.add_job(run_classification_job, 'interval', minutes=60, id='classify_papers_hourly')
        
        # Run summarization job every hour
        scheduler.add_job(run_summarization_job, 'interval', minutes=60, id='summarize_papers_hourly')
        
        scheduler.start()
        logger.info("Scheduler started: 'fetch_papers_daily', 'classify_papers_hourly', 'summarize_papers_hourly' registered.")

        from app.modules.feed.jobs.notification_job import run_weekly_notification_job
        # Run Email Job Weekly on Friday at 5:00 PM
        scheduler.add_job(run_weekly_notification_job, 'cron', day_of_week='fri', hour=17, minute=0, id='weekly_email_notification')
        logger.info("Scheduler added: 'weekly_email_notification'")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()

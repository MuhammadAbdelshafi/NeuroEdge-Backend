from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.paper import Paper
from app.modules.feed.email_service import email_service
from app.modules.feed.service import FeedService
import datetime
import logging

logger = logging.getLogger(__name__)

def run_weekly_notification_job():
    logger.info("Starting Weekly Notification Job...")
    db = SessionLocal()
    try:
        # 1. Find users who want weekly emails
        users = db.query(User).filter(
            User.email_frequency == 'weekly',
            User.email_verified == True # Ensure we only email valid users
        ).all()
        
        logger.info(f"Found {len(users)} users for weekly notifications.")
        
        feed_service = FeedService(db)
        
        for user in users:
            # 2. Find new papers for this user
            # "New" = published after last_notification_date OR within last 7 days if date is None
            last_date = user.last_notification_date
            if not last_date:
                last_date = datetime.datetime.utcnow() - datetime.timedelta(days=7)
                
            # Get feed matches (reusing logic but we need to filter by date)
            # Efficiently, we should add a date filter to FeedService, but for now let's reuse
            # getting the first page sorted by date
            feed_result = feed_service.get_feed(user, page=1, page_size=10, sort_by="date")
            papers = feed_result["papers"]
            
            # Filter papers strictly newer than last_notification_date
            new_papers = [p for p in papers if p.publication_date and p.publication_date > last_date]
            
            if not new_papers:
                logger.info(f"No new papers for user {user.email}")
                continue
                
            # 3. Send Email
            logger.info(f"Sending email to {user.email} with {len(new_papers)} papers.")
            
            subject = f"Weekly Neurology Update: {len(new_papers)} New Papers"
            
            # Simple HTML Body
            body_html = "<h1>Weekly Research Update</h1><ul>"
            for p in new_papers:
                # Use full_text_link or fallback to PubMed URL
                link = p.full_text_link if p.full_text_link else f"https://pubmed.ncbi.nlm.nih.gov/{p.pubmed_id}/"
                body_html += f"<li><a href='{link}'>{p.title}</a> ({p.journal})</li>"
            body_html += "</ul><p>Login to view summaries.</p>"
            
            email_service.send_email(user.email, subject, body_html)
            
            # 4. Update user state
            user.last_notification_date = datetime.datetime.utcnow()
            db.commit()
            
    except Exception as e:
        logger.error(f"Error in Notification Job: {e}")
    finally:
        db.close()
        logger.info("Weekly Notification Job Finished.")

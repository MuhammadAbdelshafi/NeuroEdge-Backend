from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.db.models.user import User
from app.db.models.paper import Paper
from app.db.models.summary import PaperSummary
from app.db.models.job import JobRun
from app.modules.admin.schemas import DashboardOverview, PaperStats, UserStats, PipelineStats

class AdminService:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_stats(self) -> DashboardOverview:
        now = datetime.utcnow()
        seven_days_ago = now - timedelta(days=7)
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # User Stats
        total_users = self.db.query(func.count(User.id)).scalar()
        new_users_7d = self.db.query(func.count(User.id)).filter(User.created_at >= seven_days_ago).scalar()
        active_users_7d = self.db.query(func.count(User.id)).filter(User.last_active_at >= seven_days_ago).scalar()

        # Paper Stats
        total_papers = self.db.query(func.count(Paper.id)).scalar()
        
        # Papers processed TODAY
        # Note: We don't have explicit 'fetched_at' on Paper, but created_at is close enough for 'fetched'
        fetched_today = self.db.query(func.count(Paper.id)).filter(Paper.created_at >= start_of_today).scalar()
        
        # Classified Today: We check updated_at AND status='completed'. 
        # Ideally we'd have a specific timestamp, but updated_at is a decent proxy if classification happened today.
        classified_today = self.db.query(func.count(Paper.id)).filter(
            Paper.classification_status == 'completed',
            Paper.updated_at >= start_of_today
        ).scalar()
        
        summarized_today = self.db.query(func.count(Paper.id)).filter(
            Paper.summarization_status == 'completed',
            Paper.updated_at >= start_of_today
        ).scalar()

        # Pipeline Stats
        failed_jobs_24h = self.db.query(func.count(JobRun.id)).filter(
            JobRun.status == 'failed',
            JobRun.started_at >= (now - timedelta(hours=24))
        ).scalar()

        pending_classification = self.db.query(func.count(Paper.id)).filter(
            Paper.classification_status == 'pending'
        ).scalar()
        
        pending_summarization = self.db.query(func.count(Paper.id)).filter(
            Paper.classification_status == 'completed',
            Paper.summarization_status == 'pending'
        ).scalar()

        return DashboardOverview(
            papers=PaperStats(
                total_papers=total_papers or 0,
                fetched_today=fetched_today or 0,
                classified_today=classified_today or 0,
                summarized_today=summarized_today or 0
            ),
            users=UserStats(
                total_users=total_users or 0,
                new_users_7d=new_users_7d or 0,
                active_users_7d=active_users_7d or 0
            ),
            pipeline=PipelineStats(
                failed_jobs_24h=failed_jobs_24h or 0,
                pending_classification=pending_classification or 0,
                pending_summarization=pending_summarization or 0
            )
        )

    def get_recent_jobs(self, limit: int = 20):
        return self.db.query(JobRun).order_by(JobRun.started_at.desc()).limit(limit).all()

    def get_users(self, skip: int = 0, limit: int = 50):
        # Join with UserEvent to get last active date if possible, or just return User
        # For now simple query
        return self.db.query(User).offset(skip).limit(limit).all()

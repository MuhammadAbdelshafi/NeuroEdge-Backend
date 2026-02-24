from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timedelta
from typing import Optional
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
        from app.db.models.user_profile import UserProfile
        from app.modules.admin.schemas import UserAdminStats
        
        users_with_profiles = self.db.query(User, UserProfile).outerjoin(
            UserProfile, User.id == UserProfile.user_id
        ).offset(skip).limit(limit).all()

        results = []
        for user, profile in users_with_profiles:
            stats = UserAdminStats(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                created_at=user.created_at,
                last_active_at=user.last_active_at,
                login_count=user.login_count,
                professional_title=profile.professional_title if profile else None,
                specialty=profile.specialty if profile else None,
                institution=profile.institution if profile else None,
                country=profile.country if profile else None
            )
            results.append(stats)
            
        return results

    def get_journal_stats(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        from app.modules.admin.schemas import JournalStat
        
        query = self.db.query(
            Paper.journal,
            func.count(Paper.id).label('total_papers'),
            # fetched_count = total papers (every paper in DB was fetched by definition)
            func.count(Paper.id).label('fetched_count'),
            # case-insensitive match for classification status
            func.sum(case((func.lower(Paper.classification_status) == 'completed', 1), else_=0)).label('classified_count'),
            # case-insensitive match for summarization status
            func.sum(case((func.lower(Paper.summarization_status) == 'completed', 1), else_=0)).label('summarized_count')
        )
        
        if start_date:
            query = query.filter(Paper.created_at >= start_date)
        if end_date:
            query = query.filter(Paper.created_at <= end_date)
            
        group_results = query.group_by(Paper.journal).all()
        
        stats = []
        for row in group_results:
            # Handle possible null journal name
            journal_name = row.journal if row.journal else "Unknown Journal"
            stats.append(JournalStat(
                journal_name=journal_name,
                total_papers=row.total_papers or 0,
                fetched_count=row.fetched_count or 0,
                classified_count=row.classified_count or 0,
                summarized_count=row.summarized_count or 0
            ))
            
        return stats

    def get_fetch_status(self):
        from app.modules.admin.schemas import FetchStatusResponse
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        fetched_last_24h = self.db.query(func.count(Paper.id)).filter(
            Paper.created_at >= last_24h
        ).scalar() or 0
        
        recent_job = self.db.query(JobRun).filter(
            JobRun.job_name == 'fetch_papers',
            JobRun.started_at >= start_of_today
        ).order_by(JobRun.started_at.desc()).first()
        
        if recent_job:
            return FetchStatusResponse(
                fetched_last_24h=fetched_last_24h,
                job_run_today=True,
                job_status=recent_job.status,
                job_started_at=recent_job.started_at
            )
        else:
            return FetchStatusResponse(
                fetched_last_24h=fetched_last_24h,
                job_run_today=False,
                job_status=None,
                job_started_at=None
            )

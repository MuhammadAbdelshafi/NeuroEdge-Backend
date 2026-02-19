from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import json
from app.modules.analytics.models import UserEvent
from app.modules.analytics.schemas import UsageStats, AnalyticsStats
from app.db.models.user import User

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def log_event(self, user_id: str, event_type: str, metadata: dict = None):
        try:
            event = UserEvent(
                user_id=user_id,
                event_type=event_type,
                metadata_json=json.dumps(metadata) if metadata else None
            )
            self.db.add(event)
            self.db.commit()
            return event
        except Exception as e:
            print(f"Error logging event: {e}")
            self.db.rollback()
            return None

    def get_usage_stats(self, days=7) -> AnalyticsStats:
        now = datetime.utcnow()
        start_date = now - timedelta(days=days)
        
        # Base query for timeframe
        base_query = self.db.query(UserEvent).filter(UserEvent.created_at >= start_date)

        # KPIs
        viewed = base_query.filter(UserEvent.event_type == 'viewed_paper').count()
        opened = base_query.filter(UserEvent.event_type == 'opened_summary').count()
        searched = base_query.filter(UserEvent.event_type == 'searched_topic').count()
        filtered = base_query.filter(UserEvent.event_type == 'filtered_subspecialty').count()
        
        # distinct active users based on events (login or any action)
        active_users = base_query.distinct(UserEvent.user_id).count()

        # Top Content
        # Top Searches
        top_searches = self.db.query(
            UserEvent.metadata_json, func.count(UserEvent.id).label('count')
        ).filter(
            UserEvent.event_type == 'searched_topic',
            UserEvent.created_at >= start_date
        ).group_by(UserEvent.metadata_json).order_by(desc('count')).limit(5).all()
        
        # Process JSON metadata for searches (assuming clean JSON string in GROUP BY, might need post-process if varying whitespace)
        # SQLite handles JSON as string, so exact match works.
        formatted_searches = []
        for meta_str, count in top_searches:
            try:
                term = json.loads(meta_str).get('query', 'unknown')
                formatted_searches.append({"term": term, "count": count})
            except:
                continue

        # Top Users
        top_users_query = self.db.query(
            User.email, User.full_name, func.count(UserEvent.id).label('count')
        ).join(UserEvent, User.id == UserEvent.user_id).filter(
            UserEvent.created_at >= start_date
        ).group_by(User.id).order_by(desc('count')).limit(5).all()
        
        formatted_users = [
            {"email": u[0], "name": u[1], "count": u[2]} for u in top_users_query
        ]

        # Top Subspecialties
        top_subs = self.db.query(
            UserEvent.metadata_json, func.count(UserEvent.id).label('count')
        ).filter(
            UserEvent.event_type == 'filtered_subspecialty',
            UserEvent.created_at >= start_date
        ).group_by(UserEvent.metadata_json).order_by(desc('count')).limit(5).all()

        formatted_subs = []
        for meta_str, count in top_subs:
            try:
                sub = json.loads(meta_str).get('subspecialty', 'unknown')
                formatted_subs.append({"subspecialty": sub, "count": count})
            except:
                continue
                
        # Top Papers (Viewed)
        top_papers = self.db.query(
            UserEvent.metadata_json, func.count(UserEvent.id).label('count')
        ).filter(
            UserEvent.event_type == 'viewed_paper',
            UserEvent.created_at >= start_date
        ).group_by(UserEvent.metadata_json).order_by(desc('count')).limit(5).all()

        formatted_papers = []
        for meta_str, count in top_papers:
            try:
                pid = json.loads(meta_str).get('paper_id', 'unknown')
                formatted_papers.append({"paper_id": pid, "count": count})
                # Ideally fetch Paper title here too
            except:
                continue

        return AnalyticsStats(
            usage=UsageStats(
                papers_viewed_7d=viewed,
                summaries_opened_7d=opened,
                searches_7d=searched,
                filters_7d=filtered,
                active_users_7d=active_users
            ),
            top_papers=formatted_papers,
            top_searches=formatted_searches,
            top_subspecialties=formatted_subs,
            top_users=formatted_users
        )

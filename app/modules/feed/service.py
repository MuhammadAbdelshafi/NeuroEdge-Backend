from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, cast, String, or_
from app.db.models.paper import Paper
from app.db.models.user import User
from typing import List, Optional

class FeedService:
    def __init__(self, db: Session):
        self.db = db

    def get_feed(
        self, 
        user: User, 
        page: int = 1, 
        page_size: int = 20, 
        sort_by: str = "date",
        subspecialties: Optional[List[str]] = None,
        research_types: Optional[List[str]] = None,
        journals: Optional[List[str]] = None,
        date_preset: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ):
        # Allow both completed and pending papers. 
        # Pending papers will show original abstract until summary is ready.
        query = self.db.query(Paper).filter(
            or_(
                Paper.summarization_status == 'completed',
                Paper.summarization_status == 'pending'
            )
        )

        # Apply Filters
        # 1. Subspecialties
        # Logic Change: Only fallback to user preferences if NO specific filters are applied (e.g. general feed)
        # OR if we want to ensure the feed is always personalized unless explicitly overridden.
        # But for "Browse by Journal", we usually want to see everything in that journal.
        
        target_subs = subspecialties
        
        # If no subspecialties requested, and no journals requested, fallback to user profile.
        # If journals ARE requested, we assume the user wants to see that journal's content regardless of their profile subs.
        if not subspecialties and not journals:
             target_subs = user.subspecialties
        
        # 2. Research Types
        target_types = research_types
        if not research_types and not journals:
            target_types = user.research_types
            
        if target_types:
            query = query.filter(Paper.research_type.in_(target_types))

        # 3. Journals
        if journals:
             query = query.filter(Paper.journal.in_(journals))

        # 4. Date Filter
        import datetime
        from datetime import timedelta
        
        target_start_date = None
        target_end_date = None

        if date_preset and date_preset != 'custom' and date_preset != 'all':
            today = datetime.date.today()
            if date_preset == 'today':
                target_start_date = today
            elif date_preset == '7d':
                target_start_date = today - timedelta(days=7)
            elif date_preset == '30d':
                target_start_date = today - timedelta(days=30)
            elif date_preset == '3m':
                target_start_date = today - timedelta(days=90)
            elif date_preset == '6m':
                target_start_date = today - timedelta(days=180)
            elif date_preset == '12m':
                target_start_date = today - timedelta(days=365)
            # 'all' implies no start date filter
            
        elif date_preset == 'custom':
            if date_from:
                target_start_date = datetime.datetime.strptime(date_from, "%Y-%m-%d").date()
            if date_to:
                target_end_date = datetime.datetime.strptime(date_to, "%Y-%m-%d").date()
        
        # Legacy support or direct start/end usage if preset not used but params present (fallback)
        if not date_preset and (date_from or date_to):
             if date_from:
                target_start_date = datetime.datetime.strptime(date_from, "%Y-%m-%d").date()
             if date_to:
                target_end_date = datetime.datetime.strptime(date_to, "%Y-%m-%d").date()

        if target_start_date:
            query = query.filter(Paper.publication_date >= target_start_date)
        if target_end_date:
            query = query.filter(Paper.publication_date <= target_end_date)

        # Sorting
        if sort_by == 'date':
            query = query.order_by(desc(Paper.publication_date))
        elif sort_by == 'date_asc':
            query = query.order_by(asc(Paper.publication_date))
        elif sort_by == 'title' or sort_by == 'title_asc':
            query = query.order_by(asc(Paper.title))
        elif sort_by == 'title_desc':
            query = query.order_by(desc(Paper.title))
        elif sort_by == 'journal':
            query = query.order_by(asc(Paper.journal))
        else:
             query = query.order_by(desc(Paper.publication_date))

        # Pagination - we need to fetch all matching candidates first if filtering by JSON in Python
        # This is inefficient for large datasets but necessary for SQLite + JSON lists without extensions
        
        # execution
        all_candidates = query.all()
        
        filtered_papers = []
        for p in all_candidates:
            # 1. Check Subspecialties
            if target_subs:
                if not p.subspecialties:
                    continue
                # If paper has ANY of the target subspecialties
                # p.subspecialties is a list of strings
                if not any(sub in p.subspecialties for sub in target_subs):
                    continue
            
            filtered_papers.append(p)
            
        # Update total after filtering
        total = len(filtered_papers)
        
        # Apply Pagination in Python
        offset = (page - 1) * page_size
        papers = filtered_papers[offset : offset + page_size]

        return {
            "papers": papers,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    def log_feed_interactions(self, user_id: str, subspecialties: List[str], research_types: List[str], journals: List[str]):
        try:
             from app.modules.analytics.service import AnalyticsService
             analytics = AnalyticsService(self.db)
             
             # Log Filter Events
             if subspecialties:
                 for sub in subspecialties:
                     analytics.log_event(user_id, "filtered_subspecialty", {"subspecialty": sub})
                     
             # Log Research Type Filters (Optional/Extra)
             # if research_types: ... 
             
             # Log Journal Filters
             if journals:
                 for j in journals:
                     analytics.log_event(user_id, "filtered_journal", {"journal": j})
                     
        except Exception as e:
            print(f"Error logging feed interactions: {e}")

    def update_preferences(self, user: User, subspecialties: List[str], research_types: List[str], email_frequency: str):
        user.subspecialties = subspecialties
        user.research_types = research_types
        user.email_frequency = email_frequency
        self.db.commit()
        self.db.refresh(user)
        return user

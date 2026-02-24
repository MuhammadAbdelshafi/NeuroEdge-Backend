from sqlalchemy.orm import Session
from app.db.models.paper import Paper, FetchLog, FetchStatus
from typing import List, Optional
import datetime

class PaperRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, paper_data: dict) -> Paper:
        db_paper = Paper(**paper_data)
        self.db.add(db_paper)
        self.db.commit()
        self.db.refresh(db_paper)
        return db_paper

    def get_by_doi(self, doi: str) -> Optional[Paper]:
        return self.db.query(Paper).filter(Paper.doi == doi).first()

    def get_by_pubmed_id(self, pubmed_id: str) -> Optional[Paper]:
        if pubmed_id is None:
            return None
        return self.db.query(Paper).filter(Paper.pubmed_id == pubmed_id).first()

    def get_by_title(self, title: str) -> Optional[Paper]:
        # Using exact match for now. Lowercase comparison for safety.
        from sqlalchemy import func
        return self.db.query(Paper).filter(func.lower(Paper.title) == func.lower(title)).first()
    
    def list_papers(self, skip: int = 0, limit: int = 20) -> List[Paper]:
        return self.db.query(Paper).order_by(Paper.publication_date.desc()).offset(skip).limit(limit).all()

    def count_papers(self) -> int:
        return self.db.query(Paper).count()

    def update_status(self, paper_id: str, status: FetchStatus):
        paper = self.db.query(Paper).filter(Paper.id == paper_id).first()
        if paper:
            paper.fetch_status = status
            self.db.commit()
            self.db.refresh(paper)
        return paper

class FetchLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_log(self, journal_name: str, status: str, num_papers: int, error_message: str = None) -> FetchLog:
        log = FetchLog(
            journal_name=journal_name,
            status=status,
            num_papers=num_papers,
            error_message=error_message
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

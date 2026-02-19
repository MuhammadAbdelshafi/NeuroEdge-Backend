from sqlalchemy.orm import Session
from app.db.repositories.paper_repo import PaperRepository

class Deduplicator:
    def __init__(self, db: Session):
        self.repo = PaperRepository(db)

    def is_new(self, paper_data: dict) -> bool:
        """Check if paper is new based on PMID or DOI"""
        # Check by PubMed ID (Primary check)
        if self.repo.get_by_pubmed_id(paper_data['pubmed_id']):
            return False
            
        # Check by DOI (Secondary check)
        if paper_data.get('doi') and self.repo.get_by_doi(paper_data['doi']):
            return False
            
        return True

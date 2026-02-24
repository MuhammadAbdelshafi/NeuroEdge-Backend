from sqlalchemy.orm import Session
from app.db.repositories.paper_repo import PaperRepository

class Deduplicator:
    def __init__(self, db: Session):
        self.repo = PaperRepository(db)

    def is_new(self, paper_data: dict) -> bool:
        """Check if paper is new based on PMID, DOI, or Title"""
        
        # 1. Check by PubMed ID (Primary check)
        if paper_data.get('pubmed_id') and self.repo.get_by_pubmed_id(paper_data['pubmed_id']):
            return False
            
        # 2. Check by DOI (Secondary check)
        if paper_data.get('doi') and self.repo.get_by_doi(paper_data['doi']):
            self._handle_potential_merge(paper_data, self.repo.get_by_doi(paper_data['doi']))
            return False
            
        # 3. Check by Title (Fallback for RSS papers jumping the gun)
        if paper_data.get('title'):
            existing_by_title = self.repo.get_by_title(paper_data['title'])
            if existing_by_title:
                self._handle_potential_merge(paper_data, existing_by_title)
                return False
                
        return True

    def _handle_potential_merge(self, incoming_data: dict, existing_paper):
        """If PubMed finds an RSS paper later, secretly update the RSS paper with the official PMID."""
        if incoming_data.get('pubmed_id') and not existing_paper.pubmed_id:
            existing_paper.pubmed_id = incoming_data['pubmed_id']
            # Re-fetch abstract if RSS feed abstract was missing or too short
            if incoming_data.get('abstract') and (not existing_paper.abstract or len(existing_paper.abstract) < 50):
                existing_paper.abstract = incoming_data['abstract']
            self.repo.db.commit()

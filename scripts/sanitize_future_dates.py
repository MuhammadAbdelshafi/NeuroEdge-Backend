import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the python path
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

from sqlalchemy import select
from datetime import datetime
from app.db.session import SessionLocal
from app.db.models.paper import Paper
from app.db.models.summary import PaperSummary # Required to resolve relationship

def sanitize_future_dates():
    with SessionLocal() as session:
        # Find all papers where publication_date is in the future
        current_time = datetime.now()
        query = select(Paper).where(Paper.publication_date > current_time)
        result = session.execute(query)
        future_papers = result.scalars().all()
        
        if not future_papers:
            print("No papers with future publication dates found.")
            return

        print(f"Found {len(future_papers)} papers with future dates. Fixing...")
        
        for paper in future_papers:
            print(f"Fixing paper {paper.pubmed_id}: {paper.publication_date} -> {current_time}")
            paper.publication_date = current_time
            
        session.commit()
        print("Done. Future dates sanitized.")

if __name__ == "__main__":
    sanitize_future_dates()

from app.db.session import SessionLocal
from app.db.models.paper import Paper
from app.db.models.summary import PaperSummary

db = SessionLocal()
papers = db.query(Paper).all()

print(f"Total papers: {len(papers)}")
for p in papers[:5]:
    print(f"ID: {p.id}")
    print(f"Title: {p.title}")
    print(f"Date: {p.publication_date}")
    print(f"Link: {p.full_text_link}")
    print(f"Authors: {p.authors}")
    print("-" * 20)

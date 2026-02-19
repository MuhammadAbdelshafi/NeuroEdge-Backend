from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.api.deps import get_current_user
from app.db.models.user import User
from app.modules.feed.service import FeedService
from pydantic import BaseModel
import datetime
import yaml

router = APIRouter()

class FeedResponse(BaseModel):
    papers: List[dict]
    total: int
    page: int
    page_size: int

class PreferencesUpdate(BaseModel):
    subspecialties: List[str]
    research_types: List[str]
    email_frequency: str

@router.get("/feed")
def get_user_feed(
    page: int = 1,
    page_size: int = 20,
    sort: str = "date",
    subspecialties: Optional[List[str]] = Query(None),
    research_types: Optional[List[str]] = Query(None),
    journals: Optional[List[str]] = Query(None),
    date_preset: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = FeedService(db)
    # Convert paper objects to dicts manually or use Pydantic models
    # Here we return the raw result from service, but we should serialize it
    result = service.get_feed(current_user, page, page_size, sort, subspecialties, research_types, journals, date_preset, date_from, date_to)
    
    # Log Interactions (Async ideally, but sync for now is fine)
    # Only log if explicit filters are provided
    if subspecialties or journals:
        service.log_feed_interactions(str(current_user.id), subspecialties, research_types, journals)
    
    # Serialize papers including the summary if available
    paper_list = []
    for p in result["papers"]:
        summary_data = None
        if p.summary:
            summary_data = {
                "objective": p.summary.objective,
                "methods": p.summary.methods,
                "results": p.summary.results,
                "conclusion": p.summary.conclusion,
                "key_points": p.summary.key_points
            }
            
        paper_list.append({
            "id": str(p.id),
            "title": p.title,
            "journal": p.journal,
            "authors": p.authors,
            "publication_date": p.publication_date,
            "subspecialties": p.subspecialties,
            "research_type": p.research_type,
            "summary": summary_data,
            "abstract": p.abstract, # Fallback if summary is missing
            "full_text_link": p.full_text_link
        })
        
    return {
        "papers": paper_list,
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"]
    }

@router.patch("/users/preferences")
def update_preferences(
    prefs: PreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = FeedService(db)
    updated_user = service.update_preferences(
        current_user, 
        prefs.subspecialties, 
        prefs.research_types, 
        prefs.email_frequency
    )
    return {"status": "success", "message": "Preferences updated"}

@router.get("/filters")
def get_filter_options(db: Session = Depends(get_db)):
    # In a real app, inject these dynamically.
    # For MVP, we import them or hardcode them, but ideally read from the YAML files.
    # To keep this module decoupled, we might duplicate or read the file.
    # Let's read from the YAML files used in Module 3.
    import yaml
    from app.db.models.paper import Paper
    
    with open("app/modules/classification/config/subspecialty_keywords.yaml", "r") as f:
        subs = yaml.safe_load(f)
        
    with open("app/modules/classification/config/research_type_keywords.yaml", "r") as f:
        types = yaml.safe_load(f)
        
    # Load Journals from config/journals.json
    import json
    import os
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "config", "journals.json")
        with open(config_path, 'r') as f:
            journal_list = json.load(f)
            journal_list.sort()
    except Exception as e:
        print(f"Error loading journals.json: {e}")
        # Fallback to DB
        journals = db.query(Paper.journal).distinct().all()
        journal_list = sorted([j[0] for j in journals if j[0]])

    return {
        "subspecialties": list(subs.keys()),
        "research_types": list(types.keys()),
        "journals": journal_list
    }

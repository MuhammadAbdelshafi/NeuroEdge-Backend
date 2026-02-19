from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.api_response import ApiResponse
from app.db.models.user import User
from app.db.models.preferences import UserSubspecialty, UserResearchType
from app.db.models.notification_preferences import NotificationPreference
from app.modules.papers.jobs.fetch_job import run_fetch_job
from typing import List, Dict, Any

router = APIRouter()

@router.get("/health", response_model=ApiResponse[str])
def health_check():
    return ApiResponse(success=True, data="OK", message="Service is healthy")

@router.post("/trigger-fetch", response_model=ApiResponse[bool])
def trigger_paper_fetch(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger the paper fetch job in the background.
    Requires authentication.
    """
    background_tasks.add_task(run_fetch_job)
    return ApiResponse(success=True, data=True, message="Paper fetch job triggered in background")

@router.get("/users/preferences", response_model=ApiResponse[List[Dict[str, Any]]])
def get_all_user_preferences(db: Session = Depends(get_db)):
    # This endpoint is for internal use by other modules (Paper Fetcher, etc.)
    # It aggregates user preferences efficiently.
    # In a real scenario, this might need pagination or filtering.
    
    users = db.query(User).filter(User.is_active == True).all()
    results = []
    
    for user in users:
        subspecialties = [s.subspecialty_id for s in db.query(UserSubspecialty).filter(UserSubspecialty.user_id == user.id).all()]
        research_types = [rt.research_type_id for rt in db.query(UserResearchType).filter(UserResearchType.user_id == user.id).all()]
        notif_pref = db.query(NotificationPreference).filter(NotificationPreference.user_id == user.id).first()
        
        results.append({
            "user_id": str(user.id),
            "email": user.email,
            "subspecialties": subspecialties,
            "research_types": research_types,
            "notification_frequency": notif_pref.frequency if notif_pref else "weekly"
        })
        
    return ApiResponse(success=True, data=results)

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.db.models.user import User
from app.db.repositories.preference_repo import PreferenceRepository
from app.modules.user.schemas.preferences import PreferencesResponse, PreferencesUpdate, NotificationPreferencesBase
from app.schemas.api_response import ApiResponse

router = APIRouter()

@router.get("/", response_model=ApiResponse[PreferencesResponse])
def get_my_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pref_repo = PreferenceRepository(db)
    subspecialties = pref_repo.get_subspecialties(current_user.id)
    research_types = pref_repo.get_research_types(current_user.id)
    notifications = pref_repo.get_notification_preferences(current_user.id)
    
    # Convert SQLAlchemy object to Pydantic model if it exists
    notif_data = None
    if notifications:
        notif_data = NotificationPreferencesBase(
            frequency=notifications.frequency,
            email_enabled=notifications.email_enabled,
            push_enabled=notifications.push_enabled,
            whatsapp_enabled=notifications.whatsapp_enabled
        )

    data = PreferencesResponse(
        subspecialties=subspecialties,
        research_types=research_types,
        notifications=notif_data
    )
    return ApiResponse(success=True, data=data)

@router.put("/", response_model=ApiResponse[PreferencesResponse])
def update_my_preferences(
    prefs_in: PreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pref_repo = PreferenceRepository(db)
    
    if prefs_in.subspecialties is not None:
        pref_repo.update_subspecialties(current_user.id, prefs_in.subspecialties)
        
    if prefs_in.research_types is not None:
        pref_repo.update_research_types(current_user.id, prefs_in.research_types)
        
    if prefs_in.notifications is not None:
        pref_repo.update_notification_preferences(current_user.id, prefs_in.notifications.model_dump())
        
    # Return updated preferences
    return get_my_preferences(current_user, db)

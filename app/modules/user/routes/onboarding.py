from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.db.models.user import User
from app.db.repositories.profile_repo import ProfileRepository
from app.db.repositories.preference_repo import PreferenceRepository
from app.modules.user.schemas.profile import ProfileUpdate
from app.modules.user.schemas.preferences import PreferencesUpdate
from app.schemas.api_response import ApiResponse
from pydantic import BaseModel

router = APIRouter()

class OnboardingRequest(BaseModel):
    profile: ProfileUpdate
    preferences: PreferencesUpdate

@router.post("/profile", response_model=ApiResponse[bool])
def complete_onboarding(
    data: OnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Update Profile
    profile_repo = ProfileRepository(db)
    existing_profile = profile_repo.get_by_user_id(current_user.id)
    if existing_profile:
        profile_repo.update(current_user.id, data.profile.model_dump(exclude_unset=True))
    else:
        profile_repo.create(current_user.id, data.profile.model_dump())
        
    # 2. Update Preferences
    pref_repo = PreferenceRepository(db)
    if data.preferences.subspecialties:
        pref_repo.update_subspecialties(current_user.id, data.preferences.subspecialties)
        
    if data.preferences.research_types:
        pref_repo.update_research_types(current_user.id, data.preferences.research_types)
        
    if data.preferences.notifications:
        pref_repo.update_notification_preferences(current_user.id, data.preferences.notifications.model_dump())
        
    return ApiResponse(success=True, data=True, message="Onboarding completed successfully")

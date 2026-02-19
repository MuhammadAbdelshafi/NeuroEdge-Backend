from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.db.models.user import User
from app.db.repositories.profile_repo import ProfileRepository
from app.modules.user.schemas.profile import ProfileResponse, ProfileUpdate
from app.schemas.api_response import ApiResponse

router = APIRouter()

@router.get("/", response_model=ApiResponse[ProfileResponse])
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile_repo = ProfileRepository(db)
    profile = profile_repo.get_by_user_id(current_user.id)
    if not profile:
        return ApiResponse(success=True, data=None, message="Profile not found")
    
    # Manually construct response to include user_id if needed, 
    # though Pydantic from_attributes usually handles it if the object has the attribute.
    # Here profile is an SQLAlchemy object.
    return ApiResponse(success=True, data=profile)

@router.put("/", response_model=ApiResponse[ProfileResponse])
def update_my_profile(
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile_repo = ProfileRepository(db)
    updated_profile = profile_repo.update(current_user.id, profile_in.model_dump(exclude_unset=True))
    return ApiResponse(success=True, data=updated_profile)

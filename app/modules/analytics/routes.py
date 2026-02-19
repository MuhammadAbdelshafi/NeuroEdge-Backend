from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.db.models.user import User
from app.modules.analytics.service import AnalyticsService
from app.modules.analytics.schemas import UserEventCreate, UserEventResponse
from app.schemas.api_response import ApiResponse

router = APIRouter()

@router.post("/events", response_model=ApiResponse[UserEventResponse])
def log_user_event(
    event_in: UserEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AnalyticsService(db)
    event = service.log_event(
        user_id=str(current_user.id),
        event_type=event_in.event_type,
        metadata=event_in.metadata
    )
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log event"
        )
        
    return ApiResponse(success=True, data=event)

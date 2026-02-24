from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.db.repositories.profile_repo import ProfileRepository
from app.db.repositories.user_repo import UserRepository
from app.core.auth.password_hasher import PasswordHasher
from app.core.auth.jwt_manager import JWTManager
from app.modules.user.schemas.auth import UserCreate, Token, UserLogin, UserUpdate, PasswordChange
from app.schemas.api_response import ApiResponse
from app.modules.user.schemas.profile import UserResponse
from app.db.models.user import User
import uuid

router = APIRouter()

@router.post("/signup", response_model=ApiResponse[Token])
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
    
    new_user = user_repo.create(
        email=user_in.email, 
        password=user_in.password, 
        phone=user_in.phone, 
        full_name=user_in.full_name,
        age=user_in.age,
        nationality=user_in.nationality,
        place_of_work=user_in.place_of_work or user_in.workplace, # Fallback to workplace if place_of_work is empty
        years_of_experience=user_in.years_of_experience,
        degree=user_in.degree,
        linkedin_profile=user_in.linkedin_profile
    )
    
    # Create profile if workplace is provided (Legacy support or additional profile data)
    # We might retire ProfileRepository later if all data moves to User table, 
    # but for now let's keep it if it stores distinct data. 
    # Current plan puts everything in User, so ProfileRepo might be redundant for 'workplace'.
    # We'll keep it for now to avoid breaking other things if they depend on Profile.
    if user_in.workplace and not user_in.place_of_work:
         # If place_of_work was NOT set but workplace WAS, we already used it for place_of_work above.
         # Do we still need Profile entry? Let's keep specific profile logic separate if needed.
         pass 

    if user_in.workplace:
        profile_repo = ProfileRepository(db)
        profile_repo.create(new_user.id, {"workplace": user_in.workplace})
    
    access_token = JWTManager.create_access_token(new_user.id)
    refresh_token = JWTManager.create_refresh_token(new_user.id)
    
    token_data = Token(
        access_token=access_token, 
        refresh_token=refresh_token,
        user={
            "id": str(new_user.id),
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role
        }
    )
    return ApiResponse(success=True, data=token_data)

@router.post("/login", response_model=ApiResponse[Token])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print(f"DEBUG LOGIN: Received username: '{form_data.username}', password length: {len(form_data.password)}")
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(form_data.username)
    if not user:
        print("DEBUG LOGIN: User not found!")
    elif not PasswordHasher.verify_password(form_data.password, user.password_hash):
        print("DEBUG LOGIN: Password mismatch!")
        
    if not user or not PasswordHasher.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = JWTManager.create_access_token(user.id)
    refresh_token = JWTManager.create_refresh_token(user.id)
    
    token_data = Token(
        access_token=access_token, 
        refresh_token=refresh_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    )
    print(f"LOGIN SUCECSS: Returning token data with user: {token_data.user}")

    # Log Login Event
    try:
        from app.modules.analytics.service import AnalyticsService
        analytics_service = AnalyticsService(db)
        analytics_service.log_event(user_id=str(user.id), event_type="login", metadata={})
    except Exception as e:
        print(f"Failed to log login event: {e}")

    return ApiResponse(success=True, data=token_data)

@router.get("/me", response_model=ApiResponse[UserResponse])
def read_users_me(current_user: User = Depends(get_current_user)):
    return ApiResponse(success=True, data=current_user)

@router.put("/me", response_model=ApiResponse[UserResponse])
def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    # Filter out None values to only update what's provided
    update_data = {k: v for k, v in user_in.model_dump().items() if v is not None}
    
    # Map 'phone' to 'phone_number' if present (database mismatch fix)
    if 'phone' in update_data:
        update_data['phone_number'] = update_data.pop('phone')
        
    updated_user = user_repo.update(current_user.id, update_data)
    return ApiResponse(success=True, data=updated_user)

@router.post("/change-password", response_model=ApiResponse[bool])
def change_password(
    password_in: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify current password
    if not PasswordHasher.verify_password(password_in.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="Incorrect current password"
        )
        
    user_repo = UserRepository(db)
    user_repo.change_password(current_user.id, password_in.new_password)
    
    return ApiResponse(success=True, data=True, message="Password updated successfully")

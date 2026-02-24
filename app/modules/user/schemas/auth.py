from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    phone: Optional[str] = None
    full_name: Optional[str] = None
    workplace: Optional[str] = None # Keeping for backward compatibility or mapping to place_of_work
    
    # New Fields
    age: int
    nationality: Optional[str] = "Egypt"
    place_of_work: Optional[str] = None
    years_of_experience: Optional[int] = 0
    degree: Optional[str] = None
    linkedin_profile: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict # Include user info (role, name, etc.)

class TokenRefresh(BaseModel):
    refresh_token: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None
    nationality: Optional[str] = None
    place_of_work: Optional[str] = None
    years_of_experience: Optional[int] = None
    degree: Optional[str] = None
    linkedin_profile: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str


from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
import uuid

class AcademicDegree(str, Enum):
    RESIDENT = "Resident"
    SPECIALIST = "Specialist"
    CONSULTANT = "Consultant"
    PROFESSOR = "Professor"
    STUDENT = "Student"
    OTHER = "Other"

class ProfileBase(BaseModel):
    workplace: Optional[str] = None
    academic_degree: Optional[AcademicDegree] = None
    years_experience: Optional[int] = None
    country: Optional[str] = None
    city: Optional[str] = None

class ProfileUpdate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    user_id: uuid.UUID
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: Optional[str] = None
    role: str = "user"
    is_active: bool
    email_verified: bool
    profile: Optional[dict] = None

    class Config:
        from_attributes = True

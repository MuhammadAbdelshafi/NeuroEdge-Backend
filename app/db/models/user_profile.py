from sqlalchemy import Column, String, Integer, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base
from app.db.models.user import GUID

class AcademicDegree(str, enum.Enum):
    RESIDENT = "Resident"
    SPECIALIST = "Specialist"
    CONSULTANT = "Consultant"
    PROFESSOR = "Professor"
    STUDENT = "Student"
    OTHER = "Other"

class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(GUID(), ForeignKey("users.id"), primary_key=True)
    workplace = Column(String, nullable=True)
    academic_degree = Column(Enum(AcademicDegree), nullable=True)
    years_experience = Column(Integer, nullable=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)

    user = relationship("User", backref="profile")

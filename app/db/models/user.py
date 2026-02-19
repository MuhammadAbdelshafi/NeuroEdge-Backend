import uuid
from sqlalchemy import Boolean, Column, String, DateTime, func, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import TypeDecorator, CHAR
import datetime

from sqlalchemy.orm import relationship
from app.db.base import Base
from app.db.models.favorites import user_favorites

# Compatibility for SQLite which doesn't support native UUID
class GUID(TypeDecorator):
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value

class User(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Extended Profile Fields
    age = Column(Integer, nullable=True)
    nationality = Column(String, default="Egypt")
    place_of_work = Column(String, nullable=True)
    years_of_experience = Column(Integer, default=0)
    degree = Column(String, nullable=True) # Resident, Specialist, Consultant
    linkedin_profile = Column(String, nullable=True)

    # Admin / Activity Fields
    role = Column(String, default="user") # 'admin' or 'user'. Using String for SQLite compatibility vs strict Enum
    last_active_at = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0)

    # User Preferences
    subspecialties = Column(JSON, default=list)  # List of strings
    research_types = Column(JSON, default=list)  # List of strings
    email_frequency = Column(String, default="weekly") # "daily", "weekly", "none"
    last_notification_date = Column(DateTime, nullable=True)

    # Relationships
    favorites = relationship("app.db.models.paper.Paper", secondary=user_favorites, backref="favorited_by")

    @property
    def profile(self):
        """
        Constructs a ProfileResponse-compatible dict from flattened User fields.
        """
        try:
            return {
                "user_id": self.id,
                "workplace": self.place_of_work,
                "academic_degree": self.degree,
                "years_experience": self.years_of_experience,
                "country": self.nationality,
                "city": None
            }
        except Exception as e:
            import traceback
            print(f"CRITICAL ERROR in User.profile: {e}")
            traceback.print_exc()
            return None

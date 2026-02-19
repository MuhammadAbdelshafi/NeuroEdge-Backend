from sqlalchemy.orm import Session
from app.db.models.user_profile import UserProfile
import uuid

class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: uuid.UUID) -> UserProfile:
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    def create(self, user_id: uuid.UUID, profile_data: dict) -> UserProfile:
        db_profile = UserProfile(user_id=user_id, **profile_data)
        self.db.add(db_profile)
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def update(self, user_id: uuid.UUID, profile_data: dict) -> UserProfile:
        db_profile = self.get_by_user_id(user_id)
        if db_profile:
            for key, value in profile_data.items():
                setattr(db_profile, key, value)
            self.db.commit()
            self.db.refresh(db_profile)
        return db_profile

from sqlalchemy.orm import Session
from app.db.models.preferences import UserSubspecialty, UserResearchType
from app.db.models.notification_preferences import NotificationPreference
import uuid
from typing import List

class PreferenceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_subspecialties(self, user_id: uuid.UUID) -> List[str]:
        from app.db.models.user import User
        user = self.db.query(User).filter(User.id == user_id).first()
        if user and user.subspecialties:
             # Ensure it returns a list, even if stored as something else (though JSON type ensures list/dict)
             return list(user.subspecialties)
        return []

    def update_subspecialties(self, user_id: uuid.UUID, subspecialties: List[str]):
        from app.db.models.user import User
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.subspecialties = subspecialties
            self.db.commit()
            self.db.refresh(user)

    def get_research_types(self, user_id: uuid.UUID) -> List[str]:
        from app.db.models.user import User
        user = self.db.query(User).filter(User.id == user_id).first()
        if user and user.research_types:
            return list(user.research_types)
        return []

    def update_research_types(self, user_id: uuid.UUID, research_types: List[str]):
        from app.db.models.user import User
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.research_types = research_types
            self.db.commit()
            self.db.refresh(user)

    def get_notification_preferences(self, user_id: uuid.UUID) -> NotificationPreference:
        return self.db.query(NotificationPreference).filter(NotificationPreference.user_id == user_id).first()

    def update_notification_preferences(self, user_id: uuid.UUID, data: dict) -> NotificationPreference:
        pref = self.get_notification_preferences(user_id)
        if not pref:
            pref = NotificationPreference(user_id=user_id, **data)
            self.db.add(pref)
        else:
            for key, value in data.items():
                setattr(pref, key, value)
        self.db.commit()
        self.db.refresh(pref)
        return pref

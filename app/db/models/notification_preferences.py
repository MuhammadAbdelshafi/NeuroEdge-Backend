from sqlalchemy import Column, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base
from app.db.models.user import GUID

class NotificationFrequency(str, enum.Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    user_id = Column(GUID(), ForeignKey("users.id"), primary_key=True)
    frequency = Column(Enum(NotificationFrequency), default=NotificationFrequency.WEEKLY)
    email_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=False)
    whatsapp_enabled = Column(Boolean, default=False)

    user = relationship("User", backref="notification_preferences")

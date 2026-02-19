from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime
import uuid
import json

from app.db.base import Base

class UserEvent(Base):
    __tablename__ = "user_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True) # Nullable for anonymous events if needed later
    event_type = Column(String(50), nullable=False, index=True)
    metadata_json = Column(Text, nullable=True) # SQLite doesn't strictly enforce JSON type, usually stored as Text/String
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", backref="events")

    # Removed conflicting metadata property
    # Serialization handled in service layer

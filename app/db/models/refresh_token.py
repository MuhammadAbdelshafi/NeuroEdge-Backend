from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
import datetime

from app.db.base import Base
from app.db.models.user import GUID

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(GUID(), primary_key=True)
    user_id = Column(GUID(), ForeignKey("users.id"))
    token_hash = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", backref="refresh_tokens")

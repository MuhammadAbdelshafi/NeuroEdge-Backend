from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.models.user import GUID

class UserSubspecialty(Base):
    __tablename__ = "user_subspecialties"

    user_id = Column(GUID(), ForeignKey("users.id"), primary_key=True)
    subspecialty_id = Column(String, primary_key=True) # References config ID

class UserResearchType(Base):
    __tablename__ = "user_research_types"

    user_id = Column(GUID(), ForeignKey("users.id"), primary_key=True)
    research_type_id = Column(String, primary_key=True) # References config ID

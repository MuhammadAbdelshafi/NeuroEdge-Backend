from sqlalchemy import Column, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid

class PaperSummary(Base):
    __tablename__ = "paper_summaries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    paper_id = Column(String, ForeignKey("papers.id"), nullable=False, unique=True)
    
    # Structured Summary Fields
    objective = Column(Text, nullable=True)
    methods = Column(Text, nullable=True)
    results = Column(Text, nullable=True)
    conclusion = Column(Text, nullable=True)
    clinical_relevance = Column(Text, nullable=True)
    key_points = Column(JSON, nullable=True) # List of bullet points
    
    model_used = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationship
    paper = relationship("Paper", back_populates="summary")

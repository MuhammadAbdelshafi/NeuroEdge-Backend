from sqlalchemy import Column, String, Integer, DateTime, Text, Enum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import uuid
import enum

class FetchStatus(str, enum.Enum):
    PENDING = "pending"
    CLASSIFIED = "classified"
    SUMMARIZED = "summarized"

class Paper(Base):
    __tablename__ = "papers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    doi = Column(String, unique=True, index=True, nullable=True) # DOI can be null sometimes
    pubmed_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    authors = Column(JSON, nullable=True) # Store as list of strings
    journal = Column(String, nullable=True)
    publication_date = Column(DateTime, nullable=True)
    abstract = Column(Text, nullable=True)
    full_text_link = Column(String, nullable=True)
    
    # Classification Fields
    subspecialties = Column(JSON, nullable=True) # List of subspecialties
    research_type = Column(String, nullable=True)
    classification_confidence = Column(Float, nullable=True)
    classification_status = Column(String, default="pending") # pending, completed, failed
    
    # Summarization Fields
    summarization_status = Column(String, default="pending") # pending, processing, completed, failed
    
    fetch_status = Column(Enum(FetchStatus), default=FetchStatus.PENDING)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    # Relationships
    summary = relationship("PaperSummary", back_populates="paper", uselist=False, cascade="all, delete-orphan")

class FetchLog(Base):
    __tablename__ = "fetch_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    journal_name = Column(String, nullable=False)
    fetched_at = Column(DateTime, default=func.now())
    status = Column(String, nullable=False) # 'success' or 'failure'
    num_papers = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

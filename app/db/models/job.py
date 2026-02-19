from sqlalchemy import Column, String, Integer, DateTime, Text, Float, Enum
from sqlalchemy.sql import func
from app.db.base import Base
import uuid
import enum

class JobStatus(str, enum.Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

class JobName(str, enum.Enum):
    FETCH = "fetch"
    CLASSIFY = "classify"
    SUMMARIZE = "summarize"

class JobRun(Base):
    __tablename__ = "job_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_name = Column(String, nullable=False) # Storing as string for SQLite simplicity
    status = Column(String, nullable=False)   # Storing as string for SQLite simplicity
    
    started_at = Column(DateTime, default=func.now())
    finished_at = Column(DateTime, nullable=True)
    duration_sec = Column(Float, nullable=True)
    
    items_processed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=func.now())

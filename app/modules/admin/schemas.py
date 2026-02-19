from pydantic import BaseModel, UUID4
from typing import List, Optional, Dict
from datetime import datetime

class JobRunResponse(BaseModel):
    id: str # Job IDs are strings
    job_name: str
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_sec: Optional[float] = None
    items_processed: int
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserAdminStats(BaseModel):
    id: UUID4 # User ID is UUID
    email: str
    full_name: Optional[str] = None
    role: str
    created_at: datetime
    last_active_at: Optional[datetime] = None
    login_count: int = 0
    
    class Config:
        from_attributes = True

class PaperStats(BaseModel):
    total_papers: int
    fetched_today: int
    classified_today: int
    summarized_today: int

class UserStats(BaseModel):
    total_users: int
    new_users_7d: int
    active_users_7d: int

class PipelineStats(BaseModel):
    failed_jobs_24h: int
    pending_classification: int
    pending_summarization: int

class DashboardOverview(BaseModel):
    papers: PaperStats
    users: UserStats
    pipeline: PipelineStats

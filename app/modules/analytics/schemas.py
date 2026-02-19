from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class UserEventCreate(BaseModel):
    event_type: str
    metadata: Optional[Dict[str, Any]] = None

class UserEventResponse(UserEventCreate):
    id: str
    user_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class UsageStats(BaseModel):
    papers_viewed_7d: int
    summaries_opened_7d: int
    searches_7d: int
    filters_7d: int
    active_users_7d: int

class AnalyticsStats(BaseModel):
    usage: UsageStats
    top_papers: list[dict]
    top_searches: list[dict]
    top_subspecialties: list[dict]
    top_users: list[dict]

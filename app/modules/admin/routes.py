from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user
from app.db.models.user import User
from app.modules.admin.service import AdminService
from app.modules.admin.schemas import DashboardOverview, JobRunResponse, UserAdminStats
from app.schemas.api_response import ApiResponse
from app.modules.analytics.schemas import AnalyticsStats
from app.modules.analytics.service import AnalyticsService

router = APIRouter()

def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

@router.get("/stats/overview", response_model=ApiResponse[DashboardOverview])
def get_stats_overview(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    service = AdminService(db)
    stats = service.get_dashboard_stats()
    return ApiResponse(success=True, data=stats)

@router.get("/stats/usage", response_model=ApiResponse[AnalyticsStats])
def get_usage_stats(
    days: int = 7,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    analytics = AnalyticsService(db)
    stats = analytics.get_usage_stats(days=days)
    return ApiResponse(success=True, data=stats)

@router.get("/jobs/recent", response_model=ApiResponse[List[JobRunResponse]])
def get_recent_jobs(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    service = AdminService(db)
    jobs = service.get_recent_jobs()
    return ApiResponse(success=True, data=jobs)

@router.get("/users", response_model=ApiResponse[List[UserAdminStats]])
def get_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    service = AdminService(db)
    users = service.get_users(skip, limit)
    return ApiResponse(success=True, data=users)

@router.get("/stats/journals")
def get_journal_stats(
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    from datetime import datetime
    parsed_start = None
    parsed_end = None
    if start_date:
        parsed_start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    if end_date:
        parsed_end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
    service = AdminService(db)
    stats = service.get_journal_stats(parsed_start, parsed_end)
    return ApiResponse(success=True, data=stats)

@router.get("/stats/fetch-status")
def get_fetch_status(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    service = AdminService(db)
    status_data = service.get_fetch_status()
    return ApiResponse(success=True, data=status_data)

@router.post("/jobs/trigger/fetch")
def trigger_fetch_job(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    import threading
    from app.modules.papers.jobs.fetch_job import run_fetch_job
    
    # Run fetch job in a background thread to avoid blocking the request
    thread = threading.Thread(target=run_fetch_job)
    thread.daemon = True
    thread.start()
    
    return ApiResponse(success=True, message="Scraping job triggered asynchronously. Check queue health for logs.")

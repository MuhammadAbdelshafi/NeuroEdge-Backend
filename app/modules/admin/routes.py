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

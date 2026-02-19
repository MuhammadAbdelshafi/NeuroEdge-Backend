from fastapi import APIRouter
from app.modules.user.routes.auth import router as auth_router
from app.modules.user.routes.onboarding import router as onboarding_router
from app.modules.user.routes.profile import router as profile_router
from app.modules.user.routes.preferences import router as preferences_router
from app.modules.admin.routes import router as admin_router
from app.api.taxonomy.routes import router as taxonomy_router
from app.api.internal.routes import router as internal_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(onboarding_router, prefix="/onboarding", tags=["onboarding"])
api_router.include_router(profile_router, prefix="/me/profile", tags=["profile"])
api_router.include_router(preferences_router, prefix="/me/preferences", tags=["preferences"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(taxonomy_router, prefix="/taxonomy", tags=["taxonomy"])
api_router.include_router(internal_router, prefix="/internal", tags=["internal"])

from app.api.papers.routes import router as papers_router
from app.api.favorites.routes import router as favorites_router

api_router.include_router(papers_router, prefix="/papers", tags=["papers"])
api_router.include_router(favorites_router, prefix="/favorites", tags=["favorites"])

from app.modules.analytics.routes import router as analytics_router
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])

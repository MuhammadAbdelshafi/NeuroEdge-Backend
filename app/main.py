from fastapi import FastAPI
from app.config.settings import settings
from app.api.router import api_router
from app.db.base import Base
from app.db.session import engine

# Create tables
Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

print(f"DEBUG: Loaded BACKEND_CORS_ORIGINS: {settings.BACKEND_CORS_ORIGINS}")
from fastapi import Request
from fastapi.responses import JSONResponse
import traceback

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        error_msg = traceback.format_exc()
        import logging
        logging.error(f"CRITICAL UNHANDLED EXCEPTION: {error_msg}")
        print(f"CRITICAL UNHANDLED EXCEPTION: {error_msg}") # Keep print as backup
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error", "details": str(exc)},
        )

# Set all CORS enabled origins (Moved down to be the outermost middleware)
# This prevents exception-handling middleware from stripping CORS headers
# or hiding the real error behind a CORS violation in the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://127.0.0.1:3000", 
        "http://127.0.0.1:3001",
        "https://neuroedge-frontend-production.up.railway.app" # common frontend railway name
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

from app.modules.feed.routes import router as feed_router
app.include_router(feed_router, prefix=settings.API_V1_STR, tags=["feed"])

@app.on_event("startup")
def startup_event():
    from app.core.scheduler import start_scheduler
    start_scheduler()

@app.on_event("shutdown")
def shutdown_event():
    from app.core.scheduler import stop_scheduler
    stop_scheduler()

@app.get("/")
def root():
    return {"message": "Welcome to the Neurology Research Aggregator - User Service"}

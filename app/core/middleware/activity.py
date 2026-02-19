from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.core.auth.jwt_manager import JWTManager
from app.db.session import SessionLocal
from app.db.models.user import User
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ActivityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Process the request first
        response = await call_next(request)
        
        # We only care about authenticated requests
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                # We decode token manually here to avoid dependencies on Depends() inside middleware
                # This is a lightweight check.
                payload = JWTManager.decode_token(token)
                if payload:
                    user_id = payload.get("sub")
                    if user_id:
                        self.update_last_active(user_id)
            except Exception:
                # Token might be invalid or expired, just ignore
                pass
                
        return response

    def update_last_active(self, user_id: str):
        # Fire and forget update
        # In high scale, this should be a background task or cached
        try:
            db = SessionLocal()
            stmt = User.__table__.update().where(User.id == user_id).values(last_active_at=datetime.utcnow())
            db.execute(stmt)
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Failed to update activity for user {user_id}: {e}")

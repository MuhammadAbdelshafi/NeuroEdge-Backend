from sqlalchemy import Column, ForeignKey, Table, DateTime
from sqlalchemy.sql import func
from app.db.base import Base
import app.db.models.paper # Ensure Paper model is loaded for relationship resolution

# Association table for User-Paper many-to-many relationship (Favorites)
user_favorites = Table(
    "user_favorites",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("paper_id", ForeignKey("papers.id"), primary_key=True),
    Column("created_at", DateTime, default=func.now()),
)

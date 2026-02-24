# Initialize all models here so that SQLAlchemy can resolve relationships properly
# importing this module anywhere ensures all models are registered.

from .user import User
from .user_profile import UserProfile
from .paper import Paper
from .summary import PaperSummary
from app.modules.analytics.models import UserEvent
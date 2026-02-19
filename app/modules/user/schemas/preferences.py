from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
import uuid

class NotificationFrequency(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class NotificationPreferencesBase(BaseModel):
    frequency: NotificationFrequency = NotificationFrequency.WEEKLY
    email_enabled: bool = True
    push_enabled: bool = False
    whatsapp_enabled: bool = False

class PreferencesUpdate(BaseModel):
    subspecialties: Optional[List[str]] = None
    research_types: Optional[List[str]] = None
    notifications: Optional[NotificationPreferencesBase] = None

class PreferencesResponse(BaseModel):
    subspecialties: List[str]
    research_types: List[str]
    notifications: Optional[NotificationPreferencesBase]

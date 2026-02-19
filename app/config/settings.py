import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Neurology Research Aggregator - User Service"
    API_V1_STR: str = "/api/v1"
    
    # DATABASE
    # Defaulting to SQLite for local development as agreed
    DATABASE_URL: str = "sqlite:///./user_service.db"
    
    # SECURITY
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_CHANGE_IN_PROD"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = []
    
    # EXTERNAL APIS
    OPENROUTER_API_KEY: str = ""
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra='ignore')

settings = Settings()

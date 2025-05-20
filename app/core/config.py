from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Coffee Shop API"
    
    # Database
    DATABASE_URL: str
    
    # Secret key for JWT
    SECRET_KEY: str
    
    # Mailtrap
    MAILTRAP_USERNAME: str
    MAILTRAP_PASSWORD: str
    MAILTRAP_HOST: str = "smtp.mailtrap.io"
    MAILTRAP_PORT: int = 2525
    
    # Email
    EMAILS_FROM_EMAIL: str = "coffee@example.com"
    EMAILS_FROM_NAME: str = "Coffee Shop"
    
    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
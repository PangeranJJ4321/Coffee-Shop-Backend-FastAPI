from pydantic_settings import BaseSettings
from typing import Optional

# No need for `true` import, it's not used here directly

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
    MAILTRAP_HOST: str 
    MAILTRAP_PORT: int 
    
    # Email
    EMAILS_FROM_EMAIL: str
    EMAILS_FROM_NAME: str
    
    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8   # 8 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30   # 30 days
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24
    
    # Frontend
    FRONTEND_URL: str

    # Midtrans
    MIDTRANS_SANDBOX : bool = True
    MIDTRANS_CLIENT_KEY: str
    MIDTRANS_SERVER_KEY : str

    # PASSWORD_RESET
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 1

    # Supabase Storage (ADD THESE NEW FIELDS)
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_BUCKET_NAME: str = "coffee-images"
    SUPABASE_ANON_KEY: str

    BASE_URL: str

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
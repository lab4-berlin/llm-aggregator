from pydantic_settings import BaseSettings
from typing import List
import os


def get_database_url() -> str:
    """Get database URL, supporting both Cloud SQL and standard connections."""
    # If DATABASE_URL is explicitly set (from secrets), use it
    database_url = os.getenv("DATABASE_URL", "")
    if database_url:
        return database_url
    
    # Otherwise, build from Cloud SQL connection name if available
    cloud_sql_connection = os.getenv("CLOUD_SQL_CONNECTION_NAME")
    if cloud_sql_connection:
        # Cloud SQL connection via Unix socket
        db_user = os.getenv("DB_USER", "llm_user")
        db_pass = os.getenv("DB_PASSWORD", "")
        db_name = os.getenv("DB_NAME", "llm_aggregator")
        unix_socket = f"/cloudsql/{cloud_sql_connection}"
        if db_pass:
            return f"postgresql://{db_user}:{db_pass}@/{db_name}?host={unix_socket}"
    
    # Fallback to empty string (will cause error, but that's expected)
    return ""


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = ""
    
    # Encryption
    ENCRYPTION_KEY: str
    
    # Server
    CORS_ORIGINS: str = "http://localhost:5173"
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Email (SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    FRONTEND_URL: str = "http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Override DATABASE_URL if not set in settings
if not settings.DATABASE_URL:
    settings.DATABASE_URL = get_database_url()


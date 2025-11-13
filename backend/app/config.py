from pydantic_settings import BaseSettings
from typing import List
import os


def get_database_url() -> str:
    """Get database URL, supporting both Cloud SQL and standard connections."""
    # Check if we're using Cloud SQL (via Unix socket)
    cloud_sql_connection = os.getenv("CLOUD_SQL_CONNECTION_NAME")
    if cloud_sql_connection:
        # Cloud SQL connection via Unix socket
        # Password comes from DB_PASSWORD secret or DATABASE_URL
        db_user = os.getenv("DB_USER", "llm_user")
        db_pass = os.getenv("DB_PASSWORD", "")
        db_name = os.getenv("DB_NAME", "llm_aggregator")
        unix_socket = f"/cloudsql/{cloud_sql_connection}"
        if db_pass:
            return f"postgresql://{db_user}:{db_pass}@/{db_name}?host={unix_socket}"
        else:
            # Fallback to DATABASE_URL if DB_PASSWORD not set
            return os.getenv("DATABASE_URL", "")
    else:
        # Standard connection string (local or connection string from secrets)
        return os.getenv("DATABASE_URL", "")


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

# Override DATABASE_URL if using Cloud SQL
if not settings.DATABASE_URL or os.getenv("CLOUD_SQL_CONNECTION_NAME"):
    settings.DATABASE_URL = get_database_url()


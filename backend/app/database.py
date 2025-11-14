from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import logging
import os

logger = logging.getLogger(__name__)

# Log the connection string (masked) for debugging
db_url_masked = settings.DATABASE_URL
if "@" in db_url_masked:
    # Mask password in logs
    parts = db_url_masked.split("@")
    if len(parts) == 2:
        user_pass = parts[0].split("://")[1] if "://" in parts[0] else parts[0]
        if ":" in user_pass:
            user = user_pass.split(":")[0]
            db_url_masked = db_url_masked.replace(user_pass, f"{user}:***")
logger.info(f"Connecting to database: {db_url_masked}")

# Check if Cloud SQL socket exists (for debugging)
if "/cloudsql/" in settings.DATABASE_URL:
    socket_path = settings.DATABASE_URL.split("host=")[1].split("&")[0] if "host=" in settings.DATABASE_URL else ""
    if socket_path:
        socket_dir = os.path.dirname(socket_path)
        logger.info(f"Cloud SQL socket directory: {socket_dir}")
        if os.path.exists(socket_dir):
            logger.info(f"Socket directory exists, checking for socket files...")
            try:
                files = os.listdir(socket_dir)
                logger.info(f"Files in socket directory: {files}")
            except Exception as e:
                logger.warning(f"Could not list socket directory: {e}")

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


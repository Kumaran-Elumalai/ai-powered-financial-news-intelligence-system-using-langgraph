from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config.config import Config

# Database URL (default sqlite:///news.db)
DB_URL = Config.DB_URL

engine = create_engine(
    DB_URL,
    echo=False,
    future=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)

Base = declarative_base()

def get_db():
    """FastAPI-style generator session (useful later)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

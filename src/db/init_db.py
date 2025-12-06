# src/db/init_db.py

from src.db.db import engine, Base
from src.db import models  # <-- REQUIRED to register models
from src.config.config import Config

def init_db():
    print("DB URL =", Config.DB_URL)
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database ready.")

if __name__ == "__main__":
    init_db()

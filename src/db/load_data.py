# src/db/load_data.py

import json
from pathlib import Path
from src.db.db import SessionLocal
from src.db.crud import upsert_article
from src.utils.logger import get_logger
from src.config.config import Config
print("DB URL used by load_data:", Config.DB_URL)

logger = get_logger("load_data")


def load(input_path: str = "data/news_final_enriched.json"):
    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"Input dataset not found: {path.resolve()}")

    with open(path, "r", encoding="utf-8") as f:
        docs = json.load(f)

    db = SessionLocal()

    for d in docs:
        upsert_article(db, d)

    db.close()

    logger.info(f"Loaded {len(docs)} articles into the database.")


if __name__ == "__main__":
    load()

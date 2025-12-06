import os
from dotenv import load_dotenv

load_dotenv()  # loads .env if present

class Config:
    # Vector store
    CHROMA_DIR = os.getenv("CHROMA_DIR", r"C:\financial_news_intel\chroma_db")

    # Embeddings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    # Dedup thresholds
    DEDUP_THRESHOLD = float(os.getenv("DEDUP_THRESHOLD", 0.90))
    
    # Database
    DB_URL = os.getenv("DB_URL", "sqlite:///C:/financial_news_intel/news.db")


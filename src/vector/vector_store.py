# src/vector/vector_store.py

import os
from chromadb.config import Settings

from src.utils.logger import get_logger
from src.config.config import Config

# Compatibility handling for Chroma versions
try:
    from chromadb import PersistentClient  # new versions
    CHROMA_MODE = "NEW"
except ImportError:
    from chromadb import Client            # older versions
    CHROMA_MODE = "OLD"

from sentence_transformers import SentenceTransformer

logger = get_logger("VectorStore")


class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_text(self, text: str):
        return self.model.encode(text).tolist()


class VectorStore:

    def __init__(self):
        self.logger = get_logger("VectorStore")

        # -------------------------------
        # Use NEW or OLD Chroma client
        # -------------------------------
        if CHROMA_MODE == "NEW":
            self.logger.info("Using New PersistentClient API")
            from chromadb import PersistentClient
            self.client = PersistentClient(path=Config.CHROMA_DIR)

        else:
            self.logger.info("Using Legacy Client API")
            from chromadb import Client
            self.client = Client(
                Settings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory=Config.CHROMA_DIR
                )
            )

        # Create / load collection
        self.collection = self.client.get_or_create_collection(
            name="news_articles",
            metadata={"hnsw:space": "cosine"}
        )

        self.embedder = EmbeddingService()

    # -----------------------------------
    # Add a document
    # -----------------------------------
    def add_document(self, doc_id, text, metadata):
        embedding = self.embedder.embed_text(text)

        self.collection.upsert(
            ids=[str(doc_id)],
            documents=[text],
            metadatas=[metadata],
            embeddings=[embedding]
        )

        self.logger.info(f"Indexed document {doc_id}")

    # -----------------------------------
    # Query vector search
    # -----------------------------------
    def query(self, query_text, top_k=5):
        embedding = self.embedder.embed_text(query_text)

        return self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )

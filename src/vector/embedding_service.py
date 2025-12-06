from sentence_transformers import SentenceTransformer
from src.config.config import Config

class EmbeddingService:
    """
    This service loads a SentenceTransformer model once
    and provides a simple interface to embed text.
    """
    
    def __init__(self):
        self.model = SentenceTransformer(Config.EMBEDDING_MODEL)

    def embed_text(self, text: str):
        """Return embedding for a single piece of text."""
        return self.model.encode(text, show_progress_bar=False).tolist()

    def embed_batch(self, texts: list[str]):
        """Return embeddings for multiple texts."""
        return self.model.encode(texts, show_progress_bar=False).tolist()

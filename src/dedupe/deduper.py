# src/dedupe/deduper.py
from typing import Optional, Dict, Any, List, Tuple
import numpy as np
from src.vector.vector_store import VectorStore
from src.utils.logger import get_logger
from src.utils import canonical_text
from src.config.config import Config



logger = get_logger("Deduper")

def flatten_embedding(emb):
    """
    Handle ChromaDB embedding formats safely:
    - [[...]] nested list
    - [...] flat list
    - None or empty → return None
    """
    if emb is None:
        return None
    if isinstance(emb, list):
        if len(emb) == 0:
            return None
        # case 1: nested like [[vector]]
        if isinstance(emb[0], list):
            return emb[0]
        # case 2: already flat
        return emb
    return None


def cosine_similarity(a: List[float], b: List[float]) -> float:
    # Fix nested embedding list issue from ChromaDB 1.3+
    a = flatten_embedding(a)
    b = flatten_embedding(b)
    if a is None or b is None:
        return 0.0
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)

    if np.all(a == 0) or np.all(b == 0):
        return 0.0

    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

class Deduper:
    """
    Deduper that uses VectorStore (Chroma) to find near neighbours,
    computes cosine similarity against returned candidate embeddings,
    and decides duplicates based on Config.DEDUP_THRESHOLD.
    """

    def __init__(self, top_k: int = 5, threshold: float | None = None):
        self.vs = VectorStore()
        self.top_k = top_k
        self.threshold = threshold if threshold is not None else Config.DEDUP_THRESHOLD
        self.collection = self.vs.collection
        self.embedder = self.vs.embedder
        logger.info(f"Deduper initialized: top_k={self.top_k} threshold={self.threshold}")

    def _get_candidate_ids(self, text: str) -> List[str]:
        # query with embedding to get candidate ids (may return [] if none)
        res = self.collection.query(
            query_embeddings=[self.embedder.embed_text(text)],
            n_results=self.top_k,
            where=None
        )
        # ids is nested: list of lists
        ids = res.get("ids", [[]])[0]
        return ids or []

    def _get_embeddings_by_ids(self, ids: List[str]) -> Dict[str, List[float]]:
        """
        Fetch stored embeddings for the given ids using collection.get.
        Returns dict id -> embedding (list)
        """
        if not ids:
            return {}
        resp = self.collection.get(ids=ids, include=["embeddings", "metadatas", "documents"])
        # resp['embeddings'] is nested list: [[emb1, emb2,...]]
        emb_list = resp.get("embeddings", [[]])[0]
        id_list = resp.get("ids", [[]])[0]
        clean_map = {}
        for i, emb in zip(id_list, emb_list):
            emb = flatten_embedding(emb)
            if emb is not None:
                clean_map[i] = emb
        return clean_map

    def is_duplicate(self, doc: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Returns dictionary {'duplicate_of': id, 'similarity': sim} if duplicate found,
        otherwise None.
        """
        text = canonical_text(doc)
        if not text:
            return None

        # 1) get candidate ids
        candidate_ids = self._get_candidate_ids(text)
        if not candidate_ids:
            return None

        # 2) fetch embeddings for candidates
        cand_emb_map = self._get_embeddings_by_ids(candidate_ids)

        # 3) compute doc embedding
        doc_emb = self.embedder.embed_text(text)

        # 4) compute cosine similarities
        best_sim = 0.0
        best_id = None
        for cid, cemb in cand_emb_map.items():
            sim = cosine_similarity(doc_emb, cemb)
            if sim > best_sim:
                best_sim = sim
                best_id = cid

        logger.debug(f"Doc {doc.get('id')} best_sim={best_sim} best_id={best_id}")

        if best_sim >= self.threshold:
            return {"duplicate_of": best_id, "similarity": best_sim}
        return None

    def assign_story_id_and_update(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine story_id for doc and update chroma metadata for that doc entry.
        Returns updated doc (with 'story_id' set).
        """
        dup = self.is_duplicate(doc)
        if dup:
            doc["story_id"] = dup["duplicate_of"]
            doc["_dedupe_info"] = {"duplicate": True, **dup}
            logger.info(f"Marked {doc.get('id')} duplicate of {dup['duplicate_of']} (sim={dup['similarity']:.4f})")
        else:
            doc["story_id"] = doc["id"]
            doc["_dedupe_info"] = {"duplicate": False, "similarity": None}
            logger.info(f"Marked {doc.get('id')} as new story")

        # update chroma metadata for the article to include story_id
        # if the doc isn't yet indexed in chroma, upsert it now
        text = canonical_text(doc)
        metadata = {
            "title": doc.get("title"),
            "source": doc.get("source"),
            "published": doc.get("published"),
            "url": doc.get("url"),
            "story_id": doc.get("story_id")
        }
        try:
            self.vs.collection.upsert(
                ids=[str(doc["id"])],
                documents=[text],
                metadatas=[metadata],
                embeddings=[self.embedder.embed_text(text)]
            )
        except Exception as e:
            logger.error(f"Failed to upsert doc {doc.get('id')} to vector store: {e}")
        return doc

    def process_documents(self, docs: List[Dict[str, Any]], persist: bool = True) -> List[Dict[str, Any]]:
        """
        Process a list of docs sequentially and assign story_ids.
        Returns the updated docs list. Optionally persist the vector store.
        """
        updated = []
        for i, doc in enumerate(docs):
            logger.debug(f"Processing doc {i+1}/{len(docs)} id={doc.get('id')}")
            # ensure doc has id
            if "id" not in doc:
                raise ValueError("Document missing 'id' field.")
            updated_doc = self.assign_story_id_and_update(doc)
            updated.append(updated_doc)
        if persist:
            try:
                self.vs.persist()
            except Exception:
                # Chroma v1.3 persists automatically; ignore
                pass
        return updated

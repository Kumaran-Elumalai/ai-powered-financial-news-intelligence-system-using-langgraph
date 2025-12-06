# src/pipeline/agents.py

import json
from src.dedupe.deduper import Deduper
from src.ner.ner_agent import run_ner
from src.impact.impact_mapper import ImpactMapper
from src.db.crud import upsert_article
from src.db.db import SessionLocal
from src.vector.vector_store import VectorStore
from src.utils.logger import get_logger

logger = get_logger("PipelineAgents")


# ------------------------
# Ingestion Agent
# ------------------------
def ingest_agent(data: dict):
    """
    Data = raw article dictionary:
    {
        "id": ...,
        "title": ...,
        "description": ...
    }
    """
    logger.info(f"[INGEST] Received article ID={data.get('id')}")
    return data


# ------------------------
# Dedup Agent
# ------------------------
deduper = Deduper(top_k=5, threshold=0.90)
def dedup_agent(data: dict):
    logger.info(f"[DEDUP] Processing article ID={data.get('id')}")
    updated = deduper.assign_story_id_and_update(data)
    return updated


# ------------------------
# NER Agent
# ------------------------
def ner_agent(data: dict):
    logger.info(f"[NER] Extracting entities for ID={data.get('id')}")
    data = run_ner(data)
    return data


# ------------------------
# Impact Agent
# ------------------------
mapper = ImpactMapper(mapping_csv="data/company_to_ticker.csv")
def impact_agent(data: dict):
    logger.info(f"[IMPACT] Mapping impacts for ID={data.get('id')}")
    data = mapper.compute_impacts(data)
    return data


# ------------------------
# Storage Agent
# ------------------------
def storage_agent(data: dict):
    logger.info(f"[STORE] Saving article ID={data.get('id')} to DB")
    db = SessionLocal()
    upsert_article(db, data)
    db.close()
    return data


# ------------------------
# Vector Index Agent
# ------------------------
vs = VectorStore()

def vector_agent(data: dict):
    logger.info(f"[VECTOR] Indexing article ID={data.get('id')}")

    # Extract title + full description cleanly
    title = data.get("title") or ""
    desc = data.get("description") or ""
    desc = desc.strip()

    # Build full searchable document
    text = f"{title}\n\n{desc}".strip()

    # Fallback text (ensure minimum length)
    if len(text) < 40:
        text += "\n\n(Short article, limited content.)"

    # Convert impacts list → JSON string for Chroma
    impacts_json = json.dumps(data.get("impacts", []), ensure_ascii=False)

    metadata = {
        "title": title,
        "source": data.get("source"),
        "published": data.get("published"),
        "url": data.get("url"),
        "story_id": str(data.get("story_id")),
        "impacts": impacts_json
    }

    # Store in Chroma
    vs.collection.upsert(
        ids=[str(data["id"])],
        documents=[text],
        metadatas=[metadata],
        embeddings=[vs.embedder.embed_text(text)]
    )

    return data


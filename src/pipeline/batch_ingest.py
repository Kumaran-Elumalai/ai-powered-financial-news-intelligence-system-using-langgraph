# src/pipeline/batch_ingest.py

import json
from pathlib import Path
from src.pipeline.graph import build_pipeline

pipeline = build_pipeline()

def run_batch(path="data/news_final_enriched.json"):
    file = Path(path)
    if not file.exists():
        raise FileNotFoundError(file)

    with open(file, "r", encoding="utf-8") as f:
        docs = json.load(f)

    for d in docs:
        pipeline.invoke(d)

    print("Batch ingestion completed!")

if __name__ == "__main__":
    run_batch()

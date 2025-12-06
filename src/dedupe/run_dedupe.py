# src/dedupe/run_dedupe.py
import json
from pathlib import Path
from src.dedupe.deduper import Deduper
from src.utils.logger import get_logger

logger = get_logger("run_dedupe")

def run(input_path: str = "data/news_final.json", output_path: str = "data/news_final_with_story.json"):
    input_p = Path(input_path)
    output_p = Path(output_path)

    if not input_p.exists():
        raise FileNotFoundError(f"Input dataset not found at {input_p.resolve()}")

    with open(input_p, "r", encoding="utf-8") as f:
        docs = json.load(f)

    deduper = Deduper(top_k=5)
    updated_docs = deduper.process_documents(docs, persist=True)

    # write output
    with open(output_p, "w", encoding="utf-8") as f:
        json.dump(updated_docs, f, indent=2, ensure_ascii=False)

    logger.info(f"Wrote deduplicated dataset to {output_p.resolve()}")

if __name__ == "__main__":
    run()

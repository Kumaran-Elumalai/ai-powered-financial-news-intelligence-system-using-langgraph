# src/ner/run_ner_and_impact.py

import json
from pathlib import Path
from src.ner.ner_agent import run_ner
from src.impact.impact_mapper import ImpactMapper
from src.utils.logger import get_logger
from src.vector.vector_store import VectorStore

logger = get_logger("run_ner_and_impact")


def run(
    input_path: str = "data/news_final_with_story.json",
    output_path: str = "data/news_final_enriched.json",
    mapping_csv: str | None = None
):

    in_p = Path(input_path)
    out_p = Path(output_path)

    if not in_p.exists():
        raise FileNotFoundError(f"Input not found: {in_p.resolve()}")

    # -------------------------------------------
    # Load input JSON
    # -------------------------------------------
    with open(in_p, "r", encoding="utf-8") as f:
        docs = json.load(f)

    # -------------------------------------------
    # 1) Run NER FIRST on all documents
    # -------------------------------------------
    logger.info("Running NER on all documents...")
    ner_processed_docs = []
    for d in docs:
        ner_processed_docs.append(run_ner(d))

    # -------------------------------------------
    # 2) Build ImpactMapper AFTER NER extraction
    # -------------------------------------------
    logger.info("Building ImpactMapper from extracted entities...")
    mapper = ImpactMapper(mapping_csv)

    if not mapper.table:
        company_names = []
        for d in ner_processed_docs:
            for e in d.get("entities", []):
                if e.get("label", "").upper() in ("ORG", "COMPANY"):
                    company_names.append(e.get("text"))
        mapper.build_auto_mapping(company_names)

    # -------------------------------------------
    # 3) Compute impacts AND update Chroma metadata
    # -------------------------------------------
    logger.info("Computing impacts + updating Chroma metadata...")
    vs = VectorStore()
    final_docs = []

    for d in ner_processed_docs:
        # Compute impacts
        d = mapper.compute_impacts(d)

        # Update Chroma metadata
        try:
            impacts_json = json.dumps(d.get("impacts", []), ensure_ascii=False)

            metadata = {
                "title": d.get("title"),
                "source": d.get("source"),
                "published": d.get("published"),
                "url": d.get("url"),
                "story_id": str(d.get("story_id")),
                "impacts": impacts_json
            }

            text = (d.get("title") or "") + "\n\n" + (d.get("description") or "")

            vs.collection.upsert(
                ids=[str(d["id"])],
                documents=[text],
                metadatas=[metadata],
                embeddings=[vs.embedder.embed_text(text)]
            )

        except Exception as ex:
            logger.exception(
                "Failed to update vector metadata for id=%s: %s",
                d.get("id"), ex
            )

        final_docs.append(d)

    # -------------------------------------------
    # 4) Save enriched output JSON
    # -------------------------------------------
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(final_docs, f, indent=2, ensure_ascii=False)

    logger.info("Wrote enriched dataset to %s", out_p.resolve())


if __name__ == "__main__":
    run()

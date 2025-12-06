# src/impact/impact_mapper.py

import csv
from pathlib import Path
from src.utils.logger import get_logger

logger = get_logger("ImpactMapper")

DEFAULT_MAPPING_PATH = Path("data/company_to_ticker.csv")


class ImpactMapper:
    """
    Maps detected NER entities to tickers using a clean CSV mapping.
    No fuzzy match. Strict and reliable.
    """

    def __init__(self, mapping_csv: str = None):
        self.mapping_path = Path(mapping_csv) if mapping_csv else DEFAULT_MAPPING_PATH
        self.table = []
        self._load_mapping()

    def _load_mapping(self):
        if not self.mapping_path.exists():
            logger.warning(f"Mapping CSV not found: {self.mapping_path}")
            return

        with open(self.mapping_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                self.table.append({
                    "company": r["company_name"],
                    "ticker": r["ticker"],
                    "sector": r.get("sector", "")
                })

        logger.info(f"Loaded {len(self.table)} mappings from CSV.")

    # ----------------------------------------------------------
    # STRICT Matching (no fuzzy logic)
    # ----------------------------------------------------------
    def strict_match(self, entity_text: str):
        text = entity_text.lower().strip()

        # direct match: company name or ticker exact
        for row in self.table:
            if text == row["company"].lower():
                return row
            if text == row["ticker"].lower():
                return row

        return None

    # ----------------------------------------------------------
    # Compute impacts
    # ----------------------------------------------------------
    def compute_impacts(self, doc):
        impacts = []
        ents = doc.get("entities", [])

        for e in ents:
            text = e.get("text", "").strip()
            label = e.get("label", "").upper()

            # Direct company or ticker match
            match = self.strict_match(text)
            if match:
                impacts.append({
                    "ticker": match["ticker"],
                    "company": match["company"],
                    "confidence": 1.0,
                    "type": "direct"
                })
                continue

            # Regulator → small universal impact
            if text.lower() in ("rbi", "sebi", "fed", "ecb"):
                impacts.append({
                    "ticker": text.upper(),
                    "company": text.upper(),
                    "confidence": 1.0,
                    "type": "regulator"
                })

        # Deduplicate by ticker
        unique = {}
        for imp in impacts:
            t = imp["ticker"]
            if t not in unique:
                unique[t] = imp

        doc["impacts"] = list(unique.values())
        return doc

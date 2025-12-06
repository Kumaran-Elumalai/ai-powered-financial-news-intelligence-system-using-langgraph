# src/query/query_engine.py

import json
import re
from datetime import datetime

from src.vector.vector_store import VectorStore
from src.ner.custom_ner import final_ner_logic_v4
from src.impact.impact_mapper import ImpactMapper
from src.utils.logger import get_logger

logger = get_logger("QueryEngine")

SECTOR_MAP = {
    "HDFC Bank": "BANKING",
    "ICICI Bank": "BANKING",
    "Axis Bank": "BANKING",
    "Kotak Mahindra Bank": "BANKING",
    "Infosys": "IT",
    "Wipro": "IT",
    "TCS": "IT",
    "Adani Enterprises": "INFRA"
}


class QueryEngine:

    def __init__(self):
        self.vs = VectorStore()
        self.mapper = ImpactMapper()

    # -----------------------------------------------------
    # STEP 1: Extract NER entities
    # -----------------------------------------------------
    def extract_query_entities(self, query: str):
        ents = final_ner_logic_v4(query)
        return [{"text": e["entity"], "label": e["type"]} for e in ents]

    # -----------------------------------------------------
    # STEP 2: Expand → company, ticker, sector
    # -----------------------------------------------------
    def expand_entities(self, entities):
        companies = [e["text"] for e in entities if e["label"] == "ORG"]
        tickers = [c.upper().replace(" ", "") for c in companies]
        sectors = [SECTOR_MAP.get(c) for c in companies if SECTOR_MAP.get(c)]

        return {
            "companies": companies,
            "tickers": tickers,
            "sectors": list(set(sectors)),
        }

    # -----------------------------------------------------
    # STEP 3: Ultra-strict ranking engine
    # -----------------------------------------------------
    def search(self, query: str, top_k=10):

        logger.info("Using ULTRA-STRICT ranking engine...")

        query_entities = self.extract_query_entities(query)
        expanded = self.expand_entities(query_entities)

        companies = set(expanded["companies"])
        tickers = set(expanded["tickers"])

        results = self.vs.query(query, top_k=top_k)
        final_ranked = []

        for i in range(len(results["ids"][0])):
            art_id = results["ids"][0][i]
            text = results["documents"][0][i]
            dist = results["distances"][0][i]

            meta = self.vs.collection.get(ids=[art_id])
            metadata = meta["metadatas"][0]
            impacts = json.loads(metadata.get("impacts", "[]"))

            # -------------------------------------------------------------
            # STRICT COMPANY MENTION CHECK
            # -------------------------------------------------------------
            lower_text = (text or "").lower()

            def mentions_company():
                for c in companies:
                    if re.search(rf"\b{re.escape(c.lower())}\b", lower_text):
                        return True
                for t in tickers:
                    if t.lower() in lower_text:
                        return True
                return False

            company_mentioned = mentions_company()

            # -------------------------------------------------------------
            # SCORING
            # -------------------------------------------------------------
            semantic = 1 / (1 + dist)

            impact_score = sum(
                1.0
                for imp in impacts
                if (
                    imp["ticker"] in tickers
                    or imp["company"].lower() in {c.lower() for c in companies}
                )
            )

            # 🚨 If article does NOT mention the company → huge penalty
            if not company_mentioned:
                impact_score = -5

            # Recency
            recency = 0
            pub = metadata.get("published")
            if pub:
                try:
                    dt = datetime.strptime(pub[:25], "%a, %d %b %Y %H:%M:%S")
                    recency = max(0, 1 - (datetime.utcnow() - dt).days / 40)
                except:
                    pass

            final_score = (
                semantic * 0.70 +
                impact_score * 0.25 +
                recency * 0.05
            )

            final_ranked.append({
                "id": art_id,
                "title": metadata.get("title"),
                "source": metadata.get("source"),
                "published": metadata.get("published"),
                "impacts": impacts,
                "similarity": round(semantic, 3),
                "impact_score": round(impact_score, 3),
                "recency_score": round(recency, 3),
                "final_score": round(final_score, 3),
                "doc_text": text,
            })

        # sort by final score
        final_ranked = sorted(final_ranked, key=lambda x: x["final_score"], reverse=True)

        # -----------------------------------------------------
        # STEP 4: LLM Summaries + Explanations (LAZY LOAD)
        # -----------------------------------------------------
        try:
            from src.llm.service import summarize_article, explain_impact
        except:
            summarize_article = None
            explain_impact = None

        TOP_N = 2  # summarise ONLY top 2

        for item in final_ranked[:TOP_N]:
            doc_id = item["id"]
            title = item["title"] or ""

            meta = self.vs.collection.get(ids=[doc_id])
            body = meta["documents"][0] if meta["documents"] else ""

            # --- Summary ---
            if summarize_article:
                item["summary"] = summarize_article(title, body)
            else:
                item["summary"] = "LLM unavailable."

            # --- Impact Explanation ---
            company = expanded["companies"][0] if expanded["companies"] else None
            if company and explain_impact:
                item["impact_explain"] = explain_impact(title, body, company)
            else:
                item["impact_explain"] = "LLM unavailable."

        return {
            "query": query,
            "query_entities": query_entities,
            "expanded": expanded,
            "results": final_ranked,
        }

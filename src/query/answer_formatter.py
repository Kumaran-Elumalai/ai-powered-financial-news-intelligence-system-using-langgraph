# src/query/answer_formatter.py

from typing import List, Dict
from datetime import datetime


class AnswerFormatter:

    @staticmethod
    def format_results(query: str, data: Dict):
        """
        Convert ranked search results into a clean, human-readable response.
        """

        entities = data.get("expanded", {})
        results = data.get("results", [])

        companies = entities.get("companies", [])
        tickers = entities.get("tickers", [])
        sectors = entities.get("sectors", [])

        # --------------------------
        # 1) Header Summary
        # --------------------------
        header = f"**Query:** {query}\n\n"
        header += "**Detected Entities:**\n"
        if companies:
            header += f"- Companies: {', '.join(companies)}\n"
        if tickers:
            header += f"- Tickers: {', '.join(tickers)}\n"
        if sectors:
            header += f"- Sectors: {', '.join(sectors)}\n"
        header += "\n"

        # --------------------------
        # 2) Top Articles Summary
        # --------------------------
        summary = "**Top Impactful News Articles:**\n\n"

        for i, item in enumerate(results[:5], start=1):

            title = item.get("title")
            pub = item.get("published")
            pub_str = pub if pub else "Unknown Date"

            impacts = item.get("impacts", [])
            impact_texts = [
                f"{imp['company']} ({imp['ticker']}) [{imp['type']}]"
                for imp in impacts
            ]
            impact_line = ", ".join(impact_texts) if impact_texts else "No direct impacts identified"

            summary += (
                f"**{i}. {title}**\n"
                f"- Published: {pub_str}\n"
                f"- Impact: {impact_line}\n"
                f"- Relevance Score: {item['final_score']}\n\n"
            )

        # --------------------------
        # 3) Explanation Section
        # --------------------------
        explanation = "**Why these articles matter:**\n"

        if tickers:
            explanation += f"- Articles are ranked by how strongly they affect **{tickers[0]}**.\n"
        if sectors:
            explanation += (
                f"- {', '.join(sectors)} sector news influences companies in that sector.\n"
            )
        explanation += (
            "- Impact scores boost articles where entities match companies or regulators.\n"
            "- Recency score increases relevance for fresh market-moving updates.\n"
            "- Semantic similarity ensures articles match the intent of the query.\n"
        )

        # --------------------------
        # Final Answer
        # --------------------------
        return header + summary + explanation

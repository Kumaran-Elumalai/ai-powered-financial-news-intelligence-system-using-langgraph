# src/query/query_agent.py

from src.query.answer_formatter import AnswerFormatter
from src.utils.logger import get_logger

logger = get_logger("QueryAgent")


class QueryAgent:
    """
    Lightweight QueryAgent — does NOT create QueryEngine at import time.
    QueryEngine will be created lazily on first run() call to avoid blocking
    the FastAPI import/startup sequence.
    """

    def __init__(self):
        self._engine = None

    def _get_engine(self):
        # Import and create engine lazily (only when needed)
        if self._engine is None:
            from src.query.query_engine import QueryEngine  # local import
            logger.info("Initializing QueryEngine (lazy)...")
            self._engine = QueryEngine()
        return self._engine

    def run(self, query: str) -> str:
        """
        Takes a user query, runs:
        - Query NER
        - Query expansion
        - Hybrid semantic + impact-aware search
        - Ranking
        - Formatting

        Returns final markdown string for the user.
        """
        logger.info(f"QueryAgent received query: {query}")

        try:
            engine = self._get_engine()
            results = engine.search(query)
            formatted = AnswerFormatter.format_results(query, results)
            return formatted
        except Exception as ex:
            logger.exception(f"QueryAgent failed for query={query}: {ex}")
            return f"Sorry, I could not process your query due to an internal error.\n\nDetails: {ex}"

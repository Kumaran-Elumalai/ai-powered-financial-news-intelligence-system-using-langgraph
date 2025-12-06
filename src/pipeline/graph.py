# src/pipeline/graph.py

from langgraph.graph import StateGraph
from src.pipeline.agents import (
    ingest_agent,
    dedup_agent,
    ner_agent,
    impact_agent,
    storage_agent,
    vector_agent
)

# Pipeline state is just a dict
State = dict

def build_pipeline():
    g = StateGraph(State)

    # Add nodes
    g.add_node("ingest", ingest_agent)
    g.add_node("dedup", dedup_agent)
    g.add_node("ner", ner_agent)
    g.add_node("impact", impact_agent)
    g.add_node("store", storage_agent)
    g.add_node("index", vector_agent)

    # Define edges
    g.add_edge("ingest", "dedup")
    g.add_edge("dedup", "ner")
    g.add_edge("ner", "impact")
    g.add_edge("impact", "store")
    g.add_edge("store", "index")

    # Start point
    g.set_entry_point("ingest")

    return g.compile()

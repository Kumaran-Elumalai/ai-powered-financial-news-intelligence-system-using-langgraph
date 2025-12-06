from fastapi import APIRouter
from src.api.schemas import IngestRequest, QueryRequest, QueryResponse
from src.pipeline.graph import build_pipeline
from src.query.query_agent import QueryAgent

router = APIRouter()

pipeline = build_pipeline()
query_agent = QueryAgent()


@router.post("/ingest")
def ingest_article(payload: IngestRequest):
    data = payload.dict()
    enriched = pipeline.invoke(data)
    return {"status": "success", "article": enriched}


@router.post("/query", response_model=QueryResponse)
def query_news(payload: QueryRequest):
    answer = query_agent.run(payload.query)
    return QueryResponse(result=answer)


@router.get("/health")
def health_check():
    return {"status": "ok"}

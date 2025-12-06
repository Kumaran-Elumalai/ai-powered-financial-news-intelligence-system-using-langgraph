from pydantic import BaseModel
from typing import Optional, List, Dict


class IngestRequest(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    source: Optional[str] = None
    published: Optional[str] = None
    url: Optional[str] = None


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    result: str

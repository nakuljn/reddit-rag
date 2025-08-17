from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")
    
class SearchResult(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any]
    distance: Optional[float] = None
    
class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    total_results: int

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="User question")
    top_k: int = Field(default=5, ge=1, le=10, description="Number of documents to retrieve")

class Source(BaseModel):
    id: str
    subreddit: Optional[str] = None
    url: Optional[str] = None
    score: Optional[int] = None

class QueryResponse(BaseModel):
    answer: str
    query: str
    sources: List[Source]
    total_sources: int

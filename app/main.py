from fastapi import FastAPI, HTTPException
from app.models import SearchRequest, SearchResponse, SearchResult, QueryRequest, QueryResponse, Source
from app.search import search_similar_documents, search_with_multiple_queries
from app.llm import LLMService
from app.query_processor import QueryProcessor

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Reddit-Powered LLM API is running."}

@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    try:
        docs = search_similar_documents(request.query, top_k=request.top_k)
        results = [
            SearchResult(
                id=doc["id"],
                text=doc["text"],
                metadata=doc["metadata"],
                distance=doc.get("distance")
            )
            for doc in docs
        ]
        return SearchResponse(
            results=results,
            query=request.query,
            total_results=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

async def generate_answer_with_context(query: str, top_k: int = 5, model: str = "claude") -> QueryResponse:
    try:
        query_processor = None
        if model and model.startswith("claude"):
            query_processor = QueryProcessor()
        
        if query_processor and query_processor.should_preprocess(query):
            search_queries = query_processor.enhance_query(query)
            docs = search_with_multiple_queries(search_queries, top_k=top_k)
        else:
            docs = search_similar_documents(query, top_k=top_k)
        
        llm_service = LLMService(model=model)
        answer, used_doc_ids = llm_service.generate_response(query, docs)
        
        sources = []
        for doc in docs:
            if doc["id"] in used_doc_ids:
                metadata = doc.get("metadata", {})
                sources.append(Source(
                    id=doc["id"],
                    subreddit=metadata.get("subreddit"),
                    url=metadata.get("url"),
                    score=metadata.get("score")
                ))
        
        return QueryResponse(
            answer=answer,
            query=query,
            sources=sources,
            total_sources=len(sources)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Configuration error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    return await generate_answer_with_context(request.query, request.top_k)

@app.get("/ingest/{subreddit}")
async def ingest_subreddit(subreddit: str, post_limit: int = 20, comment_limit: int = 2):
    """Manual endpoint to ingest Reddit data"""
    try:
        from app.ingestion import RedditIngester
        ingester = RedditIngester()
        result = ingester.ingest_subreddit(subreddit, post_limit=post_limit, comment_limit=comment_limit)
        return {"status": "success", "message": f"Ingested data from r/{subreddit}", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
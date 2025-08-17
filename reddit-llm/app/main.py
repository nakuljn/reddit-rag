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
    """Search for similar documents using vector similarity."""
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

async def generate_answer_with_context(query: str, top_k: int = 5) -> QueryResponse:
    """Generate an answer using enhanced RAG: query preprocessing + search + LLM generation."""
    try:
        # Step 1: Query preprocessing for better search (cost-optimized)
        query_processor = QueryProcessor()
        
        if query_processor.should_preprocess(query):
            print(f"[Query Preprocessing] Original: {query}")
            search_queries = query_processor.enhance_query(query)
            print(f"[Query Preprocessing] Enhanced queries: {search_queries}")
            # Use enhanced multi-query search
            docs = search_with_multiple_queries(search_queries, top_k=top_k)
        else:
            print(f"[Query Preprocessing] Skipped - using original query")
            # Use original single query search
            docs = search_similar_documents(query, top_k=top_k)
        
        print(f"[Search] Found {len(docs)} documents")
        
        # Step 2: Generate answer using LLM
        llm_service = LLMService()
        answer, used_doc_ids = llm_service.generate_response(query, docs)
        
        # Step 3: Extract sources for attribution (only relevant ones)
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
        # Handle validation errors (e.g., missing API keys)
        raise HTTPException(status_code=400, detail=f"Configuration error: {str(e)}")
    except Exception as e:
        # Handle other errors (network, API failures, etc.)
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """Ask a question and get an answer using Reddit-powered RAG."""
    return await generate_answer_with_context(request.query, request.top_k)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

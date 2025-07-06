# Reddit-Powered LLM System - Pragmatic HLD

## 1. System Overview
A lightweight system that answers user questions by retrieving relevant Reddit discussions and using them as context for LLM responses. Built for learning, but with production-quality patterns.

## 2. Core Principles
- **Start Simple, Scale Smart**: MVP first, complexity later
- **Learn by Doing**: Each component teaches a key concept
- **Production Patterns**: Use real-world best practices, even at small scale
- **Fast Iteration**: Deploy early, improve often

## 3. Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│  Reddit API     │────▶│   Ingestion  │────▶│  Vector DB  │
│  (PRAW)         │     │   Worker     │     │  (Chroma)   │
└─────────────────┘     └──────────────┘     └─────────────┘
                                                     │
┌─────────────────┐     ┌──────────────┐            │
│   User Query    │────▶│   FastAPI    │────────────┘
└─────────────────┘     │   Server     │
                        └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │   OpenAI/    │
                        │   Claude API │
                        └──────────────┘
```

## 4. Component Details

### 4.1 Ingestion Worker
**Purpose**: Fetch Reddit content and prepare it for search

```python
# Simple, focused implementation
class RedditIngester:
    def __init__(self, subreddits: List[str]):
        self.reddit = praw.Reddit(...)
        self.embedder = OpenAIEmbeddings()
        self.vector_db = Chroma(persist_directory="./chroma_db")
    
    def ingest_subreddit(self, subreddit: str, limit: int = 100):
        # Fetch top posts from last week
        # Create smart chunks
        # Generate embeddings
        # Store in Chroma with metadata
```

**Key Decisions**:
- Use PRAW (official Reddit API) - reliable, well-documented
- Process top 100 posts per subreddit initially
- Store post + top 3 comments as one document
- Run manually first, cron job later

### 4.2 Vector Storage (Chroma)
**Why Chroma?**
- Embedded database - no separate service to manage
- Persistent storage out of the box
- Built-in metadata filtering
- Perfect for learning/MVP

**Document Structure**:
```json
{
    "id": "post_id_comment_hash",
    "text": "Title: How to learn FastAPI?\n\nPost: I'm new to...\n\nTop Comment: Start with...",
    "metadata": {
        "subreddit": "fastapi",
        "post_id": "abc123",
        "score": 42,
        "created_utc": 1701234567,
        "url": "reddit.com/r/fastapi/..."
    }
}
```

### 4.3 API Server (FastAPI)
**Why FastAPI?**
- Automatic API documentation
- Type hints = better code
- Async support built-in
- Great for learning modern Python

```python
@app.post("/ask")
async def ask_question(query: QueryRequest) -> QueryResponse:
    # 1. Search vector DB for relevant posts
    # 2. Create prompt with context
    # 3. Call LLM
    # 4. Return response with sources
```

### 4.4 LLM Integration
**Smart Approach**:
- Start with OpenAI (simpler API)
- Add Claude later (learn differences)
- Use Langchain for abstraction

```python
class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo")
        self.prompt = PromptTemplate(...)
    
    async def generate_response(self, query: str, context: List[Document]):
        # Simple, readable prompt construction
        # Clear source attribution
        # Token limit handling
```

## 5. Data Flow

### Ingestion Flow (Run Weekly)
1. **Fetch**: Get top 100 posts from r/programming, r/learnpython
2. **Filter**: Score > 10, not NSFW, has meaningful content
3. **Chunk**: Post + top 3 comments = 1 document
4. **Embed**: OpenAI text-embedding-3-small (cheap & good)
5. **Store**: Save to Chroma with metadata

### Query Flow
1. **User Query**: "How do I handle errors in Python?"
2. **Vector Search**: Find 5 most relevant Reddit discussions
3. **Prompt Construction**:
   ```
   Based on these Reddit discussions:
   [Context from 5 posts]
   
   Answer this question: {user_query}
   
   Include specific examples from the discussions.
   ```
4. **LLM Response**: Generated answer with citations
5. **Return**: JSON with answer + source links

## 6. MVP Implementation Plan

### Week 1: Foundation
- [ ] Set up FastAPI project structure
- [ ] Configure Reddit API credentials
- [ ] Basic ingestion script for 1 subreddit
- [ ] Store in Chroma locally

### Week 2: Core Features  
- [ ] Vector search endpoint
- [ ] LLM integration (OpenAI first)
- [ ] Basic prompt engineering
- [ ] Simple web UI (Streamlit)

### Week 3: Quality & Polish
- [ ] Error handling & retries
- [ ] Response caching (simple dict first)
- [ ] Source attribution in responses
- [ ] Basic monitoring (log files)

## 7. Code Quality Standards

### Project Structure
```
reddit-llm/
├── app/
│   ├── main.py           # FastAPI app
│   ├── ingestion.py      # Reddit crawler
│   ├── search.py         # Vector search
│   ├── llm.py           # LLM service
│   └── models.py        # Pydantic models
├── data/
│   └── chroma_db/       # Vector storage
├── tests/               # Pytest tests
├── .env                 # Config
└── requirements.txt     # Dependencies
```

### Key Libraries
```txt
fastapi==0.104.1
praw==7.7.1
chromadb==0.4.22
openai==1.12.0
langchain==0.1.0
pydantic==2.5.0
python-dotenv==1.0.0
pytest==7.4.3
structlog==23.2.0
httpx==0.25.2
uvicorn==0.24.0
```

### Quality Checklist
- Type hints everywhere
- Docstrings for public functions
- Error handling with proper logging
- Environment variables for secrets
- Basic pytest for critical paths

## 8. Monitoring & Observability

### Simple but Effective
```python
import structlog

logger = structlog.get_logger()

# Log every query
logger.info("query_received", query=query, user_id=user_id)

# Log search results
logger.info("search_completed", query=query, results_count=len(results))

# Log LLM calls
logger.info("llm_called", model=model, tokens=token_count)
```

### Metrics to Track
- Query response time
- Number of results found
- LLM token usage
- Cache hit rate

## 9. Getting Started

### Prerequisites
- Python 3.11+
- Reddit API credentials (free)
- OpenAI API key ($5 credits to start)

### Quick Start
```bash
# Clone repo
git clone https://github.com/yourusername/reddit-llm
cd reddit-llm

# Setup environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run ingestion
python -m app.ingestion

# Start server
uvicorn app.main:app --reload

# Visit http://localhost:8000/docs
```

## 10. Example Implementation

### Minimal Ingestion Script
```python
import praw
from chromadb import Client
from chromadb.config import Settings
from langchain.embeddings import OpenAIEmbeddings
from typing import List, Dict
import os
from datetime import datetime, timedelta

class RedditIngester:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="reddit-llm-bot"
        )
        self.embeddings = OpenAIEmbeddings()
        self.chroma = Client(Settings(
            persist_directory="./data/chroma_db"
        ))
        self.collection = self.chroma.get_or_create_collection("reddit_posts")
    
    def ingest_subreddit(self, subreddit_name: str, limit: int = 100):
        subreddit = self.reddit.subreddit(subreddit_name)
        posts_processed = 0
        
        # Get top posts from last week
        for post in subreddit.top(time_filter="week", limit=limit):
            if post.score < 10 or post.over_18:
                continue
                
            # Build document
            doc_text = self._build_document(post)
            doc_id = f"{post.id}_{posts_processed}"
            
            # Generate embedding and store
            embedding = self.embeddings.embed_query(doc_text)
            
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[doc_text],
                metadatas=[{
                    "subreddit": subreddit_name,
                    "post_id": post.id,
                    "title": post.title,
                    "score": post.score,
                    "url": f"https://reddit.com{post.permalink}",
                    "created_utc": int(post.created_utc)
                }]
            )
            
            posts_processed += 1
            print(f"Processed: {post.title[:50]}...")
        
        return posts_processed
    
    def _build_document(self, post) -> str:
        # Get top 3 comments
        post.comments.replace_more(limit=0)
        top_comments = sorted(
            post.comments.list(), 
            key=lambda x: x.score, 
            reverse=True
        )[:3]
        
        # Build formatted document
        doc_parts = [
            f"Title: {post.title}",
            f"Post: {post.selftext[:500]}..." if post.selftext else "",
            ""
        ]
        
        for i, comment in enumerate(top_comments, 1):
            doc_parts.append(f"Comment {i}: {comment.body[:300]}...")
        
        return "\n".join(doc_parts)
```

### Basic API Endpoint
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import chromadb
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

app = FastAPI(title="Reddit LLM API")

# Models
class QueryRequest(BaseModel):
    question: str
    num_results: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, str]]

# Services
chroma_client = chromadb.Client(Settings(persist_directory="./data/chroma_db"))
collection = chroma_client.get_collection("reddit_posts")
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    # Search for relevant posts
    results = collection.query(
        query_texts=[request.question],
        n_results=request.num_results
    )
    
    if not results['documents'][0]:
        raise HTTPException(status_code=404, detail="No relevant posts found")
    
    # Build context
    context = "\n\n---\n\n".join(results['documents'][0])
    
    # Create prompt
    messages = [
        SystemMessage(content="""You are a helpful assistant that answers questions 
        based on Reddit discussions. Always cite which discussion you're referencing."""),
        HumanMessage(content=f"""Based on these Reddit discussions:

{context}

Answer this question: {request.question}

Include specific examples from the discussions and mention which posts you're referencing.""")
    ]
    
    # Get response
    response = llm.invoke(messages)
    
    # Format sources
    sources = []
    for i, metadata in enumerate(results['metadatas'][0]):
        sources.append({
            "title": metadata.get('title', 'Unknown'),
            "url": metadata.get('url', ''),
            "score": metadata.get('score', 0)
        })
    
    return QueryResponse(
        answer=response.content,
        sources=sources
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

## 11. Deployment Strategy

### MVP Deployment
```yaml
# docker-compose.yml
version: '3.8'
services:
  reddit-llm:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
```

### Simple Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 12. Future Enhancements (After MVP)

### Phase 2 (Learning Opportunities)
- Add MongoDB for raw post storage
- Implement semantic caching with Redis
- A/B test different embedding models
- Build proper async ingestion pipeline
- Add rate limiting and auth

### Phase 3 (If It Takes Off)
- Multi-subreddit support with ranking
- User feedback loop
- Real-time ingestion via Reddit streams
- Deploy to cloud (Railway/Fly.io)
- Add conversation memory

## 13. Cost Estimates

### MVP Costs (Monthly)
- Reddit API: **Free**
- OpenAI Embeddings: ~$0.50 (100k tokens)
- OpenAI Completions: ~$2.00 (light usage)
- Hosting: **Free** (local) or $5 (VPS)
- **Total: < $10/month**

## 14. Success Metrics

### Technical Learning
- Understand vector databases
- Master FastAPI patterns
- Learn prompt engineering
- Practice DevOps basics

### Project Success
- 10 test users find it useful
- < 2 second response time
- 80%+ relevant search results
- Clean, documented codebase

## 15. Common Pitfalls to Avoid

1. **Over-engineering early**: Start with hardcoded subreddits
2. **Perfect chunking**: Good enough > perfect
3. **Complex caching**: In-memory dict is fine for MVP
4. **Multi-model support**: Master one LLM first
5. **Real-time everything**: Batch ingestion is simpler

## Remember

This project is about **learning by building**. Every component teaches you something valuable:
- **PRAW**: Working with APIs
- **Chroma**: Vector databases
- **FastAPI**: Modern web frameworks
- **LangChain**: LLM orchestration
- **Docker**: Containerization

The goal isn't perfection - it's a working system that you understand completely and can explain to others.

**Next Step**: Create that GitHub repo and make your first commit! 🚀
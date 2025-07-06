# Reddit RAG (Retrieval-Augmented Generation) System

A powerful Retrieval-Augmented Generation system that ingests Reddit content, stores it in a vector database, and provides intelligent Q&A capabilities using LLMs.

## 🚀 Features

- **Reddit Content Ingestion**: Automatically fetch and process posts and comments from any subreddit
- **Vector Storage**: Store content in ChromaDB with semantic embeddings for efficient retrieval
- **Intelligent Search**: Semantic search through ingested content with metadata filtering
- **LLM Integration**: OpenAI-powered Q&A with context from Reddit content
- **RESTful API**: FastAPI-based endpoints for search and question answering
- **Robust Error Handling**: Graceful handling of API failures, network issues, and edge cases
- **Comprehensive Testing**: Full test coverage with mocked external dependencies

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Reddit API    │───▶│   Ingestion     │───▶│   ChromaDB      │
│   (PRAW)        │    │   Pipeline      │    │   Vector Store  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   FastAPI       │    │   OpenAI        │
                       │   REST API      │    │   LLM Service   │
                       └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.11+
- Reddit API credentials
- OpenAI API key (optional, for LLM features)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/nakuljn/reddit-rag.git
   cd reddit-rag/reddit-llm
   ```

2. **Create and activate virtual environment**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `reddit-llm` directory with the following variables:

```env
# Reddit API Credentials (Required)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=reddit-rag-bot/1.0

# OpenAI API Key (Required for LLM features)
OPENAI_API_KEY=your_openai_api_key

# ChromaDB Configuration (Optional)
CHROMA_DB_DIR=./data/chroma_db
CHROMA_COLLECTION=reddit_docs
```

### Getting Reddit API Credentials

1. Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Select "script" as the app type
4. Fill in the required fields
5. Copy the client ID (under your app name) and client secret

## 🚀 Usage

### 1. Ingest Reddit Content

Ingest posts and comments from a subreddit:

```bash
python -m app.ingestion <subreddit> [post_limit] [comment_limit] [min_score] [time_filter]
```

**Examples:**
```bash
# Ingest 50 posts from r/askreddit with 3 comments each, min score 10, from past week
python -m app.ingestion askreddit 50 3 10 week

# Ingest 20 posts from r/python with 5 comments each, min score 5, from past day
python -m app.ingestion python 20 5 5 day

# Ingest 100 posts from r/explainlikeimfive with 2 comments each, min score 15, from past month
python -m app.ingestion explainlikeimfive 100 2 15 month
```

**Parameters:**
- `subreddit`: Subreddit name (without r/)
- `post_limit`: Number of posts to fetch (default: 100)
- `comment_limit`: Number of top comments per post (default: 3)
- `min_score`: Minimum upvotes for a post (default: 10)
- `time_filter`: Time period (`day`, `week`, `month`, `year`, `all`)

### 2. Start the API Server

```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

### 3. Use the API

#### Search for Similar Content
```bash
curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "What are the best programming languages?", "limit": 5}'
```

#### Ask Questions (RAG)
```bash
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "What programming advice do Redditors give to beginners?"}'
```

### 4. API Documentation

Once the server is running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_ingestion.py
```

## 📁 Project Structure

```
reddit-rag/
├── reddit-llm/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application
│   │   ├── ingestion.py     # Reddit content ingestion
│   │   ├── search.py        # Vector search functionality
│   │   ├── llm.py          # LLM integration
│   │   ├── models.py       # Pydantic models
│   │   └── vector_store.py # ChromaDB operations
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_ingestion.py
│   │   ├── test_search.py
│   │   ├── test_llm.py
│   │   └── test_main.py
│   ├── data/
│   │   └── chroma_db/      # Vector database storage
│   ├── requirements.txt
│   ├── .env.example
│   └── .gitignore
├── Documents/
│   ├── PROGRESS.md         # Project progress tracking
│   ├── CODE_PRACTICES.md   # Coding standards
│   └── reddit-llm-hld.md   # High-level design
└── README.md
```

## 🔍 API Endpoints

### GET `/`
Health check endpoint

### POST `/search`
Search for similar content in the vector database

**Request:**
```json
{
  "query": "your search query",
  "limit": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "post_id",
      "text": "post content...",
      "metadata": {
        "subreddit": "askreddit",
        "score": 150,
        "url": "https://reddit.com/...",
        "created_utc": 1640995200
      },
      "distance": 0.123
    }
  ]
}
```

### POST `/ask`
Ask questions using RAG (Retrieval-Augmented Generation)

**Request:**
```json
{
  "question": "What programming advice do Redditors give to beginners?"
}
```

**Response:**
```json
{
  "answer": "Based on the Reddit content, here are the key pieces of advice...",
  "sources": [
    {
      "id": "post_id",
      "url": "https://reddit.com/...",
      "relevance": 0.95
    }
  ]
}
```

## 🛡️ Security

- **Environment Variables**: All sensitive data (API keys) are stored in `.env` files
- **Git Ignore**: `.env` files are excluded from version control
- **Input Validation**: All API inputs are validated using Pydantic models
- **Error Handling**: Sensitive information is not exposed in error messages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Troubleshooting

### Common Issues

**"Missing Reddit API credentials"**
- Ensure your `.env` file exists and contains valid Reddit API credentials
- Verify the credentials are correct at [Reddit App Preferences](https://www.reddit.com/prefs/apps)

**"No documents fetched"**
- Check if the subreddit exists and is accessible
- Try reducing `min_score` or changing `time_filter`
- Verify your Reddit API credentials have proper permissions

**"ChromaDB errors"**
- Ensure the `data/chroma_db` directory exists and is writable
- Check if you have sufficient disk space

**"OpenAI API errors"**
- Verify your OpenAI API key is valid and has sufficient credits
- Check if the API key has access to the required models

## 📊 Performance

- **Ingestion**: ~100 posts/minute (depends on Reddit API rate limits)
- **Search**: <100ms for typical queries
- **RAG**: 2-5 seconds depending on context length and model

## 🔮 Roadmap

- [ ] Web UI using Streamlit
- [ ] Support for multiple LLM providers
- [ ] Real-time ingestion with webhooks
- [ ] Advanced filtering and search options
- [ ] User authentication and rate limiting
- [ ] Docker containerization
- [ ] Kubernetes deployment guides

## 📞 Support

If you encounter any issues or have questions:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review the [API documentation](http://localhost:8000/docs)
3. Open an issue on GitHub

---

**Built with ❤️ using FastAPI, ChromaDB, PRAW, and OpenAI** 
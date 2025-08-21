---
title: Ask Reddit
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: gradio
app_file: app.py
pinned: false
license: mit
---

# Ask Reddit - AI-Powered Q&A

A conversational AI system that answers questions using Reddit discussions powered by Anthropic Claude and Gradio.

## 🚀 Features

- 💬 **Chat Interface**: ChatGPT-style conversational UI with Gradio
- 🔍 **Smart Query Processing**: Automatically enhances user queries for better search results
- 🧠 **Claude Integration**: Uses Anthropic Claude for intelligent responses  
- 📚 **Reddit Data**: Searches through ingested Reddit discussions
- 🎯 **Relevant Sources**: Shows only the Reddit threads actually used in answers
- **Vector Storage**: Store content in ChromaDB with semantic embeddings for efficient retrieval
- **RESTful API**: FastAPI-based endpoints for search and question answering
- **Robust Error Handling**: Graceful handling of API failures, network issues, and edge cases

## 🏗️ Architecture

```
Data Ingestion (One-time):
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Reddit API    │───▶│   Ingestion     │───▶│   ChromaDB      │
│   (PRAW)        │    │   Pipeline      │    │   Vector Store  │
└─────────────────┘    └─────────────────┘    └─────────────────┘

Query Processing Flow:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gradio UI     │───▶│   Claude LLM    │───▶│   Query         │
│   User Input    │    │   Expand Query  │    │   Enhancement   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Final Result  │◄───│   Claude LLM    │◄───│   ChromaDB      │
│   to User       │    │   Generalize    │    │   Fetch Data    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.11+
- Reddit API credentials
- Anthropic API key (required for LLM features)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/nakuljn/reddit-rag.git
   cd reddit-rag
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

Create a `.env` file in the root directory with the following variables:

```env
# Reddit API Credentials (Required)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=reddit-rag-bot/1.0

# Anthropic API Key (Required for LLM features)
ANTHROPIC_API_KEY=your_anthropic_api_key

# ChromaDB Configuration (Optional)
CHROMA_DB_DIR=./chroma_db
CHROMA_COLLECTION=reddit_docs
```

### Getting Reddit API Credentials

1. Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Select "script" as the app type
4. Fill in the required fields
5. Copy the client ID (under your app name) and client secret

## 🚀 Usage

### 1. Run the Application

Start the full application (backend + chat interface):

```bash
python app.py
```

This will start both the FastAPI backend and Gradio chat interface. Access the chat at `http://localhost:7860`.

### 2. Ingest Reddit Content

In a separate terminal, ingest posts and comments from a subreddit:

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

### 3. Alternative: Run API Server Only

If you want to run just the FastAPI backend:

```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

### 4. Use the API

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

### 5. API Documentation

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
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── ingestion.py     # Reddit content ingestion
│   ├── search.py        # Vector search functionality
│   ├── llm.py          # LLM integration
│   ├── models.py       # Pydantic models
│   └── vector_store.py # ChromaDB operations
├── tests/
│   ├── __init__.py
│   ├── test_ingestion.py
│   ├── test_search.py
│   ├── test_llm.py
│   └── test_main.py
├── chroma_db/          # Vector database storage
├── app.py              # Gradio chat interface + backend launcher
├── requirements.txt
├── Dockerfile
├── .env
├── .gitignore
├── CLAUDE.md
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
- Ensure the `chroma_db` directory exists and is writable
- Check if you have sufficient disk space

**"Anthropic API errors"**
- Verify your Anthropic API key is valid and has sufficient credits
- Check if the API key has access to Claude models

## 📊 Performance

- **Ingestion**: ~100 posts/minute (depends on Reddit API rate limits)
- **Search**: <100ms for typical queries
- **RAG**: 2-5 seconds depending on context length and model


**Built with ❤️ using FastAPI, ChromaDB, PRAW, Anthropic Claude, and Gradio** 

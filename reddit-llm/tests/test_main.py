import pytest
from httpx import AsyncClient
from unittest import mock
from app.main import app

@pytest.mark.asyncio
async def test_read_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "Reddit-Powered LLM API" in data["message"]

@pytest.mark.asyncio
@mock.patch("app.main.search_similar_documents")
async def test_search_endpoint_success(mock_search):
    mock_search.return_value = [
        {
            "id": "doc1",
            "text": "Sample document text",
            "metadata": {"subreddit": "test"},
            "distance": 0.1
        }
    ]
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/search", json={
            "query": "test query",
            "top_k": 3
        })
    
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "test query"
    assert data["total_results"] == 1
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == "doc1"
    assert data["results"][0]["text"] == "Sample document text"
    mock_search.assert_called_once_with("test query", top_k=3)

@pytest.mark.asyncio
async def test_search_endpoint_validation_error():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/search", json={
            "query": "",  # Empty query should fail validation
            "top_k": 3
        })
    
    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
@mock.patch("app.main.LLMService")
@mock.patch("app.main.search_similar_documents")
async def test_ask_endpoint_success(mock_search, mock_llm_service):
    # Mock search results
    mock_search.return_value = [
        {
            "id": "doc1",
            "text": "Python is a programming language",
            "metadata": {
                "subreddit": "learnpython",
                "url": "https://reddit.com/r/learnpython/doc1",
                "score": 42
            }
        }
    ]
    
    # Mock LLM response
    mock_llm_instance = mock.Mock()
    mock_llm_instance.generate_response.return_value = "Python is a great programming language for beginners."
    mock_llm_service.return_value = mock_llm_instance
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/ask", json={
            "query": "What is Python?",
            "top_k": 3
        })
    
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "What is Python?"
    assert data["answer"] == "Python is a great programming language for beginners."
    assert data["total_sources"] == 1
    assert len(data["sources"]) == 1
    assert data["sources"][0]["id"] == "doc1"
    assert data["sources"][0]["subreddit"] == "learnpython"
    assert data["sources"][0]["url"] == "https://reddit.com/r/learnpython/doc1"
    assert data["sources"][0]["score"] == 42

@pytest.mark.asyncio
async def test_ask_endpoint_validation_error():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/ask", json={
            "query": "",  # Empty query should fail validation
            "top_k": 3
        })
    
    assert response.status_code == 422  # Validation error 
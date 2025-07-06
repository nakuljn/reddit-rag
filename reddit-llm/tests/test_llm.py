import pytest
from unittest import mock
from app.llm import LLMService

def test_llm_service_initialization():
    with mock.patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        service = LLMService()
        assert service.api_key == 'test_key'
        assert service.model == 'gpt-3.5-turbo'

def test_llm_service_missing_api_key():
    with mock.patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="OpenAI API key not found"):
            LLMService()

@mock.patch('app.llm.OpenAI')
def test_generate_response_with_context(mock_openai):
    # Mock OpenAI response structure
    mock_choice = mock.Mock()
    mock_choice.message.content = "This is a helpful answer based on the context."
    mock_response = mock.Mock()
    mock_response.choices = [mock_choice]
    mock_openai.return_value.chat.completions.create.return_value = mock_response
    
    with mock.patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        service = LLMService()
        context_docs = [
            {"text": "Document 1 content about Python"},
            {"text": "Document 2 content about FastAPI"}
        ]
        
        response = service.generate_response("How do I learn Python?", context_docs)
        
        assert response == "This is a helpful answer based on the context."
        mock_openai.return_value.chat.completions.create.assert_called_once()

def test_generate_response_no_context():
    with mock.patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        service = LLMService()
        response = service.generate_response("How do I learn Python?", [])
        assert response == "I don't have enough context to answer this question."

def test_generate_response_empty_query():
    with mock.patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        service = LLMService()
        response = service.generate_response("", [{"text": "Some context"}])
        assert response == "Please provide a valid question."
        
        response = service.generate_response("   ", [{"text": "Some context"}])
        assert response == "Please provide a valid question."

@mock.patch('app.llm.OpenAI')
def test_generate_response_api_failure(mock_openai):
    mock_openai.return_value.chat.completions.create.side_effect = Exception("API Error")
    
    with mock.patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        service = LLMService()
        response = service.generate_response("Test question", [{"text": "Context"}])
        assert "Sorry, I'm having trouble" in response

@mock.patch('app.llm.OpenAI')
def test_generate_response_empty_response(mock_openai):
    mock_response = mock.Mock()
    mock_response.choices = []
    mock_openai.return_value.chat.completions.create.return_value = mock_response
    
    with mock.patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        service = LLMService()
        response = service.generate_response("Test question", [{"text": "Context"}])
        assert "Sorry, I couldn't generate a response" in response

def test_build_context():
    with mock.patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        service = LLMService()
        docs = [
            {"text": "First document content"},
            {"text": "Second document content"}
        ]
        context = service._build_context(docs)
        assert "Document 1:" in context
        assert "Document 2:" in context
        assert "First document content" in context
        assert "Second document content" in context

def test_build_context_with_empty_text():
    with mock.patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        service = LLMService()
        docs = [
            {"text": "First document content"},
            {"text": ""},  # Empty text
            {"text": "Third document content"}
        ]
        context = service._build_context(docs)
        assert "Document 1:" in context
        assert "Document 3:" in context
        assert "Document 2:" not in context  # Should skip empty text 
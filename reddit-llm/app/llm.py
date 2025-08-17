import os
from anthropic import Anthropic
from typing import List, Dict, Any

class LLMService:
    def __init__(self, api_key: str = None, model: str = "claude-3-haiku-20240307"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not found in environment variables")
        self.client = Anthropic(api_key=self.api_key)
        self.model = model
    
    def generate_response(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """Generate a response using the query and retrieved context documents."""
        if not context_docs:
            return "I don't have enough context to answer this question."
        
        if not query or not query.strip():
            return "Please provide a valid question."
        
        try:
            # Build context from documents
            context_text = self._build_context(context_docs)
            
            # Create prompt
            prompt = self._create_prompt(query, context_text)
            
            # Call Anthropic API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Handle empty response
            if not response.content or not response.content[0].text:
                return "Sorry, I couldn't generate a response. Please try again."
            
            return response.content[0].text
            
        except Exception as e:
            print(f"LLM API call failed: {str(e)}")
            return "Sorry, I'm having trouble processing your request. Please try again later."
    
    def _build_context(self, docs: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents."""
        context_parts = []
        for i, doc in enumerate(docs, 1):
            if doc.get("text"):
                context_parts.append(f"Document {i}:\n{doc['text']}\n")
        return "\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str) -> str:
        """Create the prompt for the LLM with query and context."""
        return f"""You are a helpful assistant that answers questions based on Reddit discussions. Your goal is to provide useful, friendly responses.

Reddit discussions:
{context}

User question: {query}

Instructions:
- Extract and present any relevant information from the Reddit discussions
- Be conversational and helpful in tone
- If you find specific recommendations, present them clearly with any available details
- Don't start with negative statements about what the discussions don't contain
- If limited information is available, acknowledge it briefly but focus on what you can provide
- Format recommendations in a clear, easy-to-read way

Answer:"""

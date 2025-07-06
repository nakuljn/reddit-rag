import os
from openai import OpenAI
from typing import List, Dict, Any

class LLMService:
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        self.client = OpenAI(api_key=self.api_key)
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
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            # Handle empty response
            if not response.choices or not response.choices[0].message.content:
                return "Sorry, I couldn't generate a response. Please try again."
            
            return response.choices[0].message.content
            
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
        return f"""Based on the following Reddit discussions:

{context}

Answer this question: {query}

Provide a helpful answer using information from the discussions above. If the discussions don't contain relevant information, say so clearly."""

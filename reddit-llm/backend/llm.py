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
    
    def generate_response(self, query: str, context_docs: List[Dict[str, Any]]) -> tuple[str, List[str]]:
        """
        Generate a response using the query and retrieved context documents.
        Returns (answer, used_doc_ids) where used_doc_ids are documents referenced in the answer.
        """
        if not context_docs:
            return ("I don't have enough context to answer this question.", [])
        
        if not query or not query.strip():
            return ("Please provide a valid question.", [])
        
        try:
            # Build context from documents with numbered references
            context_text = self._build_context_with_refs(context_docs)
            
            # Create prompt
            prompt = self._create_prompt_with_refs(query, context_text)
            
            # Call Anthropic API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Handle empty response
            if not response.content or not response.content[0].text:
                return ("Sorry, I couldn't generate a response. Please try again.", [])
            
            answer = response.content[0].text
            
            # Extract which documents were referenced in the answer
            used_doc_ids = self._extract_used_sources(answer, context_docs)
            
            return (answer, used_doc_ids)
            
        except Exception as e:
            print(f"LLM API call failed: {str(e)}")
            return ("Sorry, I'm having trouble processing your request. Please try again later.", [])
    
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
    
    def _build_context_with_refs(self, docs: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents with numbered references."""
        context_parts = []
        for i, doc in enumerate(docs, 1):
            if doc.get("text"):
                context_parts.append(f"[Source {i}] {doc['text']}\n")
        return "\n".join(context_parts)
    
    def _create_prompt_with_refs(self, query: str, context: str) -> str:
        """Create the prompt for the LLM with numbered source references."""
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
    
    def _extract_used_sources(self, answer: str, context_docs: List[Dict[str, Any]]) -> List[str]:
        """
        Simple heuristic to determine which sources were likely used in the answer.
        This is a basic implementation - could be improved with more sophisticated matching.
        """
        used_doc_ids = []
        
        # For now, we'll do a simple approach: if any content from a document 
        # appears to be referenced in the answer, consider it used
        for doc in context_docs:
            doc_text = doc.get("text", "").lower()
            answer_lower = answer.lower()
            
            # Look for specific indicators that this source was used
            # Check if any significant phrases (3+ words) from the document appear in the answer
            doc_words = doc_text.split()
            for i in range(len(doc_words) - 2):
                phrase = " ".join(doc_words[i:i+3])
                if len(phrase) > 10 and phrase in answer_lower:
                    used_doc_ids.append(doc["id"])
                    break
        
        # If no sources were detected as used, include top 2 sources as fallback
        if not used_doc_ids and context_docs:
            used_doc_ids = [doc["id"] for doc in context_docs[:2]]
        
        return used_doc_ids

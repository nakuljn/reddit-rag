import os
from anthropic import Anthropic
from openai import OpenAI
from typing import List, Dict, Any

class LLMService:
    def __init__(self, model: str = "claude"):
        self.model = model
        
        if model.startswith("claude"):
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("Anthropic API key not found")
            self.client = self._create_anthropic_client()
            self.model_name = "claude-3-haiku-20240307"
        elif model.startswith("grok"):
            self.api_key = os.getenv("XAI_API_KEY")
            if not self.api_key:
                raise ValueError("xAI API key not found")
            self.client = self._create_openai_client()
            self.model_name = "grok-2-1212"
    
    def _create_anthropic_client(self) -> Anthropic:
        """Create Anthropic client with proxy error handling"""
        try:
            return Anthropic(api_key=self.api_key)
        except TypeError as e:
            if "proxies" in str(e):
                return Anthropic(api_key=self.api_key)
            raise e
    
    def _create_openai_client(self) -> OpenAI:
        """Create OpenAI client with proxy error handling"""
        try:
            return OpenAI(api_key=self.api_key, base_url="https://api.x.ai/v1")
        except TypeError as e:
            if "proxies" in str(e):
                import inspect
                sig = inspect.signature(OpenAI.__init__)
                valid_params = set(sig.parameters.keys()) - {'self'}
                client_kwargs = {'api_key': self.api_key, 'base_url': "https://api.x.ai/v1"}
                filtered_kwargs = {k: v for k, v in client_kwargs.items() if k in valid_params}
                return OpenAI(**filtered_kwargs)
            raise e
    
    def generate_response(self, query: str, context_docs: List[Dict[str, Any]]) -> tuple[str, List[str]]:
        if not context_docs:
            return ("I don't have enough context to answer this question.", [])
        
        if not query or not query.strip():
            return ("Please provide a valid question.", [])
        
        try:
            context_text = self._build_context_with_refs(context_docs)
            prompt = self._create_prompt_with_refs(query, context_text)
            
            if self.model.startswith("claude"):
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=500,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                answer = response.content[0].text
            else:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    max_tokens=500,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                answer = response.choices[0].message.content
            
            if not answer:
                return ("Sorry, I couldn't generate a response. Please try again.", [])
            
            used_doc_ids = self._extract_used_sources(answer, context_docs)
            return (answer, used_doc_ids)
            
        except Exception as e:
            return ("Sorry, I'm having trouble processing your request. Please try again later.", [])
    
    def _build_context_with_refs(self, docs: List[Dict[str, Any]]) -> str:
        context_parts = []
        for i, doc in enumerate(docs, 1):
            if doc.get("text"):
                context_parts.append(f"[Source {i}] {doc['text']}\n")
        return "\n".join(context_parts)
    
    def _create_prompt_with_refs(self, query: str, context: str) -> str:
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
        used_doc_ids = []
        
        for doc in context_docs:
            doc_text = doc.get("text", "").lower()
            answer_lower = answer.lower()
            
            doc_words = doc_text.split()
            for i in range(len(doc_words) - 2):
                phrase = " ".join(doc_words[i:i+3])
                if len(phrase) > 10 and phrase in answer_lower:
                    used_doc_ids.append(doc["id"])
                    break
        
        if not used_doc_ids and context_docs:
            used_doc_ids = [doc["id"] for doc in context_docs[:2]]
        
        return used_doc_ids
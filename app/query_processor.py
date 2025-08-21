import os
from anthropic import Anthropic
from typing import List

class QueryProcessor:
    def __init__(self, api_key: str = None, model: str = "claude-3-haiku-20240307"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not found in environment variables")
        
        self.client = self._create_client()
        self.model = model
    
    def _create_client(self) -> Anthropic:
        """Create Anthropic client with proxy error handling"""
        try:
            return Anthropic(api_key=self.api_key)
        except TypeError as e:
            if "proxies" in str(e):
                return Anthropic(api_key=self.api_key)
            raise e
    
    def enhance_query(self, user_query: str) -> List[str]:
        if not user_query or not user_query.strip():
            return [user_query]
        
        try:
            prompt = f"""You are a search query optimizer for Reddit content retrieval. Your job is to generate 2-3 alternative search queries that would help find relevant Reddit discussions.

User's question: "{user_query}"

Generate 2-3 short, specific search queries (each 3-8 words) that would find relevant Reddit posts. Focus on:
- Synonyms and related terms
- Different ways people might discuss this topic
- Common Reddit terminology

Format your response as a simple list, one query per line:
- query1
- query2
- query3

Example:
User asks: "what are some great cafe in bangalore"
Response:
- best coffee shops bangalore
- bangalore cafe recommendations
- good cafes bengaluru reviews"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            if not response.content or not response.content[0].text:
                return [user_query]
            
            search_queries = []
            lines = response.content[0].text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('- '):
                    query = line[2:].strip()
                    if query and len(query) > 2:
                        search_queries.append(query)
            
            if not search_queries:
                return [user_query]
            
            all_queries = [user_query] + search_queries
            return list(dict.fromkeys(all_queries))
            
        except Exception:
            return [user_query]
    
    def should_preprocess(self, query: str) -> bool:
        if not query or len(query.strip()) < 3:
            return False
        
        specific_indicators = ['reddit.com', 'r/', 'u/', 'post:', 'thread:']
        if any(indicator in query.lower() for indicator in specific_indicators):
            return False
        
        if len(query.split()) <= 2:
            return False
        
        return True
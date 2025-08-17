import os
from anthropic import Anthropic
from typing import List

class QueryProcessor:
    def __init__(self, api_key: str = None, model: str = "claude-3-haiku-20240307"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not found in environment variables")
        self.client = Anthropic(api_key=self.api_key)
        self.model = model
    
    def enhance_query(self, user_query: str) -> List[str]:
        """
        Generate multiple search variations of the user query to improve retrieval.
        Returns a list of search queries that are more likely to find relevant content.
        
        Cost optimization: Single LLM call generates multiple search variations.
        """
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
                max_tokens=200,  # Keep tokens low for cost efficiency
                temperature=0.3,  # Lower temperature for consistent results
                messages=[{"role": "user", "content": prompt}]
            )
            
            if not response.content or not response.content[0].text:
                return [user_query]
            
            # Parse the response to extract search queries
            search_queries = []
            lines = response.content[0].text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('- '):
                    query = line[2:].strip()
                    if query and len(query) > 2:
                        search_queries.append(query)
            
            # Fallback: if parsing failed, return original query
            if not search_queries:
                return [user_query]
            
            # Always include original query as fallback + enhanced queries
            all_queries = [user_query] + search_queries
            return list(dict.fromkeys(all_queries))  # Remove duplicates while preserving order
            
        except Exception as e:
            print(f"Query preprocessing failed: {str(e)}")
            return [user_query]  # Fallback to original query
    
    def should_preprocess(self, query: str) -> bool:
        """
        Determine if a query needs preprocessing based on simple heuristics.
        This avoids unnecessary LLM calls for already good queries.
        """
        if not query or len(query.strip()) < 3:
            return False
        
        # Skip preprocessing for very specific queries (likely already well-formed)
        specific_indicators = ['reddit.com', 'r/', 'u/', 'post:', 'thread:']
        if any(indicator in query.lower() for indicator in specific_indicators):
            return False
        
        # Skip preprocessing for very short queries (likely keywords already)
        if len(query.split()) <= 2:
            return False
        
        return True
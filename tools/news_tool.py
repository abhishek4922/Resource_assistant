"""
NewsAPI Tool
Fetches latest news, funding, and investment info about a company
"""
import requests
import os
from typing import List, Dict, Any

class NewsTool:
    """Tool for searching news using NewsAPI"""
    
    def __init__(self, max_results: int = 5):
        """
        Initialize NewsAPI tool
        
        Args:
            max_results: Maximum number of articles to return
        """
        self.max_results = max_results
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2/everything"
    
    def search_company_news(self, company_name: str) -> List[Dict[str, Any]]:
        """
        Search for recent news, funding, and investment info
        
        Args:
            company_name: Name of the company
            
        Returns:
            List of news articles
        """
        if not self.api_key:
            return []
            
        try:
            # Query for news AND funding/business terms
            # Broadened query to capture more results
            query = f'"{company_name}" AND (funding OR investment OR business OR startup OR finance OR growth OR launch)'
            
            params = {
                "q": query,
                "language": "en",
                "sortBy": "relevancy",  # Changed to relevancy to get best matches first
                "pageSize": self.max_results,
                "apiKey": self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"NewsAPI Error: {response.status_code}")
                return []
                
            data = response.json()
            articles = []
            
            for item in data.get("articles", []):
                articles.append({
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                    "url": item.get("url", ""),
                    "source": item.get("source", {}).get("name", "Unknown"),
                    "published_at": item.get("publishedAt", "")[:10],
                    "content": item.get("content", "")
                })
            
            return articles
            
        except Exception as e:
            print(f"NewsAPI search error: {e}")
            return []

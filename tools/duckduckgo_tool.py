"""
DuckDuckGo Search Tool
Searches for company information using DuckDuckGo
"""
from duckduckgo_search import DDGS
from typing import List, Dict, Any
import time

class DuckDuckGoTool:
    """Tool for searching DuckDuckGo"""
    
    def __init__(self, max_results: int = 5):
        """
        Initialize DuckDuckGo tool
        
        Args:
            max_results: Maximum number of results to return
        """
        self.max_results = max_results
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Generic search method"""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=self.max_results))
            
            formatted_results = []
            for res in results:
                formatted_results.append({
                    "title": res.get("title", ""),
                    "link": res.get("href", ""),
                    "snippet": res.get("body", "")
                })
            return formatted_results
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return []

    def search_company_info(self, company_name: str) -> List[Dict[str, Any]]:
        """
        Search for detailed company information
        
        Args:
            company_name: Name of the company
            
        Returns:
            List of search results about the company
        """
        query = f"{company_name} company business model products services analysis"
        return self.search(query)
    
    def _get_fallback_results(self, company_name: str) -> List[Dict[str, Any]]:
        """Return fallback results if search fails"""
        return [{
            "title": f"Search DuckDuckGo for {company_name}",
            "link": f"https://duckduckgo.com/?q={company_name}",
            "snippet": "Could not fetch live search results due to rate limits or connection issues."
        }]

"""
DuckDuckGo Search Tool
Fetches company information from web search
"""
from typing import List, Dict, Any
from duckduckgo_search import DDGS
import time


class DuckDuckGoTool:
    """Tool for searching company information using DuckDuckGo"""
    
    def __init__(self, max_results: int = 5):
        """
        Initialize DuckDuckGo search tool
        
        Args:
            max_results: Maximum number of search results to return
        """
        self.max_results = max_results
    
    def search(self, query: str, retries: int = 2) -> List[Dict[str, Any]]:
        """
        Search for information about a company
        
        Args:
            query: Search query (company name)
            retries: Number of retry attempts on failure
            
        Returns:
            List of search results with title, body, and href
        """
        for attempt in range(retries):
            try:
                with DDGS() as ddgs:
                    results = []
                    search_results = ddgs.text(
                        query, 
                        max_results=self.max_results
                    )
                    
                    for result in search_results:
                        results.append({
                            "title": result.get("title", ""),
                            "body": result.get("body", ""),
                            "url": result.get("href", "")
                        })
                    
                    return results
                    
            except Exception as e:
                print(f"DuckDuckGo search error (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2)  # Wait before retry
                else:
                    return []
        
        return []
    
    def search_company_info(self, company_name: str) -> List[Dict[str, Any]]:
        """
        Search for company information
        
        Args:
            company_name: Name of the company
            
        Returns:
            List of search results about the company
        """
        query = f"{company_name} company what does it do business overview"
        return self.search(query)

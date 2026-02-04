"""
arXiv Search Tool
Searches academic papers related to AI use-cases
"""
import arxiv
from typing import List, Dict, Any
import time


class ArxivTool:
    """Tool for searching arXiv papers"""
    
    def __init__(self, max_results: int = 5):
        """
        Initialize arXiv search tool
        
        Args:
            max_results: Maximum number of papers to return
        """
        self.max_results = max_results
    
    def search(self, query: str, retries: int = 2) -> List[Dict[str, Any]]:
        """
        Search for papers on arXiv
        
        Args:
            query: Search query
            retries: Number of retry attempts on failure
            
        Returns:
            List of papers with title and URL
        """
        for attempt in range(retries):
            try:
                client = arxiv.Client()
                search = arxiv.Search(
                    query=query,
                    max_results=self.max_results,
                    sort_by=arxiv.SortCriterion.Relevance
                )
                
                results = []
                for paper in client.results(search):
                    results.append({
                        "title": paper.title,
                        "url": paper.entry_id,
                        "summary": paper.summary[:200] + "..." if len(paper.summary) > 200 else paper.summary
                    })
                
                return results
                
            except Exception as e:
                print(f"arXiv search error (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2)
                else:
                    return []
        
        return []
    
    def search_use_case(self, use_case: str) -> List[Dict[str, Any]]:
        """
        Search for papers related to an AI use-case
        
        Args:
            use_case: AI use-case description or keywords
            
        Returns:
            List of relevant papers
        """
        # Use the provided query directly as it likely contains specific keywords now
        return self.search(use_case)

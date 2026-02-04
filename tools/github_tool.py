"""
GitHub Search Tool
Searches repositories on GitHub
"""
import requests
from typing import List, Dict, Any
import time
import os


class GitHubTool:
    """Tool for searching GitHub repositories"""
    
    def __init__(self, max_results: int = 5):
        """
        Initialize GitHub search tool
        
        Args:
            max_results: Maximum number of repositories to return
        """
        self.max_results = max_results
        self.base_url = "https://api.github.com"
        self.token = os.getenv("GITHUB_TOKEN")  # Optional, for higher rate limits
    
    def search(self, query: str, retries: int = 2) -> List[Dict[str, Any]]:
        """
        Search for repositories on GitHub
        
        Args:
            query: Search query
            retries: Number of retry attempts on failure
            
        Returns:
            List of repositories with name, URL, and stars
        """
        for attempt in range(retries):
            try:
                url = f"{self.base_url}/search/repositories"
                params = {
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": self.max_results
                }
                
                headers = {
                    "Accept": "application/vnd.github.v3+json"
                }
                
                # Add token if available
                if self.token:
                    headers["Authorization"] = f"token {self.token}"
                
                response = requests.get(url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                results = []
                
                for repo in data.get("items", [])[:self.max_results]:
                    results.append({
                        "name": repo.get("full_name", ""),
                        "url": repo.get("html_url", ""),
                        "stars": repo.get("stargazers_count", 0),
                        "description": repo.get("description", "")[:150] if repo.get("description") else ""
                    })
                
                return results
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    print(f"GitHub API rate limit exceeded. Consider adding GITHUB_TOKEN to .env")
                print(f"GitHub search error (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2)
                else:
                    return []
            except Exception as e:
                print(f"GitHub search error (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2)
                else:
                    return []
        
        return []
    
    def search_use_case(self, use_case: str) -> List[Dict[str, Any]]:
        """
        Search for repositories related to an AI use-case with fallback strategy
        
        Args:
            use_case: AI use-case description or keywords
            
        Returns:
            List of relevant repositories
        """
        # Try 1: Exact query provided (usually specific keywords now)
        results = self.search(use_case)
        if results:
            return results
        
        # Try 2: If query is long (>3 words), try just the first 3 words
        # This handles cases where "xgboost demand forecasting retail" might fail, 
        # but "demand forecasting retail" might work
        words = use_case.split()
        if len(words) > 3:
            shortened_query = " ".join(words[:3])
            print(f"GitHub: Retrying with broader query: '{shortened_query}'")
            results = self.search(shortened_query)
            if results:
                return results
                
        # Try 3: If still nothing, try just the first 2 words for maximum breadth
        if len(words) > 2:
            super_broad_query = " ".join(words[:2])
            print(f"GitHub: Retrying with broadest query: '{super_broad_query}'")
            results = self.search(super_broad_query)
            if results:
                return results
                
        return []

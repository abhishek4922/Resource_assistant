"""
Kaggle Search Tool
Searches datasets and notebooks on Kaggle
"""
import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import time


class KaggleTool:
    """Tool for searching Kaggle datasets and notebooks"""
    
    def __init__(self, max_results: int = 5):
        """
        Initialize Kaggle search tool
        
        Args:
            max_results: Maximum number of results to return
        """
        self.max_results = max_results
        self.base_url = "https://www.kaggle.com"
    
    def search(self, query: str, search_type: str = "datasets", retries: int = 2) -> List[Dict[str, Any]]:
        """
        Search Kaggle using web scraping
        
        Args:
            query: Search query
            search_type: Type of search ("datasets" or "notebooks")
            retries: Number of retry attempts on failure
            
        Returns:
            List of results with title and URL
        """
        for attempt in range(retries):
            try:
                # Use Kaggle's search URL
                search_url = f"{self.base_url}/search"
                params = {
                    "q": query
                }
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                
                response = requests.get(search_url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                
                # Parse the search results page
                soup = BeautifulSoup(response.content, 'html.parser')
                
                results = []
                
                # Try to find dataset/notebook links
                # Note: This is a simplified approach - Kaggle's structure may change
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link.get('href', '')
                    
                    # Filter based on search type
                    if search_type == "datasets" and '/datasets/' in href:
                        title = link.get_text(strip=True)
                        if title and len(title) > 5:  # Filter out empty or very short titles
                            results.append({
                                "title": title,
                                "url": f"{self.base_url}{href}" if not href.startswith('http') else href
                            })
                    elif search_type == "notebooks" and ('/code/' in href or '/notebooks/' in href):
                        title = link.get_text(strip=True)
                        if title and len(title) > 5:
                            results.append({
                                "title": title,
                                "url": f"{self.base_url}{href}" if not href.startswith('http') else href
                            })
                    
                    if len(results) >= self.max_results:
                        break
                
                # Remove duplicates
                seen_urls = set()
                unique_results = []
                for result in results:
                    if result['url'] not in seen_urls:
                        seen_urls.add(result['url'])
                        unique_results.append(result)
                
                return unique_results[:self.max_results]
                
            except Exception as e:
                print(f"Kaggle search error (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2)
                else:
                    # Return placeholder results if search fails
                    return self._get_placeholder_results(query, search_type)
        
        return self._get_placeholder_results(query, search_type)
    
    def _get_placeholder_results(self, query: str, search_type: str) -> List[Dict[str, Any]]:
        """
        Generate placeholder results when search fails
        
        Args:
            query: Original search query
            search_type: Type of search
            
        Returns:
            List of placeholder results
        """
        search_url = f"{self.base_url}/search?q={query.replace(' ', '+')}"
        return [{
            "title": f"Search Kaggle {search_type} for: {query}",
            "url": search_url
        }]
    
    def search_use_case(self, use_case: str) -> List[Dict[str, Any]]:
        """
        Search for datasets and notebooks related to an AI use-case with fallback strategy
        
        Args:
            use_case: AI use-case description or keywords
            
        Returns:
            Combined list of datasets and notebooks
        """
        # Helper to check if results are valid (not just placeholders)
        def is_valid_result(res_list):
            if not res_list:
                return False
            # Check if it's a placeholder (url contains 'search?q=')
            if len(res_list) == 1 and 'search?q=' in res_list[0]['url']:
                return False
            return True

        # Try 1: Exact query provided
        datasets = self.search(use_case, search_type="datasets")
        notebooks = self.search(use_case, search_type="notebooks")
        
        # If we have valid results, return them
        if is_valid_result(datasets) or is_valid_result(notebooks):
            # Filter out placeholders if we have mixed results
            valid_datasets = [d for d in datasets if 'search?q=' not in d['url']]
            valid_notebooks = [n for n in notebooks if 'search?q=' not in n['url']]
            
            # If after filtering we have real results, return them
            if valid_datasets or valid_notebooks:
                return (valid_datasets + valid_notebooks)[:self.max_results]
        
        # Try 2: Broader query (first 3 words)
        words = use_case.split()
        if len(words) > 3:
            shortened_query = " ".join(words[:3])
            print(f"Kaggle: Retrying with broader query: '{shortened_query}'")
            
            datasets = self.search(shortened_query, search_type="datasets")
            notebooks = self.search(shortened_query, search_type="notebooks")
            
            if is_valid_result(datasets) or is_valid_result(notebooks):
                valid_datasets = [d for d in datasets if 'search?q=' not in d['url']]
                valid_notebooks = [n for n in notebooks if 'search?q=' not in n['url']]
                if valid_datasets or valid_notebooks:
                    return (valid_datasets + valid_notebooks)[:self.max_results]

        # Try 3: Broadest query (first 2 words)
        if len(words) > 2:
            super_broad_query = " ".join(words[:2])
            print(f"Kaggle: Retrying with broadest query: '{super_broad_query}'")
            
            datasets = self.search(super_broad_query, search_type="datasets")
            notebooks = self.search(super_broad_query, search_type="notebooks")
            
            if is_valid_result(datasets) or is_valid_result(notebooks):
                valid_datasets = [d for d in datasets if 'search?q=' not in d['url']]
                valid_notebooks = [n for n in notebooks if 'search?q=' not in n['url']]
                if valid_datasets or valid_notebooks:
                    return (valid_datasets + valid_notebooks)[:self.max_results]
        
        # Finally, if all else fails, return the placeholder for the original query
        # This ensures the user at least gets a clickable link to try themselves
        return self._get_placeholder_results(use_case, "datasets + notebooks")

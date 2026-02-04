"""
Hugging Face Search Tool
Searches models and datasets on Hugging Face
"""
import requests
from typing import List, Dict, Any
import time


class HuggingFaceTool:
    """Tool for searching Hugging Face models and datasets"""
    
    def __init__(self, max_results: int = 5):
        """
        Initialize Hugging Face search tool
        
        Args:
            max_results: Maximum number of results to return
        """
        self.max_results = max_results
        self.base_url = "https://huggingface.co/api"
    
    def search_models(self, query: str, retries: int = 2) -> List[Dict[str, Any]]:
        """
        Search for models on Hugging Face
        
        Args:
            query: Search query
            retries: Number of retry attempts on failure
            
        Returns:
            List of models with name and URL
        """
        for attempt in range(retries):
            try:
                url = f"{self.base_url}/models"
                params = {
                    "search": query,
                    "limit": self.max_results,
                    "sort": "downloads",
                    "direction": -1
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                models = response.json()
                results = []
                
                for model in models[:self.max_results]:
                    results.append({
                        "name": model.get("id", ""),
                        "url": f"https://huggingface.co/{model.get('id', '')}",
                        "downloads": model.get("downloads", 0),
                        "type": "model"
                    })
                
                return results
                
            except Exception as e:
                print(f"Hugging Face models search error (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2)
                else:
                    return []
        
        return []
    
    def search_datasets(self, query: str, retries: int = 2) -> List[Dict[str, Any]]:
        """
        Search for datasets on Hugging Face
        
        Args:
            query: Search query
            retries: Number of retry attempts on failure
            
        Returns:
            List of datasets with name and URL
        """
        for attempt in range(retries):
            try:
                url = f"{self.base_url}/datasets"
                params = {
                    "search": query,
                    "limit": self.max_results,
                    "sort": "downloads",
                    "direction": -1
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                datasets = response.json()
                results = []
                
                for dataset in datasets[:self.max_results]:
                    results.append({
                        "name": dataset.get("id", ""),
                        "url": f"https://huggingface.co/datasets/{dataset.get('id', '')}",
                        "downloads": dataset.get("downloads", 0),
                        "type": "dataset"
                    })
                
                return results
                
            except Exception as e:
                print(f"Hugging Face datasets search error (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2)
                else:
                    return []
        
        return []
    
    def search_use_case(self, use_case: str) -> List[Dict[str, Any]]:
        """
        Search for models and datasets related to an AI use-case
        
        Args:
            use_case: AI use-case description
            
        Returns:
            Combined list of models and datasets
        """
        models = self.search_models(use_case)
        datasets = self.search_datasets(use_case)
        
        # Combine and limit results
        all_results = models + datasets
        return all_results[:self.max_results]

"""
Verifier Agent
Validates completeness and fixes missing data
"""
from typing import Dict, Any, List
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.llm_client import LLMClient


class VerifierAgent:
    """Agent responsible for verifying and validating results"""
    
    def __init__(self):
        """Initialize the Verifier Agent"""
        self.llm = LLMClient(temperature=0.1)
    
    def verify_and_finalize(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify the results and ensure completeness
        
        Args:
            results: Results from Executor Agent
            
        Returns:
            Verified and normalized results
        """
        issues = self._check_completeness(results)
        
        if issues:
            print(f"Verification found issues: {issues}")
            results = self._fix_issues(results, issues)
        
        # Normalize the output
        normalized = self._normalize_output(results)
        
        return normalized
    
    def _check_completeness(self, results: Dict[str, Any]) -> List[str]:
        """
        Check if results are complete
        
        Args:
            results: Results to check
            
        Returns:
            List of issues found
        """
        issues = []
        
        # Check company summary
        if not results.get("company_summary") or len(results.get("company_summary", "")) < 10:
            issues.append("Missing or incomplete company summary")
        
        # Check use-cases
        use_cases = results.get("ai_use_cases", [])
        if not use_cases:
            issues.append("No AI use-cases generated")
        
        # Check resources for each use-case
        for idx, use_case in enumerate(use_cases):
            resources = use_case.get("resources", {})
            
            if not resources.get("arxiv"):
                issues.append(f"Use-case {idx + 1}: Missing arXiv resources")
            if not resources.get("huggingface"):
                issues.append(f"Use-case {idx + 1}: Missing Hugging Face resources")
            if not resources.get("kaggle"):
                issues.append(f"Use-case {idx + 1}: Missing Kaggle resources")
            if not resources.get("github"):
                issues.append(f"Use-case {idx + 1}: Missing GitHub resources")
        
        return issues
    
    def _fix_issues(self, results: Dict[str, Any], issues: List[str]) -> Dict[str, Any]:
        """
        Attempt to fix issues in results
        
        Args:
            results: Results with issues
            issues: List of issues to fix
            
        Returns:
            Fixed results
        """
        # For now, we'll add placeholder data for missing resources
        # In a production system, this would trigger re-execution
        
        for use_case in results.get("ai_use_cases", []):
            resources = use_case.get("resources", {})
            
            # Add placeholders for missing resources
            if not resources.get("arxiv"):
                resources["arxiv"] = [{
                    "title": f"Search arXiv for: {use_case.get('use_case', '')}",
                    "url": f"https://arxiv.org/search/?query={use_case.get('use_case', '').replace(' ', '+')}"
                }]
            
            if not resources.get("huggingface"):
                resources["huggingface"] = [{
                    "name": f"Search Hugging Face for: {use_case.get('use_case', '')}",
                    "url": f"https://huggingface.co/search?q={use_case.get('use_case', '').replace(' ', '+')}"
                }]
            
            if not resources.get("kaggle"):
                resources["kaggle"] = [{
                    "title": f"Search Kaggle for: {use_case.get('use_case', '')}",
                    "url": f"https://www.kaggle.com/search?q={use_case.get('use_case', '').replace(' ', '+')}"
                }]
            
            if not resources.get("github"):
                resources["github"] = [{
                    "name": f"Search GitHub for: {use_case.get('use_case', '')}",
                    "url": f"https://github.com/search?q={use_case.get('use_case', '').replace(' ', '+')}&type=repositories",
                    "stars": 0
                }]
        
        return results
    
    def _normalize_output(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize output to match the required schema
        
        Args:
            results: Results to normalize
            
        Returns:
            Normalized results
        """
        normalized = {
            "company": results.get("company", ""),
            "company_summary": results.get("company_summary", ""),
            "news_summary": results.get("news_summary", ""),
            "ai_use_cases": []
        }
        
        for use_case in results.get("ai_use_cases", []):
            normalized_use_case = {
                "use_case": use_case.get("use_case", ""),
                "description": use_case.get("description", ""),
                "resources": {
                    "arxiv": self._normalize_arxiv(use_case.get("resources", {}).get("arxiv", [])),
                    "huggingface": self._normalize_huggingface(use_case.get("resources", {}).get("huggingface", [])),
                    "kaggle": self._normalize_kaggle(use_case.get("resources", {}).get("kaggle", [])),
                    "github": self._normalize_github(use_case.get("resources", {}).get("github", []))
                }
            }
            normalized["ai_use_cases"].append(normalized_use_case)
        
        return normalized
    
    def _normalize_arxiv(self, resources: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Normalize arXiv resources"""
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", "")
            }
            for r in resources
        ]
    
    def _normalize_huggingface(self, resources: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Normalize Hugging Face resources"""
        return [
            {
                "name": r.get("name", ""),
                "url": r.get("url", "")
            }
            for r in resources
        ]
    
    def _normalize_kaggle(self, resources: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Normalize Kaggle resources"""
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", "")
            }
            for r in resources
        ]
    
    def _normalize_github(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize GitHub resources"""
        return [
            {
                "name": r.get("name", ""),
                "url": r.get("url", ""),
                "stars": r.get("stars", 0)
            }
            for r in resources
        ]

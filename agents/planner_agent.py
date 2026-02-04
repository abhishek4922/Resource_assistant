"""
Planner Agent
Converts user requests into structured execution plans
"""
from typing import Dict, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.llm_client import LLMClient


class PlannerAgent:
    """Agent responsible for creating execution plans"""
    
    def __init__(self):
        """Initialize the Planner Agent"""
        self.llm = LLMClient(temperature=0.1)
    
    def create_plan(self, company_name: str) -> Dict[str, Any]:
        """
        Create a structured execution plan for analyzing a company
        
        Args:
            company_name: Name of the company to analyze
            
        Returns:
            Structured plan as JSON
        """
        system_prompt = """You are a Planner Agent.
Your task is to convert user requests into a step-by-step execution plan.
You must return ONLY valid JSON following the exact schema provided.
Do not add explanations, comments, or any text outside the JSON structure.

The plan must include these steps in order:
1. Search for company information using DuckDuckGo
2. Summarize what the company does using LLM
3. Generate AI use-cases for the company using LLM
4. Search for resources (arXiv, Hugging Face, Kaggle, GitHub) for each use-case
5. Verify and finalize the output

Return the plan in this exact JSON format:
{
  "company": "company name here",
  "steps": [
    {
      "id": 1,
      "action": "search_company_info",
      "tool": "DuckDuckGoTool"
    },
    {
      "id": 2,
      "action": "summarize_company",
      "tool": "LLM"
    },
    {
      "id": 3,
      "action": "generate_ai_use_cases",
      "tool": "LLM"
    },
    {
      "id": 4,
      "action": "search_resources",
      "tool": ["ArxivTool", "HuggingFaceTool", "KaggleTool", "GitHubTool"]
    },
    {
      "id": 5,
      "action": "verify_and_finalize",
      "tool": "VerifierAgent"
    }
  ]
}"""

        user_prompt = f"Create an execution plan to analyze the company: {company_name}"
        
        try:
            plan = self.llm.generate_structured_output(system_prompt, user_prompt)
            
            # Ensure company name is set correctly
            plan["company"] = company_name
            
            return plan
            
        except Exception as e:
            print(f"Error creating plan: {e}")
            # Return a default plan if LLM fails
            return self._get_default_plan(company_name)
    
    def _get_default_plan(self, company_name: str) -> Dict[str, Any]:
        """
        Get a default execution plan
        
        Args:
            company_name: Name of the company
            
        Returns:
            Default plan structure
        """
        return {
            "company": company_name,
            "steps": [
                {
                    "id": 1,
                    "action": "search_company_info",
                    "tool": "DuckDuckGoTool"
                },
                {
                    "id": 2,
                    "action": "summarize_company",
                    "tool": "LLM"
                },
                {
                    "id": 3,
                    "action": "generate_ai_use_cases",
                    "tool": "LLM"
                },
                {
                    "id": 4,
                    "action": "search_resources",
                    "tool": ["ArxivTool", "HuggingFaceTool", "KaggleTool", "GitHubTool"]
                },
                {
                    "id": 5,
                    "action": "verify_and_finalize",
                    "tool": "VerifierAgent"
                }
            ]
        }

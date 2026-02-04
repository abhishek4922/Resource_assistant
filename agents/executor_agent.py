"""
Executor Agent
Executes the plan step-by-step and calls appropriate tools
"""
from typing import Dict, Any, List, Callable
import sys
import os
import concurrent.futures


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.llm_client import LLMClient
from tools.duckduckgo_tool import DuckDuckGoTool
from tools.arxiv_tool import ArxivTool
from tools.huggingface_tool import HuggingFaceTool
from tools.kaggle_tool import KaggleTool
from tools.github_tool import GitHubTool
from tools.news_tool import NewsTool


class ExecutorAgent:
    """Agent responsible for executing the plan"""
    
    def __init__(self, progress_callback: Callable[[str], None] = None):
        """
        Initialize the Executor Agent
        
        Args:
            progress_callback: Optional callback function for progress updates
        """
        self.llm = LLMClient(temperature=0.7)  # Higher temperature for more varied responses
        self.ddg_tool = DuckDuckGoTool(max_results=5)
        self.arxiv_tool = ArxivTool(max_results=5)
        self.hf_tool = HuggingFaceTool(max_results=5)
        self.kaggle_tool = KaggleTool(max_results=5)
        self.github_tool = GitHubTool(max_results=5)
        self.news_tool = NewsTool(max_results=5)
        self.progress_callback = progress_callback
    
    def _update_progress(self, message: str):
        """Update progress if callback is provided"""
        if self.progress_callback:
            self.progress_callback(message)
    
    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the plan step by step
        
        Args:
            plan: Execution plan from Planner Agent
            
        Returns:
            Execution results
        """
        company_name = plan.get("company", "")
        results = {
            "company": company_name,
            "company_summary": "",
            "news_summary": "",
            "ai_use_cases": []
        }
        
        # Step 1: Search company info
        self._update_progress("🔍 Searching for company information...")
        company_info = self._search_company_info(company_name)
        
        # Step 2: Fetch and summarize news/funding
        self._update_progress("📰 Analyzing recent news & funding...")
        results["news_summary"] = self._fetch_and_summarize_news(company_name)
        
        # Step 3: Summarize company
        self._update_progress("📝 Generating company summary...")
        results["company_summary"] = self._summarize_company(company_name, company_info)
        
        # Step 3: Generate AI use-cases
        self._update_progress("💡 Generating AI use-cases...")
        use_cases = self._generate_use_cases(company_name, results["company_summary"])
        
        # Step 4: Search resources for each use-case
        for idx, use_case in enumerate(use_cases, 1):
            self._update_progress(f"🔎 Searching resources for use-case {idx}/{len(use_cases)}...")
            resources = self._search_resources(use_case)
            
            # Ensure search_keywords key exists for the final output result
            keywords = use_case.get("search_keywords", use_case["use_case"])
            
            results["ai_use_cases"].append({
                "use_case": use_case["use_case"],
                "description": use_case["description"],
                "search_keywords": keywords,
                "resources": resources
            })
        
        return results
        
    def _search_company_info(self, company_name: str) -> List[Dict[str, Any]]:
        """Search for company information using DuckDuckGo"""
        try:
            return self.ddg_tool.search_company_info(company_name)
        except Exception as e:
            print(f"Error searching company info: {e}")
            return []

    def _fetch_and_summarize_news(self, company_name: str) -> str:
        """Fetch news/funding and summarize it"""
        news_text = "No recent news found."
        
        # Try NewsAPI first
        try:
            articles = self.news_tool.search_company_news(company_name)
            if articles:
                # Use data from NewsAPI
                news_text = "\n\n".join([
                    f"Title: {a.get('title', '')}\nDate: {a.get('published_at', '')}\nContent: {a.get('description', '')}"
                    for a in articles[:7] # Increased to 7
                ])
                print(f"Summarizing {len(articles)} articles from NewsAPI")
            else:
                # Fallback to DuckDuckGo
                raise ValueError("No articles from NewsAPI")
                
        except Exception:
            print("Fallback: Using DuckDuckGo for news/funding")
            try:
                # Dual search strategy for better coverage
                search_results = []
                
                # 1. Search for Funding specifically
                query_funding = f"{company_name} funding rounds investors crunchbase"
                results_funding = self.ddg_tool.search(query_funding)
                if results_funding:
                    search_results.extend(results_funding[:3])
                
                # 2. Search for General News
                query_news = f"{company_name} latest business news"
                results_news = self.ddg_tool.search(query_news)
                if results_news:
                    search_results.extend(results_news[:3])
                
                if search_results:
                    news_text = "\n\n".join([
                        f"Title: {r.get('title', '')}\nSnippet: {r.get('snippet', '')}"
                        for r in search_results
                    ])
                    print(f"Summarizing {len(search_results)} results from DDG")
            except Exception as e:
                print(f"DDG fallback error: {e}")
                return "Could not retrieve news or funding information."

        if not news_text or news_text == "No recent news found.":
            return "No recent news or funding information available."

        # Summarize using LLM - Requested to NOT be too concise
        system_prompt = """You are a financial news analyst.
Analyze the provided search results to create a DETAILED report on the company's recent activities.

Your goal is to extract specific details. Do NOT summarize too heavily; preserve the facts.

Structure your response exactly as follows:

**💰 Funding & Financials:**
*   List any funding rounds found (Series A/B/C, amounts in $, lists of investors, valuations).
*   If exact dates/amounts are found, include them.
*   If NO specific funding data is found, explicitly state: "No specific recent funding details found."

**📰 Recent Developments:**
*   List major product launches, partnerships, or expansions.
*   Include dates if available.

**📉 Market/Business Status:**
*   Briefly mention their current market position or Recent strategic moves.

Keep the tone professional and factual. Use bullet points for readability."""

        user_prompt = f"""Company: {company_name}

Raw Search Data:
{news_text}

Provide a detailed financial and news analysis based ONLY on this data."""

        try:
            summary = self.llm.generate_text(system_prompt, user_prompt)
            return summary
        except Exception as e:
            print(f"Summarization error: {e}")
            return "Error generating news summary."

    def _summarize_company(self, company_name: str, company_info: List[Dict[str, Any]]) -> str:
        """Summarize what the company does using LLM"""
        system_prompt = """You are a business analyst specializing in company research.
Analyze the search results and create a DETAILED summary of what this company does.

Your summary should include:
- The company's primary business and core offerings
- The specific industry/sector and market they operate in
- Their main products, services, or platform
- Their target customers or user base
- Any unique aspects of their business model

Write 3-4 sentences with specific details. Be factual and professional."""

        # Combine search results
        context = "\n\n".join([
            f"Title: {item['title']}\nContent: {item['body']}"
            for item in company_info[:3]
        ])
        
        user_prompt = f"""Company Name: {company_name}

Web Search Results:
{context}

Provide a DETAILED summary that captures the specific nature of {company_name}'s business, industry, and offerings."""

        try:
            summary = self.llm.generate_text(system_prompt, user_prompt)
            return summary
        except Exception as e:
            print(f"Error summarizing company: {e}")
            return f"{company_name} is a company in the technology/business sector."
    
    def _generate_use_cases(self, company_name: str, company_summary: str) -> List[Dict[str, Any]]:
        """Generate AI use-cases for the company using LLM"""
        system_prompt = """You are an AI consultant specializing in identifying AI opportunities for businesses.
Based on the SPECIFIC company description provided, propose EXACTLY 3 UNIQUE and RELEVANT AI use-cases.

IMPORTANT:
- Generate EXACTLY 3 use-cases. No more, no less.
- Each use-case must be SPECIFIC to this company's industry and business model
- Avoid generic use-cases like "chatbot" or "predictive analytics" unless highly relevant
- Focus on innovative, practical AI solutions that match the company's actual operations
- Consider the company's unique challenges and opportunities

For each use-case, provide:
- A clear, specific use-case name tailored to this company
- A detailed description of how it would work and benefit THIS SPECIFIC company
- 3-5 specific technical keywords for searching resources (e.g., "transformer NLP", "demand forecasting xgboost", "computer vision detection")

Return your response as a JSON array with this exact format:
[
  {
    "use_case": "Specific Use Case Name",
    "description": "Detailed description specific to this company's business",
    "search_keywords": "keyword1 keyword2 keyword3"
  }
]

Do not add any text before or after the JSON.
Start with [ and end with ]."""

        user_prompt = f"""Analyze this SPECIFIC company and generate UNIQUE AI use-cases:

Company Name: {company_name}

Company Description:
{company_summary}

Generate EXACTLY 3 AI use-cases that are SPECIFICALLY tailored to {company_name}'s business model, industry, and operations.
Make each use-case unique and relevant to what {company_name} actually does."""

        try:
            use_cases = self.llm.generate_structured_output(system_prompt, user_prompt)
            
            # Handle both list and dict responses
            if isinstance(use_cases, list):
                return use_cases[:10]  # Limit to 10 use-cases
            elif isinstance(use_cases, dict) and "use_cases" in use_cases:
                return use_cases["use_cases"][:10]
            else:
                return self._get_default_use_cases(company_name)
                
        except Exception as e:
            print(f"Error generating use-cases: {e}")
            return self._get_default_use_cases(company_name)
    
    def _get_default_use_cases(self, company_name: str) -> List[Dict[str, Any]]:
        """Get default use-cases if LLM fails"""
        return [
            {
                "use_case": "Customer Service Chatbot",
                "description": f"Implement an AI-powered chatbot to handle customer inquiries for {company_name}, improving response times and customer satisfaction."
            },
            {
                "use_case": "Predictive Analytics",
                "description": f"Use machine learning to predict trends and patterns in {company_name}'s business data for better decision-making."
            },
            {
                "use_case": "Process Automation",
                "description": f"Automate repetitive tasks and workflows at {company_name} using AI to increase efficiency and reduce costs."
            }
        ]
    
    def _search_resources(self, use_case_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Search for resources across all platforms in parallel"""
        resources = {
            "arxiv": [],
            "huggingface": [],
            "kaggle": [],
            "github": []
        }
        
        # Use specific keywords if available, otherwise just use the name
        if isinstance(use_case_data, dict):
            search_query = use_case_data.get("search_keywords", use_case_data.get("use_case", ""))
        else:
            search_query = str(use_case_data)
            
        # Clean up query
        if not search_query:
            return resources
            
        print(f"Searching resources for: {search_query}")
        
        # Define helper functions for parallel execution with error handling
        def search_arxiv():
            try:
                return "arxiv", self.arxiv_tool.search_use_case(search_query)
            except Exception as e:
                print(f"Error searching arXiv: {e}")
                return "arxiv", []

        def search_hf():
            try:
                return "huggingface", self.hf_tool.search_use_case(search_query)
            except Exception as e:
                print(f"Error searching Hugging Face: {e}")
                return "huggingface", []

        def search_kaggle():
            try:
                return "kaggle", self.kaggle_tool.search_use_case(search_query)
            except Exception as e:
                print(f"Error searching Kaggle: {e}")
                return "kaggle", []

        def search_github():
            try:
                return "github", self.github_tool.search_use_case(search_query)
            except Exception as e:
                print(f"Error searching GitHub: {e}")
                return "github", []
        
        # Execute searches in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(search_arxiv),
                executor.submit(search_hf),
                executor.submit(search_kaggle),
                executor.submit(search_github)
            ]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    key, result = future.result()
                    resources[key] = result
                except Exception as e:
                    print(f"Parallel search execution error: {e}")
        
        return resources

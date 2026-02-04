"""
LLM Client for interacting with Groq API
Uses Llama 3 for structured reasoning and generation
"""
import os
from typing import Optional, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import json
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Client for LLM operations using Groq"""
    
    def __init__(self, model: str = "llama-3.1-8b-instant", temperature: float = 0.1):
        """
        Initialize LLM client
        
        Args:
            model: Model name to use
            temperature: Temperature for generation (lower = more deterministic)
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name=model,
            temperature=temperature
        )
    
    def generate_structured_output(
        self, 
        system_prompt: str, 
        user_prompt: str,
        json_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output from LLM
        
        Args:
            system_prompt: System instructions
            user_prompt: User query
            json_schema: Optional JSON schema for validation
            
        Returns:
            Parsed JSON response
        """
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            content = response.content.strip()
            
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Smart JSON extraction: find first [ or { and last ] or }
            start_index = -1
            end_index = -1
            
            # Find start
            json_start_chars = ['[', '{']
            for char in json_start_chars:
                pos = content.find(char)
                if pos != -1 and (start_index == -1 or pos < start_index):
                    start_index = pos
            
            if start_index != -1:
                # Determine corresponding end char
                start_char = content[start_index]
                end_char = ']' if start_char == '[' else '}'
                
                # Find last occurrence of end char
                end_index = content.rfind(end_char)
                
                if end_index != -1 and end_index > start_index:
                    content = content[start_index : end_index + 1]
            
            # Parse JSON
            result = json.loads(content)
            return result
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Raw content: {content[:1000]}")  # Print more content for debugging
            raise
        except Exception as e:
            print(f"LLM generation error: {e}")
            raise
    
    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate plain text output from LLM
        
        Args:
            system_prompt: System instructions
            user_prompt: User query
            
        Returns:
            Generated text
        """
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            print(f"LLM generation error: {e}")
            raise

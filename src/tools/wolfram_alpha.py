"""
Wolfram Alpha API tool for mathematical computations.

This tool provides an interface to Wolfram Alpha's computational knowledge engine
for solving mathematical problems, symbolic computations, and data analysis.
"""

import os
import requests
import re
from typing import Optional, Dict, Any
from langchain_core.tools import BaseTool, tool
from pydantic import Field, BaseModel


class WolframAlphaQueryInput(BaseModel):
    """Input schema for Wolfram Alpha query."""
    query: str = Field(description="The mathematical query or problem to solve")
    format: str = Field(default="plaintext", description="Output format (plaintext, image, html)")


class SolveMathProblemInput(BaseModel):
    """Input schema for solving math problems."""
    problem: str = Field(description="The mathematical problem to solve")


class WolframAlphaTool(BaseTool):
    """A LangChain tool for interacting with Wolfram Alpha API."""
    
    name: str = "wolfram_alpha"
    description: str = (
        "A computational knowledge engine for solving mathematical problems, "
        "symbolic computations, and data analysis. Use for complex math problems "
        "that require step-by-step solutions or symbolic computation."
    )
    args_schema: type[BaseModel] = WolframAlphaQueryInput
    # Define fields explicitly for pydantic BaseTool
    app_id: Optional[str] = Field(default=None, description="Wolfram Alpha App ID")
    base_url: str = Field(default="http://api.wolframalpha.com/v2/query")
    
    def __init__(self, app_id: Optional[str] = None, **kwargs):
        """
        Initialize the Wolfram Alpha tool.
        
        Args:
            app_id: Wolfram Alpha App ID. If None, will try to get from 
                   WOLFRAM_ALPHA_APP_ID environment variable.
        """
        resolved_app_id = app_id or os.getenv("WOLFRAM_ALPHA_APP_ID")
        if not resolved_app_id:
            raise ValueError(
                "Wolfram Alpha App ID is required. "
                "Set WOLFRAM_ALPHA_APP_ID environment variable or pass app_id parameter."
            )
        # Pass validated values to pydantic BaseTool
        super().__init__(app_id=resolved_app_id, **kwargs)
    
    def _run(self, query: str, format: str = "plaintext") -> Dict[str, Any]:
        """
        Send a query to Wolfram Alpha API.
        
        Args:
            query: The query string to send to Wolfram Alpha
            format: The output format (plaintext, image, html, etc.)
            
        Returns:
            Dictionary containing the API response
        """
        params = {
            "input": query,
            "appid": self.app_id,
            "format": format,
            "output": "json"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Wolfram Alpha API request failed: {e}")
    
    def solve_math_problem(self, problem: str) -> Dict[str, Any]:
        """
        Solve a mathematical problem using Wolfram Alpha.
        
        Args:
            problem: The mathematical problem to solve
            
        Returns:
            Dictionary containing the solution and steps
        """
        result = self._run(problem)
        return self._parse_math_result(result)
    
    def _parse_math_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Wolfram Alpha API response for mathematical results.
        
        Args:
            result: Raw API response from Wolfram Alpha
            
        Returns:
            Parsed result with solution steps and final answer
        """
        if not result.get("queryresult", {}).get("success", False):
            return {"success": False, "error": "Query failed"}
        
        pods = result.get("queryresult", {}).get("pods", [])
        
        solution = {"success": True, "steps": [], "final_answer": None}
        
        for pod in pods:
            title = pod.get("title", "")
            subpods = pod.get("subpods", [])
            
            for subpod in subpods:
                plaintext = subpod.get("plaintext", "")
                if plaintext:
                    if title.lower() in ["result", "solution", "answer"]:
                        solution["final_answer"] = plaintext
                    else:
                        solution["steps"].append({"title": title, "content": plaintext})
        
        return solution
    
    def get_numeric_result(self, expression: str) -> Optional[float]:
        """
        Get numeric result from a mathematical expression.
        
        Args:
            expression: Mathematical expression to evaluate
            
        Returns:
            Numeric result if available, None otherwise
        """
        result = self.solve_math_problem(expression)
        if result["success"] and result["final_answer"]:
            try:
                # Try to extract numeric value from the answer
                answer = result["final_answer"]
                # Remove units and extract number
                match = re.search(r'[-+]?\d*\.?\d+', answer)
                if match:
                    return float(match.group())
            except (ValueError, TypeError):
                pass
        return None


# Structured tool for solving math problems
@tool(args_schema=SolveMathProblemInput)
def solve_math_problem_tool(problem: str) -> Dict[str, Any]:
    """
    Solve mathematical problems using Wolfram Alpha.
    
    Args:
        problem: The mathematical problem to solve
        
    Returns:
        Dictionary containing solution steps and final answer
    """
    tool = WolframAlphaTool()
    return tool.solve_math_problem(problem)


def create_wolfram_alpha_tool() -> WolframAlphaTool:
    """
    Factory function to create a Wolfram Alpha tool instance.
    
    Returns:
        WolframAlphaTool instance
    """
    return WolframAlphaTool()


# Example usage
if __name__ == "__main__":
    # This requires WOLFRAM_ALPHA_APP_ID environment variable to be set
    try:
        tool = create_wolfram_alpha_tool()
        
        # Test with a simple math problem
        result = tool.solve_math_problem("solve x^2 + 2x + 1 = 0")
        print("Math problem result:", result)
        
        # Test numeric evaluation
        numeric_result = tool.get_numeric_result("2 + 2")
        print("Numeric result:", numeric_result)
        
        # Test LangChain tool functionality
        tool_result = tool._run("integrate x^2")
        print("Tool result:", tool_result)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Please set WOLFRAM_ALPHA_APP_ID environment variable with your Wolfram Alpha App ID")
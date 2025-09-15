import os
from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Any 
from enum import Enum
from langgraph.graph import RunnableConfig

class SearchAPI(Enum):
    """Enumeration of available search API providers."""
    
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    WOLFRAM_ALPHA_ID = "wolfram_alpha_id"
    TAVILY = "tavily"
    NONE = "none"

class MCPConfig(BaseModel):
    """Configuration for Model Context Protocol (MCP) servers."""
    
    url: Optional[str] = Field(
        default=None,
        optional=True,
    )
    """The URL of the MCP server"""
    tools: Optional[List[str]] = Field(
        default=None,
        optional=True,
    )
    """The tools to make available to the LLM"""
    auth_required: Optional[bool] = Field(
        default=False,
        optional=True,
    )
    """Whether the MCP server requires authentication"""

class Configuration(BaseModel):
    """Main configuration class for the Math solver agent."""

    # General Configuration
    max_structured_output_retries: int = Field(
        default=3,
        metadata={
            "x_oap_ui_config": {
                "type": "number",
                "default": 3,
                "min": 1,
                "max": 10,
                "description": "Maximum number of retries for structured output calls from models"
            }
        }
    )

    # LLM configuration for comprehension phase
    comprehension_model: str = Field(
        default=os.getenv("COMPREHENSION_MODEL", "deepseek-r1"),
        description="Model name for the comprehension agent"
    )
    comprehension_temperature: float = Field(
        default=float(os.getenv("COMPREHENSION_TEMPERATURE", "0.2")),
        description="Sampling temperature for the comprehension agent"
    )
    comprehension_max_retries: int = Field(
        default=int(os.getenv("COMPREHENSION_MAX_RETRIES", "2")),
        description="Max retries for LLM invocation in comprehension agent"
    )

    # Verification limit
    verification_max_retries: int = Field(
        default=int(os.getenv("VERIFICATION_MAX_RETRIES", "2")),
        description="Max times to retry verification before ending the graph"
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        # Get raw values from environment or config
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }

        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**values)

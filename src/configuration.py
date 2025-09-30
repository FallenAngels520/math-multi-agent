import os
from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Any 
from enum import Enum
from typing import Any, Dict

class SearchAPI(Enum):
    """Enumeration of available search API providers."""
    
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    QWEN_3 = "qwen-3"
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

    allow_clarification: bool = Field(
        default=True,
        metadata={
            "x_oap_ui_config": {
                "type": "boolean",
                "default": True,
                "description": "Whether to allow the researcher to ask the user clarifying questions before starting research"
            }
        }
    )

    max_iterations: int = Field(
        default=6,
        metadata={
            "x_oap_ui_config": {
                "type": "slider",
                "default": 6,
                "min": 1,
                "max": 10,
                "step": 1,
                "description": "Maximum number of research iterations for the Research Supervisor. This is the number of times the Research Supervisor will reflect on the research and ask follow-up questions."
            }
        }
    )

    coordinator_model: str = Field(
        default="deepseek-r1",
        metadata={
            "x_oap_ui_config": {
                "type": "text",
                "default": "deepseek-r1",
                "description": "Model for conducting research. NOTE: Make sure your Researcher Model supports the selected search API."
            }
        }
    )

    # Verification limit
    verification_max_retries: int = Field(
        default=int(os.getenv("VERIFICATION_MAX_RETRIES", "2")),
        description="Max times to retry verification before ending the graph"
    )

    # ✨ Geometric-Algebraic Integration Agent Configuration
    enable_geometric_algebraic: bool = Field(
        default=True,
        metadata={
            "x_oap_ui_config": {
                "type": "boolean",
                "default": True,
                "description": "Enable Geometric-Algebraic Integration Agent for combining algebraic and geometric approaches"
            }
        }
    )
    """Whether to enable the Geometric-Algebraic Integration Agent"""

    geometric_algebraic_model: str = Field(
        default="qwen-3:20b",
        metadata={
            "x_oap_ui_config": {
                "type": "text",
                "default": "qwen-3:20b",
                "description": "Model for Geometric-Algebraic analysis"
            }
        }
    )
    """Model to use for Geometric-Algebraic Integration Agent"""

    # MCP Configuration for Geometric-Algebraic Tools
    mcp_geometric_config: Optional[MCPConfig] = Field(
        default=None,
        metadata={
            "x_oap_ui_config": {
                "type": "object",
                "description": "MCP server configuration for geometric visualization tools"
            }
        }
    )
    """MCP configuration for geometric-algebraic tools"""
    
    mcp_server_url: Optional[str] = Field(
        default=os.getenv("MCP_SERVER_URL"),
        metadata={
            "x_oap_ui_config": {
                "type": "text",
                "default": "",
                "description": "URL of the MCP server for geometric tools (e.g., http://localhost:3000)"
            }
        }
    )
    """URL of the MCP server"""
    
    mcp_tools: Optional[List[str]] = Field(
        default_factory=lambda: ["geometric_visualization", "algebraic_analysis", "correspondence_mapping"],
        metadata={
            "x_oap_ui_config": {
                "type": "array",
                "default": ["geometric_visualization", "algebraic_analysis", "correspondence_mapping"],
                "description": "List of MCP tools to enable for geometric-algebraic integration"
            }
        }
    )
    """List of MCP tools for geometric-algebraic integration"""
    
    mcp_auth_required: bool = Field(
        default=False,
        metadata={
            "x_oap_ui_config": {
                "type": "boolean",
                "default": False,
                "description": "Whether MCP server requires authentication"
            }
        }
    )
    """Whether MCP authentication is required"""
    
    # Confidence threshold for geometric-algebraic applicability
    geometric_algebraic_threshold: float = Field(
        default=0.6,
        metadata={
            "x_oap_ui_config": {
                "type": "slider",
                "default": 0.6,
                "min": 0.0,
                "max": 1.0,
                "step": 0.1,
                "description": "Confidence threshold for applying geometric-algebraic approach (0.0-1.0)"
            }
        }
    )
    """Minimum confidence score to apply geometric-algebraic integration"""

    @classmethod
    def from_runnable_config(
        cls, config: Optional[Dict[str, Any]] = None
    ) -> "Configuration":
        """Create a Configuration instance from a config dictionary."""
        configurable = (
            config.get("configurable", {}) if config else {}
        )

        # Get raw values from environment or config
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }

        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**values)

"""
State management module for the multi-agent math problem solving system.
Defines the core state structures used by LangGraph for agent coordination.
"""

import operator
from typing import Annotated, Optional, List, Dict, Any
from enum import Enum

from langchain_core.messages import MessageLikeRepresentation
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


###################
# Structured Outputs
###################

class SolveMathProblem(BaseModel):
    """Call this tool to solve a specific math problem step."""
    problem_step: str = Field(
        description="The specific math problem step to solve with detailed instructions.",
    )

class VerifySolution(BaseModel):
    """Call this tool to verify a mathematical solution."""
    solution_to_verify: str = Field(
        description="The mathematical solution to verify for correctness.",
    )

class PlanSolutionStrategy(BaseModel):
    """Model for planning mathematical solution strategies."""
    solution_strategy: str = Field(
        description="The planned strategy for solving the mathematical problem.",
    )
    steps_required: int = Field(
        description="Number of steps required to solve the problem.",
    )


###################
# State Definitions
###################

def override_reducer(current_value, new_value):
    """Reducer：默认追加合并；当传入 {"type": "override", "value": ...} 时执行覆盖。"""
    if isinstance(new_value, dict) and new_value.get("type") == "override":
        return new_value.get("value", new_value)
    return operator.add(current_value, new_value)


def dict_merge_reducer(current_value: Optional[Dict[str, Any]], new_value: Any) -> Any:
    """
    Reducer：用于 dict 字段的合并/覆盖。
    - 覆盖：当 new_value 为 {"type": "override", "value": {...}}
    - 合并：其余情况若均为 dict，执行浅合并（右侧覆盖左侧键）。
    - 兜底：返回 new_value（允许首次赋值或类型不匹配时直接替换）。
    """
    if isinstance(new_value, dict) and new_value.get("type") == "override":
        return new_value.get("value", {})
    if current_value is None:
        return new_value if isinstance(new_value, dict) else {}
    if isinstance(current_value, dict) and isinstance(new_value, dict):
        return {**current_value, **new_value}
    return new_value


class ProblemType(str, Enum):
    """Enumeration of supported math problem types."""
    ALGEBRA = "algebra"
    GEOMETRY = "geometry" 
    CALCULUS = "calculus"
    PROBABILITY = "probability"
    STATISTICS = "statistics"
    DIFFERENTIAL_EQUATIONS = "differential_equations"
    LINEAR_ALGEBRA = "linear_algebra"
    OTHER = "other"


class ExecutionStatus(str, Enum):
    """Enumeration of execution status states."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_RETRY = "needs_retry"


class MathInputState(MessagesState):
    """Input state containing only user messages with math problems."""


class ComprehensionState(TypedDict):
    """State structure for comprehension agent results."""
    problem_type: ProblemType
    known_conditions: Annotated[Dict[str, Any], dict_merge_reducer]
    unknown_variables: Annotated[List[str], override_reducer]
    constraints: Annotated[List[str], override_reducer]
    hidden_conditions: Annotated[List[str], override_reducer]
    potential_pitfalls: Annotated[List[str], override_reducer]
    structured_input: Annotated[Dict[str, Any], dict_merge_reducer]
    comprehension_messages: Annotated[List[MessageLikeRepresentation], operator.add]


class PlanningState(TypedDict):
    """State structure for planning agent results."""
    solution_strategy: str
    roadmap: Annotated[List[Dict[str, Any]], override_reducer]
    current_step_index: int
    total_steps: int
    alternative_strategies: Annotated[List[Dict[str, Any]], override_reducer]
    complexity_estimate: str
    planning_messages: Annotated[List[MessageLikeRepresentation], operator.add]
    planning_iterations: int = 0


class ExecutionState(TypedDict):
    """State structure for execution agent results."""
    current_step: Dict[str, Any]
    intermediate_results: Annotated[List[Dict[str, Any]], override_reducer]
    tools_used: Annotated[List[str], override_reducer]
    derivation_process: str
    step_status: ExecutionStatus
    execution_messages: Annotated[List[MessageLikeRepresentation], operator.add]
    execution_iterations: int = 0


class VerificationState(TypedDict):
    """State structure for verification agent results."""
    is_valid: bool
    validation_method: str
    error_details: Optional[Dict[str, Any]]
    optimization_suggestions: Annotated[List[str], override_reducer]
    confidence_score: float
    verification_messages: Annotated[List[MessageLikeRepresentation], operator.add]


class MathProblemState(MessagesState):
    """
    Main state structure for the LangGraph workflow.
    
    This is the primary state object that flows through the entire
    multi-agent problem solving pipeline.
    """
    # Input/output related fields
    user_input: str
    final_answer: Optional[str]
    solution_steps: Annotated[List[str], override_reducer]
    
    # Math-specific shared fields across agents (see .cursorrule §11)
    assumptions: Annotated[List[str], override_reducer]
    expressions: Annotated[List[str], override_reducer]
    sympy_objects: Annotated[Dict[str, Any], dict_merge_reducer]
    proof_steps: Annotated[List[str], override_reducer]
    counter_examples: Annotated[List[str], override_reducer]
    
    # Flow control fields
    current_agent: str
    execution_status: ExecutionStatus
    error_message: Optional[str]
    total_iterations: int = 0
    verification_iterations: int = 0
    
    # Sub-state fields for each agent with proper reducers
    comprehension_result: Optional[ComprehensionState]
    planning_result: Optional[PlanningState]
    execution_result: Optional[ExecutionState]
    verification_result: Optional[VerificationState]
    
    # Agent-specific message tracks
    coordinator_messages: Annotated[List[MessageLikeRepresentation], operator.add]
    comprehension_messages: Annotated[List[MessageLikeRepresentation], operator.add]
    planning_messages: Annotated[List[MessageLikeRepresentation], operator.add]
    execution_messages: Annotated[List[MessageLikeRepresentation], operator.add]
    verification_messages: Annotated[List[MessageLikeRepresentation], operator.add]

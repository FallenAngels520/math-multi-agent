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

class ComprehensionAnalysis(BaseModel):
    """Structured output model for comprehension agent analysis based on prompt template."""
    
    # 第一阶段：问题表象解构
    givens: List[str] = Field(
        description="已知信息 (Givens): 结构化地列出所有明确给出的条件、数据、定义和关系",
        default_factory=list
    )
    objectives: List[str] = Field(
        description="求解目标 (Objectives): 准确无误地阐述问题最终要求解或证明什么",
        default_factory=list
    )
    explicit_constraints: List[str] = Field(
        description="显性约束 (Explicit Constraints): 识别所有对变量或解的明确限制",
        default_factory=list
    )
    
    # 第二阶段：核心原理溯源
    primary_field: str = Field(
        description="核心领域 (Primary Field): 问题所属的主要数学分支",
        default=""
    )
    fundamental_principles: List[Dict[str, Any]] = Field(
        description="基础原理与工具 (Principles & Tools): 识别驱动该问题的根本数学思想或原理",
        default_factory=list
    )
    
    # 第三阶段：策略路径构建
    strategy_deduction: str = Field(
        description="从原理到策略的推演 (Deduction from Principles to Strategy): 详细阐述如何从基础原理构建解题思路",
        default=""
    )
    key_breakthroughs: List[str] = Field(
        description="关键转化与突破口 (Key Transformations & Breakthroughs): 解决此问题的关键步骤或思维转化点",
        default_factory=list
    )
    potential_risks: List[str] = Field(
        description="潜在风险与验证点 (Potential Risks & Verification Points): 逻辑陷阱、计算易错点或需要验证的环节",
        default_factory=list
    )
    
    # 元数据
    problem_type: str = Field(
        description="The primary mathematical field of the problem (algebra, geometry, calculus, etc.)",
        default=""
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "description": "代数方程问题示例",
                    "givens": ["方程 x^2 - 5x + 6 = 0"],
                    "objectives": ["求解方程的所有实数根"],
                    "explicit_constraints": ["x ∈ ℝ"],
                    "primary_field": "代数",
                    "fundamental_principles": [
                        {
                            "principle": "方程求解思想",
                            "related_tools": ["因式分解法", "求根公式", "韦达定理"],
                            "principle_manifestation": "将方程转化为可解的形式"
                        }
                    ],
                    "strategy_deduction": "本题的核心是方程求解思想。最基础的方法是尝试因式分解，将二次方程分解为两个一次因式的乘积。如果因式分解困难，则使用求根公式直接计算。",
                    "key_breakthroughs": ["识别出方程可因式分解为 (x-2)(x-3)=0"],
                    "potential_risks": ["需要验证解是否满足原方程", "检查判别式非负性"],
                    "problem_type": "algebra"
                },
                {
                    "description": "几何问题示例", 
                    "givens": ["直角三角形 ABC，∠C=90°", "AC=3, BC=4"],
                    "objectives": ["求斜边 AB 的长度"],
                    "explicit_constraints": ["三角形为直角三角形"],
                    "primary_field": "几何",
                    "fundamental_principles": [
                        {
                            "principle": "勾股定理",
                            "related_tools": ["毕达哥拉斯定理"],
                            "principle_manifestation": "直角三角形两直角边平方和等于斜边平方"
                        }
                    ],
                    "strategy_deduction": "本题的核心是勾股定理的应用。直接应用定理公式 AB² = AC² + BC² 计算斜边长度。",
                    "key_breakthroughs": ["识别出这是标准的勾股定理应用场景"],
                    "potential_risks": ["需要确保三角形确实是直角三角形", "单位一致性检查"],
                    "problem_type": "geometry"
                },
                {
                    "description": "概率问题示例",
                    "givens": ["一副标准扑克牌（52张）", "随机抽取一张牌"],
                    "objectives": ["求抽到红心的概率"],
                    "explicit_constraints": ["等概率随机抽取"],
                    "primary_field": "概率",
                    "fundamental_principles": [
                        {
                            "principle": "古典概型",
                            "related_tools": ["概率公式 P(A)=m/n"],
                            "principle_manifestation": "每个基本事件等可能发生"
                        }
                    ],
                    "strategy_deduction": "本题的核心是古典概型思想。需要计算有利事件数（红心牌数13）与总事件数（总牌数52）的比值。",
                    "key_breakthroughs": ["识别出这是标准的古典概型问题"],
                    "potential_risks": ["需要确认牌是否完整且洗匀", "概率值应在0到1之间"],
                    "problem_type": "probability"
                }
            ]
        }


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
    """State structure for comprehension agent results aligned with prompt template."""
    
    # 第一阶段：问题表象解构
    givens: Annotated[List[str], override_reducer]
    objectives: Annotated[List[str], override_reducer]
    explicit_constraints: Annotated[List[str], override_reducer]
    
    # 第二阶段：核心原理溯源
    primary_field: str
    fundamental_principles: Annotated[List[Dict[str, Any]], override_reducer]
    
    # 第三阶段：策略路径构建
    strategy_deduction: str
    key_breakthroughs: Annotated[List[str], override_reducer]
    potential_risks: Annotated[List[str], override_reducer]
    
    # 元数据和兼容字段
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

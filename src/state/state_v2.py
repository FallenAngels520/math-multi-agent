"""
Revised State Management Module for Math Multi-Agent System
基于提示词与Agent深度绑定的状态设计
"""

import operator
from typing import Annotated, Optional, List, Dict, Any, TypedDict
from enum import Enum
from pydantic import BaseModel, Field
from langchain_core.messages import MessageLikeRepresentation
from langgraph.graph import MessagesState


###################
# Reducer Functions
###################

def override_reducer(current_value, new_value):
    """Reducer：默认追加合并；当传入 {"type": "override", "value": ...} 时执行覆盖。"""
    if isinstance(new_value, dict) and new_value.get("type") == "override":
        return new_value.get("value", new_value)
    return operator.add(current_value, new_value)


def dict_merge_reducer(current_value: Optional[Dict[str, Any]], new_value: Any) -> Any:
    """Reducer：用于 dict 字段的合并/覆盖。"""
    if isinstance(new_value, dict) and new_value.get("type") == "override":
        return new_value.get("value", {})
    if current_value is None:
        return new_value if isinstance(new_value, dict) else {}
    if isinstance(current_value, dict) and isinstance(new_value, dict):
        return {**current_value, **new_value}
    return new_value


def list_append_reducer(current_value: Optional[List[Any]], new_value: Any) -> List[Any]:
    """Reducer：用于列表字段的追加合并。"""
    if current_value is None:
        return [new_value] if new_value is not None else []
    if isinstance(new_value, list):
        return current_value + new_value
    return current_value + [new_value]


###################
# Enumerations
###################

class ProblemType(str, Enum):
    """数学问题类型枚举"""
    ALGEBRA = "algebra"
    GEOMETRY = "geometry" 
    CALCULUS = "calculus"
    PROBABILITY = "probability"
    STATISTICS = "statistics"
    DIFFERENTIAL_EQUATIONS = "differential_equations"
    LINEAR_ALGEBRA = "linear_algebra"
    OTHER = "other"


class ExecutionStatus(str, Enum):
    """执行状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_RETRY = "needs_retry"


class ToolType(str, Enum):
    """工具类型枚举"""
    SYMPY = "sympy"
    WOLFRAM = "wolfram"
    INTERNAL_REASONING = "internal_reasoning"


class VerificationVerdict(str, Enum):
    """验证裁决枚举"""
    PASSED = "PASSED"
    PASSED_WITH_WARNINGS = "PASSED_WITH_WARNINGS"
    FAILED = "FAILED"


###################
# Structured Output Models (基于提示词模板)
###################

class ClarifyWithUser(BaseModel):
    """Model for user clarification requests."""
    
    need_clarification: bool = Field(
        description="Whether the user needs to be asked a clarifying question.",
    )
    question: str = Field(
        description="A question to ask the user to clarify the report scope",
    )
    verification: str = Field(
        description="Verify message that we will start research after the user has provided the necessary information.",
    )

class LaTeXNormalization(BaseModel):
    """LaTeX标准化预处理结果"""
    original_text: str = Field(description="原始问题文本")
    normalized_latex: str = Field(description="标准化LaTeX版本")
    preprocessing_notes: List[str] = Field(default_factory=list, description="预处理说明")


class ProblemSurfaceDeconstruction(BaseModel):
    """问题表象解构结果"""
    givens: List[str] = Field(default_factory=list, description="已知信息")
    objectives: List[str] = Field(default_factory=list, description="求解目标")
    explicit_constraints: List[str] = Field(default_factory=list, description="显性约束")


class CorePrinciplesTracing(BaseModel):
    """核心原理溯源结果"""
    primary_field: str = Field(default="", description="核心领域")
    fundamental_principles: List[Dict[str, Any]] = Field(default_factory=list, description="基础原理与工具")


class StrategicPathBuilding(BaseModel):
    """策略路径构建结果"""
    strategy_deduction: str = Field(default="", description="从原理到策略的推演")
    key_breakthroughs: List[str] = Field(default_factory=list, description="关键转化与突破口")
    potential_risks: List[str] = Field(default_factory=list, description="潜在风险与验证点")


class ComprehensionAnalysis(BaseModel):
    """题目理解智能体结构化输出（完全匹配提示词模板）"""
    latex_normalization: LaTeXNormalization
    surface_deconstruction: ProblemSurfaceDeconstruction
    principles_tracing: CorePrinciplesTracing
    path_building: StrategicPathBuilding
    problem_type: ProblemType = ProblemType.OTHER


class ExecutionTask(BaseModel):
    """执行任务定义（基于规划提示词模板）"""
    task_id: str = Field(description="任务唯一标识符")
    description: str = Field(description="任务描述")
    principle_link: str = Field(description="原理链接")
    method: str = Field(description="执行方法")
    params: Dict[str, Any] = Field(default_factory=dict, description="参数配置")
    dependencies: List[str] = Field(default_factory=list, description="依赖任务")
    output_id: str = Field(description="输出标识符")


class ExecutionPlan(BaseModel):
    """执行计划（基于规划提示词模板）"""
    plan_metadata: Dict[str, Any] = Field(default_factory=dict, description="计划元数据")
    workspace_initialization: List[Dict[str, Any]] = Field(default_factory=list, description="工作区初始化")
    execution_plan: Dict[str, List[ExecutionTask]] = Field(default_factory=dict, description="执行任务计划")
    final_output: Dict[str, Any] = Field(default_factory=dict, description="最终输出配置")


class ToolExecution(BaseModel):
    """工具执行记录（基于执行提示词模板）"""
    task_id: str = Field(description="对应任务ID")
    tool_selected: ToolType = Field(description="选择的工具")
    tool_call_code: str = Field(description="工具调用代码")
    tool_output: Any = Field(description="工具输出结果")
    analysis_rationale: str = Field(description="工具选择分析理由")
    workspace_update: Dict[str, Any] = Field(default_factory=dict, description="工作区更新")


class VerificationCheck(BaseModel):
    """验证检查项（基于验证提示词模板）"""
    check_type: str = Field(description="检查类型")
    status: str = Field(description="检查状态")
    details: str = Field(description="检查详情")
    constraints_verified: List[str] = Field(default_factory=list, description="验证的约束条件")


class VerificationReport(BaseModel):
    """验证报告（基于验证提示词模板）"""
    verdict: VerificationVerdict = Field(description="最终裁决")
    consistency_check: VerificationCheck = Field(description="一致性检查")
    logical_chain_audit: VerificationCheck = Field(description="逻辑链审计")
    constraint_verification: VerificationCheck = Field(description="约束满足验证")
    final_answer_assessment: VerificationCheck = Field(description="最终答案评估")
    rationale: str = Field(description="裁决理由")


###################
# State Definitions (基于Agent功能分解)
###################

class MathInputState(MessagesState):
    """输入状态：仅包含用户消息"""
    user_input: str = Field(description="用户输入的数学问题")


class ComprehensionState(TypedDict):
    """题目理解智能体状态（完全匹配提示词三阶段框架）"""
    
    # 预处理阶段
    latex_normalization: Annotated[LaTeXNormalization, override_reducer]
    
    # 第一阶段：问题表象解构
    surface_deconstruction: Annotated[ProblemSurfaceDeconstruction, override_reducer]
    
    # 第二阶段：核心原理溯源
    principles_tracing: Annotated[CorePrinciplesTracing, override_reducer]
    
    # 第三阶段：策略路径构建
    path_building: Annotated[StrategicPathBuilding, override_reducer]
    
    # 元数据
    problem_type: ProblemType
    analysis_completed: bool
    comprehension_messages: Annotated[List[MessageLikeRepresentation], operator.add]
    
    # 错误处理
    error_details: Optional[Dict[str, Any]]
    retry_count: int


class PlanningState(TypedDict):
    """策略规划智能体状态（基于规划提示词模板）"""
    
    # 计划生成
    execution_plan: Annotated[ExecutionPlan, override_reducer]
    
    # 任务管理
    current_task_index: int
    total_tasks: int
    completed_tasks: Annotated[List[str], list_append_reducer]
    
    # 替代策略
    alternative_strategies: Annotated[List[Dict[str, Any]], list_append_reducer]
    complexity_estimate: str
    
    # 元数据
    planning_messages: Annotated[List[MessageLikeRepresentation], operator.add]
    planning_iterations: int
    
    # 错误处理
    error_details: Optional[Dict[str, Any]]


class ExecutionState(TypedDict):
    """计算执行智能体状态（基于执行提示词模板）"""
    
    # 工作区管理
    workspace: Annotated[Dict[str, Any], dict_merge_reducer]
    
    # 工具执行记录
    tool_executions: Annotated[List[ToolExecution], list_append_reducer]
    tools_used: Annotated[List[ToolType], list_append_reducer]
    
    # 计算轨迹
    computational_trace: Annotated[List[Dict[str, Any]], list_append_reducer]
    intermediate_results: Annotated[List[Dict[str, Any]], list_append_reducer]
    
    # 当前任务
    current_task: Optional[ExecutionTask]
    step_status: ExecutionStatus
    
    # 元数据
    execution_messages: Annotated[List[MessageLikeRepresentation], operator.add]
    execution_iterations: int
    
    # 错误处理
    error_details: Optional[Dict[str, Any]]


class VerificationState(TypedDict):
    """验证反思智能体状态（基于验证提示词模板）"""
    
    # 验证报告
    verification_report: Annotated[VerificationReport, override_reducer]
    
    # 检查记录
    verification_checks: Annotated[List[VerificationCheck], list_append_reducer]
    
    # 约束验证
    constraints_verified: Annotated[List[str], list_append_reducer]
    violations_found: Annotated[List[str], list_append_reducer]
    
    # 优化建议
    optimization_suggestions: Annotated[List[str], list_append_reducer]
    
    # 元数据
    verification_messages: Annotated[List[MessageLikeRepresentation], operator.add]
    verification_iterations: int
    confidence_score: float
    
    # 错误处理
    error_details: Optional[Dict[str, Any]]


class CoordinatorState(TypedDict):
    """协调管理智能体状态（基于流程控制需求）"""
    
    # 流程控制
    current_phase: str  # "comprehension", "planning", "execution", "verification"
    execution_status: ExecutionStatus
    
    # 迭代管理
    total_iterations: int
    phase_iterations: Annotated[Dict[str, int], dict_merge_reducer]
    
    # 重试管理
    retry_counts: Annotated[Dict[str, int], dict_merge_reducer]
    max_retries: Annotated[Dict[str, int], dict_merge_reducer]
    
    # 错误处理
    error_messages: Annotated[List[str], list_append_reducer]
    fatal_errors: Annotated[List[str], list_append_reducer]
    
    # 协调消息
    coordinator_messages: Annotated[List[MessageLikeRepresentation], operator.add]


class MathProblemStateV2(MessagesState):
    """
    主状态结构 - 基于提示词与Agent深度绑定的设计
    
    设计原则：
    1. 每个Agent的状态字段完全匹配其提示词模板的结构
    2. 使用适当的reducer策略管理状态更新
    3. 保持状态字段的单一职责和清晰边界
    """
    
    # 输入输出
    user_input: str
    final_answer: Optional[str]
    solution_steps: Annotated[List[str], list_append_reducer]
    
    # 数学特定字段
    assumptions: Annotated[List[str], list_append_reducer]
    expressions: Annotated[List[str], list_append_reducer]
    sympy_objects: Annotated[Dict[str, Any], dict_merge_reducer]
    proof_steps: Annotated[List[str], list_append_reducer]
    counter_examples: Annotated[List[str], list_append_reducer]
    
    # 全局控制字段
    is_completed: bool
    completion_reason: Optional[str]
    
    # 性能监控
    start_time: Optional[float]
    end_time: Optional[float]
    performance_metrics: Annotated[Dict[str, Any], dict_merge_reducer]


###################
# State Utilities
###################

def create_initial_state(user_input: str) -> MathProblemStateV2:
    """创建初始状态"""
    return MathProblemStateV2(
        user_input=user_input,
        final_answer=None,
        solution_steps=[],
        assumptions=[],
        expressions=[],
        sympy_objects={},
        proof_steps=[],
        counter_examples=[],
        comprehension_state=None,
        planning_state=None,
        execution_state=None,
        verification_state=None,
        coordinator_state={
            "current_phase": "comprehension",
            "execution_status": ExecutionStatus.PENDING,
            "total_iterations": 0,
            "phase_iterations": {},
            "retry_counts": {},
            "max_retries": {
                "comprehension": 3,
                "planning": 3,
                "execution": 5,
                "verification": 3
            },
            "error_messages": [],
            "fatal_errors": [],
            "coordinator_messages": []
        },
        is_completed=False,
        completion_reason=None,
        start_time=None,
        end_time=None,
        performance_metrics={}
    )


def get_current_phase(state: MathProblemStateV2) -> str:
    """获取当前阶段"""
    if state.get("coordinator_state"):
        return state["coordinator_state"].get("current_phase", "comprehension")
    return "comprehension"


def should_retry_phase(state: MathProblemStateV2, phase: str) -> bool:
    """判断是否应该重试某个阶段"""
    if not state.get("coordinator_state"):
        return False
    
    coordinator = state["coordinator_state"]
    current_retries = coordinator.get("retry_counts", {}).get(phase, 0)
    max_retries = coordinator.get("max_retries", {}).get(phase, 3)
    
    return current_retries < max_retries


def mark_phase_completed(state: MathProblemStateV2, phase: str) -> MathProblemStateV2:
    """标记阶段完成"""
    if not state.get("coordinator_state"):
        return state
    
    coordinator = state["coordinator_state"].copy()
    coordinator["current_phase"] = phase
    coordinator["execution_status"] = ExecutionStatus.COMPLETED
    
    return {
        **state,
        "coordinator_state": coordinator
    }
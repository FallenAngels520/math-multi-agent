"""
精简State设计 - 基于open_deep_research模式

设计原则：
1. 全局状态（AgentState）：跨智能体共享的核心数据
2. 子图状态：每个智能体独立的工作区
3. Reducer模式：追加（operator.add）和覆盖（override_reducer）
4. 结构化输出：Pydantic BaseModel定义标准输出
5. 迭代优化：支持带反馈的迭代优化模式（agent.md）
"""

import operator
from typing import Annotated, Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from langchain_core.messages import MessageLikeRepresentation
from langgraph.graph import MessagesState


###################
# Reducer Functions
###################

def override_reducer(current_value, new_value):
    """
    覆盖式Reducer：支持强制覆盖模式
    - 正常追加：new_value直接追加
    - 强制覆盖：{"type": "override", "value": ...} 完全替换
    """
    if isinstance(new_value, dict) and new_value.get("type") == "override":
        return new_value.get("value", new_value)
    if current_value is None:
        return new_value
    if isinstance(current_value, list) and isinstance(new_value, list):
        return current_value + new_value
    return new_value


###################
# Enumerations
###################

class ProblemType(str, Enum):
    """数学问题类型"""
    ALGEBRA = "algebra"
    GEOMETRY = "geometry" 
    CALCULUS = "calculus"
    PROBABILITY = "probability"
    STATISTICS = "statistics"
    DIFFERENTIAL_EQUATIONS = "differential_equations"
    LINEAR_ALGEBRA = "linear_algebra"
    OTHER = "other"


class ToolType(str, Enum):
    """工具类型"""
    SYMPY = "sympy"
    WOLFRAM = "wolfram_alpha"
    INTERNAL_REASONING = "internal_reasoning"


class VerificationStatus(str, Enum):
    """验证状态（agent.md定义）"""
    PASSED = "PASSED"                      # 通过
    NEEDS_REVISION = "NEEDS_REVISION"      # 需要修订
    FATAL_ERROR = "FATAL_ERROR"            # 致命错误


class IssueType(str, Enum):
    """问题类型（agent.md定义）"""
    FACTUAL_ERROR = "Factual Error"              # 事实错误
    LOGICAL_FLAW = "Logical Flaw"                # 逻辑缺陷
    INCOMPLETENESS = "Incompleteness"            # 不完整
    CALCULATION_ERROR = "Calculation Error"      # 计算错误
    FORMAT_ERROR = "Format Error"                # 格式错误
    MISSING_STEP = "Missing Step"                # 缺失步骤


class ProblemLevel(str, Enum):
    """问题层级（决定返回哪个阶段）"""
    COMPREHENSION_LEVEL = "comprehension"  # 理解层面的根本偏差
    PLANNING_LEVEL = "planning"            # 规划层面的策略问题
    EXECUTION_LEVEL = "execution"          # 执行层面的小错


###################
# 结构化输出模型（Structured Output Models）
###################

class ComprehensionOutput(BaseModel):
    """题目理解智能体的结构化输出"""
    
    # LaTeX标准化
    normalized_latex: str = Field(description="标准化的LaTeX题目描述")
    
    # 第一阶段：问题表象解构
    givens: List[str] = Field(default_factory=list, description="已知信息")
    objectives: List[str] = Field(default_factory=list, description="求解目标")
    explicit_constraints: List[str] = Field(default_factory=list, description="显性约束")
    
    # 第二阶段：核心原理溯源
    primary_field: str = Field(default="", description="核心数学领域")
    fundamental_principles: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="基础原理：[{principle, related_tools, manifestation}]"
    )
    
    # 第三阶段：策略路径构建
    strategy_deduction: str = Field(default="", description="从原理到策略的推演")
    key_breakthroughs: List[str] = Field(default_factory=list, description="关键转化点")
    potential_risks: List[str] = Field(default_factory=list, description="潜在风险")
    
    # 元数据
    problem_type: ProblemType = ProblemType.OTHER


class ExecutionTask(BaseModel):
    """单个执行任务定义"""
    task_id: str = Field(description="任务唯一标识")
    description: str = Field(description="任务描述")
    principle_link: str = Field(description="链接的原理")
    method: str = Field(description="执行方法")
    params: Dict[str, Any] = Field(default_factory=dict, description="任务参数")
    dependencies: List[str] = Field(default_factory=list, description="依赖的任务ID")
    output_id: str = Field(description="输出结果的标识符")


class PlanningOutput(BaseModel):
    """策略规划智能体的结构化输出"""
    
    plan_metadata: Dict[str, Any] = Field(default_factory=dict, description="计划元数据")
    workspace_init: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="工作区初始化变量"
    )
    execution_tasks: List[ExecutionTask] = Field(
        default_factory=list, 
        description="执行任务列表（DAG结构）"
    )
    alternative_strategies: List[str] = Field(
        default_factory=list, 
        description="备选策略"
    )


class ToolExecutionRecord(BaseModel):
    """单个工具执行记录"""
    task_id: str = Field(description="对应的任务ID")
    tool_type: ToolType = Field(description="使用的工具类型")
    tool_input: str = Field(description="工具输入代码/查询")
    tool_output: Any = Field(description="工具输出结果")
    rationale: str = Field(description="工具选择理由")


class ExecutionOutput(BaseModel):
    """计算执行智能体的结构化输出"""
    
    workspace: Dict[str, Any] = Field(default_factory=dict, description="当前工作区变量")
    tool_executions: List[ToolExecutionRecord] = Field(
        default_factory=list, 
        description="工具执行记录"
    )
    computational_trace: List[str] = Field(
        default_factory=list, 
        description="计算轨迹说明"
    )
    final_result: Optional[Any] = Field(default=None, description="最终计算结果")


class Issue(BaseModel):
    """单个问题描述（agent.md定义的诊断报告格式）"""
    issue_type: IssueType = Field(description="问题类型")
    detail: str = Field(description="问题详细说明")
    location: Optional[str] = Field(default=None, description="问题位置（如第几步、哪个计算）")


class VerificationOutput(BaseModel):
    """
    验证反思智能体的结构化输出（完全符合agent.md的诊断报告格式）
    
    诊断报告包含：
    1. 评估状态：PASSED, NEEDS_REVISION, FATAL_ERROR
    2. 问题列表：清晰指出问题类型和详情
    3. 修正建议：具体可执行的修改意见
    4. 问题层级：决定返回到哪个智能体
    """
    
    # 评估状态
    status: VerificationStatus = Field(description="评估状态")
    
    # 问题列表（详细的诊断信息）
    issues: List[Issue] = Field(
        default_factory=list, 
        description="发现的问题列表"
    )
    
    # 修正建议（可执行的具体建议）
    suggestions: List[str] = Field(
        default_factory=list, 
        description="具体、可执行的修改建议"
    )
    
    # 问题层级（决定路由到哪个阶段）
    problem_level: Optional[ProblemLevel] = Field(
        default=None,
        description="问题所在层级：comprehension/planning/execution"
    )
    
    # 详细裁决理由
    rationale: str = Field(description="裁决的详细理由")
    
    # 置信度评分
    confidence_score: float = Field(
        default=0.0,
        description="验证结果的置信度 (0-1)",
        ge=0.0,
        le=1.0
    )


class IterationRecord(BaseModel):
    """单次迭代记录"""
    iteration_number: int = Field(description="迭代次数")
    phase: str = Field(description="执行阶段")
    result_version: str = Field(description="结果版本号，如 Result_v1, Result_v2")
    verification_status: Optional[VerificationStatus] = Field(
        default=None,
        description="验证状态"
    )
    issues_found: List[str] = Field(
        default_factory=list,
        description="发现的问题摘要"
    )
    actions_taken: str = Field(description="采取的行动")


###################
# 子图状态定义（Subgraph States）
###################

class ComprehensionState(MessagesState):
    """题目理解智能体的子图状态"""
    
    # 输入
    user_input: str
    
    # 输出（结构化）
    comprehension_output: Annotated[Optional[ComprehensionOutput], override_reducer]
    
    # 迭代控制
    comprehension_iterations: int


class PlanningState(MessagesState):
    """策略规划智能体的子图状态"""
    
    # 输入（来自理解阶段）
    comprehension_output: ComprehensionOutput
    
    # 输出（结构化）
    planning_output: Annotated[Optional[PlanningOutput], override_reducer]
    
    # 迭代控制
    planning_iterations: int
    
    # 验证反馈（用于重新规划）
    verification_feedback: Optional[VerificationOutput]


class ExecutionState(MessagesState):
    """计算执行智能体的子图状态"""
    
    # 输入（来自规划阶段）
    planning_output: PlanningOutput
    
    # 输出（结构化）
    execution_output: Annotated[Optional[ExecutionOutput], override_reducer]
    
    # 当前任务索引
    current_task_index: int
    
    # 迭代控制
    execution_iterations: int
    
    # 验证反馈（用于修正执行）
    verification_feedback: Optional[VerificationOutput]


class VerificationState(MessagesState):
    """验证反思智能体的子图状态"""
    
    # 输入（来自执行阶段）
    comprehension_output: ComprehensionOutput
    execution_output: ExecutionOutput
    
    # 输出（结构化）
    verification_output: Annotated[Optional[VerificationOutput], override_reducer]
    
    # 迭代控制
    verification_iterations: int


###################
# 全局状态（Global Agent State）
###################

class AgentState(MessagesState):
    """
    全局状态 - 整个多智能体系统的主状态
    
    设计原则：
    1. 最小化字段，只保留跨智能体必需的共享数据
    2. 使用 messages 字段存储对话历史（继承自MessagesState）
    3. 各智能体的专有数据存放在结构化输出中
    4. 支持迭代优化模式（agent.md）
    """
    
    # ========== 输入输出 ==========
    user_input: str  # 用户原始输入
    final_answer: Optional[str]  # 最终答案
    
    # ========== 各智能体的结构化输出 ==========
    comprehension_output: Annotated[Optional[ComprehensionOutput], override_reducer]
    planning_output: Annotated[Optional[PlanningOutput], override_reducer]
    execution_output: Annotated[Optional[ExecutionOutput], override_reducer]
    verification_output: Annotated[Optional[VerificationOutput], override_reducer]
    
    # ========== 流程控制 ==========
    current_phase: str  # comprehension/planning/execution/verification/completed
    total_iterations: int  # 全局迭代计数
    
    # ========== 迭代历史追踪 ==========
    iteration_history: Annotated[List[IterationRecord], operator.add]
    
    # ========== 错误处理 ==========
    error_message: Optional[str]
    needs_retry: bool
    
    # ========== 配置 ==========
    max_iterations: int  # 最大迭代次数（防止死循环）


###################
# 状态工具函数（State Utilities）
###################

def create_initial_state(user_input: str, max_iterations: int = 10) -> AgentState:
    """创建初始状态"""
    return AgentState(
        messages=[],
        user_input=user_input,
        final_answer=None,
        comprehension_output=None,
        planning_output=None,
        execution_output=None,
        verification_output=None,
        current_phase="comprehension",
        total_iterations=0,
        iteration_history=[],
        error_message=None,
        needs_retry=False,
        max_iterations=max_iterations
    )


def should_continue(state: AgentState) -> bool:
    """判断是否应该继续迭代"""
    if state.get("total_iterations", 0) >= state.get("max_iterations", 10):
        return False
    if state.get("current_phase") == "completed":
        return False
    if state.get("error_message") and not state.get("needs_retry"):
        return False
    return True


def add_iteration_record(
    state: AgentState,
    phase: str,
    result_version: str,
    verification_status: Optional[VerificationStatus],
    issues_found: List[str],
    actions_taken: str
) -> Dict[str, Any]:
    """添加迭代记录"""
    record = IterationRecord(
        iteration_number=state.get("total_iterations", 0) + 1,
        phase=phase,
        result_version=result_version,
        verification_status=verification_status,
        issues_found=issues_found,
        actions_taken=actions_taken
    )
    
    return {
        "iteration_history": [record]
    } 
"""
重构后的智能体节点实现

设计原则：
1. 每个智能体是独立的节点函数
2. 使用LangChain调用LLM并产生结构化输出
3. 基于提示词模板生成响应
4. 返回更新后的全局状态
5. Coordinator作为真正的智能体，由LLM决策下一步
"""

from typing import Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from src.state.state_refactored import (
    AgentState,
    ComprehensionOutput,
    PlanningOutput,
    ExecutionOutput,
    VerificationOutput,
    ToolType,
    ToolExecutionRecord,
    VerificationStatus,
    IssueType,
    Issue,
    ProblemLevel,
    add_iteration_record
)
from src.prompts.prompt import (
    COMPREHENSION_PROMPT,
    PREPROCESSING_PROMPT,
    EXECUTION_PROMPT,
    VERIFICATION_PROMPT,
    COORDINATOR_PROMPT
)
from src.configuration import Configuration
from src.tools.sympy import create_sympy_tool
from src.tools.wolfram_alpha import create_wolfram_alpha_tool
from dotenv import load_dotenv

import os

load_dotenv()

###################
# 辅助函数
###################

def get_llm(config: Optional[Configuration] = None) -> BaseChatModel:
    """获取配置的LLM实例"""
    if config is None:
        config = Configuration.from_runnable_config()
    
    # 这里可以根据配置选择不同的模型
    # 简化版本，使用OpenAI
    return ChatOpenAI(
        model=config.coordinator_model,
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com/v1",
        temperature=0.2
    )


###################
# Coordinator决策模型
###################

class CoordinatorDecision(BaseModel):
    """
    Coordinator的决策输出（由LLM生成）
    
    让LLM智能决定下一步该做什么，而不是硬编码规则
    """
    next_action: str = Field(
        description="下一步行动：comprehension/planning/execution/verification/complete"
    )
    reasoning: str = Field(
        description="决策理由：为什么选择这个行动"
    )
    instructions: str = Field(
        description="给下一个智能体的具体指令"
    )
    should_continue: bool = Field(
        description="是否应该继续迭代"
    )


class ToolSelectionDecision(BaseModel):
    """
    工具选择决策（由LLM生成）
    
    让LLM智能决定使用哪个工具，而不是硬编码关键词匹配
    """
    tool_name: str = Field(
        description="选择的工具：sympy/wolfram_alpha/internal_reasoning"
    )
    reasoning: str = Field(
        description="选择理由：为什么这个工具最适合这个任务"
    )
    confidence: float = Field(
        description="选择的置信度（0-1之间）"
    )


###################
# 协调管理智能体（Coordinator Agent）- agent.md的灵魂
###################

def coordinator_agent(state: AgentState, config: Optional[Configuration] = None) -> AgentState:
    """
    协调管理智能体（agent.md: 流程控制器、守门员）
    
    职责：
    1. 分析当前状态和验证反馈
    2. 智能决策下一步应该调用哪个agent
    3. 决定是继续迭代还是结束流程
    4. 由LLM做决策，而不是硬编码规则
    
    这是agent.md中描述的真正的"协调管理智能体"
    """
    
    iteration_num = state.get("total_iterations", 0)
    print(f"\n🎯 [Coordinator Agent] 第{iteration_num}轮协调...")
    
    try:
        llm = get_llm(config)
        llm_with_structure = llm.with_structured_output(CoordinatorDecision)
        
        # 构建协调上下文
        current_phase = state.get("current_phase", "start")
        verification_output = state.get("verification_output")
        comprehension_output = state.get("comprehension_output")
        planning_output = state.get("planning_output")
        execution_output = state.get("execution_output")
        
        # 构建状态摘要
        status_summary = f"""
【当前迭代】第 {iteration_num} 轮

【原始问题】
{state.get('user_input')}

【当前阶段】{current_phase}

【已完成的工作】
"""
        
        if comprehension_output:
            status_summary += f"""
- ✅ 题目理解完成
  - 问题类型: {comprehension_output.problem_type}
  - 核心领域: {comprehension_output.primary_field}
  - 求解目标: {', '.join(comprehension_output.objectives[:2])}...
"""
        
        if planning_output:
            status_summary += f"""
- ✅ 策略规划完成
  - 生成了 {len(planning_output.execution_tasks)} 个执行任务
"""
        
        if execution_output:
            status_summary += f"""
- ✅ 计算执行完成
  - 执行了 {len(execution_output.tool_executions)} 个工具调用
  - 最终结果: {str(execution_output.final_result)[:100]}...
"""
        
        # 如果有验证反馈，这是最关键的信息
        if verification_output:
            status_summary += f"""

【验证反馈】（最重要！）
- 验证状态: {verification_output.status.value}
- 置信度: {verification_output.confidence_score}

发现的问题：
"""
            for i, issue in enumerate(verification_output.issues, 1):
                status_summary += f"{i}. [{issue.issue_type.value}] {issue.detail}\n"
            
            if verification_output.suggestions:
                status_summary += f"\n改进建议：\n"
                for i, suggestion in enumerate(verification_output.suggestions, 1):
                    status_summary += f"{i}. {suggestion}\n"
            
            status_summary += f"\n裁决理由：\n{verification_output.rationale}\n"
        
        # 迭代历史
        if state.get("iteration_history"):
            status_summary += f"\n【迭代历史】\n"
            for record in state["iteration_history"][-3:]:  # 最近3次
                status_summary += f"- 迭代{record.iteration_number}: {record.phase} → {record.actions_taken}\n"
        
        # 限制条件
        max_iterations = state.get("max_iterations", 10)
        status_summary += f"""

【限制条件】
- 最大迭代次数: {max_iterations}
- 当前迭代: {iteration_num}
- 剩余迭代: {max_iterations - iteration_num}
"""
        
        # 构建决策提示词
        decision_prompt = f"""
{COORDINATOR_PROMPT}

{status_summary}

---

现在请你作为协调管理智能体，分析当前情况并做出决策：

1. **如果验证状态是PASSED**：
   - next_action: "complete"
   - 理由：验证通过，可以交付最终结果

2. **如果验证状态是NEEDS_REVISION**：
   - 仔细分析问题列表和改进建议
   - 判断问题根源在哪个层面：
     * 理解层面的根本偏差（极罕见） → next_action: "comprehension"
     * 规划层面的策略问题（计划步骤缺失、方法不当） → next_action: "planning"
     * 执行层面的小错（计算错误、格式问题） → next_action: "execution"
   - 给出清晰的reasoning和具体的instructions

3. **如果验证状态是FATAL_ERROR**：
   - next_action: "complete"
   - 理由：致命错误，无法继续

4. **如果还没有验证结果**：
   - 根据当前阶段决定下一步
   - 通常顺序是：comprehension → planning → execution → verification

5. **如果达到最大迭代次数**：
   - should_continue: false
   - next_action: "complete"
   - 理由：达到最大迭代限制

请返回你的决策（JSON格式）：
{{
    "next_action": "comprehension/planning/execution/verification/complete",
    "reasoning": "详细的决策理由",
    "instructions": "给下一个智能体的具体指令",
    "should_continue": true/false
}}
        """
        
        messages = [
            SystemMessage(content="你是一位经验丰富的协调管理专家，负责智能决策整个解题流程。"),
            HumanMessage(content=decision_prompt)
        ]
        
        # 调用LLM做决策
        decision = llm_with_structure.invoke(messages)
        
        # 打印决策
        print(f"\n  📊 Coordinator决策：")
        print(f"     下一步: {decision.next_action}")
        print(f"     理由: {decision.reasoning}")
        print(f"     指令: {decision.instructions[:100]}...")
        print(f"     继续: {decision.should_continue}")
        
        # ✅ 如果决定complete，并且验证通过，生成最终报告
        if decision.next_action == "complete" and verification_output and verification_output.status == VerificationStatus.PASSED:
            print(f"\n  📝 生成最终报告...")
            final_answer = _generate_final_report(state, config)
            
            return {
                "current_phase": "complete",
                "final_answer": final_answer,
                "needs_retry": False,
                "messages": [AIMessage(content=f"✅ 解题完成！Coordinator已生成最终报告")]
            }
        
        # 其他情况：正常路由
        return {
            "current_phase": decision.next_action,
            "needs_retry": decision.should_continue and decision.next_action != "complete",
            "messages": [AIMessage(content=f"Coordinator决策：{decision.reasoning}")]
        }
    
    except Exception as e:
        print(f"❌ [Coordinator Agent] 错误: {e}")
        # 出错时默认完成
        return {
            "current_phase": "complete",
            "error_message": f"Coordinator决策失败: {str(e)}",
            "needs_retry": False
        }


###################
# 题目理解智能体（Comprehension Agent）
###################

def comprehension_agent(state: AgentState, config: Optional[Configuration] = None) -> AgentState:
    """
    题目理解智能体节点
    
    任务：
    1. LaTeX标准化
    2. 问题表象解构（已知、目标、约束）
    3. 核心原理溯源
    4. 策略路径构建
    
    输入：state.user_input
    输出：state.comprehension_output
    """
    
    print("🧠 [Comprehension Agent] 开始分析题目...")
    
    try:
        llm = get_llm(config)
        
        # 使用结构化输出
        llm_with_structure = llm.with_structured_output(ComprehensionOutput)
        
        # 构建提示词
        prompt = COMPREHENSION_PROMPT.format(user_input=state["user_input"])
        messages = [
            SystemMessage(content="你是一位顶尖的数学问题分析专家。"),
            HumanMessage(content=prompt)
        ]
        
        # 调用LLM
        comprehension_output = llm_with_structure.invoke(messages)
        
        # ✅ 只返回理解结果，不设置current_phase
        # 由Coordinator决定下一步
        return {
            "comprehension_output": comprehension_output,
            # ❌ 不设置current_phase，让Coordinator的LLM决策
            "messages": [AIMessage(content=f"题目理解完成：{comprehension_output.normalized_latex}")]
        }
    
    except Exception as e:
        print(f"❌ [Comprehension Agent] 错误: {e}")
        return {
            "error_message": f"题目理解失败: {str(e)}",
            "needs_retry": True
        }


###################
# 策略规划智能体（Planning Agent）
###################

def planning_agent(state: AgentState, config: Optional[Configuration] = None) -> AgentState:
    """
    策略规划智能体节点（agent.md: 执行核心之一）
    
    任务：
    1. 基于理解结果制定执行计划
    2. 分解为原子任务（DAG结构）
    3. 链接到基础原理
    4. 定义任务依赖关系
    5. 处理验证反馈，优化或重写计划
    
    输入：state.comprehension_output, state.verification_output (可选)
    输出：state.planning_output
    """
    
    iteration_num = state.get("total_iterations", 0) + 1
    verification_feedback = state.get("verification_output")
    
    if verification_feedback:
        print(f"📋 [Planning Agent] 第{iteration_num}轮规划（基于验证反馈）...")
    else:
        print(f"📋 [Planning Agent] 第{iteration_num}轮规划（首次）...")
    
    # 检查前置条件
    if not state.get("comprehension_output"):
        return {
            "error_message": "缺少题目理解结果，无法进行规划",
            "needs_retry": False
        }
    
    try:
        llm = get_llm(config)
        llm_with_structure = llm.with_structured_output(PlanningOutput)
        
        # 构建提示词
        comprehension_result = state["comprehension_output"]
        analysis_summary = f"""
问题类型：{comprehension_result.problem_type}
核心领域：{comprehension_result.primary_field}
已知信息：{', '.join(comprehension_result.givens)}
求解目标：{', '.join(comprehension_result.objectives)}
策略推演：{comprehension_result.strategy_deduction}
        """
        
        # 如果有验证反馈，添加改进指导
        if verification_feedback and verification_feedback.suggestions:
            print("  → 处理验证反馈，优化计划...")
            for i, suggestion in enumerate(verification_feedback.suggestions, 1):
                print(f"    {i}. {suggestion}")
            
            improvement_guidance = f"""

【验证反馈】
发现问题：
{chr(10).join(f"- {issue.issue_type.value}: {issue.detail}" for issue in verification_feedback.issues)}

改进建议：
{chr(10).join(f"- {sugg}" for sugg in verification_feedback.suggestions)}

请根据上述反馈，优化或重写执行计划，确保：
1. 解决所有指出的问题
2. 遵循所有改进建议
3. 保持计划的原子性和确定性
            """
            analysis_summary += improvement_guidance
        
        prompt = PREPROCESSING_PROMPT.format(math_problem_analysis=analysis_summary)
        messages = [
            SystemMessage(content="你是一位顶尖的计算策略规划师。"),
            HumanMessage(content=prompt)
        ]
        
        # 调用LLM
        planning_output = llm_with_structure.invoke(messages)
        
        print(f"  ✓ 规划完成：生成 {len(planning_output.execution_tasks)} 个任务")
        
        # 记录迭代
        iteration_update = add_iteration_record(
            state,
            phase="planning",
            result_version=f"Plan_v{iteration_num}",
            verification_status=None,
            issues_found=[],
            actions_taken=f"生成{len(planning_output.execution_tasks)}个执行任务"
        )
        
        # ✅ 只返回规划结果，不设置current_phase
        # 由Coordinator决定下一步
        return {
            **iteration_update,
            "planning_output": planning_output,
            # ❌ 不设置current_phase，让Coordinator的LLM决策
            "messages": [AIMessage(content=f"规划完成：生成了 {len(planning_output.execution_tasks)} 个执行任务")]
        }
    
    except Exception as e:
        print(f"❌ [Planning Agent] 错误: {e}")
        return {
            "error_message": f"策略规划失败: {str(e)}",
            "needs_retry": True
        }


###################
# 计算执行智能体（Execution Agent）
###################

def execution_agent(state: AgentState, config: Optional[Configuration] = None) -> AgentState:
    """
    计算执行智能体节点（agent.md: 执行核心之一）
    
    任务：
    1. 按照计划执行每个任务
    2. 选择合适的工具（SymPy/Wolfram Alpha/Internal Reasoning）
    3. 记录计算轨迹
    4. 管理工作区变量
    5. 处理验证反馈，修正执行错误
    
    使用prompt.py中精心设计的EXECUTION_PROMPT
    
    输入：state.planning_output, state.verification_output (可选)
    输出：state.execution_output
    """
    
    iteration_num = state.get("total_iterations", 0) + 1
    verification_feedback = state.get("verification_output")
    
    if verification_feedback:
        print(f"⚙️ [Execution Agent] 第{iteration_num}轮执行（基于验证反馈）...")
    else:
        print(f"⚙️ [Execution Agent] 第{iteration_num}轮执行（首次）...")
    
    # 检查前置条件
    if not state.get("planning_output"):
        return {
            "error_message": "缺少执行计划，无法执行",
            "needs_retry": False
        }
    
    try:
        llm = get_llm(config)
        
        planning_output = state["planning_output"]
        workspace = {}
        tool_executions = []
        computational_trace = []
        
        # 如果有验证反馈，显示修正指导
        feedback_context = ""
        if verification_feedback and verification_feedback.suggestions:
            print("  → 处理验证反馈，修正执行...")
            for i, suggestion in enumerate(verification_feedback.suggestions, 1):
                print(f"    {i}. {suggestion}")
            
            feedback_context = f"""

【验证反馈修正指导】
发现的问题：
{chr(10).join(f"- {issue.issue_type.value}: {issue.detail}" for issue in verification_feedback.issues)}

改进建议（必须遵循）：
{chr(10).join(f"- {sugg}" for sugg in verification_feedback.suggestions)}

请在执行过程中特别注意这些反馈，确保修正所有问题。
            """
        
        # 构建完整的执行提示词（使用精心设计的EXECUTION_PROMPT）
        preprocessing_plan_json = planning_output.model_dump_json(indent=2)
        
        full_execution_prompt = EXECUTION_PROMPT.format(
            preprocessing_plan=preprocessing_plan_json
        ) + feedback_context
        
        messages = [
            SystemMessage(content="你是一位专家级的计算数学家，精通SymPy和Wolfram Alpha等计算工具。"),
            HumanMessage(content=full_execution_prompt)
        ]
        
        # 调用LLM执行（简化版本 - 实际应该解析LLM的结构化输出）
        response = llm.invoke(messages)
        
        print(f"  ✓ LLM执行完成，正在解析结果...")
        
        # 初始化工作区
        for var in planning_output.workspace_init:
            workspace[var["variable_name"]] = var.get("value_ref", None)
            computational_trace.append(f"初始化变量 {var['variable_name']}")
        
        # 执行任务（✅ LLM智能选择工具）
        for task in planning_output.execution_tasks:
            print(f"  → 执行任务 {task.task_id}: {task.description}")
            
            # ✅ LLM智能选择并调用工具
            tool_result = _execute_tool_call(task, response.content, workspace, config)
            
            tool_executions.append(tool_result)
            computational_trace.append(f"任务 {task.task_id} 完成，输出保存到 {task.output_id}")
            
            # 更新工作区
            workspace[task.output_id] = tool_result.tool_output
        
        # 构建执行输出
        execution_output = ExecutionOutput(
            workspace=workspace,
            tool_executions=tool_executions,
            computational_trace=computational_trace,
            final_result=workspace.get("final_result")
        )
        
        print(f"  ✓ 执行完成：{len(tool_executions)}个工具调用")
        
        # 记录迭代
        iteration_update = add_iteration_record(
            state,
            phase="execution",
            result_version=f"Result_v{iteration_num}",
            verification_status=None,
            issues_found=[],
            actions_taken=f"执行{len(tool_executions)}个工具调用"
        )
        
        # ✅ 只返回执行结果，不设置current_phase
        # 由Coordinator决定下一步
        return {
            **iteration_update,
            "execution_output": execution_output,
            # ❌ 不设置current_phase，让Coordinator的LLM决策
            "messages": [AIMessage(content=f"执行完成：共执行 {len(tool_executions)} 个工具调用")]
        }
    
    except Exception as e:
        print(f"❌ [Execution Agent] 错误: {e}")
        return {
            "error_message": f"计算执行失败: {str(e)}",
            "needs_retry": True
        }


def _execute_tool_call(task, llm_response: str, workspace: dict, config: Optional[Configuration] = None) -> ToolExecutionRecord:
    """
    执行实际的工具调用（辅助函数）
    
    ✅ 使用LLM智能决策工具选择，而不是硬编码关键词匹配
    
    工具选项：
    1. SymPy：符号计算、代数、微积分、方程求解
    2. Wolfram Alpha：复杂计算、数值计算、数据查询
    3. Internal Reasoning：逻辑推理、格式化、简单运算
    """
    
    try:
        # ✅ 使用LLM做工具选择决策
        llm = get_llm(config)
        llm_with_structure = llm.with_structured_output(ToolSelectionDecision)
        
        # 构建工具选择提示词
        tool_selection_prompt = f"""
你是一个专业的工具选择专家。你需要分析任务并选择最合适的工具。

【任务信息】
任务ID: {task.task_id}
任务描述: {task.description}
方法: {task.method if hasattr(task, 'method') else '未指定'}
参数: {task.params if hasattr(task, 'params') else {}}

【可用工具】

1. **SymPy** (符号计算库)
   - 适用场景：
     * 精确的代数运算（方程求解、简化、因式分解、展开）
     * 微积分（导数、积分、极限、级数展开）
     * 线性代数（矩阵运算、特征值、行列式）
     * 微分方程求解
     * 数论运算（质数、最大公约数、因数分解）
     * 符号表达式处理
   - 优势：精确的符号计算，完整的推导步骤
   - 示例：求解方程 x^2 + 2x + 1 = 0，求导数 d/dx(sin(x))

2. **Wolfram Alpha** (计算知识引擎)
   - 适用场景：
     * 复杂的数值计算
     * 需要外部知识的计算（物理常数、单位转换）
     * 统计分析、数据查询
     * 当SymPy无法处理的复杂问题
   - 优势：强大的计算能力，丰富的知识库
   - 注意：需要API调用，可能较慢

3. **Internal Reasoning** (内部推理)
   - 适用场景：
     * 简单的逻辑推理
     * 格式化输出
     * 工作区变量管理
     * 不需要复杂计算的任务
   - 优势：快速，无需外部调用

【工作区状态】
当前工作区变量: {list(workspace.keys()) if workspace else '空'}

---

请分析上述任务，并选择最合适的工具。考虑因素：
1. 任务的性质（代数/微积分/数值/逻辑）
2. 所需的精度（符号vs数值）
3. 计算的复杂度
4. 是否需要外部知识

返回你的决策（JSON格式）：
{{
    "tool_name": "sympy/wolfram_alpha/internal_reasoning",
    "reasoning": "详细的选择理由",
    "confidence": 0.0-1.0
}}
        """
        
        messages = [
            SystemMessage(content="你是一个专业的工具选择专家，擅长分析任务并选择最合适的计算工具。"),
            HumanMessage(content=tool_selection_prompt)
        ]
        
        # 调用LLM做决策
        decision = llm_with_structure.invoke(messages)
        
        print(f"    🤖 LLM工具选择: {decision.tool_name}")
        print(f"       理由: {decision.reasoning}")
        print(f"       置信度: {decision.confidence}")
        
        # ✅ 根据LLM的决策调用相应的工具
        if decision.tool_name.lower() == "sympy":
            tool_type = ToolType.SYMPY
            tool_result = _call_sympy_tool(task, workspace)
            
        elif decision.tool_name.lower() == "wolfram_alpha":
            tool_type = ToolType.WOLFRAM_ALPHA
            tool_result = _call_wolfram_tool(task, workspace)
            
        else:  # internal_reasoning
            tool_type = ToolType.INTERNAL_REASONING
            tool_result = _call_internal_reasoning(task, workspace)
        
        return ToolExecutionRecord(
            task_id=task.task_id,
            tool_type=tool_type,
            tool_input=task.description,
            tool_output=tool_result,
            rationale=f"LLM选择: {decision.reasoning} (置信度: {decision.confidence})"
        )
        
    except Exception as e:
        print(f"    ⚠️ LLM工具选择失败: {e}，回退到内部推理")
        # 出错时回退到内部推理
        tool_result = _call_internal_reasoning(task, workspace)
        return ToolExecutionRecord(
            task_id=task.task_id,
            tool_type=ToolType.INTERNAL_REASONING,
            tool_input=task.description,
            tool_output=tool_result,
            rationale=f"LLM决策失败，回退到内部推理: {str(e)}"
        )


def _call_sympy_tool(task, workspace: dict) -> str:
    """
    调用SymPy工具执行符号计算
    """
    try:
        # 创建SymPy工具实例
        tool = create_sympy_tool()
        
        # 根据任务类型调用相应的方法
        params = task.params if hasattr(task, 'params') else {}
        method_lower = task.method.lower() if hasattr(task, 'method') else ""
        
        if 'solve' in method_lower and 'equation' in method_lower:
            # 求解方程
            equation = params.get('equation', task.description)
            variable = params.get('variable', 'x')
            result = tool.solve_equation(equation, variable)
            
        elif 'simplify' in method_lower:
            # 简化表达式
            expression = params.get('expression', task.description)
            result = tool.simplify_expression(expression)
            
        elif 'differentiate' in method_lower or 'derivative' in method_lower:
            # 微分
            expression = params.get('expression', task.description)
            variable = params.get('variable', 'x')
            order = params.get('order', 1)
            result = tool.differentiate(expression, variable, order)
            
        elif 'integrate' in method_lower or 'integral' in method_lower:
            # 积分
            expression = params.get('expression', task.description)
            variable = params.get('variable', 'x')
            limits = params.get('limits', None)
            result = tool.integrate(expression, variable, limits)
            
        else:
            # 通用求解
            result = tool.solve_math_problem(task.description)
        
        # 格式化输出
        if result.get('success'):
            output = f"SymPy计算结果：{result.get('result', result.get('solution', result.get('simplified', 'N/A')))}"
            if result.get('latex'):
                output += f"\nLaTeX: {result['latex']}"
            return output
        else:
            return f"SymPy计算失败：{result.get('error', '未知错误')}"
            
    except Exception as e:
        return f"SymPy工具调用错误：{str(e)}"


def _call_wolfram_tool(task, workspace: dict) -> str:
    """
    调用Wolfram Alpha工具执行计算
    """
    try:
        # 创建Wolfram Alpha工具实例
        tool = create_wolfram_alpha_tool()
        
        # 调用Wolfram Alpha求解
        result = tool.solve_math_problem(task.description)
        
        # 格式化输出
        if result.get('success'):
            output = "Wolfram Alpha计算结果：\n"
            if result.get('final_answer'):
                output += f"最终答案：{result['final_answer']}\n"
            if result.get('steps'):
                output += "步骤：\n"
                for step in result['steps']:
                    output += f"  - {step['title']}: {step['content']}\n"
            return output
        else:
            return f"Wolfram Alpha计算失败：{result.get('error', '未知错误')}"
            
    except Exception as e:
        return f"Wolfram Alpha工具调用错误：{str(e)}"


def _call_internal_reasoning(task, workspace: dict) -> str:
    """
    使用内部逻辑推理（不调用外部工具）
    """
    # 简单的内部推理，可以处理：
    # 1. 从工作区获取变量
    # 2. 简单的逻辑判断
    # 3. 格式化输出
    
    try:
        # 如果任务需要从工作区获取值
        if hasattr(task, 'params') and task.params:
            params = task.params
            if isinstance(params, dict):
                # 替换工作区引用
                for key, value in params.items():
                    if isinstance(value, str) and value in workspace:
                        params[key] = workspace[value]
        
        # 执行简单的逻辑操作
        return f"内部推理完成：{task.description}"
        
    except Exception as e:
        return f"内部推理错误：{str(e)}"


###################
# 验证反思智能体（Verification Agent）
###################

def verification_agent(state: AgentState, config: Optional[Configuration] = None) -> AgentState:
    """
    验证反思智能体节点（agent.md: 迭代模式的灵魂）
    
    任务：
    1. 生成诊断报告（Verification Report）
    2. 评估状态：PASSED / NEEDS_REVISION / FATAL_ERROR
    3. 问题列表：清晰指出问题类型（Factual Error, Logical Flaw等）
    4. 修正建议：具体可执行的修改意见
    5. 判定问题层级：决定返回哪个阶段
    
    输入：state.comprehension_output, state.execution_output
    输出：state.verification_output
    """
    
    iteration_num = state.get("total_iterations", 0) + 1
    print(f"✅ [Verification Agent] 第{iteration_num}轮验证...")
    
    # 检查前置条件
    if not state.get("comprehension_output") or not state.get("execution_output"):
        return {
            "error_message": "缺少理解结果或执行结果，无法验证",
            "needs_retry": False
        }
    
    try:
        llm = get_llm(config)
        llm_with_structure = llm.with_structured_output(VerificationOutput)
        
        # 构建验证输入（包含完整上下文）
        comprehension = state["comprehension_output"]
        execution = state["execution_output"]
        planning = state.get("planning_output")
        
        # 准备VERIFICATION_PROMPT所需的参数
        analysis_report_json = comprehension.model_dump_json(indent=2)
        executor_report_json = execution.model_dump_json(indent=2)
        
        # 使用精心设计的VERIFICATION_PROMPT
        full_verification_prompt = VERIFICATION_PROMPT.format(
            analysis_report=analysis_report_json,
            executor_report=executor_report_json
        )
        
        # 添加额外的上下文信息
        additional_context = f"""

【补充上下文】
原始问题：{state.get('user_input')}
执行计划：
{planning.model_dump_json(indent=2) if planning else "无"}

---

请严格按照上述验证协议生成结构化的诊断报告（VerificationOutput），包含：
1. status: PASSED / NEEDS_REVISION / FATAL_ERROR
2. issues: 发现的问题列表（每个问题包含issue_type和detail）
3. suggestions: 具体可执行的修改建议
4. problem_level: execution / planning / comprehension
5. rationale: 裁决理由
6. confidence_score: 0-1之间的置信度
        """
        
        messages = [
            SystemMessage(content="你是一个专家级的数学问题验证专家，精通交叉验证和审计。"),
            HumanMessage(content=full_verification_prompt + additional_context)
        ]
        
        # 调用LLM生成诊断报告
        verification_output = llm_with_structure.invoke(messages)
        
        # 记录本轮迭代
        result_version = f"Result_v{iteration_num}"
        issues_summary = [f"{issue.issue_type.value}: {issue.detail[:50]}..." 
                         for issue in verification_output.issues]
        
        # 根据验证结果返回诊断报告
        if verification_output.status == VerificationStatus.PASSED:
            print(f"  ✅ 验证通过！")
            print(f"  → 将验证通过的报告返回给Coordinator...")
            
            # 记录迭代
            iteration_update = add_iteration_record(
                state,
                phase="verification",
                result_version=result_version,
                verification_status=VerificationStatus.PASSED,
                issues_found=[],
                actions_taken="验证通过，建议Coordinator完成流程"
            )
            
            # ✅ 只返回验证报告，不生成最终答案
            # 最终答案由Coordinator生成
            return {
                **iteration_update,
                "verification_output": verification_output,
                # ❌ 不生成final_answer，这是Coordinator的职责
                # 不设置current_phase，让Coordinator决策
                "messages": [AIMessage(content="✅ 验证通过，等待Coordinator生成最终报告")]
            }
        
        elif verification_output.status == VerificationStatus.NEEDS_REVISION:
            print(f"  ⚠️ 需要修订：发现 {len(verification_output.issues)} 个问题")
            for issue in verification_output.issues:
                print(f"    - {issue.issue_type.value}: {issue.detail[:80]}")
            
            print(f"  → 诊断完成，问题层级：{verification_output.problem_level.value}")
            print(f"  → 将诊断报告返回给Coordinator进行智能决策...")
            
            # 记录迭代（不做决策，只记录发现的问题）
            iteration_update = add_iteration_record(
                state,
                phase="verification",
                result_version=result_version,
                verification_status=VerificationStatus.NEEDS_REVISION,
                issues_found=issues_summary,
                actions_taken=f"发现{len(verification_output.issues)}个问题，等待Coordinator决策"
            )
            
            # ✅ 只返回诊断报告，不做任何决策
            # ❌ 不设置 current_phase（由Coordinator决策）
            # ❌ 不判断问题根源（由Coordinator的LLM智能分析）
            return {
                **iteration_update,
                "verification_output": verification_output,
                "needs_retry": True,
                "messages": [AIMessage(
                    content=f"⚠️ 验证发现{len(verification_output.issues)}个问题，已生成诊断报告\n问题摘要：{'; '.join(issues_summary)}"
                )]
            }
        
        else:  # FATAL_ERROR
            print(f"  ❌ 致命错误")
            print(f"  → 将致命错误报告返回给Coordinator...")
            
            # 记录迭代
            iteration_update = add_iteration_record(
                state,
                phase="verification",
                result_version=result_version,
                verification_status=VerificationStatus.FATAL_ERROR,
                issues_found=issues_summary,
                actions_taken="检测到致命错误，建议Coordinator终止流程"
            )
            
            # ✅ 返回致命错误报告
            # Coordinator会根据FATAL_ERROR状态决定是否终止
            return {
                **iteration_update,
                "verification_output": verification_output,
                "error_message": f"致命错误：{verification_output.rationale}",
                "needs_retry": False,
                # 不设置current_phase，让Coordinator决策
                "messages": [AIMessage(content=f"❌ 致命错误：{verification_output.rationale}")]
            }
    
    except Exception as e:
        print(f"❌ [Verification Agent] 错误: {e}")
        return {
            "error_message": f"验证失败: {str(e)}",
            "needs_retry": True
        }


def _generate_final_report(state: AgentState, config: Optional[Configuration] = None) -> str:
    """
    生成最终报告（由Coordinator调用）
    
    职责：
    1. 整合所有智能体的输出
    2. 生成结构化的解题报告
    3. 使用LLM生成专业、清晰的报告
    """
    
    try:
        comprehension = state.get("comprehension_output")
        planning = state.get("planning_output")
        execution = state.get("execution_output")
        verification = state.get("verification_output")
        
        if not execution:
            return "❌ 错误：缺少执行结果，无法生成最终报告"
        
        # 使用LLM生成专业的最终报告
        llm = get_llm(config)
        
        report_prompt = f"""
你是一位专业的数学解题报告撰写专家。请基于以下信息，生成一份清晰、专业的解题报告。

【原始问题】
{state.get('user_input')}

【题目分析】
{comprehension.model_dump_json(indent=2) if comprehension else '无'}

【解题计划】
{planning.model_dump_json(indent=2) if planning else '无'}

【计算过程】
{execution.model_dump_json(indent=2) if execution else '无'}

【验证结果】
{verification.model_dump_json(indent=2) if verification else '无'}

---

请生成结构化的解题报告，包含以下部分：

## 📋 问题理解
[简要说明问题的类型、已知条件、求解目标]

## 🎯 解题思路
[说明采用的策略和方法]

## 📐 解题步骤
[详细的计算过程，使用清晰的步骤编号]

## ✅ 最终答案
[明确的最终答案，使用适当的格式（LaTeX/文本）]

## 🔍 验证说明
[说明答案已通过验证，置信度等]

请使用Markdown格式，确保报告专业、清晰、易读。
        """
        
        messages = [
            SystemMessage(content="你是一位经验丰富的数学教师，擅长撰写清晰、专业的解题报告。"),
            HumanMessage(content=report_prompt)
        ]
        
        print(f"  → 调用LLM生成专业报告...")
        final_report = llm.invoke(messages)
        
        return final_report.content
        
    except Exception as e:
        print(f"  ⚠️ LLM生成报告失败: {e}，使用简化版本")
        # 回退到简化版本
        return _format_final_answer_simple(state)


def _format_final_answer_simple(state: AgentState) -> str:
    """简化版本的最终答案格式化（作为回退）"""
    execution = state.get("execution_output")
    if not execution:
        return "❌ 无法生成最终答案：缺少执行结果"
    
    report = f"""
# 解题报告

## 最终结果
{execution.final_result if execution.final_result else "计算完成"}

## 计算轨迹
"""
    for i, trace in enumerate(execution.computational_trace, 1):
        report += f"{i}. {trace}\n"
    
    # 添加工具调用信息
    if execution.tool_executions:
        report += f"\n## 工具调用记录\n"
        for tool_exec in execution.tool_executions:
            report += f"- 任务 {tool_exec.task_id}: {tool_exec.tool_type.value}\n"
            report += f"  输出: {tool_exec.tool_output[:100]}...\n"
    
    return report
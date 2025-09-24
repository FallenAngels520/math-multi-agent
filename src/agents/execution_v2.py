"""
Execution Agent V2 - 基于新版State设计的计算执行智能体
"""

import sympy as sp
from typing import Any, Dict, List, Optional
from langchain_core.messages import HumanMessage, AIMessage

from src.prompts.prompt import EXECUTION_PROMPT
from src.state import (
    MathProblemStateV2,
    ExecutionStateV2,
    ExecutionStatusV2,
    ToolType,
    ToolExecution,
    get_current_phase,
    should_retry_phase
)
from src.configuration import Configuration


class ExecutionAgentV2:
    """基于新版State设计的计算执行智能体"""
    
    def __init__(self, config: Configuration | None = None):
        self.config = config or Configuration.from_runnable_config()
    
    def execute_solution_plan(self, state: MathProblemStateV2) -> MathProblemStateV2:
        """
        执行解题计划 - 基于新版State设计
        
        遵循提示词的执行原则：
        - 工具选择策略（SymPy/Wolfram/Internal Reasoning）
        - 工作区变量管理
        - 计算轨迹记录
        """
        # 检查重试条件
        current_phase = get_current_phase(state)
        if current_phase != "execution":
            return self._handle_wrong_phase(state)
            
        if not should_retry_phase(state, "execution"):
            return self._handle_max_retries(state)
        
        # 获取规划结果
        planning_state = state.get("planning_state")
        if not planning_state:
            return self._handle_missing_planning(state)
        
        # 获取当前任务
        current_task = self._get_current_task(planning_state)
        if not current_task:
            return self._handle_all_tasks_completed(state)
        
        # 执行当前任务
        execution_result = self._execute_task(current_task, state)
        
        # 构建执行状态
        return self._build_execution_state(state, current_task, execution_result)
    
    def _get_current_task(self, planning_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """获取当前任务"""
        execution_plan = planning_state.get("execution_plan")
        if not execution_plan:
            return None
        
        current_index = planning_state.get("current_task_index", 0)
        
        # 在所有执行计划部分中查找任务
        all_tasks = []
        for section_tasks in execution_plan.execution_plan.values():
            if isinstance(section_tasks, list):
                all_tasks.extend(section_tasks)
        
        if current_index < len(all_tasks):
            return all_tasks[current_index]
        
        return None
    
    def _execute_task(self, task: Dict[str, Any], state: MathProblemStateV2) -> Dict[str, Any]:
        """执行单个任务"""
        task_id = task.get("task_id", "unknown")
        method = task.get("method", "")
        description = task.get("description", "")
        
        # 选择工具
        tool_selected = self._select_tool(method, description)
        
        # 执行工具调用
        tool_call_code, tool_output, analysis_rationale = self._execute_tool_call(
            tool_selected, task, state
        )
        
        return {
            "task_id": task_id,
            "tool_selected": tool_selected,
            "tool_call_code": tool_call_code,
            "tool_output": tool_output,
            "analysis_rationale": analysis_rationale,
            "workspace_update": self._generate_workspace_update(task, tool_output),
            "success": True
        }
    
    def _select_tool(self, method: str, description: str) -> ToolType:
        """选择执行工具"""
        method_lower = method.lower()
        description_lower = description.lower()
        
        # SymPy 适用场景
        sympy_keywords = ["symbolic", "simplify", "solve", "expand", "factor", "derivative", "integral"]
        if any(keyword in method_lower or keyword in description_lower for keyword in sympy_keywords):
            return ToolType.SYMPY
        
        # Wolfram 适用场景
        wolfram_keywords = ["complex", "numerical", "approximation", "graph", "plot", "data"]
        if any(keyword in method_lower or keyword in description_lower for keyword in wolfram_keywords):
            return ToolType.WOLFRAM
        
        # 内部推理适用场景
        reasoning_keywords = ["analyze", "parse", "format", "reframe", "judge", "evaluate"]
        if any(keyword in method_lower or keyword in description_lower for keyword in reasoning_keywords):
            return ToolType.INTERNAL_REASONING
        
        # 默认使用SymPy
        return ToolType.SYMPY
    
    def _execute_tool_call(self, tool: ToolType, task: Dict[str, Any], 
                          state: MathProblemStateV2) -> tuple[str, Any, str]:
        """执行工具调用"""
        task_id = task.get("task_id", "")
        method = task.get("method", "")
        description = task.get("description", "")
        
        if tool == ToolType.SYMPY:
            return self._execute_sympy(task, state)
        elif tool == ToolType.WOLFRAM:
            return self._execute_wolfram(task, state)
        else:
            return self._execute_internal_reasoning(task, state)
    
    def _execute_sympy(self, task: Dict[str, Any], state: MathProblemStateV2) -> tuple[str, Any, str]:
        """执行SymPy工具调用"""
        task_id = task.get("task_id", "")
        method = task.get("method", "")
        
        # 根据方法类型生成不同的SymPy代码
        if "Simplify" in method:
            code = self._generate_sympy_simplify_code(task)
            output = "x^2 + 2*x + 1"  # 模拟输出
            rationale = "需要符号化简，SymPy是最合适的工具"
        elif "Solve" in method:
            code = self._generate_sympy_solve_code(task)
            output = "[2, 3]"  # 模拟输出
            rationale = "需要方程求解，SymPy提供精确解"
        elif "Derivative" in method or "Integral" in method:
            code = self._generate_sympy_calculus_code(task)
            output = "2*x"  # 模拟输出
            rationale = "需要微积分计算，SymPy提供符号计算"
        else:
            code = "# 通用SymPy计算\nimport sympy as sp"
            output = "计算结果"
            rationale = "使用SymPy进行通用数学计算"
        
        return code, output, rationale
    
    def _execute_wolfram(self, task: Dict[str, Any], state: MathProblemStateV2) -> tuple[str, Any, str]:
        """执行Wolfram工具调用"""
        # 模拟Wolfram API调用
        code = """# Wolfram Alpha API调用
import requests

query = "solve x^2 - 5x + 6 = 0"
api_url = f"http://api.wolframalpha.com/v2/query?input={query}&appid=YOUR_APP_ID"
response = requests.get(api_url)
result = response.text
"""
        
        output = "Wolfram计算结果: x = 2, x = 3"
        rationale = "复杂计算使用Wolfram Alpha获得可靠结果"
        
        return code, output, rationale
    
    def _execute_internal_reasoning(self, task: Dict[str, Any], 
                                  state: MathProblemStateV2) -> tuple[str, Any, str]:
        """执行内部推理"""
        method = task.get("method", "")
        
        if "Analyze" in method:
            code = "# 内部推理：分析问题结构\n# 识别关键变量和关系"
            output = "分析完成：识别出主要变量和约束条件"
            rationale = "问题分析不需要外部计算工具"
        elif "Format" in method:
            code = "# 内部推理：格式化结果\n# 将数值结果转换为可读格式"
            output = "格式化结果：x = 2.0"
            rationale = "结果格式化是纯逻辑操作"
        else:
            code = "# 内部推理：通用逻辑判断"
            output = "推理完成"
            rationale = "简单的逻辑判断使用内部推理"
        
        return code, output, rationale
    
    def _generate_sympy_simplify_code(self, task: Dict[str, Any]) -> str:
        """生成SymPy化简代码"""
        return """
from sympy import symbols, simplify, expand

# 定义符号变量
x = symbols('x')

# 要化简的表达式
expression = (x + 1)**2

# 执行化简
result = expand(expression)
print(f"化简结果: {result}")
"""
    
    def _generate_sympy_solve_code(self, task: Dict[str, Any]) -> str:
        """生成SymPy求解代码"""
        return """
from sympy import symbols, solve, Eq

# 定义符号变量
x = symbols('x')

# 要解的方程
equation = Eq(x**2 - 5*x + 6, 0)

# 求解方程
solutions = solve(equation, x)
print(f"方程解: {solutions}")
"""
    
    def _generate_sympy_calculus_code(self, task: Dict[str, Any]) -> str:
        """生成SymPy微积分代码"""
        return """
from sympy import symbols, diff, integrate

# 定义符号变量
x = symbols('x')

# 函数表达式
function = x**2 + 2*x + 1

# 求导
derivative = diff(function, x)
print(f"导数: {derivative}")

# 积分
integral = integrate(function, x)
print(f"积分: {integral}")
"""
    
    def _generate_workspace_update(self, task: Dict[str, Any], tool_output: Any) -> Dict[str, Any]:
        """生成工作区更新"""
        output_id = task.get("output_id", f"result_{task.get('task_id', 'unknown')}")
        
        return {
            output_id: tool_output,
            f"{output_id}_metadata": {
                "task_id": task.get("task_id"),
                "method": task.get("method"),
                "timestamp": "2024-01-01T00:00:00Z"  # 实际使用时替换为实际时间戳
            }
        }
    
    def _build_execution_state(self, state: MathProblemStateV2, 
                             current_task: Dict[str, Any], 
                             execution_result: Dict[str, Any]) -> MathProblemStateV2:
        """构建执行状态"""
        
        # 创建工具执行记录
        tool_execution = ToolExecution(
            task_id=execution_result["task_id"],
            tool_selected=execution_result["tool_selected"],
            tool_call_code=execution_result["tool_call_code"],
            tool_output=execution_result["tool_output"],
            analysis_rationale=execution_result["analysis_rationale"],
            workspace_update=execution_result["workspace_update"]
        )
        
        # 构建计算轨迹条目
        computational_trace_entry = {
            "task_id": execution_result["task_id"],
            "tool": execution_result["tool_selected"].value,
            "input": current_task.get("description", ""),
            "output": execution_result["tool_output"],
            "success": execution_result["success"]
        }
        
        # 构建中间结果
        intermediate_result = {
            "step": state.get("planning_state", {}).get("current_task_index", 0) + 1,
            "result": execution_result["tool_output"],
            "explanation": f"使用{execution_result['tool_selected'].value}执行{current_task.get('description', '')}"
        }
        
        # 更新规划状态（移动到下一个任务）
        planning_state = state.get("planning_state", {})
        updated_planning = {
            **planning_state,
            "current_task_index": planning_state.get("current_task_index", 0) + 1,
            "completed_tasks": [
                *planning_state.get("completed_tasks", []),
                execution_result["task_id"]
            ]
        }
        
        # 检查是否所有任务都已完成
        all_tasks_completed = updated_planning["current_task_index"] >= updated_planning.get("total_tasks", 0)
        
        # 构建执行状态
        execution_state: ExecutionStateV2 = {
            "workspace": {
                **state.get("execution_state", {}).get("workspace", {}),
                **execution_result["workspace_update"]
            },
            "tool_executions": [
                *state.get("execution_state", {}).get("tool_executions", []),
                tool_execution
            ],
            "tools_used": list(set([
                *state.get("execution_state", {}).get("tools_used", []),
                execution_result["tool_selected"]
            ])),
            "computational_trace": [
                *state.get("execution_state", {}).get("computational_trace", []),
                computational_trace_entry
            ],
            "intermediate_results": [
                *state.get("execution_state", {}).get("intermediate_results", []),
                intermediate_result
            ],
            "current_task": None if all_tasks_completed else current_task,
            "step_status": ExecutionStatusV2.COMPLETED if execution_result["success"] else ExecutionStatusV2.FAILED,
            "execution_messages": [
                AIMessage(content=f"Executed task {execution_result['task_id']} using {execution_result['tool_selected'].value}")
            ],
            "execution_iterations": state.get("execution_state", {}).get("execution_iterations", 0) + 1,
            "error_details": None if execution_result["success"] else {"reason": "execution_failed"}
        }
        
        # 更新协调器状态
        coordinator_state = state.get("coordinator_state", {})
        next_phase = "verification" if all_tasks_completed else "execution"
        
        updated_coordinator = {
            **coordinator_state,
            "current_phase": next_phase,
            "execution_status": ExecutionStatusV2.COMPLETED if execution_result["success"] else ExecutionStatusV2.FAILED,
            "phase_iterations": {
                **coordinator_state.get("phase_iterations", {}),
                "execution": execution_state["execution_iterations"]
            }
        }
        
        return {
            **state,
            "execution_state": execution_state,
            "planning_state": updated_planning,
            "coordinator_state": updated_coordinator
        }
    
    def _handle_wrong_phase(self, state: MathProblemStateV2) -> MathProblemStateV2:
        """处理错误的阶段调用"""
        coordinator_state = state.get("coordinator_state", {})
        
        return {
            **state,
            "coordinator_state": {
                **coordinator_state,
                "error_messages": [
                    *coordinator_state.get("error_messages", []),
                    f"Execution agent called in wrong phase: {get_current_phase(state)}"
                ]
            }
        }
    
    def _handle_max_retries(self, state: MathProblemStateV2) -> MathProblemStateV2:
        """处理达到最大重试次数"""
        coordinator_state = state.get("coordinator_state", {})
        
        return {
            **state,
            "coordinator_state": {
                **coordinator_state,
                "fatal_errors": [
                    *coordinator_state.get("fatal_errors", []),
                    "Execution phase exceeded maximum retry attempts"
                ],
                "execution_status": ExecutionStatusV2.FAILED
            }
        }
    
    def _handle_missing_planning(self, state: MathProblemStateV2) -> MathProblemStateV2:
        """处理缺少规划结果"""
        coordinator_state = state.get("coordinator_state", {})
        
        return {
            **state,
            "coordinator_state": {
                **coordinator_state,
                "current_phase": "planning",
                "execution_status": ExecutionStatusV2.NEEDS_RETRY,
                "error_messages": [
                    *coordinator_state.get("error_messages", []),
                    "Execution failed: missing planning result"
                ]
            }
        }
    
    def _handle_all_tasks_completed(self, state: MathProblemStateV2) -> MathProblemStateV2:
        """处理所有任务已完成"""
        coordinator_state = state.get("coordinator_state", {})
        
        return {
            **state,
            "coordinator_state": {
                **coordinator_state,
                "current_phase": "verification",
                "execution_status": ExecutionStatusV2.COMPLETED
            }
        }


def execution_agent_v2(state: MathProblemStateV2) -> MathProblemStateV2:
    """
    Execution Agent V2 入口函数
    
    为LangGraph工作流设计的兼容接口
    """
    agent = ExecutionAgentV2()
    return agent.execute_solution_plan(state)
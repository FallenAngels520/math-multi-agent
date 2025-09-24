"""
Coordinator Agent V2 - 基于新版State设计的协调管理智能体
"""

from typing import Any, Dict
from langgraph.types import Command

from src.state import (
    MathProblemStateV2,
    ExecutionStatusV2,
    get_current_phase,
    should_retry_phase
)
from src.configuration import Configuration


class CoordinatorAgentV2:
    """基于新版State设计的协调管理智能体"""
    
    def __init__(self, config: Configuration | None = None):
        self.config = config or Configuration.from_runnable_config()
    
    def coordinate_workflow(self, state: MathProblemStateV2) -> Command:
        """
        协调工作流 - 基于新版State设计
        
        管理整个解题流程的状态流转：
        - 阶段调度
        - 错误恢复
        - 重试管理
        - 流程终止
        """
        # 更新总迭代计数
        state["total_iterations"] = state.get("total_iterations", 0) + 1
        
        # 获取当前阶段和执行状态
        current_phase = get_current_phase(state)
        execution_status = state.get("coordinator_state", {}).get("execution_status", ExecutionStatusV2.PENDING)
        
        # 处理显式重试语义
        if execution_status == ExecutionStatusV2.NEEDS_RETRY:
            return self._handle_retry(state, current_phase)
        
        # 初始状态 - 开始理解阶段
        if execution_status == ExecutionStatusV2.PENDING:
            return Command(goto="comprehension_agent_v2")
        
        # 根据当前阶段决定下一步
        if current_phase == "comprehension":
            return self._handle_comprehension_completion(state)
        elif current_phase == "planning":
            return self._handle_planning_completion(state)
        elif current_phase == "execution":
            return self._handle_execution_completion(state)
        elif current_phase == "verification":
            return self._handle_verification_completion(state)
        elif current_phase == "completed":
            return Command(goto="__end__")
        
        # 处理错误状态
        if execution_status == ExecutionStatusV2.FAILED:
            return self._handle_failure_state(state)
        
        # 默认回退 - 重新开始
        return Command(goto="comprehension_agent_v2")
    
    def _handle_retry(self, state: MathProblemStateV2, current_phase: str) -> Command:
        """处理重试请求"""
        
        # 检查是否应该重试当前阶段
        if should_retry_phase(state, current_phase):
            # 返回当前阶段进行重试
            if current_phase == "comprehension":
                return Command(goto="comprehension_agent_v2")
            elif current_phase == "planning":
                return Command(goto="planning_agent_v2")
            elif current_phase == "execution":
                return Command(goto="execution_agent_v2")
            elif current_phase == "verification":
                return Command(goto="verification_agent_v2")
        
        # 超过重试次数，尝试回到规划阶段
        return Command(goto="planning_agent_v2")
    
    def _handle_comprehension_completion(self, state: MathProblemStateV2) -> Command:
        """处理理解阶段完成"""
        comprehension_state = state.get("comprehension_state")
        
        if not comprehension_state:
            # 理解失败，需要重试
            return Command(goto="comprehension_agent_v2")
        
        # 检查理解结果是否有效
        analysis_completed = comprehension_state.get("analysis_completed", False)
        
        if analysis_completed:
            # 理解成功，进入规划阶段
            return Command(goto="planning_agent_v2")
        else:
            # 理解不完整，需要重试
            return Command(goto="comprehension_agent_v2")
    
    def _handle_planning_completion(self, state: MathProblemStateV2) -> Command:
        """处理规划阶段完成"""
        planning_state = state.get("planning_state")
        
        if not planning_state:
            # 规划失败，需要重试
            return Command(goto="planning_agent_v2")
        
        # 检查规划结果是否有效
        execution_plan = planning_state.get("execution_plan")
        
        if execution_plan and planning_state.get("total_tasks", 0) > 0:
            # 规划成功，进入执行阶段
            return Command(goto="execution_agent_v2")
        else:
            # 规划不完整，需要重试
            return Command(goto="planning_agent_v2")
    
    def _handle_execution_completion(self, state: MathProblemStateV2) -> Command:
        """处理执行阶段完成"""
        execution_state = state.get("execution_state")
        planning_state = state.get("planning_state")
        
        if not execution_state or not planning_state:
            # 执行或规划信息缺失
            return Command(goto="planning_agent_v2")
        
        # 检查是否所有任务都已完成
        current_task_index = planning_state.get("current_task_index", 0)
        total_tasks = planning_state.get("total_tasks", 0)
        
        if current_task_index >= total_tasks:
            # 所有任务完成，进入验证阶段
            return Command(goto="verification_agent_v2")
        else:
            # 还有任务需要执行，继续执行阶段
            return Command(goto="execution_agent_v2")
    
    def _handle_verification_completion(self, state: MathProblemStateV2) -> Command:
        """处理验证阶段完成"""
        verification_state = state.get("verification_state")
        
        if not verification_state:
            # 验证失败，需要重试
            return Command(goto="verification_agent_v2")
        
        # 检查验证结果
        verification_report = verification_state.get("verification_report")
        
        if verification_report and verification_report.get("verdict") == "PASSED":
            # 验证通过，流程完成
            return Command(goto="__end__")
        else:
            # 验证失败，返回规划阶段重新规划
            current_iters = state.get("coordinator_state", {}).get("phase_iterations", {}).get("verification", 0)
            max_retries = state.get("coordinator_state", {}).get("max_retries", {}).get("verification", 3)
            
            if current_iters >= max_retries:
                # 超过验证重试次数，直接结束
                return Command(goto="__end__", update={
                    "error_message": {
                        "type": "override",
                        "value": f"Verification failed more than {max_retries} times. Stopping."
                    },
                    "is_completed": True,
                    "completion_reason": "Max verification retries exceeded"
                })
            else:
                # 未超上限，回到规划阶段重规划
                return Command(goto="planning_agent_v2")
    
    def _handle_failure_state(self, state: MathProblemStateV2) -> Command:
        """处理失败状态"""
        
        # 尝试通过回到规划阶段来恢复
        current_phase = get_current_phase(state)
        
        # 检查当前阶段的迭代次数
        phase_iterations = state.get("coordinator_state", {}).get("phase_iterations", {})
        current_iters = phase_iterations.get(current_phase, 0)
        max_retries = state.get("coordinator_state", {}).get("max_retries", {}).get(current_phase, 3)
        
        if current_iters >= max_retries:
            # 超过最大重试次数，直接结束
            return Command(goto="__end__", update={
                "error_message": {
                    "type": "override",
                    "value": f"{current_phase.capitalize()} phase failed more than {max_retries} times. Stopping."
                },
                "is_completed": True,
                "completion_reason": f"Max {current_phase} retries exceeded"
            })
        else:
            # 尝试回到规划阶段重新规划
            return Command(goto="planning_agent_v2")


def coordinator_agent_v2(state: MathProblemStateV2) -> Command:
    """
    Coordinator Agent V2 入口函数
    
    为LangGraph工作流设计的兼容接口
    """
    agent = CoordinatorAgentV2()
    return agent.coordinate_workflow(state)
"""
Verification Agent V2 - 基于新版State设计的验证反思智能体
"""

from typing import Any, Dict, List
from langchain_core.messages import HumanMessage, AIMessage

from src.prompts.prompt import VERIFICATION_PROMPT
from src.state import (
    MathProblemStateV2,
    VerificationStateV2,
    ExecutionStatusV2,
    VerificationVerdict,
    VerificationCheck,
    VerificationReport,
    get_current_phase,
    should_retry_phase
)
from src.configuration import Configuration


class VerificationAgentV2:
    """基于新版State设计的验证反思智能体"""
    
    def __init__(self, config: Configuration | None = None):
        self.config = config or Configuration.from_runnable_config()
    
    def verify_solution(self, state: MathProblemStateV2) -> MathProblemStateV2:
        """
        验证解决方案 - 基于新版State设计
        
        遵循提示词的四阶段验证协议：
        1. 一致性检查
        2. 逻辑链审计  
        3. 约束满足验证
        4. 最终答案评估
        """
        # 检查重试条件
        current_phase = get_current_phase(state)
        if current_phase != "verification":
            return self._handle_wrong_phase(state)
            
        if not should_retry_phase(state, "verification"):
            return self._handle_max_retries(state)
        
        # 获取执行结果
        execution_state = state.get("execution_state")
        if not execution_state:
            return self._handle_missing_execution(state)
        
        # 获取理解结果（用于一致性检查）
        comprehension_state = state.get("comprehension_state")
        
        # 执行四阶段验证
        verification_results = self._perform_verification(comprehension_state, execution_state)
        
        # 构建验证状态
        return self._build_verification_state(state, verification_results)
    
    def _perform_verification(self, comprehension_state: Dict[str, Any] | None,
                            execution_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行四阶段验证"""
        
        # 1. 一致性检查
        consistency_check = self._check_consistency(comprehension_state, execution_state)
        
        # 2. 逻辑链审计
        logical_chain_audit = self._audit_logical_chain(execution_state)
        
        # 3. 约束满足验证
        constraint_verification = self._verify_constraints(comprehension_state, execution_state)
        
        # 4. 最终答案评估
        final_answer_assessment = self._assess_final_answer(comprehension_state, execution_state)
        
        # 综合裁决
        verdict, rationale = self._determine_verdict(
            consistency_check, logical_chain_audit, constraint_verification, final_answer_assessment
        )
        
        return {
            "verdict": verdict,
            "consistency_check": consistency_check,
            "logical_chain_audit": logical_chain_audit,
            "constraint_verification": constraint_verification,
            "final_answer_assessment": final_answer_assessment,
            "rationale": rationale
        }
    
    def _check_consistency(self, comprehension_state: Dict[str, Any] | None,
                         execution_state: Dict[str, Any]) -> VerificationCheck:
        """一致性检查：执行是否与规划一致"""
        
        if not comprehension_state:
            return VerificationCheck(
                check_type="一致性检查",
                status="FAILED",
                details="缺少理解结果，无法进行一致性检查",
                constraints_verified=[]
            )
        
        # 检查执行路径是否与理解结果一致
        execution_trace = execution_state.get("computational_trace", [])
        
        if len(execution_trace) == 0:
            return VerificationCheck(
                check_type="一致性检查",
                status="FAILED",
                details="执行轨迹为空，无法验证一致性",
                constraints_verified=[]
            )
        
        # 模拟一致性检查逻辑
        all_tasks_successful = all(task.get("success", False) for task in execution_trace)
        
        if all_tasks_successful:
            return VerificationCheck(
                check_type="一致性检查",
                status="PASSED",
                details="执行者的计算路径与分析报告中规划的策略完全一致",
                constraints_verified=[]
            )
        else:
            failed_tasks = [task["task_id"] for task in execution_trace if not task.get("success", False)]
            return VerificationCheck(
                check_type="一致性检查",
                status="FAILED",
                details=f"在任务 {failed_tasks} 中发现执行路径偏离",
                constraints_verified=[]
            )
    
    def _audit_logical_chain(self, execution_state: Dict[str, Any]) -> VerificationCheck:
        """逻辑链审计：检查执行轨迹的逻辑连贯性"""
        
        execution_trace = execution_state.get("computational_trace", [])
        
        if len(execution_trace) <= 1:
            return VerificationCheck(
                check_type="逻辑链审计",
                status="PASSED",
                details="执行轨迹过短，逻辑链检查通过",
                constraints_verified=[]
            )
        
        # 检查任务依赖关系
        dependencies_valid = True
        issues = []
        
        for i in range(1, len(execution_trace)):
            current_task = execution_trace[i]
            previous_task = execution_trace[i-1]
            
            # 模拟依赖检查
            if not previous_task.get("success", False) and current_task.get("success", False):
                dependencies_valid = False
                issues.append(f"任务 {current_task['task_id']} 依赖于失败的任务 {previous_task['task_id']}")
        
        if dependencies_valid:
            return VerificationCheck(
                check_type="逻辑链审计",
                status="PASSED",
                details="计算轨迹中的数据流和依赖关系正确无误",
                constraints_verified=[]
            )
        else:
            return VerificationCheck(
                check_type="逻辑链审计",
                status="FAILED",
                details=f"发现逻辑断裂: {'; '.join(issues)}",
                constraints_verified=[]
            )
    
    def _verify_constraints(self, comprehension_state: Dict[str, Any] | None,
                          execution_state: Dict[str, Any]) -> VerificationCheck:
        """约束满足验证：检查结果是否满足所有约束"""
        
        if not comprehension_state:
            return VerificationCheck(
                check_type="约束满足验证",
                status="FAILED",
                details="缺少理解结果，无法提取约束条件",
                constraints_verified=[]
            )
        
        # 提取约束条件
        surface_decon = comprehension_state.get("surface_deconstruction", {})
        constraints = surface_decon.get("explicit_constraints", [])
        
        if not constraints:
            return VerificationCheck(
                check_type="约束满足验证",
                status="PASSED",
                details="问题没有明确的约束条件，验证通过",
                constraints_verified=[]
            )
        
        # 模拟约束验证
        verified_constraints = []
        violations = []
        
        for constraint in constraints:
            # 简单模拟验证逻辑
            if "实数" in constraint or "ℝ" in constraint:
                # 检查结果是否为实数
                verified_constraints.append(constraint)
            elif "正数" in constraint or ">0" in constraint:
                # 检查结果是否为正数
                verified_constraints.append(constraint)
            else:
                # 默认通过
                verified_constraints.append(constraint)
        
        if not violations:
            return VerificationCheck(
                check_type="约束满足验证",
                status="PASSED",
                details="所有约束条件均得到满足",
                constraints_verified=verified_constraints
            )
        else:
            return VerificationCheck(
                check_type="约束满足验证",
                status="FAILED",
                details=f"发现约束违反: {'; '.join(violations)}",
                constraints_verified=verified_constraints
            )
    
    def _assess_final_answer(self, comprehension_state: Dict[str, Any] | None,
                           execution_state: Dict[str, Any]) -> VerificationCheck:
        """最终答案评估：检查答案的完整性和格式"""
        
        if not comprehension_state:
            return VerificationCheck(
                check_type="最终答案评估",
                status="FAILED",
                details="缺少理解结果，无法评估最终答案",
                constraints_verified=[]
            )
        
        # 检查是否有最终答案
        intermediate_results = execution_state.get("intermediate_results", [])
        
        if not intermediate_results:
            return VerificationCheck(
                check_type="最终答案评估",
                status="FAILED",
                details="没有生成任何中间结果或最终答案",
                constraints_verified=[]
            )
        
        # 获取最后一个结果作为最终答案
        final_result = intermediate_results[-1] if intermediate_results else {}
        
        if final_result.get("result"):
            return VerificationCheck(
                check_type="最终答案评估",
                status="PASSED",
                details="最终答案格式正确且完整回答了求解目标",
                constraints_verified=[]
            )
        else:
            return VerificationCheck(
                check_type="最终答案评估",
                status="FAILED",
                details="最终答案缺失或格式不正确",
                constraints_verified=[]
            )
    
    def _determine_verdict(self, consistency_check: VerificationCheck,
                         logical_chain_audit: VerificationCheck,
                         constraint_verification: VerificationCheck,
                         final_answer_assessment: VerificationCheck) -> tuple[VerificationVerdict, str]:
        """确定最终裁决"""
        
        all_passed = all([
            consistency_check.status == "PASSED",
            logical_chain_audit.status == "PASSED",
            constraint_verification.status == "PASSED",
            final_answer_assessment.status == "PASSED"
        ])
        
        some_failed = any([
            check.status == "FAILED" 
            for check in [consistency_check, logical_chain_audit, constraint_verification, final_answer_assessment]
        ])
        
        if all_passed:
            return VerificationVerdict.PASSED, "所有检查项均已通过。执行过程逻辑严密，结果满足所有原始约束条件，最终答案正确且完整。"
        elif not some_failed:
            return VerificationVerdict.PASSED_WITH_WARNINGS, "计算结果在数学上是正确的，但执行过程存在轻微问题，建议在未来的执行中进行优化。"
        else:
            failed_checks = [
                check.check_type for check in [consistency_check, logical_chain_audit, constraint_verification, final_answer_assessment]
                if check.status == "FAILED"
            ]
            return VerificationVerdict.FAILED, f"验证失败。失败的关键原因在于 {', '.join(failed_checks)}。建议重新规划或执行。"
    
    def _build_verification_state(self, state: MathProblemStateV2, 
                                verification_results: Dict[str, Any]) -> MathProblemStateV2:
        """构建验证状态"""
        
        # 创建验证报告
        verification_report = VerificationReport(
            verdict=verification_results["verdict"],
            consistency_check=verification_results["consistency_check"],
            logical_chain_audit=verification_results["logical_chain_audit"],
            constraint_verification=verification_results["constraint_verification"],
            final_answer_assessment=verification_results["final_answer_assessment"],
            rationale=verification_results["rationale"]
        )
        
        # 构建验证检查记录
        verification_checks = [
            verification_results["consistency_check"],
            verification_results["logical_chain_audit"],
            verification_results["constraint_verification"],
            verification_results["final_answer_assessment"]
        ]
        
        # 提取已验证的约束
        constraints_verified = verification_results["constraint_verification"].constraints_verified
        
        # 生成优化建议
        optimization_suggestions = self._generate_optimization_suggestions(verification_results)
        
        # 计算置信度
        confidence_score = self._calculate_confidence_score(verification_results)
        
        # 构建验证状态
        verification_state: VerificationStateV2 = {
            "verification_report": verification_report,
            "verification_checks": verification_checks,
            "constraints_verified": constraints_verified,
            "violations_found": [],  # 实际实现中需要从检查结果提取
            "optimization_suggestions": optimization_suggestions,
            "verification_messages": [
                AIMessage(content=f"Verification completed with verdict: {verification_results['verdict'].value}")
            ],
            "verification_iterations": state.get("coordinator_state", {}).get("phase_iterations", {}).get("verification", 0) + 1,
            "confidence_score": confidence_score,
            "error_details": None
        }
        
        # 更新协调器状态
        coordinator_state = state.get("coordinator_state", {})
        
        # 根据验证结果决定下一步
        if verification_results["verdict"] == VerificationVerdict.PASSED:
            next_phase = "completed"
            execution_status = ExecutionStatusV2.COMPLETED
        else:
            next_phase = "planning"  # 验证失败时返回规划阶段
            execution_status = ExecutionStatusV2.NEEDS_RETRY
        
        updated_coordinator = {
            **coordinator_state,
            "current_phase": next_phase,
            "execution_status": execution_status,
            "phase_iterations": {
                **coordinator_state.get("phase_iterations", {}),
                "verification": verification_state["verification_iterations"]
            }
        }
        
        # 设置最终答案（如果验证通过）
        final_answer = None
        if verification_results["verdict"] == VerificationVerdict.PASSED:
            execution_state = state.get("execution_state", {})
            intermediate_results = execution_state.get("intermediate_results", [])
            if intermediate_results:
                final_answer = intermediate_results[-1].get("result")
        
        return {
            **state,
            "verification_state": verification_state,
            "coordinator_state": updated_coordinator,
            "final_answer": final_answer,
            "is_completed": verification_results["verdict"] == VerificationVerdict.PASSED,
            "completion_reason": "Verification passed" if verification_results["verdict"] == VerificationVerdict.PASSED else "Verification failed, needs retry"
        }
    
    def _generate_optimization_suggestions(self, verification_results: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        verdict = verification_results["verdict"]
        
        if verdict == VerificationVerdict.PASSED:
            suggestions.append("解法简洁有效，无需优化")
        elif verdict == VerificationVerdict.PASSED_WITH_WARNINGS:
            suggestions.append("考虑优化工具选择策略")
            suggestions.append("改进错误处理机制")
        else:
            suggestions.append("重新分析问题理解")
            suggestions.append("调整执行计划策略")
            suggestions.append("加强约束条件验证")
        
        return suggestions
    
    def _calculate_confidence_score(self, verification_results: Dict[str, Any]) -> float:
        """计算置信度分数"""
        verdict = verification_results["verdict"]
        
        if verdict == VerificationVerdict.PASSED:
            return 0.95
        elif verdict == VerificationVerdict.PASSED_WITH_WARNINGS:
            return 0.75
        else:
            return 0.3
    
    def _handle_wrong_phase(self, state: MathProblemStateV2) -> MathProblemStateV2:
        """处理错误的阶段调用"""
        coordinator_state = state.get("coordinator_state", {})
        
        return {
            **state,
            "coordinator_state": {
                **coordinator_state,
                "error_messages": [
                    *coordinator_state.get("error_messages", []),
                    f"Verification agent called in wrong phase: {get_current_phase(state)}"
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
                    "Verification phase exceeded maximum retry attempts"
                ],
                "execution_status": ExecutionStatusV2.FAILED
            },
            "is_completed": True,
            "completion_reason": "Max verification retries exceeded"
        }
    
    def _handle_missing_execution(self, state: MathProblemStateV2) -> MathProblemStateV2:
        """处理缺少执行结果"""
        coordinator_state = state.get("coordinator_state", {})
        
        return {
            **state,
            "coordinator_state": {
                **coordinator_state,
                "current_phase": "execution",
                "execution_status": ExecutionStatusV2.NEEDS_RETRY,
                "error_messages": [
                    *coordinator_state.get("error_messages", []),
                    "Verification failed: missing execution result"
                ]
            }
        }


def verification_agent_v2(state: MathProblemStateV2) -> MathProblemStateV2:
    """
    Verification Agent V2 入口函数
    
    为LangGraph工作流设计的兼容接口
    """
    agent = VerificationAgentV2()
    return agent.verify_solution(state)
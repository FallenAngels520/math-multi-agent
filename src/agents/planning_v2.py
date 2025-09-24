"""
Planning Agent V2 - 基于新版State设计的策略规划智能体
"""

from typing import Any, Dict, List
from langchain_core.messages import HumanMessage, AIMessage

from src.prompts.prompt import PREPROCESSING_PROMPT
from src.state import (
    MathProblemStateV2,
    PlanningStateV2,
    ExecutionStatusV2,
    ExecutionTask,
    ExecutionPlan,
    get_current_phase,
    should_retry_phase
)
from src.configuration import Configuration


class PlanningAgentV2:
    """基于新版State设计的策略规划智能体"""
    
    def __init__(self, config: Configuration | None = None):
        self.config = config or Configuration.from_runnable_config()
    
    def create_solution_plan(self, state: MathProblemStateV2) -> MathProblemStateV2:
        """
        创建解题计划 - 基于新版State设计
        
        遵循提示词的规划原则：
        - 原子性任务分解
        - 依赖关系管理（DAG结构）
        - 原理驱动规划
        """
        # 检查重试条件
        current_phase = get_current_phase(state)
        if current_phase != "planning":
            return self._handle_wrong_phase(state)
            
        if not should_retry_phase(state, "planning"):
            return self._handle_max_retries(state)
        
        # 获取理解结果
        comprehension_state = state.get("comprehension_state")
        if not comprehension_state:
            return self._handle_missing_comprehension(state)
        
        # 基于理解结果创建执行计划
        execution_plan = self._create_execution_plan(comprehension_state)
        
        # 构建规划状态
        return self._build_planning_state(state, execution_plan)
    
    def _create_execution_plan(self, comprehension_state: Dict[str, Any]) -> ExecutionPlan:
        """基于理解结果创建执行计划"""
        
        # 提取理解信息
        problem_type = comprehension_state.get("problem_type", "other")
        surface_decon = comprehension_state.get("surface_deconstruction", {})
        principles_trace = comprehension_state.get("principles_tracing", {})
        path_build = comprehension_state.get("path_building", {})
        
        # 根据问题类型创建不同的执行计划
        if problem_type == "algebra":
            return self._create_algebra_plan(surface_decon, principles_trace, path_build)
        elif problem_type == "geometry":
            return self._create_geometry_plan(surface_decon, principles_trace, path_build)
        elif problem_type == "calculus":
            return self._create_calculus_plan(surface_decon, principles_trace, path_build)
        else:
            return self._create_general_plan(surface_decon, principles_trace, path_build)
    
    def _create_algebra_plan(self, surface_decon: Dict[str, Any], 
                           principles_trace: Dict[str, Any], 
                           path_build: Dict[str, Any]) -> ExecutionPlan:
        """创建代数问题执行计划"""
        
        return ExecutionPlan(
            plan_metadata={
                "problem_id": "algebra_001",
                "planner_version": "3.0_algebra",
                "problem_type": "algebra"
            },
            workspace_initialization=[
                {
                    "variable_name": "equation",
                    "description": "原始方程",
                    "value_ref": "surface_deconstruction.givens[0]"
                },
                {
                    "variable_name": "constraints",
                    "description": "约束条件", 
                    "value_ref": "surface_deconstruction.explicit_constraints"
                }
            ],
            execution_plan={
                "problem_setup": [
                    ExecutionTask(
                        task_id="setup.1",
                        description="解析方程结构",
                        principle_link="方程求解思想",
                        method="AnalyzeEquationStructure",
                        params={
                            "equation_ref": "equation",
                            "constraints_ref": "constraints"
                        },
                        dependencies=[],
                        output_id="equation_structure"
                    )
                ],
                "main_logic": [
                    ExecutionTask(
                        task_id="logic.1",
                        description="对方程进行符号化简",
                        principle_link="等价转换思想",
                        method="SymbolicSimplify",
                        params={
                            "expression_ref": "equation_structure"
                        },
                        dependencies=["setup.1"],
                        output_id="simplified_equation"
                    ),
                    ExecutionTask(
                        task_id="logic.2", 
                        description="求解化简后的方程",
                        principle_link="方程求解思想",
                        method="SolveEquation",
                        params={
                            "target_ref": "simplified_equation",
                            "solver_type": "auto_detect"
                        },
                        dependencies=["logic.1"],
                        output_id="raw_solutions"
                    )
                ],
                "verification_and_filtering": [
                    ExecutionTask(
                        task_id="verify.1",
                        description="验证并筛选解",
                        principle_link="约束满足验证",
                        method="FilterSolutions",
                        params={
                            "solutions_ref": "raw_solutions",
                            "constraints_ref": "constraints"
                        },
                        dependencies=["logic.2"],
                        output_id="validated_solutions"
                    )
                ]
            },
            final_output={
                "task_id": "final",
                "description": "输出最终答案",
                "dependencies": ["validated_solutions"],
                "method": "FormatResult",
                "params": {
                    "source_ref": "validated_solutions"
                }
            }
        )
    
    def _create_geometry_plan(self, surface_decon: Dict[str, Any],
                            principles_trace: Dict[str, Any], 
                            path_build: Dict[str, Any]) -> ExecutionPlan:
        """创建几何问题执行计划"""
        
        return ExecutionPlan(
            plan_metadata={
                "problem_id": "geometry_001",
                "planner_version": "3.0_geometry",
                "problem_type": "geometry"
            },
            workspace_initialization=[
                {
                    "variable_name": "geometric_info",
                    "description": "几何信息",
                    "value_ref": "surface_deconstruction.givens"
                },
                {
                    "variable_name": "formulas",
                    "description": "相关公式",
                    "value_ref": "principles_tracing.fundamental_principles"
                }
            ],
            execution_plan={
                "problem_setup": [
                    ExecutionTask(
                        task_id="setup.1",
                        description="建立几何模型",
                        principle_link="数形结合思想",
                        method="BuildGeometricModel",
                        params={
                            "info_ref": "geometric_info",
                            "formulas_ref": "formulas"
                        },
                        dependencies=[],
                        output_id="geometric_model"
                    )
                ],
                "main_logic": [
                    ExecutionTask(
                        task_id="logic.1",
                        description="应用几何公式计算",
                        principle_link="几何公式应用",
                        method="ApplyGeometricFormula",
                        params={
                            "model_ref": "geometric_model",
                            "target_quantity": "surface_deconstruction.objectives[0]"
                        },
                        dependencies=["setup.1"],
                        output_id="calculated_result"
                    )
                ],
                "verification_and_filtering": [
                    ExecutionTask(
                        task_id="verify.1",
                        description="验证几何关系",
                        principle_link="几何关系验证",
                        method="VerifyGeometricRelations",
                        params={
                            "result_ref": "calculated_result",
                            "model_ref": "geometric_model"
                        },
                        dependencies=["logic.1"],
                        output_id="verified_result"
                    )
                ]
            },
            final_output={
                "task_id": "final",
                "description": "输出几何计算结果",
                "dependencies": ["verified_result"],
                "method": "FormatGeometricResult",
                "params": {
                    "source_ref": "verified_result"
                }
            }
        )
    
    def _create_calculus_plan(self, surface_decon: Dict[str, Any],
                            principles_trace: Dict[str, Any],
                            path_build: Dict[str, Any]) -> ExecutionPlan:
        """创建微积分问题执行计划"""
        
        return ExecutionPlan(
            plan_metadata={
                "problem_id": "calculus_001",
                "planner_version": "3.0_calculus",
                "problem_type": "calculus"
            },
            workspace_initialization=[
                {
                    "variable_name": "function_expression",
                    "description": "函数表达式",
                    "value_ref": "surface_deconstruction.givens[0]"
                },
                {
                    "variable_name": "operation_type",
                    "description": "操作类型（求导/积分等）",
                    "value_ref": "surface_deconstruction.objectives[0]"
                }
            ],
            execution_plan={
                "problem_setup": [
                    ExecutionTask(
                        task_id="setup.1",
                        description="解析函数表达式",
                        principle_link="函数分析思想",
                        method="ParseFunctionExpression",
                        params={
                            "expression_ref": "function_expression"
                        },
                        dependencies=[],
                        output_id="parsed_function"
                    )
                ],
                "main_logic": [
                    ExecutionTask(
                        task_id="logic.1",
                        description="执行微积分操作",
                        principle_link="微积分原理",
                        method="PerformCalculusOperation",
                        params={
                            "function_ref": "parsed_function",
                            "operation_ref": "operation_type"
                        },
                        dependencies=["setup.1"],
                        output_id="operation_result"
                    )
                ],
                "verification_and_filtering": [
                    ExecutionTask(
                        task_id="verify.1",
                        description="验证微积分结果",
                        principle_link="微积分验证",
                        method="VerifyCalculusResult",
                        params={
                            "result_ref": "operation_result",
                            "original_ref": "parsed_function"
                        },
                        dependencies=["logic.1"],
                        output_id="verified_calculus_result"
                    )
                ]
            },
            final_output={
                "task_id": "final",
                "description": "输出微积分结果",
                "dependencies": ["verified_calculus_result"],
                "method": "FormatCalculusResult",
                "params": {
                    "source_ref": "verified_calculus_result"
                }
            }
        )
    
    def _create_general_plan(self, surface_decon: Dict[str, Any],
                           principles_trace: Dict[str, Any],
                           path_build: Dict[str, Any]) -> ExecutionPlan:
        """创建通用问题执行计划"""
        
        return ExecutionPlan(
            plan_metadata={
                "problem_id": "general_001",
                "planner_version": "3.0_general",
                "problem_type": "general"
            },
            workspace_initialization=[
                {
                    "variable_name": "problem_data",
                    "description": "问题数据",
                    "value_ref": "surface_deconstruction.givens"
                },
                {
                    "variable_name": "solution_goal",
                    "description": "求解目标",
                    "value_ref": "surface_deconstruction.objectives"
                }
            ],
            execution_plan={
                "problem_setup": [
                    ExecutionTask(
                        task_id="setup.1",
                        description="分析问题结构",
                        principle_link="问题分析思想",
                        method="AnalyzeProblemStructure",
                        params={
                            "data_ref": "problem_data",
                            "goal_ref": "solution_goal"
                        },
                        dependencies=[],
                        output_id="problem_structure"
                    )
                ],
                "main_logic": [
                    ExecutionTask(
                        task_id="logic.1",
                        description="应用适当方法求解",
                        principle_link="数学方法应用",
                        method="ApplyMathematicalMethod",
                        params={
                            "structure_ref": "problem_structure",
                            "method_type": "auto_select"
                        },
                        dependencies=["setup.1"],
                        output_id="solution_result"
                    )
                ],
                "verification_and_filtering": [
                    ExecutionTask(
                        task_id="verify.1",
                        description="验证求解结果",
                        principle_link="结果验证",
                        method="VerifySolution",
                        params={
                            "result_ref": "solution_result",
                            "original_data_ref": "problem_data"
                        },
                        dependencies=["logic.1"],
                        output_id="verified_solution"
                    )
                ]
            },
            final_output={
                "task_id": "final",
                "description": "输出最终答案",
                "dependencies": ["verified_solution"],
                "method": "FormatGeneralResult",
                "params": {
                    "source_ref": "verified_solution"
                }
            }
        )
    
    def _build_planning_state(self, state: MathProblemStateV2, execution_plan: ExecutionPlan) -> MathProblemStateV2:
        """构建规划状态"""
        
        planning_state: PlanningStateV2 = {
            "execution_plan": execution_plan,
            "current_task_index": 0,
            "total_tasks": self._count_total_tasks(execution_plan),
            "completed_tasks": [],
            "alternative_strategies": self._generate_alternative_strategies(execution_plan),
            "complexity_estimate": self._estimate_complexity(execution_plan),
            "planning_messages": [
                AIMessage(content=f"Planning completed with {self._count_total_tasks(execution_plan)} tasks")
            ],
            "planning_iterations": state.get("coordinator_state", {}).get("phase_iterations", {}).get("planning", 0) + 1,
            "error_details": None
        }
        
        # 更新协调器状态
        coordinator_state = state.get("coordinator_state", {})
        updated_coordinator = {
            **coordinator_state,
            "current_phase": "execution",
            "execution_status": ExecutionStatusV2.COMPLETED,
            "phase_iterations": {
                **coordinator_state.get("phase_iterations", {}),
                "planning": planning_state["planning_iterations"]
            }
        }
        
        return {
            **state,
            "planning_state": planning_state,
            "coordinator_state": updated_coordinator
        }
    
    def _count_total_tasks(self, execution_plan: ExecutionPlan) -> int:
        """计算总任务数"""
        total = 0
        for section_tasks in execution_plan.execution_plan.values():
            if isinstance(section_tasks, list):
                total += len(section_tasks)
        return total
    
    def _generate_alternative_strategies(self, execution_plan: ExecutionPlan) -> List[Dict[str, Any]]:
        """生成替代策略"""
        strategies = []
        
        # 根据计划类型生成替代策略
        problem_type = execution_plan.plan_metadata.get("problem_type", "general")
        
        if problem_type == "algebra":
            strategies.extend([
                {
                    "strategy": "graphical_method",
                    "complexity": "medium",
                    "applicability": "visualization_required",
                    "description": "使用图形方法求解方程"
                },
                {
                    "strategy": "numerical_approximation", 
                    "complexity": "low",
                    "applicability": "approximate_solutions",
                    "description": "使用数值近似方法"
                }
            ])
        
        return strategies
    
    def _estimate_complexity(self, execution_plan: ExecutionPlan) -> str:
        """估计复杂度"""
        total_tasks = self._count_total_tasks(execution_plan)
        
        if total_tasks <= 3:
            return "low"
        elif total_tasks <= 6:
            return "medium"
        else:
            return "high"
    
    def _handle_wrong_phase(self, state: MathProblemStateV2) -> MathProblemStateV2:
        """处理错误的阶段调用"""
        coordinator_state = state.get("coordinator_state", {})
        
        return {
            **state,
            "coordinator_state": {
                **coordinator_state,
                "error_messages": [
                    *coordinator_state.get("error_messages", []),
                    f"Planning agent called in wrong phase: {get_current_phase(state)}"
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
                    "Planning phase exceeded maximum retry attempts"
                ],
                "execution_status": ExecutionStatusV2.FAILED
            }
        }
    
    def _handle_missing_comprehension(self, state: MathProblemStateV2) -> MathProblemStateV2:
        """处理缺少理解结果"""
        coordinator_state = state.get("coordinator_state", {})
        
        return {
            **state,
            "coordinator_state": {
                **coordinator_state,
                "current_phase": "comprehension",
                "execution_status": ExecutionStatusV2.NEEDS_RETRY,
                "error_messages": [
                    *coordinator_state.get("error_messages", []),
                    "Planning failed: missing comprehension result"
                ]
            }
        }


def planning_agent_v2(state: MathProblemStateV2) -> MathProblemStateV2:
    """
    Planning Agent V2 入口函数
    
    为LangGraph工作流设计的兼容接口
    """
    agent = PlanningAgentV2()
    return agent.create_solution_plan(state)
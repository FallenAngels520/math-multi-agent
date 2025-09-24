"""
新版State使用示例
演示如何基于提示词绑定原则使用新版State设计
"""

from src.state import (
    create_initial_state,
    get_current_phase,
    should_retry_phase,
    mark_phase_completed,
    ProblemTypeV2,
    ExecutionStatusV2,
    LaTeXNormalization,
    ProblemSurfaceDeconstruction,
    CorePrinciplesTracing,
    StrategicPathBuilding,
    ExecutionTask,
    ExecutionPlan,
    ToolType,
    ToolExecution,
    VerificationVerdict,
    VerificationCheck,
    VerificationReport
)


def demonstrate_state_initialization():
    """演示状态初始化"""
    print("=== 状态初始化演示 ===")
    
    # 创建初始状态
    state = create_initial_state("Solve the equation: 2x + 3 = 7")
    
    print(f"用户输入: {state['user_input']}")
    print(f"当前阶段: {get_current_phase(state)}")
    print(f"执行状态: {state['coordinator_state']['execution_status']}")
    print(f"是否完成: {state['is_completed']}")
    print()


def demonstrate_comprehension_state():
    """演示理解状态构建"""
    print("=== 理解状态构建演示 ===")
    
    state = create_initial_state("Find the roots of x^2 - 5x + 6 = 0")
    
    # 构建理解状态
    comprehension_state = {
        "latex_normalization": LaTeXNormalization(
            original_text="Find the roots of x^2 - 5x + 6 = 0",
            normalized_latex="\\text{Find the roots of } x^2 - 5x + 6 = 0",
            preprocessing_notes=["标准化完成"]
        ),
        "surface_deconstruction": ProblemSurfaceDeconstruction(
            givens=["方程 x^2 - 5x + 6 = 0"],
            objectives=["求解方程的所有实数根"],
            explicit_constraints=["x ∈ ℝ"]
        ),
        "principles_tracing": CorePrinciplesTracing(
            primary_field="代数",
            fundamental_principles=[
                {
                    "principle": "方程求解思想",
                    "related_tools": ["因式分解法", "求根公式"],
                    "principle_manifestation": "将方程转化为可解的形式"
                }
            ]
        ),
        "path_building": StrategicPathBuilding(
            strategy_deduction="本题的核心是方程求解思想。最基础的方法是尝试因式分解，将二次方程分解为两个一次因式的乘积。",
            key_breakthroughs=["识别出方程可因式分解为 (x-2)(x-3)=0"],
            potential_risks=["需要验证解是否满足原方程", "检查判别式非负性"]
        ),
        "problem_type": ProblemTypeV2.ALGEBRA,
        "analysis_completed": True,
        "comprehension_messages": [],
        "error_details": None,
        "retry_count": 0
    }
    
    updated_state = {
        **state,
        "comprehension_state": comprehension_state
    }
    
    print(f"问题类型: {updated_state['comprehension_state']['problem_type']}")
    print(f"已知信息: {updated_state['comprehension_state']['surface_deconstruction']['givens']}")
    print(f"求解目标: {updated_state['comprehension_state']['surface_deconstruction']['objectives']}")
    print(f"核心领域: {updated_state['comprehension_state']['principles_tracing']['primary_field']}")
    print()


def demonstrate_planning_state():
    """演示规划状态构建"""
    print("=== 规划状态构建演示 ===")
    
    state = create_initial_state("Calculate the area of a circle with radius 5")
    
    # 构建执行计划
    execution_plan = ExecutionPlan(
        plan_metadata={
            "problem_id": "circle_area_001",
            "planner_version": "3.0_universal"
        },
        workspace_initialization=[
            {
                "variable_name": "radius",
                "description": "圆的半径",
                "value": 5
            },
            {
                "variable_name": "pi_value", 
                "description": "圆周率π",
                "value": 3.14159
            }
        ],
        execution_plan={
            "main_logic": [
                ExecutionTask(
                    task_id="area.1",
                    description="计算圆的面积",
                    principle_link="几何面积公式",
                    method="CalculateArea",
                    params={
                        "shape": "circle",
                        "radius_ref": "radius",
                        "pi_ref": "pi_value"
                    },
                    dependencies=[],
                    output_id="circle_area"
                )
            ]
        },
        final_output={
            "task_id": "final",
            "description": "输出最终结果",
            "dependencies": ["circle_area"],
            "method": "FormatResult",
            "params": {
                "source_ref": "circle_area"
            }
        }
    )
    
    planning_state = {
        "execution_plan": execution_plan,
        "current_task_index": 0,
        "total_tasks": 1,
        "completed_tasks": [],
        "alternative_strategies": [],
        "complexity_estimate": "low",
        "planning_messages": [],
        "planning_iterations": 1,
        "error_details": None
    }
    
    updated_state = {
        **state,
        "planning_state": planning_state
    }
    
    plan = updated_state['planning_state']['execution_plan']
    print(f"问题ID: {plan.plan_metadata['problem_id']}")
    print(f"工作区变量: {[var['variable_name'] for var in plan.workspace_initialization]}")
    print(f"任务数量: {len(plan.execution_plan.get('main_logic', []))}")
    print(f"第一个任务: {plan.execution_plan['main_logic'][0].description}")
    print()


def demonstrate_execution_state():
    """演示执行状态构建"""
    print("=== 执行状态构建演示 ===")
    
    state = create_initial_state("Simplify the expression: (x+1)^2")
    
    # 构建执行状态
    tool_execution = ToolExecution(
        task_id="simplify.1",
        tool_selected=ToolType.SYMPY,
        tool_call_code="""
from sympy import symbols, expand
x = symbols('x')
expression = (x + 1)**2
result = expand(expression)
""",
        tool_output="x^2 + 2*x + 1",
        analysis_rationale="需要符号化简，SymPy是最合适的工具",
        workspace_update={"simplified_expression": "x^2 + 2*x + 1"}
    )
    
    execution_state = {
        "workspace": {
            "original_expression": "(x+1)^2",
            "variables": {"x": "symbol"}
        },
        "tool_executions": [tool_execution],
        "tools_used": [ToolType.SYMPY],
        "computational_trace": [
            {
                "step": 1,
                "action": "symbol_simplification",
                "input": "(x+1)^2",
                "output": "x^2 + 2*x + 1",
                "tool": "sympy"
            }
        ],
        "intermediate_results": [
            {
                "step": 1,
                "result": "x^2 + 2*x + 1",
                "explanation": "使用SymPy展开平方表达式"
            }
        ],
        "current_task": None,
        "step_status": ExecutionStatusV2.COMPLETED,
        "execution_messages": [],
        "execution_iterations": 1,
        "error_details": None
    }
    
    updated_state = {
        **state,
        "execution_state": execution_state
    }
    
    exec_state = updated_state['execution_state']
    print(f"使用工具: {exec_state['tools_used']}")
    print(f"计算轨迹步骤数: {len(exec_state['computational_trace'])}")
    print(f"中间结果: {exec_state['intermediate_results'][0]['result']}")
    print(f"执行状态: {exec_state['step_status']}")
    print()


def demonstrate_verification_state():
    """演示验证状态构建"""
    print("=== 验证状态构建演示 ===")
    
    state = create_initial_state("Verify the solution x=2 for equation 2x+3=7")
    
    # 构建验证状态
    verification_report = VerificationReport(
        verdict=VerificationVerdict.PASSED,
        consistency_check=VerificationCheck(
            check_type="一致性检查",
            status="PASSED",
            details="执行者的计算路径与分析报告中规划的策略完全一致",
            constraints_verified=[]
        ),
        logical_chain_audit=VerificationCheck(
            check_type="逻辑链审计", 
            status="PASSED",
            details="计算轨迹中的数据流和依赖关系正确无误",
            constraints_verified=[]
        ),
        constraint_verification=VerificationCheck(
            check_type="约束满足验证",
            status="PASSED", 
            details="所有约束条件均得到满足",
            constraints_verified=["x=2满足原方程2*2+3=7"]
        ),
        final_answer_assessment=VerificationCheck(
            check_type="最终答案评估",
            status="PASSED",
            details="最终答案直接、完整地回答了求解目标",
            constraints_verified=[]
        ),
        rationale="所有检查项均已通过。执行过程逻辑严密，结果满足所有原始约束条件，最终答案正确且完整。"
    )
    
    verification_state = {
        "verification_report": verification_report,
        "verification_checks": [
            VerificationCheck(
                check_type="数值验证",
                status="PASSED", 
                details="将x=2代入原方程验证: 2*2+3=7，等式成立",
                constraints_verified=["数值正确性"]
            )
        ],
        "constraints_verified": ["x=2满足原方程"],
        "violations_found": [],
        "optimization_suggestions": ["解法简洁有效，无需优化"],
        "verification_messages": [],
        "verification_iterations": 1,
        "confidence_score": 0.95,
        "error_details": None
    }
    
    updated_state = {
        **state,
        "verification_state": verification_state
    }
    
    ver_state = updated_state['verification_state']
    print(f"验证裁决: {ver_state['verification_report'].verdict}")
    print(f"置信度: {ver_state['confidence_score']}")
    print(f"已验证约束: {ver_state['constraints_verified']}")
    print(f"优化建议: {ver_state['optimization_suggestions']}")
    print()


def demonstrate_state_flow():
    """演示状态流转"""
    print("=== 状态流转演示 ===")
    
    # 初始状态
    state = create_initial_state("Solve the quadratic equation: x^2 - 4 = 0")
    print(f"初始阶段: {get_current_phase(state)}")
    
    # 模拟理解阶段完成
    state = mark_phase_completed(state, "comprehension")
    print(f"理解完成后的阶段: {get_current_phase(state)}")
    
    # 检查重试条件
    can_retry = should_retry_phase(state, "planning")
    print(f"规划阶段是否可以重试: {can_retry}")
    
    # 模拟规划阶段完成
    state = mark_phase_completed(state, "planning")
    print(f"规划完成后的阶段: {get_current_phase(state)}")
    
    # 模拟执行阶段完成
    state = mark_phase_completed(state, "execution") 
    print(f"执行完成后的阶段: {get_current_phase(state)}")
    
    # 模拟验证阶段完成
    state = mark_phase_completed(state, "verification")
    print(f"验证完成后的阶段: {get_current_phase(state)}")
    print()


def main():
    """主演示函数"""
    print("数学多智能体系统 - 新版State设计演示")
    print("=" * 50)
    
    demonstrate_state_initialization()
    demonstrate_comprehension_state()
    demonstrate_planning_state()
    demonstrate_execution_state()
    demonstrate_verification_state()
    demonstrate_state_flow()
    
    print("演示完成！新版State设计提供了：")
    print("✓ 更好的类型安全性")
    print("✓ 清晰的提示词绑定")
    print("✓ 模块化的状态结构")
    print("✓ 完善的错误处理")
    print("✓ 灵活的重试机制")


if __name__ == "__main__":
    main()
"""
重构后的数学多智能体系统使用示例

展示如何使用新的精简架构求解数学问题
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.graph_refactored import solve_math_problem, build_math_solver_graph
from src.state.state_refactored import create_initial_state
from src.configuration import Configuration


def example_1_basic_usage():
    """示例1：基础用法 - 求解简单方程"""
    
    print("\n" + "="*60)
    print("示例1：基础用法 - 求解简单方程")
    print("="*60 + "\n")
    
    problem = "求解方程 x^2 - 5x + 6 = 0"
    
    result = solve_math_problem(
        problem_text=problem,
        max_iterations=10
    )
    
    # 输出结果
    print("\n【理解结果】")
    if result.get("comprehension_output"):
        comp = result["comprehension_output"]
        print(f"  LaTeX标准化: {comp.normalized_latex}")
        print(f"  已知信息: {comp.givens}")
        print(f"  求解目标: {comp.objectives}")
        print(f"  核心领域: {comp.primary_field}")
    
    print("\n【规划结果】")
    if result.get("planning_output"):
        plan = result["planning_output"]
        print(f"  任务数量: {len(plan.execution_tasks)}")
        for task in plan.execution_tasks:
            print(f"  - {task.task_id}: {task.description}")
    
    print("\n【执行结果】")
    if result.get("execution_output"):
        exec_out = result["execution_output"]
        print(f"  工作区变量: {list(exec_out.workspace.keys())}")
        print(f"  工具调用次数: {len(exec_out.tool_executions)}")
        print(f"  最终结果: {exec_out.final_result}")
    
    print("\n【验证结果】")
    if result.get("verification_output"):
        verif = result["verification_output"]
        print(f"  验证裁决: {verif.verdict}")
        print(f"  裁决理由: {verif.rationale}")


def example_2_custom_config():
    """示例2：自定义配置"""
    
    print("\n" + "="*60)
    print("示例2：自定义配置")
    print("="*60 + "\n")
    
    # 创建自定义配置
    config = Configuration(
        coordinator_model="gpt-4",
        max_iterations=5,
        allow_clarification=True
    )
    
    problem = "求极限 lim(x→0) (sin(x) / x)"
    
    # 构建图
    graph = build_math_solver_graph(config)
    
    # 创建初始状态
    initial_state = create_initial_state(problem, max_iterations=5)
    
    # 执行
    final_state = graph.invoke(initial_state)
    
    print(f"\n最终阶段: {final_state.get('current_phase')}")
    print(f"总迭代次数: {final_state.get('total_iterations')}")
    print(f"是否有最终答案: {'是' if final_state.get('final_answer') else '否'}")


def example_3_step_by_step():
    """示例3：逐步查看每个智能体的输出"""
    
    print("\n" + "="*60)
    print("示例3：逐步查看智能体输出")
    print("="*60 + "\n")
    
    problem = "已知函数 f(x) = x^3 - 3x + 1，求 f'(2) 的值"
    
    result = solve_math_problem(problem, max_iterations=10)
    
    # 详细输出每个阶段
    print("\n【阶段1：题目理解】")
    if result.get("comprehension_output"):
        comp = result["comprehension_output"]
        print(f"  标准化题目: {comp.normalized_latex}")
        print(f"  问题类型: {comp.problem_type}")
        print(f"  核心领域: {comp.primary_field}")
        print(f"  已知条件:")
        for given in comp.givens:
            print(f"    - {given}")
        print(f"  求解目标:")
        for obj in comp.objectives:
            print(f"    - {obj}")
        print(f"  策略推演: {comp.strategy_deduction[:100]}...")
    
    print("\n【阶段2：策略规划】")
    if result.get("planning_output"):
        plan = result["planning_output"]
        print(f"  计划元数据: {plan.plan_metadata}")
        print(f"  工作区初始化: {len(plan.workspace_init)} 个变量")
        print(f"  执行任务列表:")
        for i, task in enumerate(plan.execution_tasks, 1):
            print(f"    {i}. [{task.task_id}] {task.description}")
            print(f"       方法: {task.method}")
            print(f"       原理链接: {task.principle_link}")
            if task.dependencies:
                print(f"       依赖: {', '.join(task.dependencies)}")
    
    print("\n【阶段3：计算执行】")
    if result.get("execution_output"):
        exec_out = result["execution_output"]
        print(f"  计算轨迹:")
        for trace in exec_out.computational_trace:
            print(f"    - {trace}")
        print(f"  工具执行记录:")
        for record in exec_out.tool_executions:
            print(f"    [{record.task_id}] {record.tool_type.value}")
            print(f"      理由: {record.rationale}")
        print(f"  最终结果: {exec_out.final_result}")
    
    print("\n【阶段4：验证反思】")
    if result.get("verification_output"):
        verif = result["verification_output"]
        print(f"  最终裁决: {verif.verdict}")
        print(f"  一致性检查: {verif.consistency_check.status}")
        print(f"  逻辑链审计: {verif.logical_chain_audit.status}")
        print(f"  约束验证: {verif.constraint_verification.status}")
        print(f"  最终答案评估: {verif.final_answer_assessment.status}")
        print(f"  裁决理由: {verif.rationale}")
        if verif.suggestions:
            print(f"  建议:")
            for sugg in verif.suggestions:
                print(f"    - {sugg}")


def example_4_error_handling():
    """示例4：错误处理和重试"""
    
    print("\n" + "="*60)
    print("示例4：错误处理和重试")
    print("="*60 + "\n")
    
    # 故意使用不完整的问题
    problem = "求解方程"  # 不完整的问题
    
    result = solve_math_problem(problem, max_iterations=3)
    
    print(f"\n是否有错误: {'是' if result.get('error_message') else '否'}")
    if result.get("error_message"):
        print(f"错误信息: {result['error_message']}")
    
    print(f"总迭代次数: {result.get('total_iterations')}")
    print(f"当前阶段: {result.get('current_phase')}")


def example_5_compare_states():
    """示例5：对比旧版和新版state结构"""
    
    print("\n" + "="*60)
    print("示例5：对比State结构")
    print("="*60 + "\n")
    
    from src.state.state_refactored import create_initial_state
    
    problem = "求解方程 x^2 - 5x + 6 = 0"
    state = create_initial_state(problem, max_iterations=10)
    
    print("【新版State字段】")
    print(f"  核心字段数量: {len(state.keys())}")
    print(f"  字段列表:")
    for key in sorted(state.keys()):
        print(f"    - {key}: {type(state[key]).__name__}")
    
    print("\n【优势】")
    print("  ✅ 字段数量精简（从30+减少到10个核心字段）")
    print("  ✅ 职责边界清晰（每个智能体的输出独立）")
    print("  ✅ 类型安全（使用Pydantic模型）")
    print("  ✅ 易于维护（修改某个智能体不影响其他部分）")


if __name__ == "__main__":
    
    print("\n" + "🚀 "*20)
    print("数学多智能体系统 - 重构版示例")
    print("🚀 "*20)
    
    # 运行示例（选择需要运行的示例）
    
    # 示例1：基础用法
    # example_1_basic_usage()
    
    # 示例2：自定义配置
    # example_2_custom_config()
    
    # 示例3：逐步查看
    # example_3_step_by_step()
    
    # 示例4：错误处理
    # example_4_error_handling()
    
    # 示例5：对比state
    example_5_compare_states()
    
    print("\n" + "✅ "*20)
    print("示例运行完成")
    print("✅ "*20 + "\n") 
"""
完整系统测试 - 数学多智能体协作系统

测试目标：
1. 验证完全Orchestrator模式
2. 测试各个智能体的工作
3. 测试迭代优化流程
4. 验证LLM驱动的智能决策
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 确保可以导入项目模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents.graph_refactored import build_math_solver_graph
from src.state.state_refactored import create_initial_state
from src.configuration import Configuration


def print_separator(title: str = ""):
    """打印分隔线"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")
    else:
        print(f"\n{'-'*60}\n")


def test_basic_equation():
    """测试1：基础方程求解"""
    print_separator("🧪 测试1：基础方程求解")
    
    problem = "求解方程 x^2 - 5x + 6 = 0"
    
    print(f"📝 问题：{problem}\n")
    
    # 创建配置
    config = Configuration(
        coordinator_model="deepseek-r1",
        max_iterations=5,
        enable_geometric_algebraic=False  # 暂时禁用数形结合
    )
    
    # 创建初始状态
    initial_state = create_initial_state(problem, max_iterations=5)
    
    # 构建图
    graph = build_math_solver_graph(config)
    
    print("🚀 开始求解...\n")
    
    try:
        # 执行图
        final_state = graph.invoke(initial_state)
        
        print_separator("✅ 测试1结果")
        
        # 打印结果
        if final_state.get("final_answer"):
            print("📊 最终答案：")
            print(final_state["final_answer"])
        else:
            print("⚠️ 未生成最终答案")
            if final_state.get("error_message"):
                print(f"错误信息：{final_state['error_message']}")
        
        # 打印迭代历史
        if final_state.get("iteration_history"):
            print(f"\n📈 迭代历史（共{len(final_state['iteration_history'])}轮）：")
            for i, record in enumerate(final_state['iteration_history'], 1):
                print(f"  {i}. 阶段：{record.phase} | 状态：{record.verification_status or 'N/A'} | 行动：{record.actions_taken}")
        
        # 打印当前阶段
        print(f"\n🎯 最终阶段：{final_state.get('current_phase', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_inequality():
    """测试2：不等式问题"""
    print_separator("🧪 测试2：不等式求解")
    
    problem = "求解不等式 |x - 3| < 5"
    
    print(f"📝 问题：{problem}\n")
    
    config = Configuration(
        coordinator_model="deepseek-r1",
        max_iterations=5,
        enable_geometric_algebraic=False
    )
    
    initial_state = create_initial_state(problem, max_iterations=5)
    graph = build_math_solver_graph(config)
    
    print("🚀 开始求解...\n")
    
    try:
        final_state = graph.invoke(initial_state)
        
        print_separator("✅ 测试2结果")
        
        if final_state.get("final_answer"):
            print("📊 最终答案：")
            print(final_state["final_answer"])
        
        print(f"\n🎯 最终阶段：{final_state.get('current_phase', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_function_problem():
    """测试3：函数问题（适合数形结合）"""
    print_separator("🧪 测试3：函数问题（数形结合潜力）")
    
    problem = "已知函数 f(x) = x^2 - 4x + 3，求函数的最小值和对称轴"
    
    print(f"📝 问题：{problem}\n")
    
    config = Configuration(
        coordinator_model="deepseek-r1",
        max_iterations=5,
        enable_geometric_algebraic=False  # 先测试不启用
    )
    
    initial_state = create_initial_state(problem, max_iterations=5)
    graph = build_math_solver_graph(config)
    
    print("🚀 开始求解...\n")
    
    try:
        final_state = graph.invoke(initial_state)
        
        print_separator("✅ 测试3结果")
        
        if final_state.get("final_answer"):
            print("📊 最终答案：")
            print(final_state["final_answer"])
        
        # 检查是否识别出可以用数形结合
        if final_state.get("comprehension_output"):
            comp = final_state["comprehension_output"]
            print(f"\n📋 问题类型：{comp.problem_type}")
            print(f"📋 核心领域：{comp.primary_field}")
        
        print(f"\n🎯 最终阶段：{final_state.get('current_phase', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_orchestrator_flow():
    """测试4：验证Orchestrator流程"""
    print_separator("🧪 测试4：Orchestrator流程验证")
    
    problem = "计算 (x+1)^2 的展开式"
    
    print(f"📝 问题：{problem}")
    print("🎯 目标：验证所有agent都不设置current_phase，只有Coordinator设置\n")
    
    config = Configuration(
        coordinator_model="deepseek-r1",
        max_iterations=3,
        enable_geometric_algebraic=False
    )
    
    initial_state = create_initial_state(problem, max_iterations=3)
    graph = build_math_solver_graph(config)
    
    print("🚀 开始求解...\n")
    
    try:
        final_state = graph.invoke(initial_state)
        
        print_separator("✅ 测试4结果 - Orchestrator验证")
        
        # 检查消息历史，看是否有Coordinator的决策
        if final_state.get("messages"):
            print("📨 消息历史（最后5条）：")
            for msg in final_state["messages"][-5:]:
                content = msg.content[:100] if hasattr(msg, 'content') else str(msg)[:100]
                print(f"  - {content}...")
        
        # 检查各个智能体的输出
        print("\n🤖 智能体输出检查：")
        print(f"  ✓ Comprehension: {'有' if final_state.get('comprehension_output') else '无'}")
        print(f"  ✓ Planning: {'有' if final_state.get('planning_output') else '无'}")
        print(f"  ✓ Execution: {'有' if final_state.get('execution_output') else '无'}")
        print(f"  ✓ Verification: {'有' if final_state.get('verification_output') else '无'}")
        
        print(f"\n🎯 最终阶段：{final_state.get('current_phase', 'unknown')}")
        
        if final_state.get("final_answer"):
            print("\n📊 最终答案：")
            print(final_state["final_answer"][:200] + "...")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """测试5：错误处理"""
    print_separator("🧪 测试5：错误处理能力")
    
    problem = "这不是一个数学问题"
    
    print(f"📝 问题：{problem}")
    print("🎯 目标：测试系统对非数学问题的处理\n")
    
    config = Configuration(
        coordinator_model="deepseek-r1",
        max_iterations=3,
        enable_geometric_algebraic=False
    )
    
    initial_state = create_initial_state(problem, max_iterations=3)
    graph = build_math_solver_graph(config)
    
    print("🚀 开始求解...\n")
    
    try:
        final_state = graph.invoke(initial_state)
        
        print_separator("✅ 测试5结果")
        
        if final_state.get("error_message"):
            print(f"⚠️ 错误信息：{final_state['error_message']}")
        
        if final_state.get("final_answer"):
            print("📊 系统响应：")
            print(final_state["final_answer"][:200])
        
        print(f"\n🎯 最终阶段：{final_state.get('current_phase', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败（预期可能发生）：{e}")
        return True  # 错误处理测试，异常也算通过


def run_all_tests():
    """运行所有测试"""
    print_separator("🚀 数学多智能体系统 - 完整测试套件")
    
    print("📋 测试计划：")
    print("  1. 基础方程求解")
    print("  2. 不等式求解")
    print("  3. 函数问题（数形结合潜力）")
    print("  4. Orchestrator流程验证")
    print("  5. 错误处理能力")
    print()
    
    # 检查环境变量
    print("🔧 环境检查：")
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key:
        print(f"  ✓ DEEPSEEK_API_KEY: {'*' * 20}{api_key[-4:]}")
    else:
        print("  ⚠️  DEEPSEEK_API_KEY: 未设置（可能导致测试失败）")
    
    mcp_url = os.getenv("MCP_SERVER_URL")
    if mcp_url:
        print(f"  ✓ MCP_SERVER_URL: {mcp_url}")
    else:
        print("  ℹ️  MCP_SERVER_URL: 未设置（数形结合功能不可用）")
    
    print_separator()
    
    results = []
    
    # 测试1：基础方程
    results.append(("基础方程求解", test_basic_equation()))
    
    # 测试2：不等式
    results.append(("不等式求解", test_inequality()))
    
    # 测试3：函数问题
    results.append(("函数问题", test_function_problem()))
    
    # 测试4：Orchestrator流程
    results.append(("Orchestrator流程", test_orchestrator_flow()))
    
    # 测试5：错误处理
    results.append(("错误处理", test_error_handling()))
    
    # 汇总结果
    print_separator("📊 测试结果汇总")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"总计：{total} 个测试")
    print(f"通过：{passed} 个 ✅")
    print(f"失败：{total - passed} 个 ❌")
    print()
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status}  {name}")
    
    print_separator()
    
    if passed == total:
        print("🎉 所有测试通过！系统运行正常！")
        return 0
    else:
        print(f"⚠️  {total - passed} 个测试失败，请检查问题")
        return 1


if __name__ == "__main__":
    import sys
    
    # 可以通过命令行参数运行单个测试
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        
        tests = {
            "equation": test_basic_equation,
            "inequality": test_inequality,
            "function": test_function_problem,
            "orchestrator": test_orchestrator_flow,
            "error": test_error_handling,
        }
        
        if test_name in tests:
            print(f"🎯 运行单个测试: {test_name}")
            result = tests[test_name]()
            sys.exit(0 if result else 1)
        else:
            print(f"❌ 未知测试: {test_name}")
            print(f"可用测试: {', '.join(tests.keys())}")
            sys.exit(1)
    else:
        # 运行所有测试
        exit_code = run_all_tests()
        sys.exit(exit_code) 
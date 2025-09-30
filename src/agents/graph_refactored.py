"""
重构后的LangGraph主图 - 数学多智能体协作系统（基于agent.md）

架构设计：
1. Coordinator作为真正的智能体，由LLM决策下一步
2. 节点：Coordinator ⇄ Comprehension/Planning/Execution/Verification
3. 智能路由：Coordinator分析验证反馈，决定返回哪个阶段
4. 迭代优化：自动循环直到PASSED或达到最大迭代次数
"""

from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from src.state.state_refactored import AgentState, create_initial_state, should_continue
from src.configuration import Configuration
from src.agents.agents_refactored import (
    coordinator_agent,
    comprehension_agent,
    planning_agent,
    execution_agent,
    verification_agent
)


###################
# 智能路由函数（由Coordinator的决策驱动）
###################

def coordinator_router(state: AgentState) -> str:
    """
    Coordinator驱动的智能路由
    
    根据Coordinator Agent的决策（current_phase）来路由：
    - comprehension → 题目理解智能体
    - planning → 策略规划智能体
    - execution → 计算执行智能体
    - verification → 验证反思智能体
    - complete → 结束
    
    这个路由函数只是执行Coordinator的决策，决策逻辑在coordinator_agent中
    """
    current_phase = state.get("current_phase", "comprehension")
    
    # 简单映射，决策已经由LLM做出
    if current_phase == "comprehension":
        return "comprehension"
    elif current_phase == "planning":
        return "planning"
    elif current_phase == "execution":
        return "execution"
    elif current_phase == "verification":
        return "verification"
    elif current_phase == "complete":
        return "end"
    else:
        # 默认开始
        return "comprehension"


###################
# 构建图
###################

def build_math_solver_graph(config: Configuration = None) -> StateGraph:
    """
    构建数学多智能体求解图（基于agent.md的orchestrator模式）
    
    图结构（Orchestrator中心化）：
    START → Coordinator → [Comprehension/Planning/Execution/Verification] → Coordinator → ...
    
    工作流程：
    1. Coordinator接收状态，分析情况
    2. Coordinator调用LLM决策下一步调用哪个agent
    3. Agent执行任务，返回结果
    4. 回到Coordinator继续决策
    5. 循环直到Coordinator决定complete
    
    优势：
    - 由LLM智能决策，而不是硬编码规则
    - Coordinator真正成为"协调管理智能体"
    - 完全符合agent.md的设计理念
    """
    
    if config is None:
        config = Configuration.from_runnable_config()
    
    # 创建状态图
    builder = StateGraph(AgentState)
    
    # 添加所有节点
    builder.add_node("coordinator", coordinator_agent)
    builder.add_node("comprehension", comprehension_agent)
    builder.add_node("planning", planning_agent)
    builder.add_node("execution", execution_agent)
    builder.add_node("verification", verification_agent)
    
    # 定义流程（Coordinator中心化）
    # START → coordinator（第一次决策）
    builder.add_edge(START, "coordinator")
    
    # coordinator → [comprehension/planning/execution/verification/end]
    # 由Coordinator的决策（current_phase）驱动
    builder.add_conditional_edges(
        "coordinator",
        coordinator_router,
        {
            "comprehension": "comprehension",
            "planning": "planning",
            "execution": "execution",
            "verification": "verification",
            "end": END
        }
    )
    
    # 所有agent执行完后返回coordinator继续决策
    builder.add_edge("comprehension", "coordinator")
    builder.add_edge("planning", "coordinator")
    builder.add_edge("execution", "coordinator")
    builder.add_edge("verification", "coordinator")
    
    # 编译图
    return builder.compile()


###################
# 便捷入口函数
###################

def solve_math_problem(
    problem_text: str,
    max_iterations: int = 10,
    config: Configuration = None
) -> AgentState:
    """
    便捷入口：输入数学问题，返回求解结果
    
    Args:
        problem_text: 数学问题文本
        max_iterations: 最大迭代次数
        config: 配置对象
    
    Returns:
        最终状态，包含解题结果
    """
    
    print(f"\n{'='*60}")
    print(f"🚀 开始求解数学问题")
    print(f"{'='*60}\n")
    print(f"问题：{problem_text}\n")
    
    # 创建初始状态
    initial_state = create_initial_state(problem_text, max_iterations)
    
    # 构建图
    graph = build_math_solver_graph(config)
    
    # 执行图
    final_state = graph.invoke(initial_state)
    
    print(f"\n{'='*60}")
    print(f"🎉 求解完成")
    print(f"{'='*60}\n")
    
    if final_state.get("final_answer"):
        print(f"最终答案：\n{final_state['final_answer']}\n")
    else:
        print(f"求解失败：{final_state.get('error_message', '未知错误')}\n")
    
    return final_state

if __name__ == "__main__":
    problem_text = """
    
    设m为正整数，数列\(\{a_n\}\)是公差不为0的等差数列。若从中删去两项\(a_i\)和\(a_j\)（\(1 \leq i < j \leq 4m + 2\)）后，剩余的4m项可被平均分为m组，且每组的4个数都能构成等差数列，则称数列\(\{a_n\}\)是 “\(m-\)可分数列”。解答下列问题：1、写出所有的\(i,j\)（\(1 \leq i < j \leq 6\)），使数列\(\{a_n\}\)是 “\(1-\)可分数列”；2、当\(m \geq 3\)时，证明：数列\(\{a_n\}\)是 “\(m-\)可分数列” 的充要条件是\(a_2 - a_1 = \frac{a_{4m + 2} - a_1}{4m + 1}\)；3、从\(1,2,\cdots,4m + 2\)中一次任取两个数i和j（\(1 \leq i < j \leq 4m + 2\)），记数列\(\{a_n\}\)是 “\(m-\)可分数列” 的概率为\(P_m\)，证明：\(P_m > \frac{1}{2}\)。
    """
    solve_math_problem(problem_text)
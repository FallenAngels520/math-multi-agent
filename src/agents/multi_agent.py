"""
LangGraph 多智能体编排：数学解题主图

- 入口节点：`coordinator_agent`
- 主流程：Coordinator → Comprehension → Planning → Execution → Verification（循环反馈）
"""

from typing import Dict, Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from src.state import MathProblemState
from src.state.state_utils import initialize_state

from .coordinator import coordinator_agent
from .comprehension import comprehension_agent
from .planning import planning_agent
from .execution import execution_agent
from .verification import verification_agent


def build_math_solver_graph():
    """
    构建并编译数学多智能体求解主图。
    """
    builder = StateGraph(MathProblemState)

    # 节点
    builder.add_node("coordinator_agent", coordinator_agent)
    builder.add_node("comprehension_agent", comprehension_agent)
    builder.add_node("planning_agent", planning_agent)
    builder.add_node("execution_agent", execution_agent)
    builder.add_node("verification_agent", verification_agent)

    # 边：以协调者为中心的回路
    builder.add_edge(START, "coordinator_agent")
    builder.add_edge("coordinator_agent", "comprehension_agent")
    builder.add_edge("comprehension_agent", "coordinator_agent")
    builder.add_edge("planning_agent", "coordinator_agent")
    builder.add_edge("execution_agent", "coordinator_agent")
    builder.add_edge("verification_agent", "coordinator_agent")

    # 结束由 coordinator 决定，通过 Command(goto="__end__") 跳转
    return builder.compile()


math_solver_graph = build_math_solver_graph()


def solve_math_problem(problem_text: str, *, config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    便捷入口：输入题目文本，运行主图直到结束，返回最终 state。
    """
    state = initialize_state(problem_text)
    result = math_solver_graph.invoke(state, config=config or {})
    return result



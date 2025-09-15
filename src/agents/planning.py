"""
Planning agent implementation.
Creates solution strategies and roadmaps for mathematical problems.
"""

from src.state import MathProblemState, ExecutionStatus, PlanningState
from langchain_core.messages import HumanMessage, AIMessage


def planning_agent(state: MathProblemState) -> MathProblemState:
    """
    Planning agent - creates a solution strategy and roadmap.
    
    This agent performs:
    - Strategy selection based on problem type
    - Step-by-step roadmap generation
    - Alternative strategy evaluation
    - Complexity assessment
    
    Args:
        state: Current math problem state
        
    Returns:
        Updated state with planning results
    """
    # TODO: Implement actual planning logic using LLM
    
    comprehension_data = state.get("comprehension_result")
    if not comprehension_data:
        # 缺少理解结果，无法规划 → 触发重试
        return {
            **state,
            "current_agent": "planning",
            "execution_status": ExecutionStatus.NEEDS_RETRY,
            "error_message": "Planning failed: missing comprehension_result",
            "planning_messages": [
                *state.get("planning_messages", []),
                HumanMessage(content="Planning failed: no comprehension_result available")
            ]
        }

    problem_type = comprehension_data.get("problem_type", "algebra")
    if hasattr(problem_type, "value"):
        problem_type = problem_type.value

    if not isinstance(problem_type, str) or not problem_type:
        return {
            **state,
            "current_agent": "planning",
            "execution_status": ExecutionStatus.NEEDS_RETRY,
            "error_message": "Planning failed: invalid problem_type",
            "planning_messages": [
                *state.get("planning_messages", []),
                HumanMessage(content="Planning failed: invalid problem_type")
            ]
        }
    
    if problem_type == "algebra":
        planning_result: PlanningState = {
            "solution_strategy": "solve_linear_equation",
            "roadmap": [
                {"step": 1, "action": "isolate_variable", "description": "Isolate the variable term"},
                {"step": 2, "action": "solve_for_variable", "description": "Solve for the variable"},
                {"step": 3, "action": "verify_solution", "description": "Verify the solution"}
            ],
            "current_step_index": 0,
            "total_steps": 3,
            "alternative_strategies": [
                {"strategy": "graphical_method", "complexity": "medium", "applicability": "visualization"},
                {"strategy": "numerical_approximation", "complexity": "low", "applicability": "approximate solutions"}
            ],
            "complexity_estimate": "low",
            "planning_messages": [
                HumanMessage(content="Plan solution for linear equation"),
                AIMessage(content="Strategy: Standard algebraic manipulation")
            ],
            "planning_iterations": state.get("planning_result", {}).get("planning_iterations", 0) + 1
        }
    else:
        # Default planning for other problem types
        planning_result: PlanningState = {
            "solution_strategy": "general_solution",
            "roadmap": [
                {"step": 1, "action": "analyze_problem", "description": "Analyze problem structure"},
                {"step": 2, "action": "apply_appropriate_method", "description": "Apply suitable mathematical method"},
                {"step": 3, "action": "verify_result", "description": "Verify the solution"}
            ],
            "current_step_index": 0,
            "total_steps": 3,
            "alternative_strategies": [],
            "complexity_estimate": "medium",
            "planning_messages": [],
            "planning_iterations": 1
        }
    
    return {
        **state,
        "planning_result": planning_result,
        "current_agent": "planning",
        "execution_status": ExecutionStatus.COMPLETED,
        "planning_messages": [
            *state.get("planning_messages", []),
            HumanMessage(content=f"Planning completed for {problem_type} problem")
        ]
    }
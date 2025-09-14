"""
Execution agent implementation.
Performs mathematical computations and executes solution steps.
"""

from src.state import MathProblemState, ExecutionStatus, ExecutionState
from langchain_core.messages import HumanMessage, AIMessage


def execution_agent(state: MathProblemState) -> MathProblemState:
    """
    Execution agent - performs mathematical computations.
    
    This agent performs:
    - Mathematical operation execution
    - Tool calling (SymPy, Wolfram Alpha, etc.)
    - Step-by-step derivation
    - Intermediate result storage
    
    Args:
        state: Current math problem state
        
    Returns:
        Updated state with execution results
    """
    planning_data = state.get("planning_result", {})
    current_step_index = planning_data.get("current_step_index", 0)
    
    total_steps = planning_data.get("total_steps", 0)
    if current_step_index >= total_steps:
        # All steps completed
        return {
            **state,
            "current_agent": "execution",
            "execution_status": ExecutionStatus.COMPLETED
        }
    
    roadmap = planning_data.get("roadmap", [])
    current_step = roadmap[current_step_index] if current_step_index < len(roadmap) else {"action": "unknown", "description": "Unknown step"}
    
    # TODO: Implement actual execution logic using math tools
    # Mock execution based on step type
    if current_step["action"] == "isolate_variable":
        execution_result: ExecutionState = {
            "current_step": current_step,
            "intermediate_results": [{"step": 1, "result": "2x = 4", "explanation": "Subtracted 3 from both sides: 2x + 3 - 3 = 7 - 3"}],
            "tools_used": ["basic_arithmetic"],
            "derivation_process": "2x + 3 = 7 → 2x + 3 - 3 = 7 - 3 → 2x = 4",
            "step_status": ExecutionStatus.COMPLETED,
            "execution_messages": [
                HumanMessage(content="Execute: isolate variable term"),
                AIMessage(content="Executed: 2x + 3 - 3 = 7 - 3 → 2x = 4")
            ],
            "execution_iterations": state.get("execution_result", {}).get("execution_iterations", 0) + 1
        }
    elif current_step["action"] == "solve_for_variable":
        execution_result: ExecutionState = {
            "current_step": current_step,
            "intermediate_results": [{"step": 2, "result": "x = 2", "explanation": "Divided both sides by 2: 2x/2 = 4/2"}],
            "tools_used": ["basic_arithmetic"],
            "derivation_process": "2x = 4 → 2x/2 = 4/2 → x = 2",
            "step_status": ExecutionStatus.COMPLETED,
            "execution_messages": [
                HumanMessage(content="Execute: solve for variable"),
                AIMessage(content="Executed: 2x/2 = 4/2 → x = 2")
            ],
            "execution_iterations": state.get("execution_result", {}).get("execution_iterations", 0) + 1
        }
    else:
        # Default execution
        execution_result: ExecutionState = {
            "current_step": current_step,
            "intermediate_results": [{"step": current_step_index + 1, "result": "step_completed", "explanation": "Step executed successfully"}],
            "tools_used": ["general_math"],
            "derivation_process": "Step execution completed",
            "step_status": ExecutionStatus.COMPLETED,
            "execution_messages": [],
            "execution_iterations": 1
        }
    
    # Update planning state to move to next step
    planning_result = {
        **planning_data,
        "current_step_index": current_step_index + 1
    }
    
    return {
        **state,
        "execution_result": execution_result,
        "planning_result": planning_result,
        "current_agent": "execution",
        "execution_status": ExecutionStatus.COMPLETED,
        "execution_messages": [
            *state.get("execution_messages", []),
            HumanMessage(content=f"Executed step {current_step_index + 1}: {current_step['action']}")
        ]
    }
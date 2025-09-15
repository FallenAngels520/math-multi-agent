"""
Coordinator agent implementation.
Manages the overall problem solving workflow and directs traffic between agents.
"""

from langgraph.types import Command
from src.state import MathProblemState, ExecutionStatus
from src.configuration import Configuration


def coordinator_agent(state: MathProblemState) -> Command:
    """
    Coordinator agent that manages the overall problem solving workflow.
    
    This agent acts as the central dispatcher, determining which agent
    should handle the problem based on the current state.
    
    Args:
        state: Current math problem state
        
    Returns:
        Command directing to the next appropriate agent
    """
    # Track total iterations
    state["total_iterations"] += 1

    # Handle explicit retry semantics first
    if state["execution_status"] == ExecutionStatus.NEEDS_RETRY:
        # Return to the current agent to retry its logic
        current = state.get("current_agent")
        if current == "comprehension":
            return Command(goto="comprehension_agent")
        if current == "planning":
            return Command(goto="planning_agent")
        if current == "execution":
            return Command(goto="execution_agent")
        if current == "verification":
            return Command(goto="verification_agent")
        # Unknown current agent → start over
        return Command(goto="comprehension_agent")
    
    # Initial state - start with comprehension
    if state["execution_status"] == ExecutionStatus.PENDING:
        return Command(goto="comprehension_agent")
    
    # After comprehension, move to planning
    elif state["current_agent"] == "comprehension":
        return Command(goto="planning_agent")
    
    # After planning, move to execution
    elif state["current_agent"] == "planning":
        return Command(goto="execution_agent")
    
    # After execution, move to verification
    elif state["current_agent"] == "execution":
        return Command(goto="verification_agent")
    
    # After verification, check if we need to retry or complete
    elif state["current_agent"] == "verification":
        if state.get("verification_result") and state["verification_result"].get("is_valid"):
            return Command(goto="__end__")
        else:
            config = Configuration()
            current_iters = int(state.get("verification_iterations", 0) or 0)
            current_iters += 1
            state["verification_iterations"] = current_iters
            if current_iters > config.verification_max_retries:
                # 超过上限：直接结束
                return Command(goto="__end__", update={
                    "error_message": {
                        "type": "override",
                        "value": f"Verification failed more than {config.verification_max_retries} times. Stopping."
                    }
                })
            # 未超上限：回到 planning 重规划
            return Command(goto="planning_agent")
    
    # Handle error states
    elif state["execution_status"] == ExecutionStatus.FAILED:
        # Try to recover by going back to planning
        return Command(goto="planning_agent")
    
    # Default fallback - start over
    return Command(goto="comprehension_agent")
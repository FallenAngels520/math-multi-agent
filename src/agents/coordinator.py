"""
Coordinator agent implementation.
Manages the overall problem solving workflow and directs traffic between agents.
"""

from langgraph.types import Command
from src.state import MathProblemState, ExecutionStatus


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
            # Retry from planning if verification failed
            return Command(goto="planning_agent")
    
    # Handle error states
    elif state["execution_status"] == ExecutionStatus.FAILED:
        # Try to recover by going back to planning
        return Command(goto="planning_agent")
    
    # Default fallback - start over
    return Command(goto="comprehension_agent")
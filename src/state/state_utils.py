"""
Utility functions for state management and transitions.
"""

from . import (
    MathProblemState, 
    ExecutionStatus, 
    ComprehensionState, 
    PlanningState, 
    ExecutionState, 
    VerificationState,
    MathInputState
)


def initialize_state(user_input: str) -> MathProblemState:
    """
    Initialize a new MathProblemState with default values.
    
    Args:
        user_input: The original math problem text from user
        
    Returns:
        Initialized MathProblemState ready for processing
    """
    return {
        "user_input": user_input,
        "final_answer": None,
        "solution_steps": [],
        "assumptions": [],
        "expressions": [],
        "sympy_objects": {},
        "proof_steps": [],
        "counter_examples": [],
        "current_agent": "coordinator",
        "execution_status": ExecutionStatus.PENDING,
        "error_message": None,
        "total_iterations": 0,
        "comprehension_result": None,
        "planning_result": None,
        "execution_result": None,
        "verification_result": None,
        "coordinator_messages": [],
        "comprehension_messages": [],
        "planning_messages": [],
        "execution_messages": [],
        "verification_messages": [],
        "messages": []  # Inherited from MessagesState
    }


def update_comprehension_state(
    state: MathProblemState, 
    result: ComprehensionState
) -> MathProblemState:
    """
    Update state with comprehension agent results and transition to planning.
    """
    return {
        **state,
        "comprehension_result": result,
        "current_agent": "planning",
        "execution_status": ExecutionStatus.IN_PROGRESS
    }


def update_planning_state(
    state: MathProblemState, 
    result: PlanningState
) -> MathProblemState:
    """
    Update state with planning agent results and transition to execution.
    """
    return {
        **state,
        "planning_result": result,
        "current_agent": "execution",
        "execution_status": ExecutionStatus.IN_PROGRESS
    }


def update_execution_state(
    state: MathProblemState, 
    result: ExecutionState
) -> MathProblemState:
    """
    Update state with execution agent results and transition to verification.
    """
    return {
        **state,
        "execution_result": result,
        "current_agent": "verification",
        "execution_status": ExecutionStatus.IN_PROGRESS
    }


def update_verification_state(
    state: MathProblemState, 
    result: VerificationState
) -> MathProblemState:
    """
    Update state with verification agent results.
    """
    return {
        **state,
        "verification_result": result,
        "execution_status": ExecutionStatus.COMPLETED
    }


def add_solution_step(state: MathProblemState, step: str) -> MathProblemState:
    """
    Add a solution step to the state's solution_steps list.
    """
    return {
        **state,
        "solution_steps": [*state["solution_steps"], step]
    }


def set_final_answer(state: MathProblemState, answer: str) -> MathProblemState:
    """
    Set the final answer in the state.
    """
    return {
        **state,
        "final_answer": answer
    }


def set_error_state(state: MathProblemState, error_message: str) -> MathProblemState:
    """
    Set error state with appropriate error message.
    """
    return {
        **state,
        "execution_status": ExecutionStatus.FAILED,
        "error_message": error_message
    }
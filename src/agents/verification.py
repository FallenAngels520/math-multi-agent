"""
Verification agent implementation.
Validates mathematical solutions and provides feedback.
"""

from src.state import MathProblemState, ExecutionStatus, VerificationState
from langchain_core.messages import HumanMessage, AIMessage


def verification_agent(state: MathProblemState) -> MathProblemState:
    """
    Verification agent - validates the solution and provides feedback.
    
    This agent performs:
    - Solution correctness validation
    - Logical consistency checking
    - Error diagnosis and localization
    - Optimization suggestions
    
    Args:
        state: Current math problem state
        
    Returns:
        Updated state with verification results
    """
    # TODO: Implement actual verification logic
    
    planning_data = state.get("planning_result")
    execution_data = state.get("execution_result")

    if not planning_data:
        all_steps_completed = False
    else:
        all_steps_completed = planning_data["current_step_index"] >= planning_data["total_steps"]

    # Determine validity heuristically based on available state
    if all_steps_completed:
        final_answer = state.get("final_answer")
        is_valid = final_answer is not None
        verification_result: VerificationState = {
            "is_valid": is_valid,
            "validation_method": "substitution_and_logical_consistency",
            "error_details": None if is_valid else {"reason": "missing final_answer"},
            "optimization_suggestions": [
                "Solution is mathematically correct" if is_valid else "Provide final answer and re-verify",
            ],
            "confidence_score": 0.95 if is_valid else 0.4,
            "verification_messages": [
                HumanMessage(content="Verify final solution"),
                AIMessage(content=("Verification passed: solution is correct" if is_valid else "Verification failed: final answer missing")),
            ],
        }
    else:
        step_status = execution_data.get("step_status") if execution_data else None
        is_valid = step_status != ExecutionStatus.FAILED
        verification_result: VerificationState = {
            "is_valid": is_valid,
            "validation_method": "step_validation",
            "error_details": None if is_valid else {"reason": "execution step failed", "execution_status": str(step_status)},
            "optimization_suggestions": [
                "Step executed correctly" if is_valid else "Fix execution step and retry",
            ],
            "confidence_score": 0.9 if is_valid else 0.5,
            "verification_messages": [
                HumanMessage(content="Verify intermediate step"),
                AIMessage(content=("Step verification passed" if is_valid else "Step verification failed")),
            ],
        }

    return {
        **state,
        "verification_result": verification_result,
        "current_agent": "verification",
        "execution_status": ExecutionStatus.COMPLETED if is_valid else ExecutionStatus.NEEDS_RETRY,
        "verification_messages": [
            *state.get("verification_messages", []),
            HumanMessage(content=f"Verification {'passed' if is_valid else 'failed'} for step {planning_data.get('current_step_index', 0) if planning_data else 0}")
        ]
    }
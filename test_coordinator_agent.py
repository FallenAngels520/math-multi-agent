import pprint
from typing import Any, Dict

from langgraph.types import Command

from src.agents.coordinator import coordinator_agent
from src.state import MathProblemState, ExecutionStatus


def command_to_dict(cmd: Command) -> Dict[str, Any]:
    # Try common serialization methods first
    for method in ("model_dump", "dict"):
        if hasattr(cmd, method):
            try:
                return getattr(cmd, method)()  # type: ignore[misc]
            except Exception:
                pass
    # Fallback to extracting common attributes
    data: Dict[str, Any] = {}
    for key in ("goto", "update", "resume"):
        if hasattr(cmd, key):
            data[key] = getattr(cmd, key)
    if not data:
        data["repr"] = repr(cmd)
    return data


def build_initial_state(user_input: str = "Solve 1+1") -> MathProblemState:
    state: MathProblemState = {
        # I/O
        "user_input": user_input,
        "final_answer": None,
        "solution_steps": [],
        # Shared math fields
        "assumptions": [],
        "expressions": [],
        "sympy_objects": {},
        "proof_steps": [],
        "counter_examples": [],
        # Flow control
        "current_agent": "",
        "execution_status": ExecutionStatus.PENDING,
        "error_message": None,
        "total_iterations": 0,
        "verification_iterations": 0,
        # Sub-states
        "comprehension_result": None,
        "planning_result": None,
        "execution_result": None,
        "verification_result": None,
        # Message tracks
        "coordinator_messages": [],
        "comprehension_messages": [],
        "planning_messages": [],
        "execution_messages": [],
        "verification_messages": [],
    }
    return state


def run_happy_path() -> None:
    print("=== Happy Path ===")
    state = build_initial_state()

    # 1) Initial → comprehension
    cmd = coordinator_agent(state)
    print("Step 1 (initial):", pprint.pformat(command_to_dict(cmd)))

    # 2) After comprehension → planning
    state["current_agent"] = "comprehension"
    state["execution_status"] = ExecutionStatus.IN_PROGRESS
    cmd = coordinator_agent(state)
    print("Step 2 (post-comprehension):", pprint.pformat(command_to_dict(cmd)))

    # 3) After planning → execution
    state["current_agent"] = "planning"
    cmd = coordinator_agent(state)
    print("Step 3 (post-planning):", pprint.pformat(command_to_dict(cmd)))

    # 4) After execution → verification
    state["current_agent"] = "execution"
    cmd = coordinator_agent(state)
    print("Step 4 (post-execution):", pprint.pformat(command_to_dict(cmd)))

    # 5) Verification valid → end
    state["current_agent"] = "verification"
    state["verification_result"] = {"is_valid": True}
    cmd = coordinator_agent(state)
    print("Step 5 (verification valid):", pprint.pformat(command_to_dict(cmd)))


def run_retry_path() -> None:
    print("\n=== Retry Path (verification invalid once) ===")
    state = build_initial_state()

    # Drive state to verification
    coordinator_agent(state)  # initial → comp
    state["current_agent"] = "comprehension"
    state["execution_status"] = ExecutionStatus.IN_PROGRESS
    coordinator_agent(state)  # comp → planning
    state["current_agent"] = "planning"
    coordinator_agent(state)  # planning → execution
    state["current_agent"] = "execution"
    coordinator_agent(state)  # execution → verification

    # Now in verification with invalid result → planning (retry)
    state["current_agent"] = "verification"
    state["verification_result"] = {"is_valid": False}
    cmd = coordinator_agent(state)
    print("Retry Step (verification invalid):", pprint.pformat(command_to_dict(cmd)))


if __name__ == "__main__":
    run_happy_path()
    run_retry_path() 
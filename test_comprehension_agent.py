import os
import pprint
from typing import Any, Dict, List

from src.agents.comprehension import comprehension_agent
from src.state import MathProblemState, ExecutionStatus, ProblemType


def build_initial_state(user_input: str) -> MathProblemState:
    return {
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
        # Messages
        "coordinator_messages": [],
        "comprehension_messages": [],
        "planning_messages": [],
        "execution_messages": [],
        "verification_messages": [],
    }


def check_structure(result_state: MathProblemState) -> List[str]:
    problems: List[str] = []
    # Execution status should be set
    if result_state.get("current_agent") != "comprehension":
        problems.append("current_agent should be 'comprehension'")
    status = result_state.get("execution_status")
    if status not in (ExecutionStatus.COMPLETED, ExecutionStatus.FAILED):
        problems.append("execution_status should be COMPLETED or FAILED")

    comp = result_state.get("comprehension_result") or {}
    # Required keys
    required_keys = [
        "problem_type",
        "known_conditions",
        "unknown_variables",
        "constraints",
        "hidden_conditions",
        "potential_pitfalls",
        "structured_input",
        "comprehension_messages",
    ]
    for k in required_keys:
        if k not in comp:
            problems.append(f"missing key in comprehension_result: {k}")

    # Types
    if comp:
        if not isinstance(comp.get("known_conditions"), dict):
            problems.append("known_conditions should be dict")
        if not isinstance(comp.get("unknown_variables"), list):
            problems.append("unknown_variables should be list")
        if not isinstance(comp.get("constraints"), list):
            problems.append("constraints should be list")
        if not isinstance(comp.get("hidden_conditions"), list):
            problems.append("hidden_conditions should be list")
        if not isinstance(comp.get("potential_pitfalls"), list):
            problems.append("potential_pitfalls should be list")
        if not isinstance(comp.get("structured_input"), dict):
            problems.append("structured_input should be dict")
        if comp.get("problem_type") not in list(ProblemType):
            problems.append("problem_type should be a ProblemType enum value")

    return problems


def run_case(user_input: str) -> None:
    print("\n=== Case ===")
    print("Problem:", user_input)
    state = build_initial_state(user_input)

    result_state = comprehension_agent(state)

    print("Execution Status:", result_state.get("execution_status"))
    comp = result_state.get("comprehension_result") or {}
    key_view: Dict[str, Any] = {
        "problem_type": str(comp.get("problem_type")),
        "known_conditions": comp.get("known_conditions"),
        "unknown_variables": comp.get("unknown_variables"),
        "constraints": comp.get("constraints"),
        "hidden_conditions": comp.get("hidden_conditions"),
        "potential_pitfalls": comp.get("potential_pitfalls"),
        "structured_input": comp.get("structured_input"),
    }
    print("Comprehension Result (key fields):")
    print(pprint.pformat(key_view))

    problems = check_structure(result_state)
    if problems:
        print("[STRUCTURE CHECK] Issues detected:")
        for p in problems:
            print(" -", p)
    else:
        print("[STRUCTURE CHECK] OK")


if __name__ == "__main__":
    run_case("2025年湖北高考数学使用的是全国新课标Ⅰ卷，最后一道题目如下：\n"
             "设\(m\)为正整数，数列\(\{a_n\}\)是公差不为\(0\)的等差数列，若从中删去两项\(a_i\)和\(a_j\)（\(1\leq i\lt j\leq 4m+2\)）后剩余的\(4m\)项可被平均分为\(m\)组，且每组的\(4\)个数都能构成等差数列，则称数列\(\{a_n\}\)是“\(m\) - 可分数列”。\n"
             "(1)写出所有的\(i,j\)，\(1\leq i\lt j\leq 6\)，使数列\(\{a_n\}\)是“\(1\) - 可分数列”；\n"
             "(2)当\(m \geq 3\)时，证明：数列\(\{a_n\}\)是“\(m\) - 可分数列”的充要条件是\(a_2 - a_1 = \frac{a_{4m+2}-a_1}{4m+1}\)；\n"
             "(3)从\(1,2,\cdots,4m+2\)中一次任取两个数\(i\)和\(j\)（\(1\leq i\lt j\leq 4m+2\)），记数列\(\{a_n\}\)是“\(m\) - 可分数列”的概率为\(P_m\)，证明：\(P_m \gt \frac{1}{2}\)。")
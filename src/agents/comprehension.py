"""
Comprehension agent implementation.
Analyzes and understands mathematical problems.
"""

from src.state import MathProblemState, ExecutionStatus, ComprehensionState, ProblemType
from langchain_core.messages import HumanMessage, AIMessage
from langchain_deepseek import ChatDeepSeek
import json
import re
from typing import Any, Dict, List
from src.prompts.prompt import build_comprehension_prompt
from src.configuration import Configuration


def comprehension_agent(state: MathProblemState, config: Configuration | None = None) -> MathProblemState:
    """
    Comprehension agent - analyzes and understands the math problem.
    
    This agent performs:
    - Semantic parsing of the problem text
    - Information extraction (known/unknown variables, constraints)
    - Problem type classification
    - Identification of hidden conditions and potential pitfalls
    
    Args:
        state: Current math problem state
        config: Runtime configuration (model name, temperature, retries)
        
    Returns:
        Updated state with comprehension results
    """
    user_input = state["user_input"]
    config = config or Configuration.from_runnable_config()

    messages = build_comprehension_prompt(user_input)

    ai_message_content = None
    parsed: Dict[str, Any] | None = None

    last_error: str | None = None
    for attempt in range(max(1, config.comprehension_max_retries)):
        try:
            llm = ChatDeepSeek(model=config.comprehension_model, api_key="sk-54deee4c49fe457cab2fed54fda391dd", api_base="https://api.deepseek.com")
            response = llm.invoke(messages)
            ai_message_content = getattr(response, "content", None) or ""

            # 尝试从响应中提取 JSON
            text = ai_message_content if isinstance(ai_message_content, str) else str(ai_message_content)
            # 提取第一个平衡的大括号 JSON 块（较稳健）
            match = re.search(r"\{[\s\S]*\}", text)
            json_str = match.group(0) if match else text
            parsed = json.loads(json_str)
            last_error = None
            break
        except Exception as e:
            last_error = str(e)
            parsed = None
            ai_message_content = ai_message_content or ""
            # 继续重试，直至用尽
            continue

    # 将 parsed 映射到 ComprehensionState，带默认值兜底
    def to_problem_type(value: Any) -> ProblemType:
        mapping = {
            "algebra": ProblemType.ALGEBRA,
            "geometry": ProblemType.GEOMETRY,
            "calculus": ProblemType.CALCULUS,
            "probability": ProblemType.PROBABILITY,
            "statistics": ProblemType.STATISTICS,
            "differential_equations": ProblemType.DIFFERENTIAL_EQUATIONS,
            "linear_algebra": ProblemType.LINEAR_ALGEBRA,
            "other": ProblemType.OTHER,
        }
        if isinstance(value, str):
            key = value.strip().lower()
            return mapping.get(key, ProblemType.OTHER)
        return ProblemType.OTHER

    def list_of_str(value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(v) for v in value]
        return []

    known_conditions: Dict[str, Any] = {}
    unknown_variables: List[str] = []
    constraints: List[str] = []
    hidden_conditions: List[str] = []
    potential_pitfalls: List[str] = []
    structured_input: Dict[str, Any] = {
        "type": "unknown",
        "original_text": user_input,
        "normalized_form": user_input,
    }
    problem_type: ProblemType = ProblemType.OTHER

    if isinstance(parsed, dict):
        problem_type = to_problem_type(parsed.get("problem_type"))
        kc = parsed.get("known_conditions")
        if isinstance(kc, dict):
            known_conditions = kc
        unknown_variables = list_of_str(parsed.get("unknown_variables"))
        constraints = list_of_str(parsed.get("constraints"))
        hidden_conditions = list_of_str(parsed.get("hidden_conditions"))
        potential_pitfalls = list_of_str(parsed.get("potential_pitfalls"))
        si = parsed.get("structured_input")
        if isinstance(si, dict):
            structured_input.update({
                k: v for k, v in si.items() if k in {"type", "original_text", "normalized_form"}
            })

    # 若模型未能识别，则提供保守兜底（尽量不影响后续节点）
    if not unknown_variables and "x" in user_input:
        unknown_variables = ["x"]
    if not known_conditions:
        known_conditions = {"text": user_input}

    # 组合 ComprehensionState
    comprehension_result: ComprehensionState = {
        "problem_type": problem_type,
        "known_conditions": known_conditions,
        "unknown_variables": unknown_variables,
        "constraints": constraints,
        "hidden_conditions": hidden_conditions,
        "potential_pitfalls": potential_pitfalls,
        "structured_input": structured_input,
        "comprehension_messages": messages + [
            AIMessage(content=(ai_message_content or "模型未返回内容"))
        ],
    }

    # 失败回退策略：若多次调用仍失败（parsed is None 且无关键字段），标记 FAILED 并写入错误
    failed = (parsed is None) and (not known_conditions) and (not unknown_variables)

    return {
        **state,
        "comprehension_result": comprehension_result,
        "current_agent": "comprehension",
        "execution_status": ExecutionStatus.FAILED if failed else ExecutionStatus.COMPLETED,
        "error_message": last_error if failed else state.get("error_message"),
        "comprehension_messages": [
            *state.get("comprehension_messages", []),
            HumanMessage(content=f"Comprehension {'failed' if failed else 'completed'} for: {user_input}")
        ]
    }
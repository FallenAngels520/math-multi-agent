"""
Comprehension agent implementation.
Analyzes and understands mathematical problems with structured output.
"""

from src.state import MathProblemState, ExecutionStatus, ComprehensionState, ProblemType, ComprehensionAnalysis
from langchain_core.messages import HumanMessage, AIMessage
from langchain_deepseek import ChatDeepSeek
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
import json
import re
from typing import Any, Dict, List
from src.configuration import Configuration


def comprehension_agent(state: MathProblemState, config: Configuration | None = None) -> MathProblemState:
    """
    Comprehension agent - analyzes and understands the math problem with structured output.
    
    This agent performs comprehensive analysis using the three-phase framework:
    - Phase 1: Problem surface deconstruction (givens, objectives, constraints)
    - Phase 2: Core principles tracing (primary field, fundamental principles)
    - Phase 3: Strategy path building (deduction, breakthroughs, risks)
    
    Args:
        state: Current math problem state
        config: Runtime configuration (model name, temperature, retries)
        
    Returns:
        Updated state with structured comprehension results
    """
    user_input = state["user_input"]
    config = config or Configuration.from_runnable_config()

    ai_message_content = None
    structured_output: Dict[str, Any] | None = None
    last_error: str | None = None

    # Create structured output chain with LangChain
    parser = JsonOutputParser(pydantic_object=ComprehensionAnalysis)
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", COMPREHENSION_SYSTEM_CN),
        ("human", "请分析以下数学问题：{user_input}")
    ])
    
    chain = prompt_template | ChatDeepSeek(
        model=config.comprehension_model, 
        api_key="sk-54deee4c49fe457cab2fed54fda391dd", 
        api_base="https://api.deepseek.com"
    ) | parser

    for attempt in range(max(1, config.comprehension_max_retries)):
        try:
            # Get structured output using LangChain's structured output capabilities
            structured_output = chain.invoke({"user_input": user_input})
            ai_message_content = f"Structured analysis completed for: {user_input}"
            last_error = None
            break
        except Exception as e:
            last_error = str(e)
            structured_output = None
            # Fallback to traditional parsing if structured output fails
            try:
                llm = ChatDeepSeek(model=config.comprehension_model, api_key="sk-54deee4c49fe457cab2fed54fda391dd", api_base="https://api.deepseek.com")
                response = llm.invoke(COMPREHENSION_SYSTEM_CN.format(user_input=user_input))
                ai_message_content = getattr(response, "content", None) or ""
                
                # Extract JSON from response text
                text = ai_message_content if isinstance(ai_message_content, str) else str(ai_message_content)
                match = re.search(r"\{[\s\S]*\}", text)
                if match:
                    json_str = match.group(0)
                    structured_output = json.loads(json_str)
                    last_error = None
                    break
            except Exception as fallback_error:
                last_error = f"Primary: {e}, Fallback: {fallback_error}"
                continue

    # Helper functions for type conversion
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

    def dict_of_any(value: Any) -> Dict[str, Any]:
        if isinstance(value, dict):
            return value
        return {}

    # Extract data from structured output with fallbacks
    problem_type = to_problem_type(structured_output.get("problem_type", "") if structured_output else "")
    
    # Phase 1: Problem surface deconstruction
    givens = list_of_str(structured_output.get("givens", [])) if structured_output else []
    objectives = list_of_str(structured_output.get("objectives", [])) if structured_output else []
    explicit_constraints = list_of_str(structured_output.get("explicit_constraints", [])) if structured_output else []
    
    # Phase 2: Core principles tracing
    primary_field = str(structured_output.get("primary_field", "")) if structured_output else ""
    fundamental_principles = list_of_str(structured_output.get("fundamental_principles", [])) if structured_output else []
    
    # Phase 3: Strategy path building
    strategy_deduction = str(structured_output.get("strategy_deduction", "")) if structured_output else ""
    key_breakthroughs = list_of_str(structured_output.get("key_breakthroughs", [])) if structured_output else []
    potential_risks = list_of_str(structured_output.get("potential_risks", [])) if structured_output else []
    
    # Legacy fields for backward compatibility
    known_conditions = dict_of_any(structured_output.get("known_conditions", {})) if structured_output else {}
    unknown_variables = list_of_str(structured_output.get("unknown_variables", [])) if structured_output else []
    constraints = list_of_str(structured_output.get("constraints", [])) if structured_output else []
    hidden_conditions = list_of_str(structured_output.get("hidden_conditions", [])) if structured_output else []
    potential_pitfalls = list_of_str(structured_output.get("potential_pitfalls", [])) if structured_output else []
    
    structured_input = {
        "type": "math_problem",
        "original_text": user_input,
        "normalized_form": user_input,
        "analysis_available": structured_output is not None
    }

    # Fallback logic for empty results
    if not givens and user_input:
        givens = [f"原始问题: {user_input}"]
    if not objectives and user_input:
        objectives = ["解析数学问题并找到解决方案"]
    if not primary_field:
        primary_field = "数学"

    # Build comprehensive comprehension state
    comprehension_result: ComprehensionState = {
        # Phase 1: Problem surface deconstruction
        "givens": givens,
        "objectives": objectives,
        "explicit_constraints": explicit_constraints,
        
        # Phase 2: Core principles tracing
        "primary_field": primary_field,
        "fundamental_principles": fundamental_principles,
        
        # Phase 3: Strategy path building
        "strategy_deduction": strategy_deduction,
        "key_breakthroughs": key_breakthroughs,
        "potential_risks": potential_risks,
        
        # Metadata and legacy fields
        "problem_type": problem_type,
        "known_conditions": known_conditions,
        "unknown_variables": unknown_variables,
        "constraints": constraints,
        "hidden_conditions": hidden_conditions,
        "potential_pitfalls": potential_pitfalls,
        "structured_input": structured_input,
        "comprehension_messages": [
            AIMessage(content=ai_message_content or "Comprehension analysis completed")
        ],
    }

    # Determine execution status
    failed = structured_output is None and not any([givens, objectives, explicit_constraints])

    return {
        **state,
        "comprehension_result": comprehension_result,
        "current_agent": "comprehension",
        "execution_status": ExecutionStatus.FAILED if failed else ExecutionStatus.COMPLETED,
        "error_message": last_error if failed else state.get("error_message"),
        "comprehension_messages": [
            *state.get("comprehension_messages", []),
            HumanMessage(content=f"Comprehension {'failed' if failed else 'completed'} with structured output")
        ]
    }
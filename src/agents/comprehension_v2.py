"""
Comprehension Agent V2 - 基于新版State设计的题目理解智能体
"""

import json
import re
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, AIMessage
from langchain_deepseek import ChatDeepSeek
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.prompts.prompt import COMPREHENSION_PROMPT
from src.state import (
    MathProblemStateV2, 
    ComprehensionStateV2,
    ProblemTypeV2,
    ExecutionStatusV2,
    LaTeXNormalization,
    ProblemSurfaceDeconstruction,
    CorePrinciplesTracing,
    StrategicPathBuilding,
    ComprehensionAnalysis,
    create_initial_state,
    get_current_phase,
    should_retry_phase
)
from src.configuration import Configuration


class ComprehensionAgentV2:
    """基于新版State设计的题目理解智能体"""
    
    def __init__(self, config: Configuration | None = None):
        self.config = config or Configuration.from_runnable_config()
        
    def analyze_problem(self, state: MathProblemStateV2) -> MathProblemStateV2:
        """
        分析数学问题 - 基于新版State设计
        
        遵循提示词的三阶段分析框架：
        1. LaTeX标准化预处理
        2. 问题表象解构
        3. 核心原理溯源  
        4. 策略路径构建
        """
        user_input = state["user_input"]
        
        # 检查重试条件
        current_phase = get_current_phase(state)
        if current_phase != "comprehension":
            return self._handle_wrong_phase(state)
            
        if not should_retry_phase(state, "comprehension"):
            return self._handle_max_retries(state)
        
        # 创建结构化输出链
        parser = JsonOutputParser(pydantic_object=ComprehensionAnalysis)
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", COMPREHENSION_PROMPT),
            ("human", "请分析以下数学问题：{user_input}")
        ])
        
        chain = prompt_template | ChatDeepSeek(
            model=self.config.comprehension_model,
            api_key="sk-54deee4c49fe457cab2fed54fda391dd",
            api_base="https://api.deepseek.com"
        ) | parser
        
        # 执行分析
        structured_output, error_details = self._execute_analysis(chain, user_input)
        
        # 构建新版状态
        return self._build_comprehension_state(state, structured_output, error_details)
    
    def _execute_analysis(self, chain, user_input: str) -> tuple[Dict[str, Any] | None, Dict[str, Any] | None]:
        """执行分析逻辑"""
        structured_output = None
        error_details = None
        
        for attempt in range(max(1, self.config.comprehension_max_retries)):
            try:
                structured_output = chain.invoke({"user_input": user_input})
                error_details = None
                break
            except Exception as e:
                error_details = {
                    "attempt": attempt + 1,
                    "exception": str(e),
                    "exception_type": type(e).__name__
                }
                
                # 备用解析逻辑
                try:
                    llm = ChatDeepSeek(
                        model=self.config.comprehension_model,
                        api_key="sk-54deee4c49fe457cab2fed54fda391dd",
                        api_base="https://api.deepseek.com"
                    )
                    response = llm.invoke(COMPREHENSION_PROMPT.format(user_input=user_input))
                    ai_message_content = getattr(response, "content", None) or ""
                    
                    # 从响应文本提取JSON
                    text = ai_message_content if isinstance(ai_message_content, str) else str(ai_message_content)
                    match = re.search(r"\{[\s\S]*\}", text)
                    if match:
                        json_str = match.group(0)
                        structured_output = json.loads(json_str)
                        error_details = None
                        break
                except Exception as fallback_error:
                    error_details["fallback_error"] = str(fallback_error)
                    continue
        
        return structured_output, error_details
    
    def _build_comprehension_state(self, state: MathProblemStateV2, 
                                 structured_output: Dict[str, Any] | None,
                                 error_details: Dict[str, Any] | None) -> MathProblemStateV2:
        """构建新版理解状态"""
        
        # 类型转换辅助函数
        def to_problem_type(value: Any) -> ProblemTypeV2:
            mapping = {
                "algebra": ProblemTypeV2.ALGEBRA,
                "geometry": ProblemTypeV2.GEOMETRY,
                "calculus": ProblemTypeV2.CALCULUS,
                "probability": ProblemTypeV2.PROBABILITY,
                "statistics": ProblemTypeV2.STATISTICS,
                "differential_equations": ProblemTypeV2.DIFFERENTIAL_EQUATIONS,
                "linear_algebra": ProblemTypeV2.LINEAR_ALGEBRA,
                "other": ProblemTypeV2.OTHER,
            }
            if isinstance(value, str):
                key = value.strip().lower()
                return mapping.get(key, ProblemTypeV2.OTHER)
            return ProblemTypeV2.OTHER
        
        def list_of_str(value: Any) -> List[str]:
            if isinstance(value, list):
                return [str(v) for v in value]
            return []
        
        def dict_of_any(value: Any) -> Dict[str, Any]:
            if isinstance(value, dict):
                return value
            return {}
        
        # 提取数据（带回退逻辑）
        user_input = state["user_input"]
        
        if structured_output:
            # 从结构化输出提取数据
            problem_type = to_problem_type(structured_output.get("problem_type", ""))
            
            # LaTeX标准化
            latex_norm = LaTeXNormalization(
                original_text=user_input,
                normalized_latex=structured_output.get("normalized_latex", user_input),
                preprocessing_notes=["自动标准化完成"]
            )
            
            # 问题表象解构
            surface_decon = ProblemSurfaceDeconstruction(
                givens=list_of_str(structured_output.get("givens", [])),
                objectives=list_of_str(structured_output.get("objectives", [])),
                explicit_constraints=list_of_str(structured_output.get("explicit_constraints", []))
            )
            
            # 核心原理溯源
            principles_trace = CorePrinciplesTracing(
                primary_field=str(structured_output.get("primary_field", "")),
                fundamental_principles=list_of_str(structured_output.get("fundamental_principles", []))
            )
            
            # 策略路径构建
            path_build = StrategicPathBuilding(
                strategy_deduction=str(structured_output.get("strategy_deduction", "")),
                key_breakthroughs=list_of_str(structured_output.get("key_breakthroughs", [])),
                potential_risks=list_of_str(structured_output.get("potential_risks", []))
            )
            
        else:
            # 回退逻辑
            problem_type = ProblemTypeV2.OTHER
            
            latex_norm = LaTeXNormalization(
                original_text=user_input,
                normalized_latex=user_input,
                preprocessing_notes=["使用原始文本作为回退"]
            )
            
            surface_decon = ProblemSurfaceDeconstruction(
                givens=[f"原始问题: {user_input}"],
                objectives=["解析数学问题并找到解决方案"],
                explicit_constraints=[]
            )
            
            principles_trace = CorePrinciplesTracing(
                primary_field="数学",
                fundamental_principles=[]
            )
            
            path_build = StrategicPathBuilding(
                strategy_deduction="",
                key_breakthroughs=[],
                potential_risks=[]
            )
        
        # 构建理解状态
        comprehension_state: ComprehensionStateV2 = {
            "latex_normalization": latex_norm,
            "surface_deconstruction": surface_decon,
            "principles_tracing": principles_trace,
            "path_building": path_build,
            "problem_type": problem_type,
            "analysis_completed": structured_output is not None,
            "comprehension_messages": [
                AIMessage(content=f"Comprehension analysis {'completed' if structured_output else 'failed'}")
            ],
            "error_details": error_details,
            "retry_count": state.get("coordinator_state", {}).get("retry_counts", {}).get("comprehension", 0) + 1
        }
        
        # 更新协调器状态
        coordinator_state = state.get("coordinator_state", {})
        updated_coordinator = {
            **coordinator_state,
            "current_phase": "planning" if structured_output else "comprehension",
            "execution_status": ExecutionStatusV2.COMPLETED if structured_output else ExecutionStatusV2.FAILED,
            "retry_counts": {
                **coordinator_state.get("retry_counts", {}),
                "comprehension": comprehension_state["retry_count"]
            }
        }
        
        return {
            **state,
            "comprehension_state": comprehension_state,
            "coordinator_state": updated_coordinator
        }
    
    def _handle_wrong_phase(self, state: MathProblemStateV2) -> MathProblemStateV2:
        """处理错误的阶段调用"""
        coordinator_state = state.get("coordinator_state", {})
        
        return {
            **state,
            "coordinator_state": {
                **coordinator_state,
                "error_messages": [
                    *coordinator_state.get("error_messages", []),
                    f"Comprehension agent called in wrong phase: {get_current_phase(state)}"
                ]
            }
        }
    
    def _handle_max_retries(self, state: MathProblemStateV2) -> MathProblemStateV2:
        """处理达到最大重试次数"""
        coordinator_state = state.get("coordinator_state", {})
        
        return {
            **state,
            "coordinator_state": {
                **coordinator_state,
                "fatal_errors": [
                    *coordinator_state.get("fatal_errors", []),
                    "Comprehension phase exceeded maximum retry attempts"
                ],
                "execution_status": ExecutionStatusV2.FAILED
            }
        }


def comprehension_agent_v2(state: MathProblemStateV2) -> MathProblemStateV2:
    """
    Comprehension Agent V2 入口函数
    
    为LangGraph工作流设计的兼容接口
    """
    agent = ComprehensionAgentV2()
    return agent.analyze_problem(state)
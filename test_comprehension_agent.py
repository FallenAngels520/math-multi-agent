import os
import pprint
from typing import Any, Dict, List

from src.agents.comprehension import comprehension_agent
from src.state import MathProblemState, ExecutionStatus, ProblemType
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.prompts import COMPREHENSION_PROMPT, PREPROCESSING_PROMPT

def run_case(user_input: str) -> None:
    """运行测试用例，将纯文本转换为LaTeX格式并进行分析
    
    Args:
        user_input: 原始数学问题文本
    """
    # 保存原始输入的纯文本LaTeX版本
    with open("math_problem_plain_latex.tex", "w", encoding="utf-8") as f:
        f.write(user_input)
    print("\n=== Original LaTeX Text Saved to math_problem_plain_latex.tex ===")
    

    
    llm = ChatOpenAI(
        model_name='kimi-k2-0905-preview', 
        openai_api_key="sk-aPHvpw2rkczLhshnbH9W8FzImmHXp5d1CHLa90gh9Qr17ED1", 
        openai_api_base="https://api.moonshot.cn/v1",
        stream_usage=True
    )

#     # 首先将输入转换为LaTeX格式
#     latex_conversion_prompt = ChatPromptTemplate.from_messages([
#         ("system", """你是一位LaTeX格式转换专家。请将提供的数学问题文本转换为规范的LaTeX格式。
# 遵循以下规则：
# 1. 行内数学使用 \\( ... \\)，独立公式使用 \\[ ... \\] 或 equation 环境
# 2. 保留并规范题目结构与编号（如 (1)(2)(3) 等）
# 3. 正确转写与转义特殊符号
# 4. 输出仅包含转换后的LaTeX文本，不要添加任何解释或额外内容
# """),
#         ("human", "请将以下数学问题转换为LaTeX格式：{user_input}")
#     ])
    
#     # 转换为LaTeX格式
#     latex_chain = latex_conversion_prompt | llm
#     latex_result = latex_chain.invoke({"user_input": user_input})
#     print(latex_result)
    
    # 使用转换后的LaTeX格式进行分析
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", COMPREHENSION_PROMPT),
        ("human", "请分析以下数学问题：{user_input}")
    ])
    
    # 使用 chain 调用方式，确保格式化正确
    chain = prompt_template | llm
    result_state = chain.invoke({"user_input": user_input})

    print("\n=== Comprehension Analysis Results ===")
    print(result_state.content)

    # 使用planning prompt
    planning_prompt_template = ChatPromptTemplate.from_messages([
        ("system", PREPROCESSING_PROMPT),
        ("human", "请根据以下数学问题分析报告生成一个结构化的JSON格式的执行计划：{math_problem_analysis}")
    ])
    planning_chain = planning_prompt_template | llm
    planning_result = planning_chain.invoke({"math_problem_analysis": result_state.content})
    
    print("\n=== Comprehension Results ===")
    print(planning_result.content)


if __name__ == "__main__":
    run_case(r'设\(m\)为正整数，数列\(\{a_n\}\)是公差不为\(0\)的等差数列，若从中删去两项\(a_i\)和\(a_j\)（\(1\leq i\lt j\leq 4m+2\)）后剩余的\(4m\)项可被平均分为\(m\)组，且每组的\(4\)个数都能构成等差数列，则称数列\(\{a_n\}\)是“\(m\) - 可分数列”。(1)写出所有的\(i,j\)，\(1\leq i\lt j\leq 6\)，使数列\(\{a_n\}\)是“\(1\) - 可分数列”；(2)当\(m \geq 3\)时，证明：数列\(\{a_n\}\)是“\(m\) - 可分数列”的充要条件是\(a_2 - a_1 = \frac{a_{4m+2}-a_1}{4m+1}\)；(3)从\(1,2,\cdots,4m+2\)中一次任取两个数\(i\)和\(j\)（\(1\leq i\lt j\leq 4m+2\)），记数列\(\{a_n\}\)是“\(m\) - 可分数列”的概率为\(P_m\)，证明：\(P_m \gt \frac{1}{2}\)。')
# 提示词使用修复文档

## 🎯 发现的问题

用户发现：虽然在`src/prompts/prompt.py`中有精心设计的提示词，但在`src/agents/agents_refactored.py`中**没有充分使用它们**！

### 精心设计的提示词

| 提示词 | 用途 | 设计特点 |
|--------|------|---------|
| `COORDINATOR_PROMPT` | 协调管理智能体 | 详细的工作流程、迭代优化原则、安全协议 |
| `COMPREHENSION_PROMPT` | 题目理解智能体 | 三阶段分析框架、第一性原理、LaTeX标准化 |
| `PREPROCESSING_PROMPT` | 策略规划智能体 | 原子性、确定性、依赖管理、JSON结构 |
| `EXECUTION_PROMPT` | 计算执行智能体 | 工具选择策略、执行协议、Markdown报告格式 |
| `VERIFICATION_PROMPT` | 验证反思智能体 | 验证协议、约束检查、详细审查记录 |

---

## ❌ 修复前的问题

### 1. Coordinator Agent

**状态**: ✅ 已使用COORDINATOR_PROMPT

```python
# 89-258行：已经在使用
decision_prompt = f"""
{COORDINATOR_PROMPT}

{status_summary}
...
"""
```

✅ 这个是正确的！

### 2. Comprehension Agent

**状态**: ✅ 已使用COMPREHENSION_PROMPT

```python
# 288行：已经在使用
prompt = COMPREHENSION_PROMPT.format(user_input=state["user_input"])
```

✅ 这个也是正确的！

### 3. Planning Agent

**状态**: ✅ 已使用PREPROCESSING_PROMPT

```python
# 382行：已经在使用
prompt = PREPROCESSING_PROMPT.format(math_problem_analysis=analysis_summary)
```

✅ 这个也是正确的！

### 4. Execution Agent ❌ **核心问题**

**状态**: ❌ **没有使用EXECUTION_PROMPT**

**旧代码**（474-502行）：
```python
# ❌ 自己构建了简单的提示词，没有使用EXECUTION_PROMPT
tool_choice_prompt = f"""
任务描述：{task.description}
方法：{task.method}
参数：{task.params}

请选择最合适的工具并生成调用代码：
- sympy: 符号计算（代数、微积分、方程求解）
- wolfram_alpha: 复杂计算和数值计算
- internal_reasoning: 逻辑推理和格式化
"""
```

**问题**：
- 没有使用精心设计的EXECUTION_PROMPT
- 缺少详细的执行协议
- 缺少工具选择策略
- 缺少计算轨迹记录格式

### 5. Verification Agent ⚠️ **部分问题**

**状态**: ⚠️ **没有充分使用VERIFICATION_PROMPT**

**旧代码**（604-638行）：
```python
# ⚠️ 自己构建了验证提示词，没有使用VERIFICATION_PROMPT
verification_context = f"""
【原始问题】
{state.get('user_input')}

【题目理解结果】
{comprehension.model_dump_json(indent=2)}

请生成诊断报告，包含：
1. 评估状态（status）：PASSED, NEEDS_REVISION, FATAL_ERROR
...
"""

# ⚠️ 只使用了VERIFICATION_PROMPT的部分内容
messages = [
    SystemMessage(content=VERIFICATION_PROMPT.split("{")[0]),
    HumanMessage(content=verification_context)
]
```

**问题**：
- 只使用了`VERIFICATION_PROMPT.split("{")[0]`，没有完整使用
- 缺少详细的验证协议
- 缺少约束满足验证步骤

---

## ✅ 修复后的实现

### 1. Execution Agent（已修复）

**新代码**：
```python
def execution_agent(state: AgentState, config: Optional[Configuration] = None) -> AgentState:
    """
    使用prompt.py中精心设计的EXECUTION_PROMPT
    """
    
    # 如果有验证反馈，构建反馈上下文
    feedback_context = ""
    if verification_feedback and verification_feedback.suggestions:
        feedback_context = f"""

【验证反馈修正指导】
发现的问题：
{chr(10).join(f"- {issue.issue_type.value}: {issue.detail}" for issue in verification_feedback.issues)}

改进建议（必须遵循）：
{chr(10).join(f"- {sugg}" for sugg in verification_feedback.suggestions)}
        """
    
    # ✅ 使用精心设计的EXECUTION_PROMPT
    preprocessing_plan_json = planning_output.model_dump_json(indent=2)
    
    full_execution_prompt = EXECUTION_PROMPT.format(
        preprocessing_plan=preprocessing_plan_json
    ) + feedback_context
    
    messages = [
        SystemMessage(content="你是一位专家级的计算数学家，精通SymPy和Wolfram Alpha等计算工具。"),
        HumanMessage(content=full_execution_prompt)
    ]
    
    response = llm.invoke(messages)
```

**改进**：
- ✅ 完整使用`EXECUTION_PROMPT`
- ✅ 包含详细的执行协议（工具选择策略、计算轨迹等）
- ✅ 保留验证反馈的集成
- ✅ 使用精心设计的Markdown报告格式

### 2. Verification Agent（已修复）

**新代码**：
```python
def verification_agent(state: AgentState, config: Optional[Configuration] = None) -> AgentState:
    """
    使用prompt.py中精心设计的VERIFICATION_PROMPT
    """
    
    # 准备VERIFICATION_PROMPT所需的参数
    analysis_report_json = comprehension.model_dump_json(indent=2)
    executor_report_json = execution.model_dump_json(indent=2)
    
    # ✅ 使用精心设计的VERIFICATION_PROMPT
    full_verification_prompt = VERIFICATION_PROMPT.format(
        analysis_report=analysis_report_json,
        executor_report=executor_report_json
    )
    
    # 添加额外的上下文信息
    additional_context = f"""

【补充上下文】
原始问题：{state.get('user_input')}
执行计划：
{planning.model_dump_json(indent=2) if planning else "无"}

---

请严格按照上述验证协议生成结构化的诊断报告...
    """
    
    messages = [
        SystemMessage(content="你是一个专家级的数学问题验证专家，精通交叉验证和审计。"),
        HumanMessage(content=full_verification_prompt + additional_context)
    ]
```

**改进**：
- ✅ 完整使用`VERIFICATION_PROMPT`
- ✅ 包含详细的验证协议（一致性检查、逻辑链审计、约束满足验证）
- ✅ 使用精心设计的审查框架
- ✅ 保留补充上下文

---

## 📊 修复对比

| Agent | 修复前 | 修复后 |
|-------|-------|-------|
| **Coordinator** | ✅ 已使用 | ✅ 保持 |
| **Comprehension** | ✅ 已使用 | ✅ 保持 |
| **Planning** | ✅ 已使用 | ✅ 保持 |
| **Execution** | ❌ **未使用** | ✅ **已修复** |
| **Verification** | ⚠️ **部分使用** | ✅ **已修复** |

---

## 🎯 修复的价值

### 1. 更专业的提示词

精心设计的提示词包含：
- 详细的角色定义
- 明确的任务协议
- 结构化的输出格式
- 具体的执行步骤

### 2. 更好的LLM响应

使用专业提示词可以让LLM：
- 更准确地理解任务
- 生成更结构化的输出
- 遵循更严格的验证协议
- 产出更高质量的结果

### 3. 一致性

所有agent现在都使用统一风格的提示词：
- 统一的术语
- 统一的格式
- 统一的质量标准

---

## 📝 EXECUTION_PROMPT的设计亮点

```python
EXECUTION_PROMPT: str = """
你是一位专家级的计算数学家 (Computational Mathematician)...

核心任务:
接收一个由"规划者 Agent"生成的、严格格式化的JSON《执行计划 (Execution Plan)》...

可用工具集：
- SymPy (符号计算): 用于精确的代数运算、微积分、方程求解等
- Wolfram Alpha (全能计算引擎): 用于复杂的数值计算...
- 内部推理 (Internal Reasoning): 用于逻辑判断、格式化...

你必须严格遵循以下包含工具选择的协议：
1. 初始化工作区 (Initialize Workspace)
2. 迭代执行任务 (Iterate Through Tasks)
   a. 读取指令
   b. 策略性工具选择 (Strategic Tool Selection)
   c. 生成工具调用代码 (Generate Tool Call Code)
   d. 结果整合 (Integrate Result)

你的最终输出必须是一份详尽的、可供审计的Markdown报告。
"""
```

**特点**：
- 详细的工具选择策略
- 明确的执行协议
- 结构化的报告格式
- 可审计的计算轨迹

---

## 📝 VERIFICATION_PROMPT的设计亮点

```python
VERIFICATION_PROMPT: str = f"""
你是一个专家级的数学问题验证专家 (Mathematical Problem Verifier)...

核心任务:
接收两份输入文档：
- 原始的《数学问题溯源式分析报告》 (the "Source of Truth")
- 由"执行者 Agent"生成的《计算执行报告》 (the "Evidence")

验证协议 (Verification Protocol):
1. 一致性检查 (Consistency Check)
2. 逻辑链审计 (Logical Chain Audit)
3. 约束满足验证 (Constraint Satisfaction Verification)
4. 最终答案评估 (Final Answer Assessment)

你的输出必须是一份结构化的《验证报告》...
"""
```

**特点**：
- 四步验证协议
- 明确的审查标准
- 结构化的报告模板
- 非模棱两可的裁决

---

## ✅ 总结

通过这次修复，我们确保了：

1. ✅ **所有agent都使用精心设计的提示词**
2. ✅ **Execution Agent现在使用完整的EXECUTION_PROMPT**
3. ✅ **Verification Agent现在充分使用VERIFICATION_PROMPT**
4. ✅ **保持了验证反馈的集成能力**
5. ✅ **提升了整体系统的专业性和一致性**

---

**修复日期**: 2025-09-30  
**修复内容**: Execution和Verification Agent的提示词使用  
**状态**: ✅ 完成 
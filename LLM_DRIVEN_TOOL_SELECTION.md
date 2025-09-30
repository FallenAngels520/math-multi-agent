# LLM驱动的工具选择

## 🎯 核心问题

用户的洞察：**工具选择应该由大模型决策，而不是硬编码！**

### ❌ 之前的硬编码实现

```python
# ❌ 硬编码关键词匹配
if any(keyword in method_lower for keyword in [
    'solve', 'equation', 'differentiate', 'integrate'...
]):
    tool_type = ToolType.SYMPY  # 死板的规则
elif any(keyword in method_lower for keyword in [
    'wolfram', 'numerical', 'compute'...
]):
    tool_type = ToolType.WOLFRAM_ALPHA  # 死板的规则
else:
    tool_type = ToolType.INTERNAL_REASONING
```

**问题**：
- ❌ 简单的字符串匹配，不智能
- ❌ 无法处理边界情况（如"求解复杂方程"）
- ❌ 缺乏上下文理解
- ❌ 无法根据工作区状态调整
- ❌ 不符合"智能体"的理念

---

## ✅ 新的LLM驱动实现

### 1. 决策模型

```python
class ToolSelectionDecision(BaseModel):
    """
    工具选择决策（由LLM生成）
    
    让LLM智能决定使用哪个工具，而不是硬编码关键词匹配
    """
    tool_name: str = Field(
        description="选择的工具：sympy/wolfram_alpha/internal_reasoning"
    )
    reasoning: str = Field(
        description="选择理由：为什么这个工具最适合这个任务"
    )
    confidence: float = Field(
        description="选择的置信度（0-1之间）"
    )
```

### 2. LLM工具选择流程

```python
def _execute_tool_call(task, llm_response: str, workspace: dict, config: Optional[Configuration] = None):
    """
    ✅ 使用LLM智能决策工具选择
    """
    
    # 1. 准备工具选择提示词
    tool_selection_prompt = f"""
你是一个专业的工具选择专家。

【任务信息】
任务ID: {task.task_id}
任务描述: {task.description}
方法: {task.method}
参数: {task.params}

【可用工具】

1. **SymPy** (符号计算库)
   - 适用场景：代数、微积分、矩阵、微分方程...
   - 优势：精确的符号计算
   
2. **Wolfram Alpha** (计算知识引擎)
   - 适用场景：复杂数值计算、外部知识查询
   - 优势：强大的计算能力
   
3. **Internal Reasoning** (内部推理)
   - 适用场景：逻辑推理、格式化
   - 优势：快速，无外部调用

【工作区状态】
当前变量: {list(workspace.keys())}

请分析并选择最合适的工具。
    """
    
    # 2. 调用LLM做决策
    llm_with_structure = llm.with_structured_output(ToolSelectionDecision)
    decision = llm_with_structure.invoke(messages)
    
    # 3. 打印LLM的决策
    print(f"🤖 LLM工具选择: {decision.tool_name}")
    print(f"   理由: {decision.reasoning}")
    print(f"   置信度: {decision.confidence}")
    
    # 4. 根据LLM决策调用工具
    if decision.tool_name.lower() == "sympy":
        tool_result = _call_sympy_tool(task, workspace)
    elif decision.tool_name.lower() == "wolfram_alpha":
        tool_result = _call_wolfram_tool(task, workspace)
    else:
        tool_result = _call_internal_reasoning(task, workspace)
```

---

## 🎯 LLM的优势

### 1. 智能上下文理解

**示例任务**: "求解复杂三角方程 sin(x)^2 + cos(x)^2 = 1"

**硬编码**（关键词匹配）：
- 检测到"solve" → 选择SymPy ✅
- 但无法理解这是一个恒等式

**LLM决策**：
```json
{
  "tool_name": "internal_reasoning",
  "reasoning": "这是一个基本的三角恒等式 sin²(x) + cos²(x) = 1，
               对所有x都成立。不需要复杂计算，只需要输出恒等式的结论。",
  "confidence": 0.95
}
```

### 2. 考虑任务复杂度

**示例任务**: "计算 2 + 2"

**硬编码**：
- 检测到"calculate" → 选择Wolfram Alpha（浪费API调用）

**LLM决策**：
```json
{
  "tool_name": "internal_reasoning",
  "reasoning": "这是一个简单的加法运算，不需要调用外部工具。",
  "confidence": 1.0
}
```

### 3. 考虑工作区状态

**示例任务**: "将变量a和b相加"

**硬编码**：
- 无法理解工作区变量

**LLM决策**：
```json
{
  "tool_name": "internal_reasoning",
  "reasoning": "任务只需要从工作区获取变量a和b，然后相加。
               这是简单的变量操作，不需要SymPy或Wolfram Alpha。",
  "confidence": 0.9
}
```

### 4. 智能回退

**示例任务**: "求解超越方程 e^x = x"

**LLM决策**：
```json
{
  "tool_name": "wolfram_alpha",
  "reasoning": "这是一个超越方程，SymPy可能难以处理。
               Wolfram Alpha有更强的数值求解能力，更适合此任务。",
  "confidence": 0.85
}
```

---

## 📊 对比表

| 维度 | 硬编码关键词匹配 | LLM智能决策 |
|------|----------------|------------|
| **决策方式** | 字符串匹配 | 理解任务语义 |
| **上下文理解** | ❌ 无 | ✅ 完整理解 |
| **工作区感知** | ❌ 无 | ✅ 考虑变量状态 |
| **复杂度评估** | ❌ 无 | ✅ 智能评估 |
| **边界情况** | ❌ 处理不好 | ✅ 灵活处理 |
| **决策理由** | ❌ 无 | ✅ 清晰的reasoning |
| **置信度** | ❌ 无 | ✅ 量化confidence |
| **可扩展性** | ⚠️ 需要修改代码 | ✅ 无需修改 |

---

## 🔄 完整工作流程

```
1. Execution Agent遍历任务
   ↓
2. _execute_tool_call接收任务
   ↓
3. 构建工具选择提示词
   ├─ 任务信息（ID、描述、方法、参数）
   ├─ 工具介绍（SymPy、Wolfram Alpha、Internal Reasoning）
   ├─ 工作区状态
   └─ 决策考虑因素
   ↓
4. 调用LLM（with_structured_output）
   ↓
5. LLM返回ToolSelectionDecision
   {
     "tool_name": "sympy",
     "reasoning": "...",
     "confidence": 0.9
   }
   ↓
6. 打印LLM决策
   🤖 LLM工具选择: sympy
      理由: 这是符号方程求解，SymPy最适合
      置信度: 0.9
   ↓
7. 根据LLM决策调用工具
   ↓
8. 返回ToolExecutionRecord
   rationale: "LLM选择: ... (置信度: 0.9)"
```

---

## 🎯 关键改进

### 1. 提示词设计

精心设计的提示词包含：
- ✅ 完整的任务上下文
- ✅ 详细的工具介绍（适用场景、优势、示例）
- ✅ 工作区状态
- ✅ 决策考虑因素（任务性质、精度、复杂度、外部知识需求）

### 2. 结构化输出

使用Pydantic确保LLM返回：
- ✅ `tool_name`: 标准化的工具名称
- ✅ `reasoning`: 详细的选择理由（可追溯）
- ✅ `confidence`: 置信度评分（可用于监控）

### 3. 异常处理

```python
try:
    # LLM决策
    decision = llm_with_structure.invoke(messages)
    ...
except Exception as e:
    # 回退到内部推理
    print(f"⚠️ LLM工具选择失败: {e}，回退到内部推理")
    tool_result = _call_internal_reasoning(task, workspace)
```

---

## 📝 实际示例

### 示例1：方程求解

**任务**：
```python
task = {
    "task_id": "1.1",
    "description": "求解方程 x^2 - 5x + 6 = 0",
    "method": "SolveEquation",
    "params": {"equation": "x^2 - 5x + 6 = 0", "variable": "x"}
}
```

**LLM决策**：
```
🤖 LLM工具选择: sympy
   理由: 这是一个标准的二次方程求解问题。SymPy擅长符号代数运算，
         能够精确求解并给出解析解。这种问题不需要Wolfram Alpha
         的数值计算能力，SymPy足够且更快。
   置信度: 0.95
```

**执行结果**：
```
SymPy计算结果：['2', '3']
LaTeX: x = 2, x = 3
```

### 示例2：简单运算

**任务**：
```python
task = {
    "task_id": "2.1",
    "description": "计算 5 + 3",
    "method": "Calculate"
}
```

**LLM决策**：
```
🤖 LLM工具选择: internal_reasoning
   理由: 这是一个简单的算术加法运算，不需要调用SymPy或Wolfram Alpha
         这样的外部工具。使用内部推理即可快速完成，节省资源。
   置信度: 1.0
```

### 示例3：复杂积分

**任务**：
```python
task = {
    "task_id": "3.1",
    "description": "计算不定积分 ∫ e^(-x^2) dx",
    "method": "Integrate"
}
```

**LLM决策**：
```
🤖 LLM工具选择: wolfram_alpha
   理由: 这是高斯积分，没有初等函数的解析解。虽然SymPy可以处理，
         但结果会涉及误差函数(erf)。Wolfram Alpha能提供更完整的
         解释和数值近似，对于这种特殊积分更合适。
   置信度: 0.8
```

---

## ✅ 验收清单

- [x] LLM驱动的工具选择（不是硬编码）
- [x] 结构化输出（ToolSelectionDecision）
- [x] 详细的工具介绍提示词
- [x] 考虑工作区状态
- [x] 决策理由和置信度
- [x] 异常处理和回退机制
- [x] 打印LLM决策过程（可追溯）

---

## 🎓 总结

通过这次改进，我们实现了：

1. ✅ **从硬编码到智能决策** - LLM理解任务语义
2. ✅ **上下文感知** - 考虑任务复杂度和工作区状态
3. ✅ **可追溯性** - 每个决策都有reasoning和confidence
4. ✅ **灵活性** - 无需修改代码即可适应新场景
5. ✅ **鲁棒性** - 异常时自动回退

这与Coordinator Agent的LLM驱动路由决策一致，真正实现了**智能体系统的端到端LLM驱动**！

---

**实现日期**: 2025-09-30  
**改进类型**: 从硬编码到LLM驱动  
**影响**: 工具选择更智能、更灵活、更可追溯  
**状态**: ✅ 完成 
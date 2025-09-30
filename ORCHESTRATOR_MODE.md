# Orchestrator模式 - LLM驱动的智能决策

## 🎯 核心理念

**将选择权交给LLM，而不是硬编码规则**

按照agent.md的精神，Coordinator Agent应该是一个真正的"协调管理智能体"，由LLM智能分析当前情况并决策下一步，而不是通过if-else硬编码路由规则。

---

## 🔄 架构对比

### ❌ 旧版（硬编码路由）

```python
def verification_router(state):
    if verification_output.status == PASSED:
        return "end"
    elif verification_output.problem_level == EXECUTION_LEVEL:
        return "execution"  # 硬编码规则
    elif verification_output.problem_level == PLANNING_LEVEL:
        return "planning"   # 硬编码规则
    ...
```

**问题**：
- 决策逻辑硬编码，不够灵活
- 无法根据具体情况做细微调整
- 不符合agent.md中"智能决策"的理念

### ✅ 新版（Orchestrator模式）

```python
def coordinator_agent(state):
    # 构建完整的上下文
    context = build_context(state)
    
    # 由LLM分析情况并做决策
    decision = llm_with_structure.invoke(f"""
    当前状态：{context}
    验证反馈：{verification_output}
    
    请分析情况并决策下一步：
    - 如果验证通过 → complete
    - 如果是计算错误 → execution
    - 如果是策略问题 → planning
    - 如果是理解偏差 → comprehension
    """)
    
    return {
        "current_phase": decision.next_action,  # LLM的决策
        "reasoning": decision.reasoning
    }
```

**优势**：
- ✅ LLM智能分析，而不是硬编码
- ✅ 可以根据具体情况做细微调整
- ✅ 完全符合agent.md的"协调管理智能体"定义
- ✅ 更强的适应性和灵活性

---

## 🏗️ 新架构

### 流程图

```
START
  ↓
┌─────────────────┐
│  Coordinator    │ ← LLM智能决策中心
│  (Orchestrator) │
└────────┬────────┘
         │
    【LLM决策】
         │
    ┌────┴────┐
    ↓         ↓         ↓         ↓
Comprehension Planning Execution Verification
    │         │         │         │
    └─────────┴─────────┴─────────┘
              ↓
         Coordinator (继续决策)
              ↓
         【循环直到complete】
```

### 关键特性

1. **Coordinator中心化**
   - 所有agent执行完后都返回Coordinator
   - Coordinator分析结果，决定下一步

2. **LLM驱动决策**
   - Coordinator使用LLM分析当前状态
   - 生成结构化决策：`CoordinatorDecision`

3. **自适应循环**
   - 根据验证反馈智能调整
   - 自动判断何时结束

---

## 📊 决策模型

### `CoordinatorDecision`

```python
class CoordinatorDecision(BaseModel):
    next_action: str  # comprehension/planning/execution/verification/complete
    reasoning: str    # 决策理由
    instructions: str # 给下一个agent的指令
    should_continue: bool  # 是否继续迭代
```

### Coordinator的决策提示词

```python
decision_prompt = f"""
你是协调管理智能体。当前状态：

【已完成的工作】
- ✅ 题目理解: {comprehension_output}
- ✅ 策略规划: {planning_output}
- ✅ 计算执行: {execution_output}

【验证反馈】（最重要！）
- 状态: {verification_output.status}
- 问题: {verification_output.issues}
- 建议: {verification_output.suggestions}

请分析并决策下一步：
1. 如果验证通过 → next_action: "complete"
2. 如果需要修订：
   - 分析问题根源在哪个层面
   - 理解偏差 → "comprehension"
   - 策略问题 → "planning"
   - 执行错误 → "execution"
3. 如果达到最大迭代 → "complete"

返回JSON格式的决策。
"""
```

---

## 🎭 agent.md一致性

### agent.md原文

> "协调管理智能体 (Coordinator Agent): 担任**流程控制器**。它不仅是任务的启动者，更是迭代循环的'守门员'。它负责将执行结果送去验证，并根据验证反馈决定是'通过'，还是'打回重做'。"

> "智能决策: 协调管理智能体 接收并解析这份'诊断报告'。现在，它需要做出决策"

### 实现对照

| agent.md要求 | 实现方式 |
|-------------|---------|
| "流程控制器" | ✅ Coordinator控制整个流程 |
| "守门员" | ✅ 每轮都经过Coordinator审查 |
| "根据验证反馈决定" | ✅ LLM分析验证反馈做决策 |
| "解析诊断报告" | ✅ Coordinator接收完整诊断报告 |
| "智能决策" | ✅ 由LLM决策，不是硬编码 |
| "判断问题根源" | ✅ LLM分析问题层级 |

---

## 🚀 使用示例

### 基础用法（不变）

```python
from src.agents.graph_refactored import solve_math_problem

result = solve_math_problem(
    problem_text="求解方程 x^2 - 5x + 6 = 0",
    max_iterations=10
)
```

### 执行过程（新）

```
🎯 [Coordinator Agent] 第0轮协调...
  📊 Coordinator决策：
     下一步: comprehension
     理由: 首次运行，需要先理解题目
     指令: 分析题目结构，提取已知条件和求解目标

🧠 [Comprehension Agent] 第1轮理解...
  ✓ 理解完成

🎯 [Coordinator Agent] 第1轮协调...
  📊 Coordinator决策：
     下一步: planning
     理由: 理解完成，需要制定解题策略
     指令: 基于理解结果制定详细的执行计划

📋 [Planning Agent] 第1轮规划...
  ✓ 规划完成

🎯 [Coordinator Agent] 第2轮协调...
  📊 Coordinator决策：
     下一步: execution
     理由: 计划就绪，开始执行计算
     指令: 按照计划逐步执行每个任务

⚙️ [Execution Agent] 第1轮执行...
  ✓ 执行完成

🎯 [Coordinator Agent] 第3轮协调...
  📊 Coordinator决策：
     下一步: verification
     理由: 执行完成，需要验证结果
     指令: 检查计算过程和最终答案的正确性

✅ [Verification Agent] 第1轮验证...
  ⚠️ 需要修订：发现 1 个问题
    - Calculation Error: 第二步计算有误

🎯 [Coordinator Agent] 第4轮协调...
  📊 Coordinator决策：
     下一步: execution
     理由: 验证发现计算错误，这是执行层面的问题，无需重新规划
     指令: 修正第二步的计算错误，重新执行

⚙️ [Execution Agent] 第2轮执行（基于验证反馈）...
  ✓ 执行完成

🎯 [Coordinator Agent] 第5轮协调...
  📊 Coordinator决策：
     下一步: verification
     理由: 修正后需要再次验证
     指令: 确认修正后的结果是否正确

✅ [Verification Agent] 第2轮验证...
  ✅ 验证通过！

🎯 [Coordinator Agent] 第6轮协调...
  📊 Coordinator决策：
     下一步: complete
     理由: 验证通过，可以交付最终结果
     指令: 整合结果并输出

🎉 求解完成
```

---

## 💡 核心优势

### 1. 真正的智能决策

**旧版**：
```python
if problem_level == "execution":
    return "execution"  # 死板的规则
```

**新版**：
```python
# LLM分析：
# "虽然是计算错误，但由于已经重试2次都失败，
# 可能是计划本身有问题，建议返回planning重新规划"
return CoordinatorDecision(
    next_action="planning",
    reasoning="多次执行失败，可能是策略问题"
)
```

### 2. 上下文感知

Coordinator能够：
- 查看完整的迭代历史
- 分析之前尝试的方法
- 根据具体情况调整策略
- 避免重复无效的尝试

### 3. 灵活适应

- 不同问题可能需要不同的策略
- LLM可以根据具体情况调整
- 不受硬编码规则限制

---

## 📈 与硬编码路由的对比

| 方面 | 硬编码路由 | Orchestrator模式 |
|------|-----------|-----------------|
| **决策方式** | if-else规则 | LLM智能分析 |
| **灵活性** | 固定规则 | 自适应调整 |
| **上下文感知** | 有限 | 完整 |
| **可解释性** | 规则明确但死板 | 有详细reasoning |
| **符合agent.md** | 部分 | 完全 |
| **扩展性** | 需要修改代码 | 只需调整提示词 |

---

## 🎓 总结

新的Orchestrator模式将Coordinator真正变成了一个**智能体**：

1. ✅ **不是简单的路由函数**，而是使用LLM的智能决策者
2. ✅ **分析完整上下文**，包括验证反馈、迭代历史
3. ✅ **智能决策下一步**，而不是硬编码规则
4. ✅ **完全符合agent.md**的"协调管理智能体"定义
5. ✅ **更强的适应性**，可以处理复杂情况

这才是真正的"**带反馈的迭代优化模式**"！

---

## 📚 参考

- [agent.md](agent.md) - 原始设计文档
- [src/agents/agents_refactored.py](src/agents/agents_refactored.py) - Coordinator实现
- [src/agents/graph_refactored.py](src/agents/graph_refactored.py) - 图结构
- [AGENT_MD_IMPLEMENTATION.md](AGENT_MD_IMPLEMENTATION.md) - 实现总结

---

**模式实现日期**: 2025-09-30  
**版本**: v2.1 (Orchestrator Mode) 
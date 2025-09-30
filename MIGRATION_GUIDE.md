# 迁移指南 - 从旧版到新版（基于agent.md迭代优化模式）

## 📋 概述

本项目已完成重构，实现了**带反馈的迭代优化模式**（agent.md）。新版本具有：
- ✅ 精简的State设计（10个核心字段 vs 旧版30+）
- ✅ 智能路由系统（根据问题层级自动返回相应阶段）
- ✅ 迭代历史追踪
- ✅ 完整的诊断报告系统

---

## 🗂️ 文件映射关系

### 已替换的文件

| 旧版文件 | 新版文件 | 状态 |
|---------|---------|------|
| `src/state/state.py` | `src/state/state_refactored.py` | ✅ 已替换 |
| `src/state/state_v2.py` | `src/state/state_refactored.py` | ✅ 已替换 |
| `src/state/state_utils.py` | `src/state/state_refactored.py` | ✅ 已合并 |
| `src/agents/comprehension.py` | `src/agents/agents_refactored.py::comprehension_agent` | ✅ 已替换 |
| `src/agents/comprehension_v2.py` | `src/agents/agents_refactored.py::comprehension_agent` | ✅ 已替换 |
| `src/agents/planning.py` | `src/agents/agents_refactored.py::planning_agent` | ✅ 已替换 |
| `src/agents/planning_v2.py` | `src/agents/agents_refactored.py::planning_agent` | ✅ 已替换 |
| `src/agents/execution.py` | `src/agents/agents_refactored.py::execution_agent` | ✅ 已替换 |
| `src/agents/execution_v2.py` | `src/agents/agents_refactored.py::execution_agent` | ✅ 已替换 |
| `src/agents/verification.py` | `src/agents/agents_refactored.py::verification_agent` | ✅ 已替换 |
| `src/agents/verification_v2.py` | `src/agents/agents_refactored.py::verification_agent` | ✅ 已替换 |
| `src/agents/coordinator.py` | `src/agents/graph_refactored.py::verification_router` | ✅ 已替换 |
| `src/agents/coordinator_v2.py` | `src/agents/graph_refactored.py::verification_router` | ✅ 已替换 |
| `src/agents/multi_agent.py` | `src/agents/graph_refactored.py` | ✅ 已替换 |

### 保留的文件

| 文件 | 说明 |
|------|------|
| `src/prompts/prompt.py` | 提示词模板（已被新系统使用） |
| `src/tools/sympy.py` | SymPy工具（已被新系统使用） |
| `src/tools/wolfram_alpha.py` | Wolfram Alpha工具（已被新系统使用） |
| `src/configuration.py` | 配置管理（已被新系统使用） |

---

## 🔄 API变更

### 旧版API

```python
# 旧版 - 使用multi_agent.py
from src.agents.multi_agent import solve_math_problem

result = solve_math_problem("求解方程 x^2 - 5x + 6 = 0")
```

### 新版API

```python
# 新版 - 使用graph_refactored.py
from src.agents.graph_refactored import solve_math_problem

result = solve_math_problem(
    problem_text="求解方程 x^2 - 5x + 6 = 0",
    max_iterations=10  # 新增：最大迭代次数
)

# 访问结果
print(result["final_answer"])
print(result["comprehension_output"])  # 结构化输出
print(result["planning_output"])       # 结构化输出
print(result["execution_output"])      # 结构化输出
print(result["verification_output"])   # 诊断报告
print(result["iteration_history"])     # 迭代历史
```

---

## 🆕 新增特性

### 1. 迭代优化模式（agent.md）

**旧版**：线性流程，一次性交付
```
Comprehension → Planning → Execution → Verification → END
```

**新版**：带反馈的迭代循环
```
Comprehension → Planning → Execution → Verification
                   ↑                      ↓
                   └──── [根据问题层级] ───┘
                   
问题层级决定返回位置：
- execution: 执行层面小错 → 返回Execution
- planning: 规划层面策略问题 → 返回Planning
- comprehension: 理解层面根本偏差 → 返回Comprehension
```

### 2. 诊断报告系统

**旧版**：简单的验证结果
```python
{
    "is_valid": bool,
    "error_details": str
}
```

**新版**：详细的诊断报告（符合agent.md）
```python
{
    "status": "PASSED/NEEDS_REVISION/FATAL_ERROR",
    "issues": [
        {
            "issue_type": "Calculation Error",
            "detail": "第三步计算错误",
            "location": "task_3"
        }
    ],
    "suggestions": [
        "请重新计算第三步，使用SymPy验证结果"
    ],
    "problem_level": "execution",  # 决定返回哪个阶段
    "rationale": "详细裁决理由",
    "confidence_score": 0.95
}
```

### 3. 迭代历史追踪

```python
# 查看迭代历史
for record in result["iteration_history"]:
    print(f"迭代 {record.iteration_number}:")
    print(f"  阶段: {record.phase}")
    print(f"  版本: {record.result_version}")
    print(f"  状态: {record.verification_status}")
    print(f"  问题: {record.issues_found}")
    print(f"  行动: {record.actions_taken}")
```

---

## 📝 代码迁移示例

### 示例1：基础用法

**旧版**：
```python
from src.agents.multi_agent import build_math_solver_graph
from src.state.state import MathProblemState

graph = build_math_solver_graph()
initial_state = {"user_input": "求解方程 x^2 - 5x + 6 = 0"}
result = graph.invoke(initial_state)
```

**新版**：
```python
from src.agents.graph_refactored import solve_math_problem

result = solve_math_problem(
    problem_text="求解方程 x^2 - 5x + 6 = 0",
    max_iterations=10
)
```

### 示例2：访问状态字段

**旧版**：
```python
# 访问理解结果
givens = result["comprehension_result"]["givens"]
objectives = result["comprehension_result"]["objectives"]

# 访问验证结果
is_valid = result["verification_result"]["is_valid"]
```

**新版**：
```python
# 访问理解结果（Pydantic模型）
givens = result["comprehension_output"].givens
objectives = result["comprehension_output"].objectives

# 访问验证结果（完整诊断报告）
status = result["verification_output"].status
issues = result["verification_output"].issues
suggestions = result["verification_output"].suggestions
```

### 示例3：自定义配置

**旧版**：
```python
config = {"model": "gpt-4"}
result = solve_math_problem(problem, config=config)
```

**新版**：
```python
from src.configuration import Configuration

config = Configuration(
    coordinator_model="gpt-4",
    max_iterations=5
)

result = solve_math_problem(
    problem_text=problem,
    max_iterations=5,
    config=config
)
```

---

## 🗑️ 安全删除旧文件

以下文件已被完全替换，可以安全删除：

```bash
# State相关
rm src/state/state.py
rm src/state/state_v2.py
rm src/state/state_utils.py

# Agent相关
rm src/agents/comprehension.py
rm src/agents/comprehension_v2.py
rm src/agents/planning.py
rm src/agents/planning_v2.py
rm src/agents/execution.py
rm src/agents/execution_v2.py
rm src/agents/verification.py
rm src/agents/verification_v2.py
rm src/agents/coordinator.py
rm src/agents/coordinator_v2.py
rm src/agents/multi_agent.py
```

**注意**：删除前请确保没有其他文件依赖这些旧文件。

---

## ✅ 验证迁移

运行示例代码验证新系统：

```bash
# 运行使用示例
python examples/refactored_usage_example.py

# 预期输出：
# - 显示每个阶段的执行情况
# - 显示迭代历史
# - 显示最终答案
```

---

## 📚 更多资源

- [README_REFACTOR.md](README_REFACTOR.md) - 重构总结
- [docs/refactored_architecture.md](docs/refactored_architecture.md) - 详细架构文档
- [examples/refactored_usage_example.py](examples/refactored_usage_example.py) - 使用示例
- [agent.md](agent.md) - 迭代优化模式详细说明

---

## 🆘 常见问题

### Q: 旧版代码还能用吗？

A: 可以，旧版代码仍然保留在代码库中。但建议迁移到新版，享受更强大的功能和更好的维护性。

### Q: 如何回滚到旧版？

A: 使用Git回滚到重构前的提交，或手动导入旧版文件。

### Q: 新版性能如何？

A: 新版由于增加了迭代机制，可能会多次调用LLM，但换来的是更高质量的输出。可以通过`max_iterations`控制最大迭代次数。

### Q: 如何禁用迭代优化？

A: 设置`max_iterations=1`即可强制一次性交付（类似旧版行为）。

---

**迁移完成日期**: 2025-09-30 
# 数学多智能体系统重构架构文档

## 📋 概述

本文档描述了基于 **open_deep_research** 模式重构后的数学多智能体系统架构。

---

## 🏗️ 核心设计原则

### 1. 状态分层设计

```
AgentState (全局状态)
    ├── 跨智能体共享数据（user_input, final_answer）
    ├── 各智能体的结构化输出（comprehension_output, planning_output等）
    └── 流程控制字段（current_phase, total_iterations）

ComprehensionState (子图状态)
    └── 题目理解智能体的工作区

PlanningState (子图状态)
    └── 策略规划智能体的工作区

ExecutionState (子图状态)
    └── 计算执行智能体的工作区

VerificationState (子图状态)
    └── 验证反思智能体的工作区
```

**优势**：
- ✅ **精简全局状态**：只保留跨智能体必需的字段
- ✅ **清晰职责边界**：每个智能体的专有数据独立管理
- ✅ **易于维护**：修改某个智能体不影响其他部分

---

### 2. Reducer模式

```python
# 追加合并（默认）
messages: Annotated[List[Message], operator.add]

# 覆盖合并
comprehension_output: Annotated[Optional[ComprehensionOutput], override_reducer]

# 覆盖模式使用
state["comprehension_output"] = {"type": "override", "value": new_output}
```

**规则**：
- **消息列表**：使用 `operator.add` 累积历史
- **结构化输出**：使用 `override_reducer` 完整替换
- **迭代计数**：直接覆盖更新

---

### 3. 结构化输出模型

使用 **Pydantic BaseModel** 定义标准化输出：

```python
class ComprehensionOutput(BaseModel):
    """题目理解智能体的结构化输出"""
    normalized_latex: str
    givens: List[str]
    objectives: List[str]
    # ... 更多字段

class PlanningOutput(BaseModel):
    """策略规划智能体的结构化输出"""
    execution_tasks: List[ExecutionTask]
    workspace_init: List[Dict[str, Any]]
    # ... 更多字段
```

**优势**：
- ✅ **类型安全**：编译时检查
- ✅ **易于序列化**：JSON导入导出
- ✅ **自动验证**：Pydantic验证输入

---

## 🤖 智能体架构

### 智能体流程图

```
┌─────────────────────────────────────────────────────────┐
│                    START                                 │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
       ┌──────────────────────┐
       │  Comprehension Agent │ ← 题目理解
       │  (理解题目结构)      │
       └──────────┬───────────┘
                  │
                  ▼
       ┌──────────────────────┐
       │   Planning Agent     │ ← 策略规划
       │  (制定执行计划)      │
       └──────────┬───────────┘
                  │
                  ▼
       ┌──────────────────────┐
       │  Execution Agent     │ ← 计算执行
       │  (执行计算任务)      │
       └──────────┬───────────┘
                  │
                  ▼
       ┌──────────────────────┐
       │ Verification Agent   │ ← 验证反思
       │  (验证计算结果)      │
       └──────────┬───────────┘
                  │
         ┌────────┴────────┐
         │                 │
    [PASSED]          [FAILED]
         │                 │
         ▼                 └──► 返回Planning重试
       END                      (最多max_iterations次)
```

---

### 各智能体职责

#### 1. 📚 Comprehension Agent（题目理解智能体）

**输入**：`state.user_input`

**任务**：
1. LaTeX标准化
2. 问题表象解构（已知、目标、约束）
3. 核心原理溯源
4. 策略路径构建

**输出**：`ComprehensionOutput`

```python
ComprehensionOutput(
    normalized_latex="\\[ x^2 - 5x + 6 = 0 \\]",
    givens=["方程 x^2 - 5x + 6 = 0"],
    objectives=["求解方程的所有实数根"],
    primary_field="代数",
    strategy_deduction="使用因式分解法..."
)
```

---

#### 2. 📋 Planning Agent（策略规划智能体）

**输入**：`state.comprehension_output`

**任务**：
1. 基于理解结果制定执行计划
2. 分解为原子任务（DAG结构）
3. 链接到基础原理
4. 定义任务依赖关系

**输出**：`PlanningOutput`

```python
PlanningOutput(
    execution_tasks=[
        ExecutionTask(
            task_id="task_1",
            description="因式分解方程",
            method="SymbolicFactorization",
            dependencies=[]
        ),
        ExecutionTask(
            task_id="task_2",
            description="求解因式",
            method="SolveFactors",
            dependencies=["task_1"]
        )
    ]
)
```

---

#### 3. ⚙️ Execution Agent（计算执行智能体）

**输入**：`state.planning_output`

**任务**：
1. 按照计划执行每个任务
2. 选择合适的工具（SymPy/Wolfram Alpha/Internal Reasoning）
3. 记录计算轨迹
4. 管理工作区变量

**输出**：`ExecutionOutput`

```python
ExecutionOutput(
    workspace={"factored_form": "(x-2)(x-3)", "solutions": [2, 3]},
    tool_executions=[
        ToolExecutionRecord(
            task_id="task_1",
            tool_type=ToolType.SYMPY,
            tool_output="(x - 2)*(x - 3)"
        )
    ],
    final_result=[2, 3]
)
```

---

#### 4. ✅ Verification Agent（验证反思智能体）

**输入**：`state.comprehension_output`, `state.execution_output`

**任务**：
1. 一致性检查（执行是否遵循分析）
2. 逻辑链审计（计算步骤是否连贯）
3. 约束满足验证（结果是否满足原始约束）
4. 最终答案评估

**输出**：`VerificationOutput`

```python
VerificationOutput(
    verdict="PASSED",  # PASSED/PASSED_WITH_WARNINGS/FAILED
    consistency_check=VerificationCheck(status="PASSED"),
    constraint_verification=VerificationCheck(status="PASSED"),
    rationale="所有检查通过，结果正确"
)
```

---

## 🔄 循环反馈机制

### 验证失败处理

```python
if verification_output.verdict == "FAILED":
    if total_iterations < max_iterations:
        current_phase = "planning"  # 返回规划阶段
    else:
        current_phase = "completed"  # 达到最大迭代，强制结束
```

### 最大迭代保护

```python
def should_continue(state: AgentState) -> bool:
    if state["total_iterations"] >= state["max_iterations"]:
        return False  # 防止死循环
    return True
```

---

## 📦 文件结构

```
src/
├── state/
│   └── state_refactored.py         # 精简State设计
├── agents/
│   ├── agents_refactored.py        # 四个核心智能体节点
│   └── graph_refactored.py         # LangGraph主图编排
├── prompts/
│   └── prompt.py                   # 提示词模板
├── tools/
│   ├── sympy.py                    # SymPy工具
│   └── wolfram_alpha.py            # Wolfram Alpha工具
└── configuration.py                # 配置管理
```

---

## 🚀 使用示例

### 基础用法

```python
from src.agents.graph_refactored import solve_math_problem

# 求解数学问题
result = solve_math_problem(
    problem_text="求解方程 x^2 - 5x + 6 = 0",
    max_iterations=10
)

# 查看结果
print(result["final_answer"])
print(result["comprehension_output"])
print(result["execution_output"])
```

### 高级用法（使用配置）

```python
from src.configuration import Configuration
from src.agents.graph_refactored import build_math_solver_graph, create_initial_state

# 自定义配置
config = Configuration(
    coordinator_model="gpt-4",
    max_iterations=5
)

# 构建图
graph = build_math_solver_graph(config)

# 创建初始状态
initial_state = create_initial_state("求解方程 x^2 - 5x + 6 = 0")

# 执行
final_state = graph.invoke(initial_state)
```

---

## 🔍 与旧版对比

| 方面 | 旧版设计 | 新版设计 |
|------|---------|---------|
| **全局状态字段** | 30+ 字段 | 10 个核心字段 |
| **状态管理** | 混杂在一起 | 分层清晰 |
| **结构化输出** | 部分使用 | 全面使用Pydantic |
| **智能体实现** | 类+函数混合 | 统一节点函数 |
| **循环控制** | 隐式 | 显式（max_iterations） |
| **可维护性** | 🟡 中等 | 🟢 优秀 |
| **可扩展性** | 🟡 中等 | 🟢 优秀 |

---

## 💡 核心优势

1. **精简高效**：全局状态只保留必需字段，减少内存占用
2. **清晰边界**：每个智能体的数据独立管理，职责明确
3. **类型安全**：Pydantic模型提供编译时类型检查
4. **易于调试**：结构化输出便于追踪每个阶段的结果
5. **易于扩展**：添加新智能体无需修改全局状态

---

## 📚 参考

- [LangGraph官方文档](https://langchain-ai.github.io/langgraph/)
- [open_deep_research项目](https://github.com/langchain-ai/open-deep-research)
- [Pydantic文档](https://docs.pydantic.dev/)

---

## 🎯 下一步

1. **工具实现**：完善SymPy和Wolfram Alpha工具的实际调用逻辑
2. **错误处理**：增强异常处理和重试机制
3. **性能优化**：添加缓存和并发执行
4. **测试覆盖**：编写单元测试和集成测试 
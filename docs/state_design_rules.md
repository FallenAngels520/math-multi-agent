# 数学多智能体系统State设计规则

## 1. 设计原则概述

基于"提示词与Agent深度绑定"的核心洞察，State设计遵循以下原则：

### 1.1 提示词驱动原则
- **每个Agent的状态字段完全匹配其提示词模板的结构**
- **状态字段的语义与提示词中的指令一一对应**
- **状态更新逻辑与提示词中的行为约束保持一致**

### 1.2 单一职责原则
- **每个状态字段有明确的单一职责**
- **避免状态字段的语义重叠和功能耦合**
- **状态字段的边界清晰，便于理解和维护**

### 1.3 Reducer策略原则
- **基于字段用途选择适当的reducer策略**
- **保持状态更新的可预测性和一致性**
- **支持错误恢复和重试机制**

## 2. Agent功能与State字段映射

### 2.1 题目理解智能体 (Comprehension Agent)

**提示词模板特征：**
- 三阶段分析框架：问题表象解构 → 核心原理溯源 → 策略路径构建
- LaTeX标准化预处理
- 结构化输出要求

**状态字段设计：**
```python
class ComprehensionState(TypedDict):
    # 预处理阶段 - 使用override_reducer（单次生成，不累积）
    latex_normalization: Annotated[LaTeXNormalization, override_reducer]
    
    # 第一阶段：问题表象解构 - 使用override_reducer（完整替换）
    surface_deconstruction: Annotated[ProblemSurfaceDeconstruction, override_reducer]
    
    # 第二阶段：核心原理溯源 - 使用override_reducer（完整替换）
    principles_tracing: Annotated[CorePrinciplesTracing, override_reducer]
    
    # 第三阶段：策略路径构建 - 使用override_reducer（完整替换）
    path_building: Annotated[StrategicPathBuilding, override_reducer]
    
    # 消息记录 - 使用operator.add（累积记录）
    comprehension_messages: Annotated[List[MessageLikeRepresentation], operator.add]
```

**Reducer策略理由：**
- 分析结果是完整的结构化对象，应该整体替换而不是部分更新
- 消息记录需要累积，便于调试和审计

### 2.2 策略规划智能体 (Planning Agent)

**提示词模板特征：**
- 原子性任务分解
- 依赖关系管理（DAG结构）
- 原理驱动规划

**状态字段设计：**
```python
class PlanningState(TypedDict):
    # 执行计划 - 使用override_reducer（完整替换）
    execution_plan: Annotated[ExecutionPlan, override_reducer]
    
    # 任务管理 - 使用list_append_reducer（累积完成）
    completed_tasks: Annotated[List[str], list_append_reducer]
    
    # 替代策略 - 使用list_append_reducer（累积选项）
    alternative_strategies: Annotated[List[Dict[str, Any]], list_append_reducer]
    
    # 消息记录 - 使用operator.add（累积记录）
    planning_messages: Annotated[List[MessageLikeRepresentation], operator.add]
```

**Reducer策略理由：**
- 执行计划是完整的DAG结构，应该整体替换
- 完成的任务和替代策略需要累积记录

### 2.3 计算执行智能体 (Execution Agent)

**提示词模板特征：**
- 工具选择策略（SymPy/Wolfram/Internal Reasoning）
- 工作区变量管理
- 计算轨迹记录

**状态字段设计：**
```python
class ExecutionState(TypedDict):
    # 工作区管理 - 使用dict_merge_reducer（增量更新）
    workspace: Annotated[Dict[str, Any], dict_merge_reducer]
    
    # 工具执行记录 - 使用list_append_reducer（累积记录）
    tool_executions: Annotated[List[ToolExecution], list_append_reducer]
    
    # 计算轨迹 - 使用list_append_reducer（累积记录）
    computational_trace: Annotated[List[Dict[str, Any]], list_append_reducer]
    
    # 中间结果 - 使用list_append_reducer（累积记录）
    intermediate_results: Annotated[List[Dict[str, Any]], list_append_reducer]
```

**Reducer策略理由：**
- 工作区需要增量更新，支持变量值的逐步计算
- 执行记录需要累积，便于审计和调试

### 2.4 验证反思智能体 (Verification Agent)

**提示词模板特征：**
- 四阶段验证协议
- 结构化裁决输出
- 约束条件验证

**状态字段设计：**
```python
class VerificationState(TypedDict):
    # 验证报告 - 使用override_reducer（完整替换）
    verification_report: Annotated[VerificationReport, override_reducer]
    
    # 检查记录 - 使用list_append_reducer（累积记录）
    verification_checks: Annotated[List[VerificationCheck], list_append_reducer]
    
    # 约束验证 - 使用list_append_reducer（累积记录）
    constraints_verified: Annotated[List[str], list_append_reducer]
    
    # 优化建议 - 使用list_append_reducer（累积记录）
    optimization_suggestions: Annotated[List[str], list_append_reducer]
```

**Reducer策略理由：**
- 验证报告是完整的结构化裁决，应该整体替换
- 检查记录和验证结果需要累积，便于全面评估

### 2.5 协调管理智能体 (Coordinator Agent)

**提示词模板特征：**
- 流程状态机管理
- 迭代计数和重试策略
- 错误处理和恢复

**状态字段设计：**
```python
class CoordinatorState(TypedDict):
    # 迭代管理 - 使用dict_merge_reducer（增量更新）
    phase_iterations: Annotated[Dict[str, int], dict_merge_reducer]
    
    # 重试管理 - 使用dict_merge_reducer（增量更新）
    retry_counts: Annotated[Dict[str, int], dict_merge_reducer]
    
    # 错误信息 - 使用list_append_reducer（累积记录）
    error_messages: Annotated[List[str], list_append_reducer]
    
    # 协调消息 - 使用operator.add（累积记录）
    coordinator_messages: Annotated[List[MessageLikeRepresentation], operator.add]
```

**Reducer策略理由：**
- 迭代和重试计数需要增量更新
- 错误信息需要累积，便于问题诊断

## 3. Reducer策略选择指南

### 3.1 override_reducer 适用场景
- **完整结构化对象**：分析报告、执行计划、验证报告等
- **单次生成结果**：不需要累积更新的字段
- **原子性更新**：整个对象作为一个原子单位进行替换

### 3.2 list_append_reducer 适用场景
- **累积记录**：消息记录、执行轨迹、检查记录等
- **历史追踪**：需要保留完整历史的字段
- **增量添加**：每次添加新条目，不修改现有条目

### 3.3 dict_merge_reducer 适用场景
- **增量更新**：工作区变量、配置参数等
- **键值合并**：需要合并多个来源数据的字典字段
- **配置覆盖**：支持配置的层级覆盖机制

### 3.4 operator.add 适用场景
- **消息累积**：LangChain消息对象的累积
- **列表合并**：需要合并多个列表的字段
- **兼容性**：与LangGraph默认行为保持一致

## 4. 状态生命周期管理

### 4.1 状态初始化
```python
def create_initial_state(user_input: str) -> MathProblemStateV2:
    """创建包含所有必需字段的初始状态"""
```

### 4.2 状态流转规则
- **单向流动**：Comprehension → Planning → Execution → Verification
- **循环机制**：验证失败时可返回Planning或Execution阶段
- **终止条件**：验证成功或达到最大重试次数

### 4.3 错误恢复策略
- **阶段重试**：每个阶段有独立的retry_count和max_retries配置
- **状态回滚**：错误时回滚到上一个稳定状态
- **错误隔离**：错误信息隔离存储，不影响正常状态流转

## 5. 性能与可维护性考虑

### 5.1 状态大小控制
- **结构化数据**：使用Pydantic模型确保数据有效性
- **消息清理**：定期清理过时的消息记录
- **增量更新**：避免不必要的全量状态替换

### 5.2 调试与监控
- **消息追踪**：每个Agent的消息记录独立存储
- **性能指标**：记录各阶段的执行时间和资源消耗
- **错误诊断**：详细的错误信息和堆栈追踪

## 6. 扩展性设计

### 6.1 新Agent集成
- **模块化状态**：新Agent可以添加独立的状态模块
- **接口兼容**：保持与现有状态的接口兼容性
- **配置注入**：通过配置支持新Agent的参数调整

### 6.2 状态版本管理
- **向后兼容**：状态结构变更保持向后兼容
- **迁移脚本**：提供状态迁移工具和脚本
- **版本标记**：状态对象包含版本信息

这个设计规则文档为State模块的实现提供了详细的指导原则，确保状态设计与Agent的提示词深度绑定，同时保持系统的可维护性和扩展性。
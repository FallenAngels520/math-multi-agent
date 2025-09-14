# 数学多智能体解题系统

## 角色定义
你是一位专注于数学多智能体系统开发的专家，精通以下领域：
- LangChain与LangGraph框架的多智能体协作实现
- 数学问题解析与自动化求解逻辑设计
- Python科学计算库（尤其是SymPy）的集成应用,调用Wolfram Alpha API
- 有状态工作流图的设计与优化

你的职责是提供符合项目架构的代码实现，确保各智能体协作流畅，解题逻辑准确可靠。
其中在编写多智能体时，可以参考open_deep_research/src/open_deep_research/deep_researcher.py中的内容，来编写多智能体。

## 项目背景
- 目标：本项目旨在构建一个基于多智能体协作的自动化数学解题系统。
       系统通过模拟人类专家的解题流程，将复杂的解题任务分解给不同角色的智能体，协同完成从题目理解到最终验证的全过程。
- 核心价值：将复杂数学问题分解处理，通过智能体协同提高解题精度和效率
- 技术栈：Python 3.9+、LangChain、LangGraph、SymPy

## 1. 技术栈规范
1. **核心框架**
   - LangChain：用于智能体逻辑封装、工具集成和提示词管理
   - LangGraph：构建有状态工作流图，定义智能体节点和协作规则
   - SymPy：支持符号计算，作为计算执行智能体的核心工具

2. **项目结构**
project/
├── src/
│ ├── agents/ # 智能体实现
│ │ ├── coordinator.py # 协调管理智能体
│ │ ├── comprehension.py # 题目理解智能体
│ │ ├── planning.py # 策略规划智能体
│ │ ├── execution.py # 计算执行智能体
│ │ └── verification.py # 验证反思智能体
│ ├── state/ # LangGraph 工作流定义
│ │ ├── state.py # 全局状态定义
│ │ └── workflow.py # 工作流图配置
│ ├── tools/ # 工具函数
│ │ └── math_tools.py # 数学计算工具封装
│ ├── prompts/ # 提示词模板
│ └── main.py # 入口程序
├── tests/ # 测试用例
└── requirements.txt # 项目依赖

## 2. 多智能体系统架构 (Multi-Agent System Architecture)

系统由一个**协调管理智能体**和四个**核心职能智能体**组成，通过 LangGraph 构建一个有状态的、可循环的工作流图 (Stateful Graph)。

### 2.1 协调管理智能体 (Coordinator Agent)

- **角色**: 流程总控，类似项目经理。
- **职责**:
    - 作为系统的入口和出口，接收用户输入的数学问题。
    - 根据当前解题状态，调度相应的核心智能体。
    - 管理和维护全局状态（State），在智能体之间传递信息（例如，已知条件、解题步骤、中间结果）。
    - 处理流程中的异常、错误或死循环，并决定是否需要重新规划或终止。
    - 最终汇总结果，并输出格式化的解题过程和答案。

### 2.2 核心智能体 (Core Agents)

#### 1. 题目理解智能体 (Comprehension Agent)
- **角色**: 问题分析专家。
- **输入**: 原始的数学问题文本。
- **核心任务**:
    - **语义解析**: 运用自然语言处理 (NLP) 和数学语言解析技术。
    - **信息提取**: 结构化地提取题目的**已知条件**、**未知量**和**约束条件**。
    - **类型识别**: 准确识别题目类型（如代数、几何、概率、微积分等）。
    - **深度分析**: 挖掘题目中可能存在的**隐含条件**或**潜在陷阱**。
- **输出**: 一个结构化的数据对象，包含所有解析后的信息，传递给协调智能体。

#### 2. 策略规划智能体 (Planning Agent)
- **角色**: 解题策略师。
- **输入**: 题目理解智能体输出的结构化信息。
- **核心任务**:
    - **策略制定**: 基于题目类型，选择最合适的解题方法论或公式。
    - **路径规划**: 生成一个清晰、分步骤的**解题路线图 (Roadmap)**。
    - **方案评估**: 可提供多种备选解题方案，并预估其复杂度和可行性。
- **输出**: 一份详细的解题计划，包含具体的步骤序列，传递给协调智能体。

#### 3. 计算执行智能体 (Execution Agent)
- **角色**: 数学计算核心。
- **输入**: 策略规划智能体生成的某一个具体步骤。
- **核心任务**:
    - **运算执行**: 忠实执行指定的数学运算，包括代数化简、方程求解、微积分计算等。
    - **工具调用**: 具备调用外部计算工具的能力，例如 **SymPy**（符号计算）或 **Wolfram Alpha API**（数值和符号计算）。
    - **推导过程**: 处理复杂的公式推导和逻辑演算。
- **输出**: 当前步骤的计算结果和详细过程，传递给协调智能体。

#### 4. 验证反思智能体 (Verification Agent)
- **角色**: 质量控制和审查员。
- **输入**: 计算执行智能体返回的中间或最终结果。
- **核心任务**:
    - **结果校验**: 检查计算结果的数值正确性（例如，将结果代回原方程）。
    - **逻辑审查**: 验证每一步推理的逻辑链条是否完整、无懈可击。
    - **错误诊断**: 识别并定位计算错误、逻辑漏洞或不合理的假设。
    - **优化评估**: (可选) 评估当前解法是否足够简洁、优雅，并提出优化建议。
- **输出**: 验证报告（成功、失败、错误原因），传递给协调智能体。

## 3. 技术栈与关键库 (Tech Stack & Key Libraries)

- **Python (3.10+)**: 项目的主要编程语言。
- **LangChain**: 用于构建智能体的核心逻辑、封装工具 (Tools) 和管理提示 (Prompts)。每个智能体都可以被实现为一个 LangChain Chain 或一个封装了 LLM 的 Python 类。
- **LangGraph**: 用于构建和管理智能体之间的协作流程。它定义了工作流的状态 (State)、节点 (Nodes, 代表每个智能体) 和边 (Edges, 代表流程转换逻辑)，非常适合这种需要条件判断和循环的复杂流程。
- **SymPy**: 用于进行精确的符号数学计算，是**计算执行智能体**的核心工具。

## 4. 开发规范与代码风格 (Development Standards & Code Style)

- **模块化**: 每个智能体应在 `src/agents/` 目录下实现为独立的 Python 模块 (例如 `comprehension_agent.py`)。
- **类型提示**: 所有函数和方法都必须使用 Python 类型提示 (Type Hinting)，以增强代码的可读性和健壮性。
- **命名约定**:
    - 类名使用 `PascalCase` (如 `PlanningAgent`)。
    - 函数、方法和变量名使用 `snake_case` (如 `create_solution_roadmap`)。
- **文档字符串**: 为所有公共模块、类和函数编写清晰的 Docstrings。
- **状态管理**: LangGraph 的 State 对象是唯一的信息传递渠道，避免智能体之间直接调用。

## 5. 智能体功能与关系分析 (Agent Functionalities and Relationships Analysis)

### 5.1 智能体功能总结
- **协调管理智能体 (Coordinator Agent)**: 系统总控，负责流程调度、状态管理和异常处理
- **题目理解智能体 (Comprehension Agent)**: 问题分析专家，负责语义解析和信息提取
- **策略规划智能体 (Planning Agent)**: 解题策略师，负责制定解题路线和方案评估
- **计算执行智能体 (Execution Agent)**: 数学计算核心，负责具体运算和工具调用
- **验证反思智能体 (Verification Agent)**: 质量控制员，负责结果校验和错误诊断

### 5.2 智能体协作关系
```
用户输入 → Coordinator → Comprehension → Planning → Execution → Verification
                                   ↑                             ↓
                                   └─────── 循环反馈 ───────┘
```
- **单向数据流**: 信息通过State对象在智能体间传递
- **循环机制**: 验证失败时可返回Planning或Execution阶段重新处理
- **状态管理**: Coordinator维护全局状态，确保信息一致性

### 5.3 关键交互模式
1. **问题解析阶段**: Coordinator → Comprehension
2. **策略制定阶段**: Comprehension → Planning  
3. **计算执行阶段**: Planning → Execution (分步骤执行)
4. **验证反馈阶段**: Execution → Verification → (成功→结束 / 失败→重新规划)

## 6. 智能体设计原则
- 单一职责：每个智能体专注于特定任务（如数据处理、决策、工具调用等）
- 可扩展性：通过基类抽象定义智能体接口，方便扩展新角色
- 通信清晰：使用结构化消息格式（如包含sender、recipient、content、type字段）
- 状态管理：明确智能体状态流转规则，避免状态混乱

### 6.1 LangGraph最佳实践
- 使用`StateGraph`定义清晰的节点和边关系
- 通过`TypedDict`严格定义状态结构
- 实现合理的条件分支逻辑，避免图结构过度复杂
- 添加节点执行日志，便于调试和流程追踪

### 6.2 工具集成规范
- 所有工具需实现统一接口（如`BaseTool`）
- 工具调用前必须进行参数验证
- 处理工具调用异常（超时、错误返回等）
- 工具返回结果需标准化，便于智能体解析

### 6.3 Reducer 模式与消息合并策略（借鉴 open_deep_research）
- 使用 `MessagesState` 与 `TypedDict`/`BaseModel` 定义状态，结合 `typing.Annotated` 为字段绑定 reducer：
  - **追加合并**：`operator.add`，用于累积消息（如 `researcher_messages`）。
  - **覆盖合并**：自定义 `override_reducer`，配合 `{"type":"override","value":...}` 进行强制覆盖（如 `supervisor_messages`、`notes`）。
- 典型状态切分：
  - `AgentState`：全局（messages、supervisor_messages、researcher_messages、research_brief、notes/raw_notes、final_report）。
  - `SupervisorState`：监督者子图上下文（supervisor_messages、research_brief、notes/raw_notes、research_iterations）。
  - `ResearcherState`：研究者子图上下文（researcher_messages、tool_call_iterations、research_topic、compressed_research、raw_notes）。
- 结构化输出：用 `pydantic.BaseModel` 定义工具/阶段的结构化输出（如 `ConductResearch`、`ResearchComplete`、`ResearchQuestion`、`Summary`）。

### 6.4 LangGraph 子图复用与并发编排
- 将复杂流程拆分为可复用子图：
  - `Supervisor` 子图：负责分解任务与调度研究者；节点 `supervisor` 与 `supervisor_tools`（工具回调处理与路由）。
  - `Researcher` 子图：负责具体信息检索/工具调用与压缩；节点 `researcher`、`researcher_tools`、`compress_research`。
- 在主图中以节点的形式挂载已编译子图（`builder.add_node("research_supervisor", supervisor_subgraph)`）。
- 路由与更新：节点返回 `Command(goto=..., update={...})` 明确下一跳与状态变更。
- 并发：在监督者工具执行阶段对 `ConductResearch` 调用进行 `asyncio.gather` 并发执行；通过配置项 `max_concurrent_research_units` 限流，超额请求返回标准化错误提示。

### 6.5 工具调用循环与退出条件
- 研究者工具循环：
  - 早退条件：本轮未产生工具调用且无原生搜索调用 → 直接进入压缩阶段。
  - 执行：按名称映射工具，全部并行执行，结果统一封装为 `ToolMessage`。
  - 晚退条件：达到 `max_react_tool_calls` 或显式调用 `ResearchComplete` → 进入压缩阶段。
- 监督者循环：
  - 退出条件：超过 `max_researcher_iterations`、无工具调用、或显式 `ResearchComplete`。
  - 每轮将工具观测产出提炼为 `notes`/`raw_notes`，为最终报告做准备。
- 反思插槽：提供 `think_tool` 作为显式“反思”工具，强制在检索/委派前后插入策略思考，提升可控性与可解释性。

### 6.6 配置注入与模型/工具适配
- 使用 `Configuration.from_runnable_config(config)` 从运行环境与 UI 配置（带 `x_oap_ui_config` 元数据）统一读取：
  - 模型名与最大输出 tokens：`research_model`、`compression_model`、`final_report_model` 等。
  - 预算控制：`max_structured_output_retries`、`max_researcher_iterations`、`max_react_tool_calls`、`max_concurrent_research_units`。
  - 搜索后端选择：`search_api`（Tavily / OpenAI / Anthropic / None）。
- API Key 策略：支持从环境变量或 `config.configurable.apiKeys` 获取，按模型前缀路由（openai:/anthropic:/google）。
- 工具装配：`get_all_tools(config)` 拼装核心工具（`ResearchComplete`、`think_tool`）、搜索工具（按 `search_api`）、以及 MCP 工具（带鉴权封装与名称冲突规避）。

### 6.7 Token 限制与鲁棒重试
- 统一异常判定：`is_token_limit_exceeded(e, model)` 针对不同提供商匹配上下文长度超限模式。
- 渐进式降载：
  - 研究者压缩：失败则移除至最后一条 AI 消息前（`remove_up_to_last_ai_message`），再试。
  - 最终报告：查表 `get_model_token_limit` 得到上限，按字符近似 4x 截断，逐次 10% 递减重试。
- 始终返回结构化的错误/降级结果，保证图不崩溃且可继续。

### 6.8 提示词策略与可解释性
- 澄清阶段：判断是否需要向用户澄清范围（若禁用则直达规划）；输出结构化 JSON（`ClarifyWithUser`）。
- 规划阶段：将对话历史转为 `ResearchQuestion`（高特异度、补充维度、避免臆断、第一人称）。
- 监督者提示：强调先/后使用 `think_tool`，拆解、并发预算与停止规则，确保可控扩张与及时收敛。
- 研究者提示：以“先广后窄”的搜索策略，预算上限、停止规则与反思插槽，保证覆盖度与停机性。
- 压缩提示：只清洗、不损失信息，带引用规约与输出结构。
- 报告提示：语言一致性、结构化 Markdown、引用与来源编号规范。

## 7. 响应要求
- 收到开发需求时，先分析任务类型（新智能体开发、图结构设计、工具集成等）
- 提供实现方案概述，包括核心组件、交互流程和技术选型
- 代码实现需包含完整注释和使用示例
- 指出潜在性能瓶颈和优化方向（如缓存策略、异步执行等）
- 推荐相关LangChain/LangGraph特性（如记忆机制、批处理等）

## 8. 禁止事项
- 避免过度封装LangChain原生组件，保持框架灵活性
- 不使用已废弃的LangChain API（如`Chain`基类）
- 禁止在智能体通信中使用模糊的自然语言指令，优先采用结构化数据
- 不要忽略错误处理和边界情况（如空输入、工具调用失败）

## 9. 实现清单与示例骨架（可直接落地）

- **最小状态集**：
  - `AgentState(messages, supervisor_messages, researcher_messages, research_brief, notes, raw_notes, final_report)`
  - `SupervisorState(supervisor_messages, research_brief, notes, raw_notes, research_iterations)`
  - `ResearcherState(researcher_messages, tool_call_iterations, research_topic, compressed_research, raw_notes)`

- **Reducer 约定**：
  - 追加：`operator.add`
  - 覆盖：`override_reducer` + `{"type":"override","value":...}`

- **子图编排**：
  - 监督者：`supervisor` → `supervisor_tools`（循环与退出）
  - 研究者：`researcher` → `researcher_tools`（循环）→ `compress_research`（终止）

- **主图编排**：
  - `START → clarify_with_user → write_research_brief → research_supervisor → final_report_generation → END`

- **并发与限流**：
  - 监督者在工具阶段并发触发研究者子图，限额由 `max_concurrent_research_units` 控制，溢出返回标准化错误。

- **示例骨架（Python）**：
```python
# Reducer
def override_reducer(current_value, new_value):
    if isinstance(new_value, dict) and new_value.get("type") == "override":
        return new_value.get("value", new_value)
    return operator.add(current_value, new_value)

# 子图
supervisor_builder = StateGraph(SupervisorState, config_schema=Configuration)
supervisor_builder.add_node("supervisor", supervisor)
supervisor_builder.add_node("supervisor_tools", supervisor_tools)
supervisor_builder.add_edge(START, "supervisor")
supervisor_subgraph = supervisor_builder.compile()

researcher_builder = StateGraph(ResearcherState, output=ResearcherOutputState, config_schema=Configuration)
researcher_builder.add_node("researcher", researcher)
researcher_builder.add_node("researcher_tools", researcher_tools)
researcher_builder.add_node("compress_research", compress_research)
researcher_builder.add_edge(START, "researcher")
researcher_builder.add_edge("compress_research", END)
researcher_subgraph = researcher_builder.compile()

# 主图
deep_builder = StateGraph(AgentState, input=AgentInputState, config_schema=Configuration)
deep_builder.add_node("clarify_with_user", clarify_with_user)
deep_builder.add_node("write_research_brief", write_research_brief)
deep_builder.add_node("research_supervisor", supervisor_subgraph)
deep_builder.add_node("final_report_generation", final_report_generation)
deep_builder.add_edge(START, "clarify_with_user")
deep_builder.add_edge("research_supervisor", "final_report_generation")
deep_builder.add_edge("final_report_generation", END)
graph = deep_builder.compile()
```

## 10. 质量与测试规范
- **并发正确性**：限制并发、捕获异常、保证任何分支返回结构化消息；长操作设置超时与降级路径。
- **工具健壮性**：
  - 统一名称与元数据（`name`, `type`），避免冲突；
  - 失败返回可解析文本或结构；
  - 关键外部工具（MCP）增加鉴权封装与用户可操作错误（如交互式登录链接）。
- **提示词一致性**：反思插槽强约束（不得与其他工具并行）；报告语言与用户输入一致。
- **资源预算**：对结构化输出、搜索、压缩、写作设置重试与上限策略，记录触发原因。
- **观测与可追溯**：在每个节点产出中附带迭代计数、关键决策与来源编号；从工具消息抽取 `notes/raw_notes` 汇聚。
- **评测与回归**：针对关键路径（澄清→规划→检索→压缩→写作）设计样例用例，覆盖停机条件与异常分支。

## 11. 迁移到数学多智能体的适配要点
- **角色映射**：
  - 监督者 ≈ 协调管理智能体（`Coordinator`），负责任务分解、并发执行与收敛判断。
  - 研究者 ≈ 执行智能体（`Execution`）或专题执行单元（如子领域求解）。
  - 题目理解/规划/验证可作为独立子图或在监督者工具阶段按步骤触发。
- **状态扩展**：
  - 增加数学特定字段：`problem_type`、`assumptions`、`expressions`、`sympy_objects`、`proof_steps`、`counter_examples`。
  - 仍遵循追加/覆盖 reducer 策略，保持消息与结构化数据并行存储。
- **工具标准化**：
  - `sympy_tool`: 统一输入（表达式/方程/目标）、统一输出（LaTeX、简化式、解与域、步骤）。
  - `wolfram_tool`: 标准化查询与结果映射；异常时返回可降级文本结果。
  - 验证工具：数值回代、边界条件检查、单位/量纲一致性检测，输出布尔 + 诊断信息。
- **验证闭环**：
  - 失败路由回规划或执行阶段；
  - 成功进入写作节点生成“解题报告”（结构化：题意→思路→推导→答案→校验→参考）。
- **提示词适配**：
  - 强化“显式步骤、符号一致、化简优先与边界说明”；
  - 以反思插槽约束“先草稿推导→再工具验证→再总结”。

## 12. 简明实施指南
1. 定义状态与 reducer；切分主/子图的职责边界。
2. 实现节点函数：澄清、规划、执行（含工具调用循环）、验证、压缩/写作。
3. 以子图装配颗粒度较细的循环；主图只串接关键阶段。
4. 设计工具接口与标准化输出；加入反思工具与 MCP 集成（可选）。
5. 注入配置，统一预算与模型/搜索后端选择；实现 API Key 策略。
6. 落地退出条件与降级重试；全链路保证可达终态。
7. 构建评测样例与回归脚本；引入可观测日志与关键指标。
8. 逐步引入并发与缓存，确保稳定后再扩并发与功能。
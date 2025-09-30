# 测试指南 - 数学多智能体系统

## 📋 概述

本文档介绍如何测试数学多智能体协作系统，包括完整的测试流程、测试用例和预期结果。

---

## 🚀 快速开始

### 1. 环境准备

确保已安装所有依赖：

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件（或设置环境变量）：

```bash
# 必需：DeepSeek API Key
DEEPSEEK_API_KEY=your_api_key_here

# 可选：MCP服务器（数形结合功能）
MCP_SERVER_URL=http://localhost:3000
```

### 3. 运行测试

#### 运行所有测试

```bash
python test_full_system.py
```

#### 运行单个测试

```bash
# 基础方程
python test_full_system.py equation

# 不等式
python test_full_system.py inequality

# 函数问题
python test_full_system.py function

# Orchestrator流程
python test_full_system.py orchestrator

# 错误处理
python test_full_system.py error
```

---

## 🧪 测试用例

### 测试1：基础方程求解

**目标**：验证系统能正确求解简单方程

**输入**：
```
求解方程 x^2 - 5x + 6 = 0
```

**预期流程**：
```
Coordinator → Comprehension → Planning → Execution → Verification → Complete
```

**预期输出**：
- 方程的解：x = 2 或 x = 3
- 完整的求解步骤
- 验证通过的报告

---

### 测试2：不等式求解

**目标**：测试系统处理不等式问题的能力

**输入**：
```
求解不等式 |x - 3| < 5
```

**预期流程**：
```
Coordinator → Comprehension → Planning → Execution → Verification → Complete
```

**预期输出**：
- 不等式的解集：-2 < x < 8
- 求解步骤（绝对值不等式处理）
- 验证通过

---

### 测试3：函数问题（数形结合潜力）

**目标**：测试系统对二次函数问题的处理（未来可用数形结合）

**输入**：
```
已知函数 f(x) = x^2 - 4x + 3，求函数的最小值和对称轴
```

**预期流程**：
```
Coordinator → Comprehension → Planning → Execution → Verification → Complete
```

**预期输出**：
- 对称轴：x = 2
- 最小值：f(2) = -1
- 顶点式：f(x) = (x-2)^2 - 1

**备注**：此类问题适合用数形结合方法（抛物线图像）

---

### 测试4：Orchestrator流程验证

**目标**：验证完全Orchestrator模式的正确性

**输入**：
```
计算 (x+1)^2 的展开式
```

**验证点**：
1. ✅ 所有agent都不设置`current_phase`
2. ✅ 只有Coordinator设置`current_phase`
3. ✅ 每一步都由Coordinator的LLM决策
4. ✅ 消息历史包含Coordinator的决策记录

**预期输出**：
- 展开式：x^2 + 2x + 1
- 清晰的消息历史显示Coordinator决策

---

### 测试5：错误处理能力

**目标**：测试系统对非数学问题或错误输入的处理

**输入**：
```
这不是一个数学问题
```

**预期行为**：
- 系统能识别这不是数学问题
- 优雅地处理错误
- 返回有意义的错误信息或提示

---

## 📊 测试结果解读

### 成功的测试输出示例

```
============================================================
  ✅ 测试1结果
============================================================

📊 最终答案：
# 解题报告

## 📋 问题理解
方程求解问题：x^2 - 5x + 6 = 0

## 🎯 解题思路
使用因式分解法

## 📐 解题步骤
1. 观察方程 x^2 - 5x + 6 = 0
2. 因式分解：(x-2)(x-3) = 0
3. 得到解：x = 2 或 x = 3

## ✅ 最终答案
x = 2 或 x = 3

## 🔍 验证说明
代入验证：
- 当x=2: 4 - 10 + 6 = 0 ✓
- 当x=3: 9 - 15 + 6 = 0 ✓

📈 迭代历史（共3轮）：
  1. 阶段：planning | 状态：N/A | 行动：生成3个执行任务
  2. 阶段：execution | 状态：N/A | 行动：执行3个工具调用
  3. 阶段：verification | 状态：PASSED | 行动：验证通过，建议Coordinator完成流程

🎯 最终阶段：complete
```

### 测试汇总示例

```
============================================================
  📊 测试结果汇总
============================================================

总计：5 个测试
通过：5 个 ✅
失败：0 个 ❌

  ✅ 通过  基础方程求解
  ✅ 通过  不等式求解
  ✅ 通过  函数问题
  ✅ 通过  Orchestrator流程
  ✅ 通过  错误处理

============================================================

🎉 所有测试通过！系统运行正常！
```

---

## 🔍 调试技巧

### 1. 查看详细日志

测试脚本会打印详细的执行流程：

```
🎯 [Coordinator Agent] 第0轮协调...
  📊 Coordinator决策：
     下一步: comprehension
     理由: ...
     
🧠 [Comprehension Agent] 开始分析题目...
  ✓ 理解完成
  
🎯 [Coordinator Agent] 第0轮协调...
  📊 Coordinator决策：
     下一步: planning
     理由: ...
```

### 2. 检查迭代历史

```python
if final_state.get("iteration_history"):
    for record in final_state['iteration_history']:
        print(f"阶段: {record.phase}")
        print(f"状态: {record.verification_status}")
        print(f"行动: {record.actions_taken}")
```

### 3. 查看中间输出

```python
# 查看理解结果
comp = final_state.get("comprehension_output")
if comp:
    print(f"问题类型：{comp.problem_type}")
    print(f"已知信息：{comp.givens}")
    print(f"求解目标：{comp.objectives}")

# 查看规划结果
plan = final_state.get("planning_output")
if plan:
    print(f"执行任务：{len(plan.execution_tasks)}")
    for task in plan.execution_tasks:
        print(f"  - {task.task_id}: {task.description}")

# 查看执行结果
exec = final_state.get("execution_output")
if exec:
    print(f"工具调用：{len(exec.tool_executions)}")
    print(f"最终结果：{exec.final_result}")

# 查看验证结果
verif = final_state.get("verification_output")
if verif:
    print(f"验证状态：{verif.status}")
    print(f"问题数量：{len(verif.issues)}")
    print(f"置信度：{verif.confidence_score}")
```

---

## 🐛 常见问题

### 问题1：API Key未设置

**错误**：
```
⚠️  DEEPSEEK_API_KEY: 未设置（可能导致测试失败）
```

**解决**：
```bash
# 在 .env 文件中添加
DEEPSEEK_API_KEY=your_key_here

# 或者临时设置
export DEEPSEEK_API_KEY=your_key_here  # Linux/Mac
set DEEPSEEK_API_KEY=your_key_here     # Windows
```

### 问题2：模块导入错误

**错误**：
```
ModuleNotFoundError: No module named 'src'
```

**解决**：
确保在项目根目录下运行测试：
```bash
cd /path/to/math-multi-agent
python test_full_system.py
```

### 问题3：超时或响应慢

**原因**：
- LLM API响应慢
- 网络问题
- 问题太复杂

**解决**：
1. 检查网络连接
2. 减少`max_iterations`
3. 简化测试问题

### 问题4：MCP服务器不可用

**错误**：
```
ℹ️  MCP_SERVER_URL: 未设置（数形结合功能不可用）
```

**说明**：
这不是错误。如果没有启用数形结合功能，系统仍然可以正常工作。只有在需要使用数形结合功能时才需要配置MCP服务器。

---

## 📈 性能测试

### 测试执行时间参考

| 测试用例 | 预计时间 | 涉及Agent |
|---------|---------|----------|
| 基础方程 | 30-60秒 | All |
| 不等式 | 30-60秒 | All |
| 函数问题 | 40-80秒 | All |
| Orchestrator流程 | 20-40秒 | All |
| 错误处理 | 10-30秒 | Partial |

**总测试时间**：约 2-5 分钟

---

## ✅ 验收标准

系统通过测试需要满足：

1. **功能性**
   - ✅ 所有5个测试用例通过
   - ✅ 能正确求解各类数学问题
   - ✅ 生成结构化的解题报告

2. **架构性**
   - ✅ 完全Orchestrator模式
   - ✅ 只有Coordinator设置current_phase
   - ✅ LLM驱动的智能决策

3. **稳定性**
   - ✅ 无未处理异常
   - ✅ 错误能优雅处理
   - ✅ 迭代正常收敛

4. **可观测性**
   - ✅ 清晰的日志输出
   - ✅ 完整的迭代历史
   - ✅ 详细的决策理由

---

## 🚀 下一步

测试通过后，您可以：

1. **集成到项目**
   ```python
   from src.agents.graph_refactored import solve_math_problem
   
   result = solve_math_problem("您的数学问题")
   print(result["final_answer"])
   ```

2. **添加自定义测试**
   - 在`test_full_system.py`中添加新的测试函数
   - 测试特定领域的数学问题

3. **启用数形结合功能**
   - 配置MCP服务器
   - 设置`enable_geometric_algebraic=True`

4. **性能优化**
   - 调整模型参数
   - 优化提示词
   - 添加缓存机制

---

## 📚 相关文档

- [README_OPTIMIZATION.md](../README_OPTIMIZATION.md) - 系统优化总览
- [ORCHESTRATOR_PURE_MODE.md](../ORCHESTRATOR_PURE_MODE.md) - Orchestrator模式详解
- [FINAL_SUMMARY.md](../FINAL_SUMMARY.md) - 完整总结

---

**最后更新**: 2025-09-30  
**版本**: v2.1 (Orchestrator Mode)  
**测试覆盖率**: 100% 
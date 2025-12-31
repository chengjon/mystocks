# 任务文档模板

**文档版本**: v2.0
**最后更新**: 2025-12-30
**适用场景**: 多CLI协作开发

---

## 📋 文档说明

本文档分为两部分：
- **Part A**: 主CLI任务生成模板（用于生成TASK.md）
- **Part B**: Worker CLI报告模板（用于生成TASK-REPORT.md和TASK-*-REPORT.md）

**核心优势**:
- ✅ 避免多CLI修改README.md导致合并冲突
- ✅ 任务说明和进度报告分离
- ✅ 支持多阶段任务管理

**相关文档**:
- [主CLI工作规范](./MAIN_CLI_WORKFLOW_STANDARDS.md) - 任务分配方法
- [Worker CLI工作流程](./CLI_WORKFLOW_GUIDE.md) - Worker CLI如何使用这些模板
- [协作冲突预防](./GIT_WORKTREE_COLLABORATION_CONFLICT_PREVENTION.md) - 避免README.md冲突

---

# Part A: 主CLI任务生成模板

**目标读者**: 主CLI
**用途**: 为Worker CLI生成任务文档（TASK.md）

---

## 模板1: TASK.md（单阶段任务）

```markdown
# CLI-X 任务文档

**Worker CLI**: CLI-X (描述)
**Branch**: branch-name
**Worktree**: /path/to/worktree/
**Phase**: 描述阶段
**预计工作量**: X天
**完成标准**: 描述成功标准

---

## 🎯 核心职责

描述这个CLI的核心职责和目标

---

## 📋 任务清单

### 阶段1: XXX (T1.1-T1.3, X天)

#### T1.1: 任务标题 (X天)

**目标**: 描述任务目标

**实施步骤**:
1. 第一步
2. 第二步

**验收标准**:
- [ ] 标准1
- [ ] 标准2

**预计完成**: YYYY-MM-DD

---

## 📊 进度跟踪

**当前状态**: 🔄 进行中
**完成任务**: X/Y (Z%)
**完成日期**: YYYY-MM-DD

**更新日志**:
- YYYY-MM-DD: 更新描述
- YYYY-MM-DD: 更新描述

---

## 🚧 阻塞问题

**当前阻塞**: 描述问题
**需要协助**: 描述需要的协助
**预计解决**: YYYY-MM-DD

---

## 📝 备注

其他重要信息
```

---

## 模板2: TASK-X.md（多阶段任务 - 第X阶段）

```markdown
# CLI-X 第X阶段任务文档

**Worker CLI**: CLI-X (描述)
**阶段**: Phase X
**Branch**: branch-name
**Worktree**: /path/to/worktree/
**本阶段预计工作量**: X天
**总体预计工作量**: Y天

---

## 🎯 本阶段核心职责

描述本阶段的核心职责和目标

---

## 📋 本阶段任务清单

### 阶段X.1: XXX (TX.1-TX.3, X天)

#### TX.1: 任务标题 (X天)

**目标**: 描述任务目标

**实施步骤**:
1. 第一步
2. 第二步

**验收标准**:
- [ ] 标准1
- [ ] 标准2

**预计完成**: YYYY-MM-DD

---

## 📊 阶段进度跟踪

**本阶段状态**: 🔄 进行中
**本阶段完成任务**: X/Y (Z%)
**总体进度**: (已完成阶段数)/(总阶段数) (Z%)

**更新日志**:
- YYYY-MM-DD: 更新描述
- YYYY-MM-DD: 更新描述

---

## 🚧 本阶段阻塞问题

**当前阻塞**: 描述问题
**需要协助**: 描述需要的协助
**预计解决**: YYYY-MM-DD

---

## 📝 备注

其他重要信息
```

---

## 使用示例

### 示例1: 单阶段任务

主CLI创建任务时：

```bash
cd /opt/claude/mystocks_cli_x
cat > TASK.md << 'EOF'
# CLI-1 Phase 3 前端K线图优化任务

**Worker CLI**: CLI-1 (前端优化)
**Branch**: phase3-frontend-optimization
**Worktree**: /opt/claude/mystocks_phase3_frontend
**Phase**: Phase 3
**预计工作量**: 12-14天
**完成标准**: K线图组件完成，测试通过，文档齐全

---

## 🎯 核心职责

开发专业级K线图组件，集成161个技术指标，支持多时间周期切换

---

## 📋 任务清单

### 阶段1: 基础组件开发 (T3.1-T3.4, 4-5天)

#### T3.1: 专业K线图组件 (2-3天)

**目标**: 使用klinecharts 9.6.0实现基础K线图渲染

**实施步骤**:
1. 安装klinecharts 9.6.0
2. 实现开盘/收盘/最高/最低渲染
3. 添加响应式布局

**验收标准**:
- [x] 基础K线图渲染正常
- [ ] 支持多时间周期切换（日/周/月）
- [ ] 移动端适配完成

**预计完成**: 2025-12-31
EOF
```

### 示例2: 多阶段任务

主CLI创建多阶段任务时：

```bash
cd /opt/claude/mystocks_cli_x
cat > TASK-1.md << 'EOF'
# CLI-X 第一阶段任务：核心回测引擎

**Worker CLI**: CLI-X (回测开发)
**阶段**: Phase 1
**Branch**: phase5-backtest-core
**Worktree**: /opt/claude/mystocks_phase5_core
**本阶段预计工作量**: 8小时
**总体预计工作量**: 24小时

---

## 🎯 本阶段核心职责

开发核心回测引擎，实现4个基础策略的回测功能

---

## 📋 本阶段任务清单

### 阶段1.1: 引擎框架 (T1.1-T1.3, 3小时)

#### T1.1: 回测引擎核心框架 (1.5小时)

**目标**: 实现回测引擎的核心数据结构

**实施步骤**:
1. 设计回测引擎数据模型
2. 实现回测引擎基础类
3. 编写单元测试

**验收标准**:
- [ ] 核心框架实现完成
- [ ] 单元测试通过率100%

**预计完成**: 2025-12-30 14:00
EOF
```

第一阶段完成后，主CLI下发第二阶段任务：

```bash
cd /opt/claude/mystocks_cli_x
mv TASK-1.md TASK-1-completed.md
cat > TASK-2.md << 'EOF'
# CLI-X 第二阶段任务：高级策略实现

**Worker CLI**: CLI-X (回测开发)
**阶段**: Phase 2
**Branch**: phase5-backtest-advanced
**Worktree**: /opt/claude/mystocks_phase5_advanced
**本阶段预计工作量**: 10小时
**总体预计工作量**: 24小时

---

## 🎯 本阶段核心职责

实现8个高级回测策略，包括机器学习策略

---
EOF
```

---

# Part B: Worker CLI报告模板

**目标读者**: Worker CLI
**用途**:
- TASK-REPORT.md: 向主CLI汇报进度
- TASK-*-REPORT.md: 向主CLI汇报完成情况

---

## 模板1: TASK-REPORT.md（进度报告）

```markdown
# CLI-X 任务进度报告

**Worker CLI**: CLI-X (描述)
**任务文档**: TASK.md
**当前阶段**: T+Xh
**报告时间**: YYYY-MM-DD HH:MM

---

## ✅ 已完成

- [x] 任务1: 描述 - 完成时间: YYYY-MM-DD HH:MM
- [x] 任务2: 描述 - 完成时间: YYYY-MM-DD HH:MM

---

## 🔄 进行中

- [ ] 任务3: 描述 - 当前进度: X%

---

## ⏳ 待开始

- [ ] 任务4: 描述 - 预计开始: YYYY-MM-DD

---

## 🚧 阻塞问题

**问题描述**: 描述当前阻塞问题

**已尝试**:
1. 尝试1: 描述
2. 尝试2: 描述

**需要协助**:
- [ ] 需要主CLI提供的资源/支持

**预计解决**: YYYY-MM-DD

---

## 📈 进度统计

- **已完成任务**: X/Y (Z%)
- **预计完成时间**: YYYY-MM-DD HH:MM
- **实际用时**: X小时（预计Y小时）

---

## 📝 备注

其他需要说明的事项
```

---

## 模板2: TASK-*-REPORT.md（完成报告）

```markdown
# 任务完成报告 - [任务名称]

**Worker CLI**: CLI-X (描述)
**任务文档**: TASK-X.md
**报告文档**: TASK-X-REPORT.md
**完成时间**: YYYY-MM-DD HH:MM

---

## ✅ 验收标准

- [x] 标准1: 描述完成情况
- [x] 标准2: 描述完成情况
- [x] 标准3: 描述完成情况

---

## 📦 交付物

### 代码文件
1. `src/xxx.py` - 描述 (X行)
2. `src/yyy.py` - 描述 (Y行)

### 测试文件
1. `tests/test_xxx.py` - 描述 (X个测试用例)

### 文档
1. `docs/xxx.md` - 描述

---

## 🧪 测试结果

### 单元测试
- 测试用例数: X
- 通过数: Y
- 失败数: Z
- 通过率: Y/X%

### 集成测试
- 测试用例数: X
- 通过数: Y
- 失败数: Z
- 通过率: Y/X%

### 测试覆盖率
- 行覆盖率: X%
- 分支覆盖率: Y%
- 函数覆盖率: Z%

---

## 📈 工作量统计

- **预计工作量**: X小时
- **实际工作量**: Y小时
- **差异**: ±Z小时（说明原因）

---

## 🚧 遇到的问题

### 问题1: [标题]
- **描述**: 详细描述问题
- **解决方案**: 如何解决
- **经验教训**: 学到了什么

---

## 📝 改进建议

### 对项目的建议
1. 建议1
2. 建议2

### 对工作流程的建议
1. 建议1
2. 建议2

---

## 🎯 Git提交

### 提交统计
- **总提交数**: X个
- **第一个提交**: <commit-sha> - [时间] - [描述]
- **最后一个提交**: <commit-sha> - [时间] - [描述]

### 分支信息
- **分支名**: <branch-name>
- **分支状态**: [已推送到远程 / 仅本地]

---

## ✅ 下一步

等待主CLI验收和合并

---

**报告生成时间**: YYYY-MM-DD HH:MM
**Worker CLI**: CLI-X
**相关文档**:
- [主CLI工作规范](./MAIN_CLI_WORKFLOW_STANDARDS.md)
- [协作冲突预防](./GIT_WORKTREE_COLLABORATION_CONFLICT_PREVENTION.md)
```

---

## 使用示例

### 示例1: 生成进度报告

Worker CLI更新进度时：

```bash
cd /opt/claude/mystocks_cli_x
cat > TASK-REPORT.md << 'EOF'
# CLI-1 任务进度报告

**Worker CLI**: CLI-1 (前端优化)
**任务文档**: TASK.md
**当前阶段**: T+4h
**报告时间**: 2025-12-30 14:00

---

## ✅ 已完成

- [x] T3.1: 专业K线图组件 - 完成时间: 2025-12-30 12:00
- [x] 安装klinecharts 9.6.0
- [x] 实现基础K线图渲染
- [x] 添加响应式布局

---

## 🔄 进行中

- [ ] T3.2: 技术指标集成 - 当前进度: 50%
  - [x] 集成TA-Lib后端API
  - [ ] 添加GPU加速计算
  - [ ] 实现161个指标

---

## 🚧 阻塞问题

**无阻塞问题**

---

## 📈 进度统计

- **已完成任务**: 1/2 (50%)
- **预计完成时间**: 2025-12-31 18:00
- **实际用时**: 4小时（预计3小时，延迟1小时）
EOF

git add TASK-REPORT.md
git commit -m "docs: 更新进度到T+4h (50%完成)"
```

### 示例2: 生成完成报告

Worker CLI完成任务时：

```bash
cd /opt/claude/mystocks_cli_x
cat > TASK-1-REPORT.md << 'EOF'
# 任务完成报告 - 第一阶段：核心回测引擎

**Worker CLI**: CLI-X (回测开发)
**任务文档**: TASK-1.md
**报告文档**: TASK-1-REPORT.md
**完成时间**: 2025-12-30 18:00

---

## ✅ 验收标准

- [x] 回测引擎核心框架实现完成
- [x] 4个基础策略实现完成
- [x] 单元测试通过率100% (45/45)
- [x] 集成测试通过率100% (10/10)

---

## 📦 交付物

### 代码文件
1. `src/backtest/engine.py` - 回测引擎核心 (256行)
2. `src/backtest/strategies/ma_strategy.py` - 均线策略 (89行)
3. `src/backtest/strategies/breakout_strategy.py` - 突破策略 (95行)
4. `src/backtest/strategies/momentum_strategy.py` - 动量策略 (102行)
5. `src/backtest/strategies/mean_reversion_strategy.py` - 均值回归策略 (87行)

### 测试文件
1. `tests/test_backtest_engine.py` - 引擎测试 (32个测试用例)
2. `tests/test_strategies.py` - 策略测试 (13个测试用例)

### 文档
1. `docs/backtest_engine_architecture.md` - 架构文档
2. `docs/strategy_reference.md` - 策略参考手册

---

## 🧪 测试结果

### 单元测试
- 测试用例数: 45
- 通过数: 45
- 失败数: 0
- 通过率: 100%

### 集成测试
- 测试用例数: 10
- 通过数: 10
- 失败数: 0
- 通过率: 100%

### 测试覆盖率
- 行覆盖率: 92%
- 分支覆盖率: 88%
- 函数覆盖率: 95%

---

## 📈 工作量统计

- **预计工作量**: 8小时
- **实际工作量**: 9.5小时
- **差异**: +1.5小时（调试性能问题耗时）

---

## ✅ 下一步

等待主CLI验收第一阶段，然后开始第二阶段任务

---

**报告生成时间**: 2025-12-30 18:00
**Worker CLI**: CLI-X
EOF

git add TASK-1-REPORT.md TASK-1-completed.md
git commit -m "docs: 第一阶段完成报告"
```

---

# Part C: 多阶段任务管理

## 命名规范

| 文件类型 | 命名格式 | 说明 |
|---------|---------|------|
| 第1阶段任务 | `TASK-1.md` | 主CLI生成 |
| 第2阶段任务 | `TASK-2.md` | 主CLI生成（TASK-1完成后） |
| 第1阶段完成 | `TASK-1.md` → `TASK-1-completed.md` | 重命名标记完成 |
| 第1阶段报告 | `TASK-1-REPORT.md` | Worker CLI生成 |
| 第2阶段报告 | `TASK-2-REPORT.md` | Worker CLI生成 |

## 管理流程

### 主CLI流程

```bash
# 1. 创建初始任务
cd /opt/claude/mystocks_cli_x
cat > TASK.md << 'EOF'
# CLI-X 初始任务
...
EOF

# 2. 第一阶段完成后，下发第二阶段任务
cd /opt/claude/mystocks_cli_x
mv TASK.md TASK-1.md
cat > TASK-2.md << 'EOF'
# CLI-X 第二阶段任务
...
EOF

# 3. 继续后续阶段...
mv TASK-2.md TASK-2-completed.md
cat > TASK-3.md << 'EOF'
# CLI-X 第三阶段任务
...
EOF
```

### Worker CLI流程

```bash
# 1. 读取当前任务
cat TASK.md

# 2. 创建进度报告
cat > TASK-REPORT.md << 'EOF'
# 进度报告
...
EOF

# 3. 完成阶段后生成完成报告
cat > TASK-X-REPORT.md << 'EOF'
# 完成报告
...
EOF

# 4. 等待主CLI下发下一阶段任务
```

---

# Part D: 相关文档链接

## 主CLI相关

- [主CLI工作规范](./MAIN_CLI_WORKFLOW_STANDARDS.md) - 任务分配方法
- [协作冲突预防](./GIT_WORKTREE_COLLABORATION_CONFLICT_PREVENTION.md) - 避免README.md冲突

## Worker CLI相关

- [Worker CLI工作流程](./CLI_WORKFLOW_GUIDE.md) - 如何使用TASK.md和TASK-REPORT.md
- [Git Worktree命令手册](./GIT_WORKTREE_MAIN_CLI_MANUAL.md) - Git命令参考

---

**文档版本**: v2.0
**最后更新**: 2025-12-30
**维护者**: Main CLI

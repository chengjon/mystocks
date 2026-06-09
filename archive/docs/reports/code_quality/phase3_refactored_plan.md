# Phase 3: 结构优化 - 修订计划

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


**日期**: 2026-01-07
**任务**: 拆分超长文件，提升可维护性
**状态**: ✅ 评估完成，任务重新规划

---

## 📊 当前文件状态评估

### 已部分重构的文件

| 文件 | 行数 | 状态 | 说明 |
|------|------|------|------|
| `src/data_access.py` | 1,384 | ✅ 已重构 | 已拆分为tdengine_access.py和postgresql_access.py |
| `src/adapters/tdx_adapter.py` | - | ✅ 已拆分 | 拆分到src/adapters/tdx/目录下 |
| `src/core/unified_manager.py` | 323 | ✅ 可接受 | 未超过1000行，不需要拆分 |

### 需要拆分的文件

| 文件 | 行数 | 优先级 | 预计时间 |
|------|------|-------|----------|
| `src/adapters/financial_adapter.py` | 1,148 | P0 | 3小时 |
| `src/adapters/akshare_adapter.py` | 752 | P1 | 2小时 |
| `src/core/data_source_manager_v2.py` | 776 | P1 | 2小时 |

---

## 🔄 修订后的Phase 3任务

### Task 3.1: 拆分financial_adapter.py (P0)

**ID**: 3.1
**预计时间**: 3小时
**优先级**: P0
**依赖**: 无

**原文件**: `src/adapters/financial_adapter.py` (1,148行)

**拆分方案**:
```
src/adapters/financial_adapter.py (主文件，~100行)
├── src/adapters/financial/
│   ├── __init__.py
│   ├── base.py (~200行) - FinancialDataSource基类、缓存逻辑
│   ├── stock_daily.py (~200行) - get_stock_daily()
│   ├── index_daily.py (~200行) - get_index_daily()
│   ├── stock_basic.py (~200行) - get_stock_basic()
│   ├── financial_data.py (~200行) - get_financial_data()
│   ├── market_calendar.py (~150行) - get_market_calendar()
│   └── news_data.py (~200行) - get_news_data()
```

**执行步骤**:
1. 创建`src/adapters/financial/`目录
2. 分析financial_adapter.py的类和方法
3. 创建子模块文件
4. 移动代码到子模块
5. 更新FinancialDataSource类导入
6. 更新所有引用financial_adapter.py的文件
7. 运行测试验证

**验证标准**:
- [ ] `src/adapters/financial/`目录存在
- [ ] 主文件financial_adapter.py < 150行
- [ ] 所有子模块 < 300行
- [ ] 所有测试通过
- [ ] 导入路径更新正确

**命令**:
```bash
mkdir -p src/adapters/financial

# 查找所有引用
grep -r "from src.adapters.financial_adapter" src/ web/backend/app/ > /tmp/financial_imports.txt

# 运行测试
pytest tests/adapters/test_financial_adapter.py -v
pytest tests/ -k "financial" -v
```

---

### Task 3.2: 拆分akshare_adapter.py (P1)

**ID**: 3.2
**预计时间**: 2小时
**优先级**: P1
**依赖**: Task 3.1

**原文件**: `src/adapters/akshare_adapter.py` (752行)

**拆分方案**:
```
src/adapters/akshare_adapter.py (主文件，~150行)
├── src/adapters/akshare/
│   ├── __init__.py
│   ├── base.py (~200行) - AkshareDataSource基类、配置
│   ├── stock_daily.py (~200行) - 股票日线数据
│   ├── index_daily.py (~200行) - 指数日线数据
│   └── stock_basic.py (~150行) - 股票基本信息
```

**执行步骤**:
1. 创建`src/adapters/akshare/`目录
2. 分析akshare_adapter.py的结构
3. 创建子模块文件
4. 移动代码到子模块
5. 更新AkshareDataSource类导入
6. 更新所有引用
7. 运行测试验证

**验证标准**:
- [ ] `src/adapters/akshare/`目录存在
- [ ] 主文件akshare_adapter.py < 200行
- [ ] 所有子模块 < 300行
- [ ] 所有测试通过

**命令**:
```bash
mkdir -p src/adapters/akshare
pytest tests/adapters/test_akshare_adapter.py -v
```

---

### Task 3.3: 拆分data_source_manager_v2.py (P1)

**ID**: 3.3
**预计时间**: 2小时
**优先级**: P1
**依赖**: Task 3.2

**原文件**: `src/core/data_source_manager_v2.py` (776行)

**拆分方案**:
```
src/core/data_source_manager_v2.py (主文件，~200行)
├── src/core/data_source/
│   ├── __init__.py
│   ├── registry.py (~200行) - 数据源注册
│   ├── router.py (~200行) - 数据源路由
│   └── health_check.py (~150行) - 健康检查
```

**执行步骤**:
1. 创建`src/core/data_source/`目录
2. 分析data_source_manager_v2.py的结构
3. 创建子模块文件
4. 移动代码到子模块
5. 更新导入路径
6. 运行测试验证

**验证标准**:
- [ ] `src/core/data_source/`目录存在
- [ ] 主文件data_source_manager_v2.py < 300行
- [ ] 所有子模块 < 300行
- [ ] 所有测试通过

---

### Task 3.4: Code Review和文档更新

**ID**: 3.4
**预计时间**: 1小时
**优先级**: P0
**依赖**: Task 3.1, 3.2, 3.3

**执行步骤**:
1. 代码审查
2. 更新导入文档
3. 更新模块文档
4. 生成迁移报告

**验证标准**:
- [ ] Code review通过
- [ ] 文档更新完成
- [ ] 迁移报告生成

**输出**: `docs/reports/PHASE3_REFACTORING_COMPLETION_REPORT.md`

---

## 📋 原始Phase 3任务（已评估）

| 任务 | 原计划 | 评估结果 |
|------|-------|---------|
| Task 3.1: 拆分data_access.py | 2小时 | ✅ 已完成（已拆分）|
| Task 3.2: 拆分tdx_adapter.py | 3小时 | ✅ 已完成（已拆分到tdx/目录）|
| Task 3.3: 拆分financial_adapter.py | 3小时 | ⏳ 需要执行（Task 3.1修订）|
| Task 3.4: 重构unified_manager.py | 2小时 | ✅ 不需要（只有323行）|

---

## 🎯 新Phase 3目标

### 量化指标

| 指标 | 修复前 | 修复后（预期） | 改进 |
|------|-------|--------------|------|
| **最长文件** | 1,148行 | 300行 | -73.9% |
| **超长文件数** | 3个 | 0个 | -100% |
| **平均文件大小** | 758行 | 250行 | -67.0% |
| **可维护性** | 中等 | 优秀 | +⭐⭐ |

### 拆分文件清单

| 原文件 | 行数 | 拆分为 | 子模块数 |
|--------|------|--------|---------|
| `src/adapters/financial_adapter.py` | 1,148 | financial/目录 | 7个 |
| `src/adapters/akshare_adapter.py` | 752 | akshare/目录 | 4个 |
| `src/core/data_source_manager_v2.py` | 776 | data_source/目录 | 3个 |

---

## 📊 预期成果

### 可维护性提升
1. ✅ **文件更小** - 所有文件 < 300行
2. ✅ **职责清晰** - 每个文件专注单一功能
3. ✅ **易于理解** - 更快的代码阅读速度
4. ✅ **易于修改** - 更低的修改风险

### 代码质量提升
1. ✅ **更好的组织** - 逻辑相关的代码在一起
2. ✅ **更少的依赖** - 减少循环导入
3. ✅ **更好的测试** - 更容易为小模块编写测试
4. ✅ **更好的文档** - 每个模块有清晰的文档

---

## 🚀 执行计划

### 第1步: 拆分financial_adapter.py (3小时)
1. 分析文件结构 (30分钟)
2. 创建子模块 (1小时)
3. 移动代码 (1小时)
4. 更新导入 (30分钟)

### 第2步: 拆分akshare_adapter.py (2小时)
1. 分析文件结构 (20分钟)
2. 创建子模块 (40分钟)
3. 移动代码 (40分钟)
4. 更新导入 (20分钟)

### 第3步: 拆分data_source_manager_v2.py (2小时)
1. 分析文件结构 (20分钟)
2. 创建子模块 (40分钟)
3. 移动代码 (40分钟)
4. 更新导入 (20分钟)

### 第4步: Code Review和文档 (1小时)
1. 代码审查 (30分钟)
2. 文档更新 (30分钟)

---

## ✅ 验收标准

### Phase 3完成标准
- [ ] 所有超长文件已拆分（>700行）
- [ ] 所有文件 < 300行
- [ ] 所有测试通过
- [ ] 导入路径更新正确
- [ ] 文档更新完成

### Code Review标准
- [ ] 代码风格一致
- [ ] 无循环导入
- [ ] 模块职责清晰
- [ ] 测试覆盖完整

---

## 📝 总结

### 核心发现
1. **部分文件已重构** - data_access.py和tdx_adapter.py已拆分
2. **3个超长文件待拆分** - financial_adapter.py, akshare_adapter.py, data_source_manager_v2.py
3. **unified_manager.py不需要拆分** - 只有323行
4. **拆分模式一致** - 按功能拆分为子模块

### 修订策略
1. **优先拆分最长文件** - financial_adapter.py (1,148行)
2. **按功能模块拆分** - 每个子模块专注单一功能
3. **保留主文件** - 用于导入和组合
4. **保持向后兼容** - 更新所有引用

### 预期成果
- **文件大小**: 1,148行 → 300行 (最大文件)
- **超长文件数**: 3个 → 0个
- **可维护性**: 中等 → 优秀

---

**报告生成时间**: 2026-01-07 15:20
**执行者**: Main CLI (Claude Code)
**审核状态**: 待审核
**下一步**: Task 3.1 - 拆分financial_adapter.py (1,148行）

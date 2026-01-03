# Tasks: Improve Backend Code Quality

## Overview

本任务列表基于技术负债报告 (docs/reports/TECHNICAL_DEBT_STATUS_2026-01-03.md)，分4个阶段改进后端Python代码质量。

**总任务数**: 44
**预计总时间**: 135-175小时
**优先级**: P0 (高优先级)

---

## Phase 1: 快速修复 (Week 1)

**目标**: Ruff问题减少58.7%，明确测试覆盖率问题根源

**Agent选择**: 命令行工具 (无需专用agent)

### Task 1.1: 自动修复Ruff问题 (904个)

**ID**: 1.1
**预计时间**: 30分钟
**优先级**: P0
**依赖**: 无

**执行步骤**:
1. 备份当前代码状态 (git commit)
2. 运行 `ruff check --fix .`
3. 运行 `ruff check --fix --unsafe-fixes .`
4. 审查修改 (git diff)
5. 运行测试验证无破坏性修改
6. 提交修复

**验证标准**:
- [ ] Ruff问题数 < 700
- [ ] 所有现有测试通过
- [ ] Git diff显示合理修改

**命令**:
```bash
git add .
git commit -m "backup: before ruff auto-fix"
ruff check --fix .
ruff check --fix --unsafe-fixes .
git diff --stat
pytest tests/ -v
git add .
git commit -m "fix: auto-fix 904 ruff issues"
```

---

### Task 1.2: 调查测试覆盖率下降原因

**ID**: 1.2
**预计时间**: 2小时
**优先级**: P0
**依赖**: 无

**执行步骤**:
1. 收集测试信息
2. 检查pytest配置
3. 检查coverage配置
4. 对比Phase 6测试配置
5. 编写调查报告

**验证标准**:
- [ ] 明确测试覆盖率从6%降至0.16%的原因
- [ ] 提供修复方案

**命令**:
```bash
# 收集测试信息
pytest --collect-only > /tmp/test_collection.txt
coverage report --sort=cover > /tmp/coverage_report.txt

# 检查配置
cat pytest.ini
cat .coveragerc
cat pyproject.toml | grep -A 20 "\[tool.coverage\]"

# 对比历史
git log --oneline --all --grep="coverage" | head -10
git show <phase6-commit>:pytest.ini > /tmp/phase6_pytest.ini
diff /tmp/phase6_pytest.ini pytest.ini
```

**输出**: `docs/reports/TEST_COVERAGE_INVESTIGATION_2026-01-03.md`

---

### Task 1.3: 批量修复测试导入路径

**ID**: 1.3
**预计时间**: 2-3小时
**优先级**: P0
**依赖**: Task 1.2
**状态**: ✅ 完成 (2026-01-03)

**执行步骤**:
1. 根据Task 1.2的调查结果修复配置
2. 创建自动化脚本 `scripts/dev/fix_test_imports.py`
3. 运行脚本批量修复14个测试文件中的106处导入错误
4. 验证测试收集不再有导入路径错误
5. 生成准确覆盖率数据（基线：5915个测试可收集）

**实际完成**:
- [x] 创建 `fix_test_imports.py` 自动化脚本
- [x] 修复14个测试文件，共106处导入路径替换
- [x] 修复前: 83个导入错误阻止测试运行
- [x] 修复后: 5915个测试可正常收集
- [x] 测试可以运行（部分测试因环境/数据问题失败，但不再因导入错误阻塞）

**Git提交**:
- `scripts/dev/fix_test_imports.py` - 自动化修复工具
- 测试文件导入路径全部更新

**下一步**: 进入Phase 2 - 测试覆盖率提升（目标80%）

**验证标准**:
- [ ] 测试覆盖率恢复或超过6%
- [ ] 所有测试可正常收集

**命令**:
```bash
# 修复配置
vim pytest.ini  # 或 .coveragerc 或 pyproject.toml

# 验证
pytest --collect-only
coverage run -m pytest
coverage report
```

---

## Phase 2: 测试提升 (Week 2-4)

**目标**: 测试覆盖率从0.16%提升到40%

**Agent选择**: `python-development:python-pro`

### Task 2.1: 编写data_access层测试 (核心优先)

**ID**: 2.1
**预计时间**: 20小时
**优先级**: P0
**依赖**: Task 1.3
**Agent**: `python-development:python-pro`

**子任务**:
- 2.1.1: 为TDengineDataAccess编写测试 (8小时)
- 2.1.2: 为PostgreSQLDataAccess编写测试 (8小时)
- 2.1.3: 为DatabaseConnectionManager编写测试 (4小时)

**执行步骤**:
1. 创建测试目录 `tests/data_access/`
2. Mock数据库连接
3. 测试CRUD操作
4. 测试异常处理
5. 测试连接池管理
6. 运行覆盖率测试

**验证标准**:
- [ ] `tests/data_access/test_tdengine_access.py` 存在
- [ ] `tests/data_access/test_postgresql_access.py` 存在
- [ ] `tests/data_access/test_connection_manager.py` 存在
- [ ] data_access层覆盖率 ≥ 70%
- [ ] 所有测试通过

**命令**:
```bash
# 创建测试文件
mkdir -p tests/data_access

# 运行测试
pytest tests/data_access/ -v
pytest tests/data_access/ --cov=src/data_access --cov-report=html

# 查看覆盖率
coverage report --include="src/data_access/*"
```

---

### Task 2.2: 编写adapters层测试

**ID**: 2.2
**预计时间**: 15小时
**优先级**: P1
**依赖**: 无
**Agent**: `python-development:python-pro`

**子任务**:
- 2.2.1: 为AkshareDataSource编写测试 (2小时)
- 2.2.2: 为BaostockDataSource编写测试 (2小时)
- 2.2.3: 为TdxDataSource编写测试 (3小时)
- 2.2.4: 为FinancialDataSource编写测试 (3小时)
- 2.2.5: 为其他3个适配器编写测试 (5小时)

**执行步骤**:
1. 创建测试目录 `tests/adapters/`
2. Mock外部API调用
3. 测试数据转换
4. 测试数据验证
5. 运行覆盖率测试

**验证标准**:
- [ ] `tests/adapters/test_*.py` 文件存在 (至少7个)
- [ ] adapters层覆盖率 ≥ 60%
- [ ] 所有测试通过

**命令**:
```bash
mkdir -p tests/adapters
pytest tests/adapters/ -v
pytest tests/adapters/ --cov=src/adapters --cov-report=html
coverage report --include="src/adapters/*"
```

---

### Task 2.3: 编写core层测试

**ID**: 2.3
**预计时间**: 10小时
**优先级**: P1
**依赖**: 无
**Agent**: `python-development:python-pro`

**子任务**:
- 2.3.1: 测试数据分类 (DataClassification) (2小时)
- 2.3.2: 测试存储策略 (DataStorageStrategy) (3小时)
- 2.3.3: 测试配置驱动表管理 (ConfigDrivenTableManager) (5小时)

**执行步骤**:
1. 创建测试目录 `tests/core/`
2. Mock配置文件
3. 测试数据路由逻辑
4. 测试表管理功能
5. 运行覆盖率测试

**验证标准**:
- [ ] `tests/core/test_*.py` 文件存在
- [ ] core层覆盖率 ≥ 70%
- [ ] 所有测试通过

**命令**:
```bash
mkdir -p tests/core
pytest tests/core/ -v
pytest tests/core/ --cov=src/core --cov-report=html
coverage report --include="src/core/*"
```

---

### Task 2.4: 验证测试覆盖率目标

**ID**: 2.4
**预计时间**: 1小时
**优先级**: P0
**依赖**: Task 2.1, 2.2, 2.3

**执行步骤**:
1. 运行完整覆盖率测试
2. 生成覆盖率报告
3. 对比目标 (40%)
4. 编写测试提升报告

**验证标准**:
- [ ] 整体测试覆盖率 ≥ 40%
- [ ] 核心模块覆盖率 ≥ 60%
- [ ] 测试报告生成

**命令**:
```bash
coverage run -m pytest
coverage report
coverage html  # 生成HTML报告
```

**输出**: `docs/reports/TEST_COVERAGE_IMPROVEMENT_2026-01-XX.md`

---

## Phase 3: 结构优化 (Week 5-8)

**目标**: 拆分4个超长文件，提升可维护性

**Agent选择**: `python-development:python-pro` + `code-reviewer`

### Task 3.1: 拆分data_access.py

**ID**: 3.1
**预计时间**: 2小时
**优先级**: P1
**依赖**: Task 2.1 (确保测试覆盖)
**Agent**: `python-development:python-pro`

**执行步骤**:
1. 分析文件结构
2. 设计拆分方案
3. 创建3个新文件
4. 移动代码到新文件
5. 更新导入
6. 运行测试验证
7. Code review

**拆分方案**:
```
src/data_access.py (1,357行)
├── src/data_access/tdengine_access.py (TDengine实现, ~500行)
├── src/data_access/postgresql_access.py (PostgreSQL实现, ~500行)
└── src/data_access/base_access.py (基础接口, ~400行)
```

**验证标准**:
- [ ] 原文件删除或保留为导入层
- [ ] 新文件每个 < 600行
- [ ] 所有测试通过
- [ ] Code review通过

**命令**:
```bash
# 备份
git cp src/data_access.py src/data_access.py.backup

# 创建新文件
mkdir -p src/data_access/
# 创建3个新文件并移动代码

# 更新导入
# 使用 find, grep, sed 批量更新导入

# 验证
pytest tests/data_access/ -v
python -c "from src.data_access import TDengineDataAccess, PostgreSQLDataAccess"
```

---

### Task 3.2: 拆分tdx_adapter.py

**ID**: 3.2
**预计时间**: 3小时
**优先级**: P1
**依赖**: Task 2.2
**Agent**: `python-development:python-pro`

**执行步骤**:
1. 分析文件结构
2. 设计拆分方案
3. 创建3个新文件
4. 移动代码
5. 更新导入
6. 运行测试验证

**拆分方案**:
```
src/adapters/tdx_adapter.py (1,058行)
├── src/adapters/tdx/tdx_base.py (基础类和工具, ~400行)
├── src/adapters/tdx/tdx_market.py (市场数据, ~300行)
└── src/adapters/tdx/tdx_kline.py (K线数据, ~400行)
```

**验证标准**:
- [ ] 新文件每个 < 500行
- [ ] 功能完整
- [ ] 所有测试通过

**命令**:
```bash
mkdir -p src/adapters/tdx/
# 创建3个新文件
pytest tests/adapters/test_tdx_adapter.py -v
```

---

### Task 3.3: 拆分financial_adapter.py

**ID**: 3.3
**预计时间**: 3小时
**优先级**: P1
**依赖**: Task 2.2
**Agent**: `python-development:python-pro`

**执行步骤**:
1. 分析文件结构
2. 设计拆分方案
3. 创建3个新文件
4. 移动代码
5. 更新导入
6. 运行测试验证

**拆分方案**:
```
src/adapters/financial_adapter.py (1,078行)
├── src/adapters/financial/financial_base.py (基础类, ~400行)
├── src/adapters/financial/financial_report.py (财务报表, ~400行)
└── src/adapters/financial/financial_indicator.py (财务指标, ~300行)
```

**验证标准**:
- [ ] 新文件每个 < 500行
- [ ] 功能完整
- [ ] 所有测试通过

**命令**:
```bash
mkdir -p src/adapters/financial/
# 创建3个新文件
pytest tests/adapters/test_financial_adapter.py -v
```

---

### Task 3.4: 重构unified_manager.py

**ID**: 3.4
**预计时间**: 2小时
**优先级**: P2
**依赖**: Task 2.3
**Agent**: `python-development:python-pro`

**执行步骤**:
1. 分析文件结构
2. 识别维护逻辑
3. 创建maintenance_manager.py
4. 移动维护代码
5. 更新导入
6. 运行测试验证

**重构方案**:
```
src/core/unified_manager.py (792行)
├── src/core/unified_manager.py (主要逻辑, ~600行)
└── src/core/maintenance_manager.py (维护逻辑, ~200行)
```

**验证标准**:
- [ ] 主要逻辑文件 < 650行
- [ ] 维护逻辑独立
- [ ] 所有测试通过

**命令**:
```bash
# 创建新文件
# 移动维护逻辑
pytest tests/core/test_unified_manager.py -v
```

---

### Task 3.5: 验证文件拆分结果

**ID**: 3.5
**预计时间**: 1小时
**优先级**: P0
**依赖**: Task 3.1, 3.2, 3.3, 3.4

**执行步骤**:
1. 统计所有文件行数
2. 验证无超长文件
3. 运行完整测试套件
4. 编写拆分报告

**验证标准**:
- [ ] 无文件 > 1000行
- [ ] 所有测试通过
- [ ] 导入无错误

**命令**:
```bash
# 统计文件行数
find src -name "*.py" -exec wc -l {} + | sort -rn | head -20

# 运行测试
pytest tests/ -v
```

**输出**: `docs/reports/FILE_SPLIT_COMPLETION_REPORT_2026-01-XX.md`

---

## Phase 4: 深度改进 (Week 9-16)

**目标**: Ruff问题 < 100, TODO < 50, 测试覆盖率 ≥ 80%

**Agent选择**: `python-development:python-pro` + `backend-development:backend-architect` + `code-reviewer`

### Task 4.1: 手动修复Ruff问题 (636个)

**ID**: 4.1
**预计时间**: 15小时
**优先级**: P1
**依赖**: Task 1.1
**Agent**: `python-development:python-pro`

**执行步骤**:
1. 分类Ruff问题 (按严重程度)
2. 修复高优先级问题
3. 修复中优先级问题
4. 修复低优先级问题
5. 逐文件验证
6. Code review

**问题分类**:
- 高优先级: 可能影响功能的问题
- 中优先级: 代码风格问题
- 低优先级: 建议性改进

**验证标准**:
- [ ] Ruff问题数 < 100
- [ ] 所有测试通过
- [ ] Code review通过

**命令**:
```bash
# 按严重程度列出问题
ruff check . --output-format=json | jq '.[].message_id' | sort | uniq -c

# 逐文件修复
for file in $(ruff check . --output-format=json | jq -r '.[].path' | sort -u); do
    echo "Fixing $file"
    vim $file  # 或使用其他编辑器
done

# 验证
ruff check . --statistics
pytest tests/ -v
```

---

### Task 4.2: 清理TODO/FIXME注释 (266个)

**ID**: 4.2
**预计时间**: 10小时
**优先级**: P2
**依赖**: 无
**Agent**: `python-development:python-pro`

**执行步骤**:
1. 提取所有TODO/FIXME注释
2. 分类: 已完成/需实现/转为文档/保留
3. 删除已完成代码的TODO
4. 转未实现功能为Issue
5. 转设计说明为文档注释
6. 验证

**分类标准**:
- **删除**: 功能已完成或不再需要
- **Issue**: 重要功能缺失，需要跟踪
- **文档注释**: 设计说明，转为代码注释
- **保留**: 合理的待办事项

**验证标准**:
- [ ] TODO注释 < 50个
- [ ] 所有删除的TODO合理
- [ ] 创建Issue跟踪未完成功能

**命令**:
```bash
# 提取所有TODO
grep -rn "TODO\|FIXME" src/ > /tmp/todo_list.txt

# 分类处理
# 手动审查每个TODO，决定处理方式

# 创建Issue (使用GitHub CLI)
gh issue create --title "Implement TODO from src/module.py:123" --body "TODO内容"
```

---

### Task 4.3: 减少Manager类 (109 → <30)

**ID**: 4.3
**预计时间**: 40-60小时
**优先级**: P3
**依赖**: 深度分析需求
**Agent**: `backend-development:backend-architect` + `code-reviewer`

**执行步骤**:
1. 分析所有Manager类功能
2. 识别重复功能
3. 设计合并方案
4. 逐个合并相似类
5. 更新依赖
6. 完整测试验证
7. Code review

**策略**:
- **优先合并**: 功能完全重复的Manager
- **次要合并**: 功能部分重叠的Manager
- **保留**: 核心独立功能的Manager

**验证标准**:
- [ ] Manager类数量 < 30
- [ ] 所有功能保留
- [ ] 所有测试通过
- [ ] 性能无下降

**命令**:
```bash
# 分析Manager类
grep -rn "class.*Manager" src/ > /tmp/manager_list.txt

# 设计合并方案
# 需要深入分析每个Manager的职责

# 合并实现
# 逐个Manager进行合并，每次合并后测试
```

**注意**: 此任务工作量巨大，可以延后到Phase 8

---

### Task 4.4: 继续提升测试覆盖率 (40% → 80%)

**ID**: 4.4
**预计时间**: 30小时
**优先级**: P1
**依赖**: Task 2.4
**Agent**: `python-development:python-pro`

**执行步骤**:
1. 分析覆盖率缺口
2. 识别未测试代码路径
3. 补充单元测试
4. 添加集成测试
5. 添加E2E测试
6. 验证目标达成

**测试策略**:
- **单元测试**: 覆盖所有public方法
- **集成测试**: 覆盖关键业务流程
- **E2E测试**: 覆盖端到端场景

**验证标准**:
- [ ] 整体覆盖率 ≥ 80%
- [ ] 核心模块覆盖率 ≥ 90%
- [ ] 所有测试通过

**命令**:
```bash
# 分析覆盖率缺口
coverage report --sort=cover > /tmp/coverage_gap.txt

# 补充测试
# 根据覆盖率报告逐个补充测试

# 验证
coverage run -m pytest
coverage report
coverage html
```

---

## 验收标准

### 总体验收

- [ ] **阶段1完成**: Ruff问题 < 700, 测试配置修复
- [ ] **阶段2完成**: 测试覆盖率 ≥ 40%
- [ ] **阶段3完成**: 无文件 > 1000行
- [ ] **阶段4完成**: Ruff问题 < 100, TODO < 50, 覆盖率 ≥ 80%

### 质量门禁

每个阶段完成后必须通过：
1. 所有现有测试通过
2. Code review通过
3. 性能测试无退化
4. 覆盖率报告生成

---

## 任务依赖关系图

```
Task 1.1 (Ruff自动修复)
    ↓
Task 1.2 (调查测试问题) → Task 1.3 (修复测试配置)
    ↓
Task 2.1 (data_access测试)
Task 2.2 (adapters测试)  } → Task 2.4 (验证覆盖率目标40%)
Task 2.3 (core测试)      ↗
    ↓
Task 3.1 (拆分data_access)
Task 3.2 (拆分tdx)        } → Task 3.5 (验证拆分结果)
Task 3.3 (拆分financial)  ↗
Task 3.4 (重构unified)
    ↓
Task 4.1 (修复Ruff问题)
Task 4.2 (清理TODO)       } → 最终验收
Task 4.3 (减少Manager)    ↗
Task 4.4 (提升覆盖率80%)  ↗
```

---

## 时间线

| 阶段 | 任务数 | 预计时间 | 累计时间 |
|------|--------|---------|---------|
| Phase 1 | 3 | 3.5小时 | 3.5小时 |
| Phase 2 | 4 | 46小时 | 49.5小时 |
| Phase 3 | 5 | 11小时 | 60.5小时 |
| Phase 4 | 4 | 95-115小时 | 155.5-175.5小时 |

**建议执行节奏**: 每周投入20小时，约8-9周完成

---

## 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 测试编写工作量超预期 | 高 | 中 | 分阶段完成，优先核心模块 |
| 拆分文件引入错误 | 中 | 高 | 充分测试，code review |
| Manager类合并影响功能 | 低 | 高 | 延后到Phase 8，或谨慎合并 |
| Ruff自动修复改变逻辑 | 低 | 中 | 仔细审查git diff |

---

## 相关文档

- 技术负债报告: `docs/reports/TECHNICAL_DEBT_STATUS_2026-01-03.md`
- 提案文档: `openspec/changes/improve-backend-code-quality/proposal.md`
- 设计文档: `openspec/changes/improve-backend-code-quality/design.md` (待创建)

---

**任务列表创建日期**: 2026-01-03
**预计完成日期**: 2026-03-31 (约12周)
**负责人**: Main CLI + Python Development Agents

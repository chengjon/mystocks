# Proposal: Improve Backend Code Quality

## Meta
- **Change ID**: improve-backend-code-quality
- **Status**: Proposed
- **Created**: 2026-01-03
- **Priority**: High (代码质量基础)
- **Source**: 技术负债报告 docs/reports/TECHNICAL_DEBT_STATUS_2026-01-03.md

## Problem Statement

根据2026-01-03技术负债报告，后端Python代码存在以下问题：

### P0 - 立即修复问题 (1周内)

1. **Ruff代码质量问题** (1,540个)
   - 可自动修复: 904个 (58.7%)
   - 需手动修复: 636个 (41.3%)
   - 主要问题: 代码风格、导入顺序、未使用变量等

2. **测试覆盖率极低** (0.16%)
   - 核心模块无测试: data_access, adapters, core
   - 测试文件不足: 仅5个
   - 目标覆盖率: 80%

3. **超长文件待拆分** (4个文件>1000行)
   - `src/data_access.py` (1,357行)
   - `src/adapters/tdx_adapter.py` (1,058行)
   - `src/adapters/financial_adapter.py` (1,078行)
   - `src/core/unified_manager.py` (792行)

### P1 - 高优先级问题 (2-4周内)

4. **TODO/FIXME注释** (266个)
   - 需分类: 完成/删除/转为Issue
   - 部分功能未完成，存在临时实现

5. **Manager类过多** (109个)
   - 存在过度工程化问题
   - 建议合并到<30个

## Why

现在必须修复这些问题的原因：

1. **代码质量基础**: Ruff问题是代码质量的基础，影响可维护性
2. **测试覆盖不足**: 0.16%覆盖率严重影响代码质量保证
3. **可维护性**: 超长文件和过多的Manager类降低代码可读性
4. **技术债务累积**: 不及时修复会导致维护成本指数增长

## Impact

### 正面影响

- **代码质量**: Ruff问题减少58.7% (904个自动修复)
- **可维护性**: 拆分超长文件提升代码可读性
- **质量保证**: 提升测试覆盖率到80%
- **开发效率**: 清理TODO注释，减少临时实现

### 风险

- **拆分文件风险**: 可能引入导入错误 (低概率)
- **测试补充工作量**: 需要大量时间编写测试 (中等)
- **Manager类合并**: 可能影响现有功能 (低概率)

## Proposed Solution

### 阶段1: 快速修复 (Week 1)

#### 1.1 自动修复Ruff问题

**策略**: 使用Ruff自动修复功能

```bash
# 自动修复所有可修复的问题
ruff check --fix .
ruff check --fix --unsafe-fixes .

# 预计时间: 30分钟
# 预期成果: 1,540 → 636个问题 (-58.7%)
```

**验证**: Ruff问题数 < 700

#### 1.2 调查测试覆盖率问题

**策略**: 找出覆盖率从6%降至0.16%的原因

```bash
# 检查测试配置
pytest --collect-only
coverage report --sort=cover

# 预计时间: 2小时
# 目标: 明确测试覆盖率下降原因
```

**验证**: 确定测试配置问题或测试文件位置问题

### 阶段2: 测试提升 (Week 2-4)

#### 2.1 编写data_access层测试

**优先级**: 最高 (核心数据访问层)

**Agent选择**: `python-development:python-pro` (Python测试专家)

**任务**:
- 为 `src/data_access.py` 编写单元测试
- Mock数据库连接，测试CRUD操作
- 测试异常处理和错误恢复
- 目标覆盖率: 70%

**预计时间**: 20小时

**验证**: data_access层覆盖率 ≥ 70%

#### 2.2 编写adapters层测试

**优先级**: 高 (数据源适配器)

**Agent选择**: `python-development:python-pro`

**任务**:
- 为7个数据源适配器编写单元测试
- Mock外部API调用
- 测试数据转换和验证
- 目标覆盖率: 60%

**预计时间**: 15小时

**验证**: adapters层覆盖率 ≥ 60%

#### 2.3 编写core层测试

**优先级**: 高 (核心业务逻辑)

**Agent选择**: `python-development:python-pro`

**任务**:
- 为 `src/core/` 模块编写单元测试
- 测试数据分类、路由逻辑
- 测试配置驱动表管理
- 目标覆盖率: 70%

**预计时间**: 10小时

**验证**: core层覆盖率 ≥ 70%

**总体目标**: 测试覆盖率从0.16%提升到40%

### 阶段3: 结构优化 (Week 5-8)

#### 3.1 拆分data_access.py

**Agent选择**: `python-development:python-pro` + `code-reviewer`

**任务**:
```
src/data_access.py (1,357行)
├── tdengine_access.py (TDengine实现)
├── postgresql_access.py (PostgreSQL实现)
└── base_access.py (基础接口)
```

**预计时间**: 2小时

**验证**: 每个文件 < 600行，导入正常

#### 3.2 拆分tdx_adapter.py

**Agent选择**: `python-development:python-pro`

**任务**:
```
src/adapters/tdx_adapter.py (1,058行)
├── tdx_base.py (基础类和工具)
├── tdx_market.py (市场数据)
└── tdx_kline.py (K线数据)
```

**预计时间**: 3小时

**验证**: 每个文件 < 500行，功能完整

#### 3.3 拆分financial_adapter.py

**Agent选择**: `python-development:python-pro`

**任务**:
```
src/adapters/financial_adapter.py (1,078行)
├── financial_base.py (基础类)
├── financial_report.py (财务报表)
└── financial_indicator.py (财务指标)
```

**预计时间**: 3小时

**验证**: 每个文件 < 500行，功能完整

#### 3.4 重构unified_manager.py

**Agent选择**: `python-development:python-pro`

**任务**:
```
src/core/unified_manager.py (792行)
├── unified_manager.py (主要逻辑)
└── maintenance_manager.py (维护逻辑)
```

**预计时间**: 2小时

**验证**: 每个文件 < 500行，维护逻辑独立

### 阶段4: 深度改进 (Week 9-16)

#### 4.1 手动修复剩余Ruff问题 (636个)

**Agent选择**: `python-development:python-pro` + `code-reviewer`

**预计时间**: 15小时

**验证**: Ruff问题数 < 100

#### 4.2 清理TODO/FIXME (266个)

**Agent选择**: `python-development:python-pro`

**任务**:
- 分类: 已完成(删除)、需实现(Issue)、文档注释
- 预计完成/删除: ~100个
- 预计转为Issue: ~50个
- 预计转为文档: ~30个

**预计时间**: 10小时

**验证**: TODO注释 < 50个

#### 4.3 减少Manager类 (109 → <30)

**Agent选择**: `backend-development:backend-architect` + `code-reviewer`

**任务**:
- 识别重复功能
- 合并相似类
- 重构依赖关系

**预计时间**: 40-60小时

**验证**: Manager类数量 < 30

#### 4.4 继续提升测试覆盖率 (40% → 80%)

**Agent选择**: `python-development:python-pro`

**任务**:
- 补充单元测试
- 添加集成测试
- 添加E2E测试

**预计时间**: 30小时

**验证**: 整体覆盖率 ≥ 80%

## Affected Capabilities

- **python-code-quality**: Python代码质量标准
- **test-coverage**: 测试覆盖率要求
- **code-maintainability**: 代码可维护性
- **architecture**: 后端架构设计

## Success Criteria

### 短期目标 (1个月内)

- ✅ Ruff自动修复完成: 1,540 → 636个问题
- ✅ 超长文件拆分: 4 → 0个
- ✅ 测试覆盖率: 0.16% → 20%

### 中期目标 (3个月内)

- ✅ 测试覆盖率: 0.16% → 60%
- ✅ Ruff问题: 1,540 → <300个
- ✅ TODO清理: 266 → <100个

### 长期目标 (6个月内)

- ✅ 测试覆盖率: 0.16% → 80%
- ✅ Ruff问题: 1,540 → <100个
- ✅ Manager类: 109 → <30个
- ✅ TODO注释: 266 → <50个

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| 拆分文件引入导入错误 | Medium | High | 使用测试验证每个拆分步骤 |
| 测试编写工作量超预期 | High | Medium | 分阶段完成，优先核心模块 |
| Manager类合并影响功能 | Low | High | 代码审查 + E2E测试验证 |
| Ruff自动修复改变代码逻辑 | Low | Medium | 使用git diff审查所有修改 |

## Timeline

- **Week 1**: 快速修复 (Ruff自动修复 + 测试问题调查)
- **Week 2-4**: 测试提升 (data_access, adapters, core层测试)
- **Week 5-8**: 结构优化 (拆分超长文件)
- **Week 9-16**: 深度改进 (Ruff手动修复, TODO清理, Manager合并)

## Dependencies

- Python 3.12+开发环境
- Ruff 0.9.10+ 代码质量工具
- pytest测试框架
- coverage.py覆盖率工具

## Alternatives Considered

### 1. 仅修复Ruff问题，暂不提升测试覆盖率

**优点**: 快速提升代码质量指标
**缺点**: 测试覆盖率极低的问题未解决
**结论**: ❌ 不推荐 (测试覆盖是质量保证基础)

### 2. 完全重写超长文件

**优点**: 代码结构更清晰
**缺点**: 工作量大，风险高
**结论**: ❌ 不推荐 (渐进式拆分更安全)

### 3. 一次性完成所有修复

**优点**: 一次性解决所有问题
**缺点**: 工作量巨大，风险高
**结论**: ❌ 不推荐 (分阶段完成更可控)

## Agent/Plugin Selection Strategy

### 阶段1: 快速修复
- **工具**: Ruff命令行工具
- **Agent**: 无需专用agent (自动化工具即可)

### 阶段2: 测试提升
- **Agent**: `python-development:python-pro`
  - 理由: Python测试专家，熟悉pytest和最佳实践
- **Plugin**: `compound-engineering:test-automator` (可选)
  - 理由: 测试自动化专家，可以帮助生成测试代码

### 阶段3: 结构优化
- **Agent**: `python-development:python-pro` + `code-reviewer`
  - 理由: Python开发专家负责拆分，代码审查专家验证
- **Plugin**: `feature-dev:code-architect` (可选)
  - 理由: 代码架构专家，可以设计拆分方案

### 阶段4: 深度改进
- **Agent**: `backend-development:backend-architect` + `code-reviewer`
  - 理由: 后端架构专家负责Manager类合并，代码审查专家验证
- **Agent**: `python-development:python-pro`
  - 理由: Python专家负责Ruff问题修复和TODO清理

## Open Questions

1. 测试覆盖率目标是80%还是可以分阶段(40% → 60% → 80%)?
   - **建议**: 分阶段完成，降低风险

2. Manager类合并是否可以延后到Phase 8?
   - **建议**: 可以延后，优先处理代码质量和测试覆盖

3. TODO清理是否需要全部完成，还是可以保留部分合理的TODO?
   - **建议**: 保留合理的TODO(如功能增强)，删除临时实现和已完成代码

## Related Changes

- Phase 6: 技术债务修复 (已完成，语法错误清零)
- remediate-phase7-technical-debt: Phase 7前端和E2E测试修复
- 本变更: 后端Python代码质量提升

## Next Steps

1. ✅ 创建OpenSpec变更提案 (本文档)
2. ⏳ 创建tasks.md (详细任务分解)
3. ⏳ 创建design.md (架构设计文档)
4. ⏳ 创建规格增量 (spec deltas)
5. ⏳ 验证提案 (openspec validate)
6. ⏳ 执行阶段1: Ruff自动修复

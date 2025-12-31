# MyStocks 实施任务分解表

**版本**: 1.0
**日期**: 2025-12-30
**范围**: Phase 4 - Phase 7 (12 周)

---

## 📊 任务概览

| Phase | 周数 | 核心任务 | 目标指标 |
|-------|------|----------|----------|
| Phase 4.1-4.2 | Week 1-2 | TypeScript 快速修复 | 错误: 262 → ~150 |
| Phase 4.3-4.5 | Week 3 | 契约对齐 | 错误: ~150 → <50 |
| Phase 5 | Week 4-5 | 契约测试体系 | 115 APIs 测试 |
| Phase 6 | Week 6 | 开发者体验 | 自动化工具 |
| Phase 7 | Week 7-12 | 完整 API 注册 | 115 APIs 注册 |

---

## Week 1-2: Phase 4.1-4.2 快速修复

### 任务 4.1.1: 修复 Generated Types 导出

**目标**: 添加缺失的导出，修复 ~10 个类型错误

| 任务 | 类型 | 耗时 | 优先级 |
|------|------|------|--------|
| 添加 `UserProfileResponse` 导出 | Bug Fix | 2h | P0 |
| 添加 `WatchlistResponse` 导出 | Bug Fix | 2h | P0 |
| 添加 `NotificationResponse` 导出 | Bug Fix | 2h | P0 |
| 更新所有 import 引用 | Refactor | 4h | P1 |

**验收标准**:
- [ ] 3 个类型导出添加成功
- [ ] 无导入错误
- [ ] 单元测试通过

### 任务 4.1.2: ECharts 类型标准化

**目标**: 统一 `EChartOption` vs `EChartsOption`，修复 ~20 个错误

| 任务 | 类型 | 耗时 | 优先级 |
|------|------|------|--------|
| 创建标准 ChartOption 类型 | New Type | 4h | P0 |
| 更新所有 chart 组件 | Refactor | 8h | P0 |
| 添加类型守卫 | Enhancement | 2h | P1 |

**验收标准**:
- [ ] 统一的 ChartOption 类型定义
- [ ] 所有 chart 组件使用标准类型
- [ ] 无 ECharts 相关类型错误

### 任务 4.1.3: Element Plus 兼容性

**目标**: 修复组件类型兼容问题，修复 ~5 个错误

| 任务 | 类型 | 耗时 | 优先级 |
|------|------|------|--------|
| 实现 `toElementTagType()` 辅助函数 | New Function | 2h | P0 |
| 修复 TagType 兼容问题 | Bug Fix | 2h | P0 |
| 添加表单组件类型守卫 | Enhancement | 2h | P1 |

**验收标准**:
- [ ] TagType 兼容问题修复
- [ ] 表单组件类型正常

---

## Week 3: Phase 4.3-4.5 契约对齐

### 任务 4.3.1: OpenAPI 规格补全

**目标**: 更新 OpenAPI 规格，添加缺失字段

| 任务 | 类型 | 耗时 | 优先级 |
|------|------|------|--------|
| 补全 market 模块 OpenAPI | Documentation | 4h | P0 |
| 补全 strategy 模块 OpenAPI | Documentation | 4h | P0 |
| 补全 indicators 模块 OpenAPI | Documentation | 4h | P0 |
| 补全 trading 模块 OpenAPI | Documentation | 4h | P1 |

**验收标准**:
- [ ] 4 个模块 OpenAPI 补全
- [ ] 响应 schema 定义完整
- [ ] 参数文档完整

### 任务 4.3.2: 适配层创建

**目标**: 创建前后端类型映射适配层

| 任务 | 类型 | 耗时 | 优先级 |
|------|------|------|--------|
| 创建类型映射配置文件 | New File | 2h | P0 |
| 实现 `adaptAPIResponse()` 函数 | New Function | 4h | P0 |
| 实现 `formatAPIRequest()` 函数 | New Function | 2h | P1 |
| 添加单元测试 | Test | 4h | P1 |

**验收标准**:
- [ ] 类型映射覆盖所有 API
- [ ] 适配函数测试通过
- [ ] 无运行时类型错误

### 任务 4.3.3: 严格类型检查启用

**目标**: 启用 TypeScript 严格模式

| 任务 | 类型 | 耗时 | 优先级 |
|------|------|------|--------|
| 修复剩余关键类型错误 | Bug Fix | 8h | P0 |
| 启用 tsconfig strict 模式 | Config | 1h | P0 |
| 修复严格模式相关警告 | Warning Fix | 4h | P1 |

**验收标准**:
- [ ] TypeScript 严格模式启用
- [ ] 错误数 <50
- [ ] 无严格模式阻断错误

---

## Week 4-5: Phase 5 契约测试

### 任务 5.1: 契约验证测试套件

**目标**: pytest-based 契约测试

| 任务 | 类型 | 耗时 | 优先级 |
|------|------|------|--------|
| 实现 `contract_validator.py` | New Module | 8h | P0 |
| 实现 `api_consistency_checker.py` | New Module | 8h | P0 |
| 实现 `contract_engine.py` | New Module | 8h | P0 |
| 集成 VersionManager.sync | Implementation | 8h | P0 |

**验收标准**:
- [ ] 契约验证器可正常运行
- [ ] 一致性检查正常工作
- [ ] sync 方法实现完成

### 任务 5.2: API 测试覆盖

**目标**: 测试所有 4 个已注册 API

| 任务 | 类型 | 耗时 | 优先级 |
|------|------|------|--------|
| market-data API 测试 | Test | 8h | P0 |
| trading API 测试 | Test | 8h | P0 |
| technical-analysis API 测试 | Test | 4h | P0 |
| strategy-management API 测试 | Test | 8h | P0 |

**验收标准**:
- [ ] 4 个 API 完整测试覆盖
- [ ] 测试通过率 >95%
- [ ] 测试报告生成正常

### 任务 5.3: CI/CD 集成

**目标**: 自动化测试流水线

| 任务 | 类型 | 耗时 | 优先级 |
|------|------|------|--------|
| 配置 GitHub Actions | CI Config | 4h | P0 |
| 添加测试钩子 | Hook | 4h | P0 |
| 配置测试报告展示 | Report | 2h | P1 |

**验收标准**:
- [ ] PR 自动触发测试
- [ ] 测试结果可查看
- [ ] 失败时阻止合并

---

## Week 6: Phase 6 开发者体验

### 任务 6.1: Pre-commit Hooks

**目标**: 自动同步契约

| 任务 | 类型 | 耗时 | 优先级 |
|------|------|------|--------|
| 创建契约同步 hook | New Script | 4h | P0 |
| 创建类型检查 hook | New Script | 2h | P0 |
| 配置 pre-commit.yaml | Config | 2h | P0 |

**验收标准**:
- [ ] 提交前自动检查契约
- [ ] 类型检查通过才能提交
- [ ] 文档更新钩子正常

### 任务 6.2: 代码生成器

**目标**: 减少样板代码

| 任务 | 类型 | 耗时 | 优先级 |
|------|------|------|--------|
| 服务层生成器 | New Script | 8h | P0 |
| Adapter 层生成器 | New Script | 8h | P1 |
| Composable 生成器 | New Script | 8h | P1 |

**验收标准**:
- [ ] 5 分钟内集成新 API
- [ ] 生成代码符合规范
- [ ] 支持自定义模板

### 任务 6.3: 一键契约注册

**目标**: 简化契约注册流程

| 任务 | 类型 | 耗时 | 优先级 |
|------|------|------|--------|
| 注册命令工具 | New Script | 4h | P0 |
| 交互式注册向导 | New Script | 4h | P1 |
| 批量注册功能 | Enhancement | 4h | P1 |

**验收标准**:
- [ ] 单命令注册契约
- [ ] 支持批量导入
- [ ] 注册验证完整

---

## Week 7-12: Phase 7 完整 API 注册

### Week 7-8: P0 优先级 (30 APIs)

| 任务 | API 数量 | 耗时 | 模块 |
|------|----------|------|------|
| 契约注册 | 10 | 16h | trading |
| 契约注册 | 10 | 16h | market |
| 契约注册 | 10 | 16h | data |

**验收标准**:
- [ ] 30 个 API 完整注册
- [ ] 类型定义完整
- [ ] 测试覆盖 >90%

### Week 9-10: P1 优先级 (25 APIs)

| 任务 | API 数量 | 耗时 | 模块 |
|------|----------|------|------|
| 契约注册 | 12 | 16h | backtest |
| 契约注册 | 13 | 16h | risk |

**验收标准**:
- [ ] 25 个 API 完整注册
- [ ] 适配层覆盖
- [ ] 集成测试通过

### Week 11-12: P2 优先级 (40 APIs)

| 任务 | API 数量 | 耗时 | 模块 |
|------|----------|------|------|
| 契约注册 | 20 | 24h | indicators |
| 契约注册 | 20 | 24h | announcement |

**验收标准**:
- [ ] 40 个 API 完整注册
- [ ] 文档完整
- [ ] E2E 测试通过

---

## 每日任务跟踪表

### Week 1 周一

| 任务 | 负责人 | 状态 | 耗时 | 备注 |
|------|--------|------|------|------|
| 添加 UserProfileResponse 导出 | ? | ⏳ | 2h | |
| 添加 WatchlistResponse 导出 | ? | ⏳ | 2h | |
| 添加 NotificationResponse 导出 | ? | ⏳ | 2h | |
| 更新 import 引用 | ? | ⏳ | 4h | |

**今日目标**: 修复 10 个类型错误

### Week 1 周二

| 任务 | 负责人 | 状态 | 耗时 | 备注 |
|------|--------|------|------|------|
| 创建标准 ChartOption 类型 | ? | ⏳ | 4h | |
| 更新 chart 组件 (部分) | ? | ⏳ | 4h | |

**今日目标**: 修复 10 个 ECharts 错误

### Week 1 周三

| 任务 | 负责人 | 状态 | 耗时 | 备注 |
|------|--------|------|------|------|
| 继续更新 chart 组件 | ? | ⏳ | 4h | |
| 实现 toElementTagType() | ? | ⏳ | 2h | |
| 修复 TagType 兼容问题 | ? | ⏳ | 2h | |

**今日目标**: 修复 10 个错误，总进度 30/262

### Week 1 周四-周五

| 任务 | 负责人 | 状态 | 耗时 | 备注 |
|------|--------|------|------|------|
| 完成 Element Plus 修复 | ? | ⏳ | 4h | |
| 代码审查 | ? | ⏳ | 4h | |
| 单元测试 | ? | ⏳ | 4h | |

**周末检查点**: TypeScript 错误 < 230

---

## 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 类型错误超出预期 | 中 | 高 | 预留 50% 时间缓冲 |
| 契约定义不一致 | 高 | 中 | 每日同步检查 |
| 测试覆盖率不足 | 中 | 中 | 优先测试核心 API |
| 资源冲突 | 低 | 中 | 明确任务分工 |

---

## 依赖关系

```
4.1.1 修复导出
    ↓
4.1.2 ECharts 标准化 ← 依赖 4.1.1
    ↓
4.1.3 Element Plus 兼容性
    ↓
4.3 契约对齐 ← 依赖 4.1.x 完成
    ↓
5.1 契约测试套件 ← 依赖 4.3 完成
    ↓
5.2 API 测试覆盖 ← 依赖 5.1 完成
    ↓
7.x API 注册 ← 依赖 5.2 完成
```

---

## 成功标准

### 阶段性成功标准

| Phase | 成功标准 | 验收方式 |
|-------|----------|----------|
| Phase 4.1-4.2 | TypeScript 错误 < 150 | `npm run typecheck` |
| Phase 4.3-4.5 | TypeScript 错误 < 50 | `npm run typecheck` |
| Phase 5 | 4 APIs 100% 测试覆盖 | pytest --cov |
| Phase 6 | 新 API 集成 < 5 分钟 | 实际操作验证 |
| Phase 7 | 115 APIs 注册 | API 目录检查 |

### 最终成功标准 (Week 12)

- [ ] TypeScript 错误 < 20
- [ ] 契约覆盖率 > 60%
- [ ] 已注册 API 115 个
- [ ] 类型安全 > 95%
- [ ] CI/CD 测试自动化

---

*文档版本: 1.0*
*创建日期: 2025-12-30*
*下次更新: 2026-01-06*

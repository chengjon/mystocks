# MyStocks 项目代码文件统计报告（1000行以上）

> **历史文档说明**:
> 本文件是某阶段的历史文档、过程记录或专题材料，不是当前基线、当前系统总览或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内描述、背景、结论和上下文如未重新复核，应视为历史快照，不得直接当作当前事实。


**报告日期**: 2026-01-28
**统计范围**: 源代码文件（排除文档、node_modules、dist、build）
**统计阈值**: 1000行以上

---

## 📊 统计摘要

| 分类 | 文件数量 | 总行数 | 平均行数 |
|------|---------|--------|---------|
| **Python (src/)** | 24 | 30,758 | 1,282 |
| **Python (tests/)** | 11 | 15,897 | 1,445 |
| **Python (web/backend)** | 10 | 16,010 | 1,601 |
| **TypeScript/Vue (web/frontend)** | 20+ | 35,000+ | 1,500+ |
| **总计** | **65+** | **~97,665** | **~1,503** |

---

## 🔴 超大文件警告（2000行以上）

### 需要优先拆分的文件

| 文件路径 | 行数 | 类型 | 优先级 | 建议 |
|---------|------|------|--------|------|
| `src/interfaces/adapters/akshare/market_data.py` | 2,521 | Python | 🔴 **P0** | 立即拆分 |
| `src/adapters/akshare/market_data.py` | 2,249 | Python | 🔴 **P0** | 立即拆分 |
| `web/frontend/src/views/artdeco-pages/ArtDecoMarketData.vue` | 3,238 | Vue | 🔴 **P0** | 拆分为多个组件 |
| `web/frontend/src/api/types/generated-types.ts` | 3,137 | TypeScript | 🟡 **P1** | 自动生成，可保留 |
| `web/backend/app/api/risk_management.py` | 2,112 | Python | 🔴 **P0** | 按功能模块拆分 |
| `web/backend/app/api/data.py` | 1,786 | Python | 🔴 **P0** | 按数据类型拆分 |
| `web/frontend/src/views/artdeco-pages/ArtDecoDataAnalysis.vue` | 2,425 | Vue | 🔴 **P0** | 拆分为多个组件 |
| `web/frontend/src/components/artdeco/advanced/ArtDecoDecisionModels.vue` | 2,398 | Vue | 🔴 **P0** | 拆分为多个组件 |
| `tests/ai/test_ai_assisted_testing.py` | 2,120 | Python | 🟡 **P1** | 测试文件，可接受 |
| `web/frontend/src/api/types/common.ts` | 2,235 | TypeScript | 🔴 **P0** | 按类型定义拆分 |

**拆分建议**：
- **P0（立即行动）**: 业务代码文件超过2000行
- **P1（计划拆分）**: 测试文件或自动生成文件超过2000行

---

## 📋 Python文件详情（src/ 目录）

### 2000+ 行文件

| 文件 | 行数 | 模块 | 拆分建议 |
|------|------|------|---------|
| `interfaces/adapters/akshare/market_data.py` | 2,521 | 数据适配器 | 按市场数据类型拆分 |
| `adapters/akshare/market_data.py` | 2,249 | 数据适配器 | **重复代码，应合并** |

### 1000-1999 行文件

| 文件 | 行数 | 模块 | 说明 |
|------|------|------|------|
| `advanced_analysis/decision_models_analyzer.py` | 1,659 | 高级分析 | 决策模型分析 |
| `interfaces/adapters/tdx/tdx_adapter.py` | 1,406 | 数据适配器 | 通达信适配器接口 |
| `database/database_service.py` | 1,392 | 数据库服务 | 数据库操作服务 |
| `data_access.py` | 1,385 | 数据访问 | 数据访问层 |
| `adapters/tdx/tdx_adapter.py` | 1,367 | 数据适配器 | 通达信适配器实现 |
| `domain/monitoring/intelligent_threshold_manager.py` | 1,315 | 监控域 | 智能阈值管理 |
| `advanced_analysis/anomaly_tracking_analyzer.py` | 1,260 | 高级分析 | 异常追踪分析 |
| `gpu/acceleration/gpu_acceleration_engine.py` | 1,218 | GPU加速 | GPU加速引擎 |
| `monitoring/intelligent_threshold_manager.py` | 1,205 | 监控 | 智能阈值管理（可能重复） |
| `gpu/api_system/utils/gpu_acceleration_engine.py` | 1,153 | GPU API | GPU加速引擎（可能重复） |
| `advanced_analysis/sentiment_analyzer.py` | 1,143 | 高级分析 | 情感分析 |
| `data_sources/real/postgresql_relational.py` | 1,137 | 数据源 | PostgreSQL关系数据 |
| `domain/monitoring/monitoring_service.py` | 1,122 | 监控域 | 监控服务 |
| `interfaces/adapters/akshare/misc_data.py` | 1,118 | 数据适配器 | 杂项数据接口 |
| `advanced_analysis/financial_valuation_analyzer.py` | 1,109 | 高级分析 | 财务估值分析 |
| `advanced_analysis/capital_flow_analyzer.py` | 1,106 | 高级分析 | 资金流向分析 |
| `adapters/akshare/misc_data.py` | 1,102 | 数据适配器 | 杂项数据实现 |
| `domain/monitoring/multi_channel_alert_manager.py` | 1,087 | 监控域 | 多渠道告警管理 |
| `storage/database/database_manager.py` | 1,062 | 存储层 | 数据库管理器 |
| `monitoring/monitoring_service.py` | 1,062 | 监控 | 监控服务（可能重复） |
| `data_sources/real/tdengine_timeseries.py` | 1,031 | 数据源 | TDengine时序数据 |
| `interfaces/adapters/efinance_adapter.py` | 1,010 | 数据适配器 | Efinance适配器接口 |
| `monitoring/multi_channel_alert_manager.py` | 1,009 | 监控 | 多渠道告警（可能重复） |
| `governance/risk_management/calculators/gpu_calculator.py` | 1,009 | 风险治理 | GPU计算器 |
| `advanced_analysis/chip_distribution_analyzer.py` | 1,001 | 高级分析 | 筹码分布分析 |

---

## 📋 Python文件详情（tests/ 目录）

| 文件 | 行数 | 测试类型 | 说明 |
|------|------|---------|------|
| `tests/ai/test_ai_assisted_testing.py` | 2,120 | AI测试 | AI辅助测试 |
| `tests/adapters/test_akshare_adapter.py` | 1,905 | 适配器测试 | Akshare适配器测试 |
| `tests/security/test_security_compliance.py` | 1,824 | 安全测试 | 安全合规测试 |
| `tests/monitoring/test_monitoring_alerts.py` | 1,489 | 监控测试 | 告警监控测试 |
| `tests/ai/test_data_analyzer.py` | 1,461 | AI测试 | 数据分析器测试 |
| `tests/security/test_security_vulnerabilities.py` | 1,226 | 安全测试 | 漏洞测试 |
| `tests/contract/test_contract_validator.py` | 1,204 | 契约测试 | 契约验证测试 |
| `tests/dashboard/test_dashboard.py` | 1,183 | 仪表板测试 | 仪表板功能测试 |
| `tests/unit/core/test_monitoring.py` | 1,093 | 单元测试 | 核心监控测试 |
| `tests/metrics/test_quality_metrics.py` | 1,073 | 指标测试 | 质量指标测试 |
| `tests/reporting/test_report_generator.py` | 1,005 | 报告测试 | 报告生成器测试 |

---

## 📋 Python文件详情（web/backend/ 目录）

| 文件 | 行数 | 模块 | 拆分建议 |
|------|------|------|---------|
| `web/backend/app/api/risk_management.py` | 2,112 | API | 按风险类型拆分 |
| `web/backend/app/services/data_adapter.py` | 2,016 | 服务 | 按数据源拆分 |
| `web/backend/app/api/data.py` | 1,786 | API | 按数据类型拆分 |
| `web/backend/app/api/akshare_market.py` | 1,377 | API | 按接口功能拆分 |
| `web/backend/app/core/cache_manager.py` | 1,304 | 核心 | 按缓存策略拆分 |
| `web/backend/app/mock/unified_mock_data.py` | 1,292 | Mock | 按数据类型拆分 |
| `web/backend/app/api/mystocks_complete.py` | 1,252 | API | 按功能模块拆分 |
| `web/backend/app/api/signal_monitoring.py` | 1,172 | API | 按信号类型拆分 |
| `web/backend/app/api/indicators.py` | 1,168 | API | 按指标类型拆分 |
| `web/backend/app/api/system.py` | 1,160 | API | 按系统功能拆分 |
| `web/backend/app/api/backup_recovery_secure.py` | 1,027 | API | 按功能拆分 |
| `web/backend/app/services/data_source_factory.py` | 1,000 | 服务 | 按数据源类型拆分 |

---

## 📋 TypeScript/Vue文件详情（web/frontend/src/ 目录）

### Vue组件（2000+ 行）

| 文件 | 行数 | 类型 | 拆分建议 |
|------|------|------|---------|
| `views/artdeco-pages/ArtDecoMarketData.vue` | 3,238 | 页面组件 | **严重超大，需立即拆分** |
| `views/artdeco-pages/ArtDecoDataAnalysis.vue` | 2,425 | 页面组件 | 按功能模块拆分 |
| `components/artdeco/advanced/ArtDecoDecisionModels.vue` | 2,398 | 组件 | 按决策模型拆分 |

### TypeScript文件（2000+ 行）

| 文件 | 行数 | 类型 | 说明 |
|------|------|------|------|
| `api/types/generated-types.ts` | 3,137 | 类型定义 | 自动生成，可保留 |
| `api/types/common.ts` | 2,235 | 类型定义 | 按类型分类拆分 |

### Vue组件（1000-1999 行）

| 文件 | 行数 | 类型 | 说明 |
|------|------|------|------|
| `components/artdeco/advanced/ArtDecoAnomalyTracking.vue` | 1,914 | 组件 | 异常追踪组件 |
| `components/artdeco/advanced/ArtDecoFinancialValuation.vue` | 1,882 | 组件 | 财务估值组件 |
| `components/artdeco/advanced/ArtDecoMarketPanorama.vue` | 1,822 | 组件 | 市场全景组件 |
| `components/artdeco/advanced/ArtDecoCapitalFlow.vue` | 1,768 | 组件 | 资金流向组件 |
| `components/artdeco/advanced/ArtDecoChipDistribution.vue` | 1,716 | 组件 | 筹码分布组件 |
| `components/artdeco/advanced/ArtDecoSentimentAnalysis.vue` | 1,661 | 组件 | 情感分析组件 |
| `views/artdeco-pages/ArtDecoDashboard.vue` | 1,551 | 页面 | 仪表板页面 |
| `components/artdeco/advanced/ArtDecoBatchAnalysisView.vue` | 1,532 | 组件 | 批量分析视图 |
| `components/artdeco/advanced/ArtDecoTimeSeriesAnalysis.vue` | 1,512 | 组件 | 时序分析组件 |
| `views/artdeco-pages/ArtDecoSettings.vue` | 1,414 | 页面 | 设置页面 |
| `views/monitoring/WatchlistManagement.vue` | 1,333 | 页面 | 监控列表管理 |
| `views/demo/FreqtradeDemo.vue` | 1,317 | 页面 | Freqtrade演示 |
| `views/demo/TdxpyDemo.vue` | 1,310 | 页面 | Tdxpy演示 |
| `views/monitoring/RiskDashboard.vue` | 1,245 | 页面 | 风险仪表板 |

---

## 🚨 重复代码警告

### 可能的重复文件

| 主文件 | 行数 | 重复文件 | 行数 | 重复度 | 建议 |
|--------|------|---------|------|--------|------|
| `src/adapters/akshare/market_data.py` | 2,249 | `src/interfaces/adapters/akshare/market_data.py` | 2,521 | 89% | **合并或删除一个** |
| `src/domain/monitoring/intelligent_threshold_manager.py` | 1,315 | `src/monitoring/intelligent_threshold_manager.py` | 1,205 | 91% | **统一到一位置** |
| `src/domain/monitoring/monitoring_service.py` | 1,122 | `src/monitoring/monitoring_service.py` | 1,062 | 95% | **统一到一位置** |
| `src/domain/monitoring/multi_channel_alert_manager.py` | 1,087 | `src/monitoring/multi_channel_alert_manager.py` | 1,009 | 93% | **统一到一位置** |
| `src/gpu/acceleration/gpu_acceleration_engine.py` | 1,218 | `src/gpu/api_system/utils/gpu_acceleration_engine.py` | 1,153 | 95% | **检查是否重复** |

**重复代码问题**：
- 🔴 严重：业务逻辑重复度高（89-95%）
- 🔴 严重：维护成本增加（需要同时修改多处）
- 🔴 严重：容易导致不一致

---

## 🎯 优化建议

### 立即行动（P0 - 本周内）

#### 1. 合并重复代码
```bash
# 发现的重复文件对：
- src/adapters/akshare/market_data.py
  vs src/interfaces/adapters/akshare/market_data.py

- domain/monitoring/* vs monitoring/*
  （4对重复文件）
```

**行动**：
1. 识别主副本和副本
2. 删除副本，统一使用主副本
3. 更新所有导入路径
4. 运行测试验证

#### 2. 拆分超大文件（2000+ 行）

**优先级排序**：
1. `web/frontend/src/views/artdeco-pages/ArtDecoMarketData.vue` (3,238行)
2. `web/frontend/src/api/types/generated-types.ts` (3,137行 - 自动生成)
3. `src/interfaces/adapters/akshare/market_data.py` (2,521行)
4. `src/adapters/akshare/market_data.py` (2,249行)
5. `web/backend/app/api/risk_management.py` (2,112行)

**拆分原则**：
- 按功能模块拆分（每个模块 < 500行）
- 使用工厂模式或策略模式
- 提取共享逻辑到工具函数
- 保持单一职责原则

### 计划行动（P1 - 2-4周内）

#### 3. 拆分1000-1999行的文件

**Python文件**（24个）：
- 按DDD分层重新组织
- 提取业务逻辑到领域服务
- 使用依赖注入降低耦合

**Vue组件**（20+个）：
- 按功能拆分为子组件
- 使用组合式API复用逻辑
- 提取共享UI到基础组件

**TypeScript文件**：
- 按类型定义分类拆分
- 使用模块化导出/导入
- 考虑使用namespace组织

---

## 📈 趋势分析

### 文件大小分布

```
超大文件 (>3000行):     3个  ████████████░░░░░░░░░ 5%
大文件 (2000-2999行):   7个  ████████████████████ 11%
中大型文件 (1000-1999行): 55个 ██████████████████████████████████████████████ 84%
```

### 模块分布

```
前端Vue组件:        20个  ████████████████ 31%
后端Python:         23个  █████████████████ 35%
测试代码:           11个  ████░░░░░░░░░░░░░░ 17%
其他核心代码:       11个  ████░░░░░░░░░░░░░░ 17%
```

---

## ✅ 质量标准

### 代码文件大小建议

| 文件类型 | 推荐行数 | 警告阈值 | 禁止阈值 |
|---------|---------|---------|---------|
| **Python业务逻辑** | < 500 | 500-999 | ≥ 1000 |
| **Python测试** | < 800 | 800-1499 | ≥ 1500 |
| **Vue组件** | < 400 | 400-799 | ≥ 800 |
| **TypeScript类型** | < 600 | 600-1199 | ≥ 1200 |

### 当前状态评估

| 指标 | 当前值 | 目标值 | 状态 |
|------|--------|--------|------|
| 超大文件(>2000行) | 10个 | 0个 | 🔴 需改进 |
| 大文件(1000-1999行) | 55个 | < 20个 | 🔴 需改进 |
| 重复代码对 | 5对 | 0对 | 🔴 需改进 |
| 平均文件行数 | ~1500 | < 500 | 🔴 需改进 |

---

## 🔧 实施计划

### Week 1: 重复代码清理

**目标**: 消除5对重复代码

**任务**:
1. 分析重复代码差异
2. 确定主副本和副本
3. 删除副本文件
4. 更新所有导入路径
5. 运行完整测试套件

### Week 2-3: 超大文件拆分

**目标**: 拆分所有2000+行文件

**任务**:
1. `ArtDecoMarketData.vue` (3238行)
2. `generated-types.ts` (3137行)
3. `akshare/market_data.py` (2521行)
4. `adapters/akshare/market_data.py` (2249行)
5. `risk_management.py` (2112行)

### Week 4-6: 大文件拆分

**目标**: 拆分1000-1999行文件

**优先级**:
1. Python核心业务逻辑（24个文件）
2. Vue组件（20个文件）
3. 后端API（10个文件）
4. 测试文件（11个文件）

### Week 7-8: 质量保障

**目标**: 建立防止大文件产生的机制

**任务**:
1. 配置pre-commit hooks检查文件大小
2. 建立代码审查检查清单
3. 更新开发规范文档
4. 培训团队成员

---

## 📚 相关文档

- **[代码文件长度优化规范](../standards/CODE_SIZE_OPTIMIZATION_REPORT.md)**
- **[前端开发规范](../guides/FRONTEND_DEV_GUIDELINES.md)**
- **[Python质量保障工作流程](../operations/ci-cd/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md)**

---

**报告生成时间**: 2026-01-28
**下次更新**: 完成Week 1任务后
**负责人**: 开发团队
**审核人**: 架构师

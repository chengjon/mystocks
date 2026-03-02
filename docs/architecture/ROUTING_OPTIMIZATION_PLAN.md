# 路由优化方案 (Routing Optimization Plan)

**版本**: v1.0
**日期**: 2026-02-14
**状态**: 执行中

---

## 1. 现状问题分析

通过对现有路由系统 (`web/frontend/src/router/index.ts`) 和组件库的深度审计，发现以下关键问题：

1.  **Risk 域功能缺失**：
    *   `/risk/overview`, `/risk/alerts`, `/risk/indicators` 等 5 个页面全部指向同一个占位组件 `ArtDecoMarketQuotes.vue`。
    *   **后果**：风控模块完全不可用，用户点击不同菜单看到的是同一个无关页面。

2.  **高级资产闲置**：
    *   `src/views/advanced-analysis/` 目录下有 13 个高质量视图组件（如 `FundamentalAnalysisView`, `SentimentAnalysisView`），但从未被路由引用。
    *   **后果**：开发资源浪费，系统分析能力被人为阉割。

3.  **API 对接断层**：
    *   后端已提供 `/api/v1/system/api-health` 等接口，但前端 `/system/api-health` 使用占位符，未实际调用。

4.  **架构游离**：
    *   大量的 Demo 页面（如 `StockAnalysisDemo`）游离于主导航之外，难以被测试和复用。

---

## 2. 优化方案详情

本方案旨在通过**路由重构**和**组件激活**，在不大量编写新代码的前提下，显著提升系统的功能完整度。

### 2.1 变更概览

| 变更类型 | 数量 | 涉及领域 | 详情 |
| :--- | :--- | :--- | :--- |
| **替换占位符** | 5 | Risk (风控) | 将所有 Risk 路由指向真实的风控组件（如 `ArtDecoRiskMonitor`）。 |
| **组件增强** | 4 | Market/Strategy | 移除重复引用的 `ArtDecoMarketQuotes`，指向专用组件。 |
| **新增路由域** | 1 | Analysis (分析) | 新增顶级路由 `/analysis`，挂载 4-6 个核心高级分析视图。 |
| **新建页面** | 2 | Strategy/System | 实装 `GPU Backtest` 和 `API Health` 页面。 |

### 2.2 具体路由变更表

#### A. 激活 Risk 域 (替换占位符)

| 路径 | 原组件 (占位) | 新组件 (真实) | 状态 |
| :--- | :--- | :--- | :--- |
| `/risk/overview` | `ArtDecoMarketQuotes` | `src/views/artdeco-pages/risk-tabs/ArtDecoRiskMonitor.vue` | ✅ 现有 |
| `/risk/alerts` | `ArtDecoMarketQuotes` | `src/views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue` | ✅ 现有 |
| `/risk/indicators` | `ArtDecoMarketQuotes` | `src/views/artdeco-pages/components/AnalysisIndicators.vue` | ✅ 复用 |
| `/risk/sentiment` | `ArtDecoMarketQuotes` | `src/views/advanced-analysis/SentimentAnalysisView.vue` | ✅ 激活 |
| `/risk/announcement` | `ArtDecoMarketQuotes` | `src/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue` | ✅ 现有 |

#### B. 新增 Analysis 域 (激活高级视图)

新增顶级路由 `/analysis`，下设子路由：

| 路径 | 组件来源 | 功能描述 |
| :--- | :--- | :--- |
| `/analysis/fundamental` | `src/views/advanced-analysis/FundamentalAnalysisView.vue` | 基本面分析 |
| `/analysis/technical` | `src/views/advanced-analysis/TechnicalAnalysisView.vue` | 高级技术分析 |
| `/analysis/chip` | `src/views/advanced-analysis/ChipDistributionView.vue` | 筹码分布 |
| `/analysis/valuation` | `src/views/advanced-analysis/FinancialValuationView.vue` | 财务估值 |

#### C. 实装功能页面

| 路径 | 动作 | 方案 |
| :--- | :--- | :--- |
| `/strategy/gpu-backtest` | 实装 | 指向 `src/views/advanced-analysis/BatchAnalysisView.vue` (暂代) |
| `/system/api-health` | 实装 | 指向 `src/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue` (复用监控面板) |

---

## 3. 预期成果

*   **页面总数**：从 41 个提升至 **51 个**（有效叶子页面）。
*   **功能完整度**：Risk 域从 0% 提升至 100%（组件覆盖率）。
*   **资产利用率**：激活了 5+ 个沉睡的高级组件。

---

## 4. 下一步计划

1.  修改 `router/index.ts` 实施上述变更。
2.  运行 `verify:web-access` 验证新路由的可访问性。
3.  对新激活的页面进行 API 对接检查。

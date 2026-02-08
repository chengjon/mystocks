# ArtDeco System Architecture Summary (V3.0)

本系统是基于 MyStocks 项目的高端金融级 UI 体系，旨在为量化交易提供极高信息密度的专业交互体验。

## 1. 核心架构原则 (Architecture Principles)

### 1.1 "Container-Tab" 混合架构
系统弃用了过时的“超大单体组件”，演进为**容器化管理**模式：
*   **父容器 (Parent Containers)**: 位于 `views/artdeco-pages/`，负责路由接入、全局 Tab 状态管理和通用 API 配置。
*   **领域组件 (Domain Components)**: 位于 `views/artdeco-pages/components/`，按业务领域（market, risk, strategy 等）分拆，实现 1:1 的功能复刻。
*   **基础资产 (Base Assets)**: 位于 `src/components/artdeco/`，提供原子级的 UI 支持。

### 1.2 统一配置驱动
系统通过 `pageConfig.ts` 动态驱动。父容器根据当前激活的 Tab 名，自动从配置中提取 `apiEndpoint` 和 `wsChannel`，并下发给领域组件，实现了业务逻辑与界面表现的完全解耦。

## 2. 视觉规范层 (Visual Layer - V3.0)

### 2.1 设计令牌 (Design Tokens)
**文件**: `web/frontend/src/styles/artdeco-tokens.scss`
*   **主色调**: 黑曜石黑 (`#0A0A0A`) + 金属金 (`#D4AF37`)。
*   **间距体系**: 11 级精确系统，从 `4px` (`--artdeco-spacing-1`) 到 `128px` (`--artdeco-spacing-32`)。
*   **字体栈**: 
    *   Display: `Cinzel` (几何衬线，用于标题)
    *   Body: `Barlow` (现代无衬线，极佳的可读性)
    *   Mono: `JetBrains Mono` (用于金融数值对齐)

### 2.2 A 股特定规范
系统强制执行 A 股“红涨绿跌”视觉语义：
*   `--artdeco-rise`: `#FF5252` (上涨/盈利)
*   `--artdeco-down`: `#00E676` (下跌/亏损)

## 3. 领域划分与组件分布 (Domain Mapping)

| 领域 (Domain) | 父容器 | 核心分拆组件 (位于 components/) |
|:---|:---|:---|
| **市场中心** | `ArtDecoMarketData.vue` | `MarketOverview`, `FundFlow`, `LHB`, `ETFAnalysis` |
| **交易管理** | `ArtDecoTradingCenter.vue` | `SignalsView`, `HistoryView`, `PositionMonitor` |
| **风险控制** | `ArtDecoRiskManagement.vue` | `RiskMonitor`, `AnnouncementMonitor`, `RiskAlerts` |
| **策略研发** | `ArtDecoStrategyLab.vue` | `StrategyManagement`, `BacktestAnalysis`, `Optimization` |

## 4. 可验证性说明 (Verifiability)

开发者可通过以下路径验证系统一致性：
1.  **物理核实**: 检查 `src/components/artdeco/` 下的 66+ 个组件是否与 [组件目录](../web/ART_DECO_COMPONENTS_CATALOG.md) 一致。
2.  **样式验证**: 检查 `.vue` 文件是否通过 `@import '@/styles/artdeco-tokens.scss'` 导入令牌，而非硬编码颜色。
3.  **布局验证**: 检查是否使用了 `@include artdeco-grid` 实现响应式降级（4列 -> 2列 -> 1列）。

---
**维护者**: UI/UX Pro Max Agent
**最后更新**: 2026-02-08 (基于 V3.0 代码库核实)

# ArtDeco System Architecture Summary (V3.1 Governance Baseline)

本系统是 MyStocks 项目的金融级 UI 架构摘要，当前维护口径为 ArtDeco v3/v3.1。

## 1. 核心架构原则

### 1.1 Container-Tab 混合架构
系统采用容器化管理模式：
- **父容器 (Parent Containers)**: `views/artdeco-pages/`，负责路由接入、Tab 状态管理和 API 配置下发。
- **领域组件 (Domain Components)**: `views/artdeco-pages/components/`，按 market/risk/strategy 等域拆分。
- **基础资产 (Base Assets)**: `src/components/artdeco/`，提供可复用原子与业务组件。

### 1.2 配置驱动与解耦
父容器通过 `pageConfig.ts` 按激活 Tab 分发 `apiEndpoint` 与 `wsChannel`，实现展示层与业务接入层解耦。

## 2. 视觉治理层

### 2.1 设计令牌事实源
- **主令牌文件**: `web/frontend/src/styles/artdeco-tokens.scss`
- **治理清单**: `web/frontend/src/styles/artdeco-governance-manifest.json`

两者共同构成 v3.1 治理基线：前者定义 token，后者定义可验证治理约束（token/字体/间距/文档路径）。

### 2.2 视觉语义与 A 股规范
- 主色体系：黑曜石黑 + 金属金。
- 涨跌颜色：红涨绿跌（`--artdeco-rise` / `--artdeco-down`）。

## 3. 领域映射

| 领域 | 父容器 | 核心分拆组件 |
|:---|:---|:---|
| 市场中心 | `ArtDecoMarketData.vue` | `MarketOverview`, `FundFlow`, `LHB`, `ETFAnalysis` |
| 交易管理 | `ArtDecoTradingCenter.vue` | `SignalsView`, `HistoryView`, `PositionMonitor` |
| 风险控制 | `ArtDecoRiskManagement.vue` | `RiskMonitor`, `AnnouncementMonitor`, `RiskAlerts` |
| 策略研发 | `ArtDecoStrategyLab.vue` | `StrategyManagement`, `BacktestAnalysis`, `Optimization` |

## 4. 可验证性

开发者可通过以下方式验证一致性：
1. 组件目录与组件清单一致。
2. 样式使用 `--artdeco-*` token，避免硬编码。
3. 布局遵循 ArtDeco Grid/Mixin 规范。

---
**维护口径**: V3.1 Governance Baseline
**最后更新**: 2026-02-13

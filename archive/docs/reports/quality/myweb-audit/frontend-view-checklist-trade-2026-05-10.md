# Frontend View Checklist: `views/trade/*`

日期：2026-05-10

范围：`web/frontend/src/views/trade/*`

本批次目的：复核交易管理域中当前活跃路由页、view-local 支持资产、跨壳层复用关系，避免把仍在 router truth 内的 canonical 交易页误归档，也避免为旧壳层补独立 live snapshot 或平行状态。

## 1. Truth Inputs

菜单 / 路由真相：

- `web/frontend/src/layouts/MenuConfig.ts` 当前交易管理菜单包含 `/trade/positions`、`/trade/terminal`、`/trade/execution`、`/trade/signals`、`/trade/portfolio`、`/trade/history`、`/trade/reconciliation`。
- `web/frontend/src/router/index.ts` 当前动态导入：
- `/trade/positions` -> `@/views/trade/Center.vue`。
- `/trade/terminal` -> `@/views/TradingDashboard.vue`，这是顶层 special route owner，不属于 `views/trade/*` 本批次页面。
- `/trade/execution` -> `@/views/trade/Execution.vue`。
- `/trade/signals` -> `@/views/trade/Signals.vue`。
- `/trade/portfolio` -> `@/views/trade/Portfolio.vue`。
- `/trade/history` -> `@/views/trade/History.vue`。
- `/trade/reconciliation` -> `@/views/trade/Reconciliation.vue`。

配置 / 功能树证据：

- `web/frontend/src/config/pageConfig.ts` 仍登记 `trade-positions`、`trade-terminal`、`trade-signals`、`trade-portfolio`、`trade-history`、`trade-reconciliation`；其中 `trade-terminal` component 为 `TradingDashboard.vue`。
- `docs/FUNCTION_TREE.md` 将 `Center.vue`、`Portfolio.vue`、`History.vue`、`Reconciliation.vue`、`Signals.vue`、`Execution.vue` 标记为交易域持仓、组合透视、交易流水、对账、信号、执行跟踪功能入口。
- `openspec/changes/restructure-frontend-directory/tasks.md` 记录 `Center.vue`、`Signals.vue`、`Portfolio.vue`、`History.vue` 已作为 canonical route entry，旧 ArtDeco wrapper 保留为兼容包装。

跨壳层复用证据：

- `web/frontend/src/views/artdeco-pages/ArtDecoTradingManagement.vue` 复用 `@/views/trade/Portfolio.vue`、`Signals.vue`、`Center.vue`、`History.vue`。
- `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` 复用 `@/views/trade/Portfolio.vue`，并承载 `/risk/pnl` 路由包装。
- `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue`、`ArtDecoSignalsView.vue`、`ArtDecoTradingHistory.vue`、`ArtDecoPerformanceAnalysis.vue`、`ArtDecoPositionMonitor.vue` 等旧壳层反向复用 `views/trade/*` canonical 页面。
- `web/frontend/src/views/trading/History.vue`、`web/frontend/src/views/trading-decision/DecisionPositions.vue`、`web/frontend/src/views/trading-decision/DecisionPortfolio.vue` 也复用对应 canonical 交易页。

直接测试守护：

- `web/frontend/src/views/trade/__tests__/Center.spec.ts`
- `web/frontend/src/views/trade/__tests__/Execution.spec.ts`
- `web/frontend/src/views/trade/__tests__/Signals.spec.ts`
- `web/frontend/src/views/trade/__tests__/Portfolio.spec.ts`
- `web/frontend/src/views/trade/__tests__/History.spec.ts`
- `web/frontend/src/views/trade/__tests__/Reconciliation.spec.ts`

## 2. Page Classification

| 页面 | 当前分类 | 路由状态 | 资产状态 | 守护状态 | 结论 |
| --- | --- | --- | --- | --- | --- |
| `views/trade/Center.vue` | `canonical-active` | `/trade/positions` | 头寸管理 / 持仓查询 route owner | direct spec + wrapper specs | 排除归档审核 |
| `views/trade/Execution.vue` | `canonical-active` | `/trade/execution` | 执行跟踪 / 外部触发观测 route owner | direct spec + execution manifests | 排除归档审核 |
| `views/trade/Signals.vue` | `canonical-active` | `/trade/signals` | 信号监控 route owner | direct spec + wrapper specs | 排除归档审核 |
| `views/trade/Portfolio.vue` | `canonical-active` | `/trade/portfolio` | 持仓透视 / 组合归因 route owner | direct spec + risk wrapper specs | 排除归档审核 |
| `views/trade/History.vue` | `canonical-active` | `/trade/history` | 交易历史 route owner | direct spec + wrapper specs | 排除归档审核 |
| `views/trade/Reconciliation.vue` | `canonical-active` | `/trade/reconciliation` | 对账单 route owner | direct spec + reconciliation manifests | 排除归档审核 |
| `views/trade/Execution.css` | `canonical-support-asset` | style | `Execution.vue` 页面样式资产 | tied to active route | 非 view，排除归档审核 |
| `views/trade/styles/Portfolio.scss` | `canonical-support-asset` | style | `Portfolio.vue` 页面样式资产 | tied to active route | 非 view，排除归档审核 |
| `views/trade/composables/useTradeReconciliation.ts` | `canonical-support-asset` | helper | `Reconciliation.vue` view-local composable | imported by active route + direct spec | 非 view，排除归档审核 |
| `views/trade/composables/reconciliationDataTransform.ts` | `canonical-support-asset` | helper | 对账数据归一化工具 | imported by active reconciliation composable | 非 view，排除归档审核 |

## 3. Redundant-Page Checklist

本批次未发现可直接归档页面。

必须保留的页面：

- `Center.vue`、`Execution.vue`、`Signals.vue`、`Portfolio.vue`、`History.vue`、`Reconciliation.vue` 全部是当前 `router/index.ts` 的 active route owner，不能进入 archive flow。
- `Portfolio.vue` 同时是 `/trade/portfolio` 的 canonical owner，并被 `/risk/pnl` wrapper 与多个旧壳层复用；不能因为跨域复用而下沉为另一个平行页面真相。
- `Center.vue`、`Signals.vue`、`History.vue` 已作为旧 ArtDeco trading-tabs wrapper 的 canonical target；旧壳层应继续薄包装，不得反向持有独立 live snapshot。
- `Reconciliation.vue` 的 `useTradeReconciliation.ts` 和 `reconciliationDataTransform.ts` 属于 view-local canonical 支持层，符合单消费者 co-location 口径，不应为治理而机械抽到全局 `src/composables/`。

禁止误判项：

- `/trade/terminal` 当前由 `web/frontend/src/views/TradingDashboard.vue` 持有，不在 `views/trade/*` 目录；不能把 `views/trade/*` 误判为缺少 terminal 页面。
- `views/trading/*`、`views/trading-decision/*`、`views/trade-management/components/*` 是已单独审核过的旧交易壳层 / 决策壳层 / 二级组件资产；不能和本批次 canonical route owner 混为同一归档池。
- `ArtDecoTradingManagement.vue` 等壳层只能复用 canonical `/trade/*` 已有数据真相；无可复用真值的 tab 应降级为静态壳，不允许补假数据或维护壳层级 snapshot / store 独立状态。
- 壳层头部不得展示无来源实况数据，例如 source-less `REQ_ID`、`SYNC`、今日盈亏、市场状态；所有实况数据必须来自对应 `/trade/*` canonical 页面已验证快照。

## 4. Batch Conclusion

`views/trade/*` 当前应拆成两类治理：

- `canonical-active`：`Center.vue`、`Execution.vue`、`Signals.vue`、`Portfolio.vue`、`History.vue`、`Reconciliation.vue`，全部直接排除 archive flow。
- `canonical-support-asset`：`Execution.css`、`Portfolio.scss`、`useTradeReconciliation.ts`、`reconciliationDataTransform.ts`，均随 active route owner 保留。

本批次没有 `candidate-review` 页面，也没有文件进入 `archive-approved`。后续若继续治理交易相关旧壳层，应优先处理壳层是否仍需要兼容包装、是否仍有 direct spec 或 mainline guard，以及是否已经完全吸收为 canonical `/trade/*` 页面能力。

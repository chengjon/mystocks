# Frontend View Checklist: `views/risk/*`

日期：2026-05-10

范围：`web/frontend/src/views/risk/*`

本批次目的：复核风险域目录中当前路由页、跨域 wrapper 路由、已收口 orphan 静态壳的边界，避免把活跃风险页或历史守护壳按“未路由”误归档。

## 1. Truth Inputs

菜单 / 路由真相：

- `web/frontend/src/layouts/MenuConfig.ts` 当前风险菜单包含 `/risk/management`、`/risk/overview`、`/risk/pnl`、`/risk/stop-loss`、`/risk/alerts`、`/risk/news`。
- `web/frontend/src/router/index.ts` 当前动态导入：
- `/risk/management` -> `@/views/risk/Center.vue`，并保留 alias `/risk-management`。
- `/risk/overview` -> `@/views/risk/Overview.vue`。
- `/risk/pnl` -> `@/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`，实际继承 `trade/Portfolio.vue` 真值，不使用 `views/risk/Portfolio.vue`。
- `/risk/stop-loss` -> `@/views/risk/StopLoss.vue`。
- `/risk/alerts` -> `@/views/risk/Alerts.vue`。
- `/risk/news` -> `@/views/risk/News.vue`。

配置 / 功能树证据：

- `web/frontend/src/config/pageConfig.ts` 仍登记 `risk-overview`、`risk-pnl`、`risk-stop-loss`、`risk-alerts`、`risk-news`。
- `docs/FUNCTION_TREE.md` 将 `views/risk/Overview.vue`、`views/risk/Alerts.vue`、`views/risk/News.vue` 等列为风险、监控与公告能力入口。
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/risk-orphan-static-shells-truth-audit.md` 明确 `Portfolio.vue`、`Positions.vue` 已降级为 orphan static shell，未新增 API、store、snapshot、request badge 或 shell-owned execution state。

直接测试守护：

- `web/frontend/src/views/risk/__tests__/Center.spec.ts`
- `web/frontend/src/views/risk/__tests__/Overview.spec.ts`
- `web/frontend/src/views/risk/__tests__/StopLoss.spec.ts`
- `web/frontend/src/views/risk/__tests__/Alerts.spec.ts`
- `web/frontend/src/views/risk/__tests__/News.spec.ts`
- `web/frontend/tests/unit/config/risk-orphan-static-shells.spec.ts`

## 2. Page Classification

| 页面 | 当前分类 | 路由状态 | 资产状态 | 守护状态 | 结论 |
| --- | --- | --- | --- | --- | --- |
| `views/risk/Center.vue` | `canonical-active` | `/risk/management` + `/risk-management` alias | 风险管理中心 active route | direct spec + docs | 排除归档审核 |
| `views/risk/Overview.vue` | `canonical-active` | `/risk/overview` | 风险概览 active route | direct spec + audit manifests | 排除归档审核 |
| `views/risk/StopLoss.vue` | `canonical-active` | `/risk/stop-loss` | 止损雷达 active route | direct spec + audit manifests | 排除归档审核 |
| `views/risk/Alerts.vue` | `canonical-active` | `/risk/alerts` | 告警中心 active route | direct spec + function tree | 排除归档审核 |
| `views/risk/News.vue` | `canonical-wrapper-active` | `/risk/news` | 风险域公告/舆情 wrapper，复用 AI 情感工作台 | direct spec + function tree | 排除归档审核 |
| `views/risk/Portfolio.vue` | `candidate-review` | dead route | orphan static shell，不是 `/risk/pnl` owner | unit source guard + audit doc | 不归档，需先迁移/退役守护 |
| `views/risk/Positions.vue` | `candidate-review` | dead route | orphan static shell，无当前 route owner | unit source guard + audit doc | 不归档，需先迁移/退役守护 |

## 3. Redundant-Page Checklist

本批次未发现可直接归档页面。

必须保留的页面：

- `Center.vue`、`Overview.vue`、`StopLoss.vue`、`Alerts.vue` 是当前 `/risk/*` active route owner，并已有页面级测试守护。
- `News.vue` 是 `/risk/news` active wrapper route，保留风险域入口并复用 AI 情感工作台数据编排；它不是孤立重复页。

暂不归档的候选页面：

- `Portfolio.vue`、`Positions.vue` 已经降级为 honest static shell，不再展示 Phase roadmap 占位或未验证风险执行态。
- 两个 orphan 静态壳仍被 `risk-orphan-static-shells.spec.ts` 和历史审计文档守护，当前只能保留为 `candidate-review`。
- `Positions.vue` 当前 handoff 指向 `/risk/position`，而当前路由真相没有该路径；这是后续需要修正的 stale handoff 观察项，不能反向证明页面可直接归档。

禁止误判项：

- `/risk/pnl` 的当前实现是 `artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`，并继承 `trade/Portfolio.vue` 真值；不得把 `views/risk/Portfolio.vue` 当作 `/risk/pnl` 的 active implementation。
- `RiskMonitor.vue`、`EnhancedRiskMonitor.vue` 等顶层 legacy wrapper 已在 top-level legacy 批次中处理，不属于本 `views/risk/*` 目录批次。
- 旧 docs 中出现的 `RiskMonitor.vue`、`/risk-monitor/*`、`Phase 7` 描述多为历史快照，不能覆盖当前 router truth。

## 4. Batch Conclusion

`views/risk/*` 当前应拆成三类治理：

- `canonical-active`：`Center.vue`、`Overview.vue`、`StopLoss.vue`、`Alerts.vue`，直接排除 archive flow。
- `canonical-wrapper-active`：`News.vue`，作为风险域 wrapper 保留。
- `candidate-review`：`Portfolio.vue`、`Positions.vue`，仅登记为 orphan static shell 候选，不满足 archive-approved 条件。

本批次没有文件进入 `archive-approved`。后续若要处理 `Portfolio.vue`、`Positions.vue`，应先修正或明确 `Positions.vue` 的 stale handoff，再决定是否迁移/退役 `risk-orphan-static-shells.spec.ts`。

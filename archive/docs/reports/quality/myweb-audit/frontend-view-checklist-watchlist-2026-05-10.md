# Frontend View Checklist: `views/watchlist/*`

日期：2026-05-10

范围：`web/frontend/src/views/watchlist/*`

本批次目的：复核自选管理域目录是否存在可直接归档的冗余页，并确认该目录下 3 个 Vue 文件均为当前路由入口或薄包装入口，不应被误判为 legacy archive candidate。

## 1. Truth Inputs

菜单 / 路由真相：

- `web/frontend/src/layouts/MenuConfig.ts` 当前自选管理菜单包含 `/watchlist/manage`、`/watchlist/signals`、`/watchlist/screener`。
- `web/frontend/src/router/index.ts` 当前动态导入：
- `/watchlist/manage` -> `@/views/watchlist/Manage.vue`。
- `/watchlist/signals` -> `@/views/watchlist/Signals.vue`。
- `/watchlist/screener` -> `@/views/watchlist/Screener.vue`。

配置 / 历史迁移证据：

- `web/frontend/src/config/pageConfig.ts` 仍登记 `watchlist-manage`、`watchlist-signals`、`watchlist-screener`。
- `openspec/changes/restructure-frontend-directory/tasks.md` 明确：
  - `views/watchlist/Manage.vue` fronts `WatchlistManager.vue`
  - `views/watchlist/Signals.vue` fronts `StrategySignalsTab.vue`
  - `views/watchlist/Screener.vue` fronts `stocks/Screener.vue`
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/watchlist-screener-summary-truth-audit.md` 明确 `watchlist/Screener.vue` 的 routed surface owner 是 `stocks/Screener.vue`。
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/watchlist-manage-slice-summary-truth-audit.md` 明确 `watchlist/Manage.vue` 是 canonical routed entry。

直接测试守护：

- `web/frontend/src/views/watchlist/__tests__/Manage.spec.ts`
- `web/frontend/src/views/watchlist/__tests__/Signals.spec.ts`
- `web/frontend/src/views/watchlist/__tests__/Screener.spec.ts`

## 2. Page Classification

| 页面 | 当前分类 | 路由状态 | 资产状态 | 守护状态 | 结论 |
| --- | --- | --- | --- | --- | --- |
| `views/watchlist/Manage.vue` | `canonical-route-wrapper` | `/watchlist/manage` | 组合管理入口，薄包装到 `WatchlistManager.vue` | direct spec + migration tasks | 排除归档审核 |
| `views/watchlist/Signals.vue` | `canonical-route-wrapper` | `/watchlist/signals` | 信号雷达入口，薄包装到 `StrategySignalsTab.vue`，但以 watchlist surface variant 约束语义 | direct spec + migration tasks | 排除归档审核 |
| `views/watchlist/Screener.vue` | `canonical-route-wrapper` | `/watchlist/screener` | 策略选股入口，薄包装到 `stocks/Screener.vue` | direct spec + migration tasks | 排除归档审核 |

## 3. Redundant-Page Checklist

本批次未发现可直接归档页面，也未发现 `views/watchlist/*` 目录内的 `candidate-review` Vue 页面。

必须保留的页面：

- `Manage.vue`、`Signals.vue`、`Screener.vue` 全部是当前 route truth，且都处于薄包装或 surface-variant 入口形态。
- `Signals.vue` 虽复用策略域的 `StrategySignalsTab.vue`，但它是 watchlist 入口的语义化包装，不是冗余复制页。
- `Screener.vue` 直接包装 `views/stocks/Screener.vue`，这说明 watchlist 域当前承接的是跨域复用入口，不是待清理的独立死页。

必须保留的支持依赖：

- `views/stocks/Screener.vue` 是 `watchlist/Screener.vue` 的 routed surface owner，因此 `watchlist` 域的治理必须与 `stocks` 域的兼容关系一起看。
- `watchlist` 目录当前没有任何“可直接归档但未审”的残留壳页，因此不需要 successor / no-successor-needed 单独判定。

禁止误判项：

- `watchlist` 目录中的 3 个 Vue 文件都在 router truth 内，不能按“未路由”处理。
- `Signals.vue` 复用策略域组件不等于策略域入口回流到 watchlist；它仍是 watchlist 域的兼容包装。
- `Screener.vue` 的跨域依赖是设计上的转发，不是重复实现。

## 4. Batch Conclusion

`views/watchlist/*` 当前应拆成一类治理：

- `canonical-route-wrapper`：`Manage.vue`、`Signals.vue`、`Screener.vue`，全部直接排除 archive flow。

本批次没有文件进入 `archive-approved`，也没有 `candidate-review` 页面需要继续拆解。后续治理应优先沿跨域依赖链检查 `stocks/Screener.vue` 的兼容边界，而不是把 watchlist 目录本身视作冗余来源。

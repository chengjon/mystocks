# Frontend View Governance A4 Demo OpenStock Root Sidecars Inventory

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: read-only exact inventory for `A4-demo-openstock-root-sidecars-inventory`.

This inventory does not move files, edit runtime code, update routes, or retire tests.

## Scope Boundary

Included:

- `web/frontend/src/views/OpenStockDemo.vue`
- `web/frontend/src/views/demo/OpenStockDemo.vue`
- `web/frontend/src/views/demo/openstock/components/*`
- `web/frontend/src/views/demo/openstock/config.ts`
- `web/frontend/src/views/examples/*`
- `web/frontend/src/views/freqtrade-demo/*`
- `web/frontend/src/views/tdxpy-demo/*`
- root demo/test/sandbox pages covered by `frontend-view-checklist-root-demo-sidecars-2026-05-11.md`

Excluded:

- `web/frontend/src/views/TradingDashboard.vue`: active `/trade/terminal` route truth.
- `web/frontend/src/views/Login.vue` and `web/frontend/src/views/NotFound.vue`: already covered by blank-layout governance.
- `web/frontend/src/views/PageTitleDemo.vue`: already archived by A1-minimal and absent from the active root view directory.
- Full `views/demo/pyprofiling/*` and `views/demo/stock-analysis/*` child trees: already covered by the broader demo-directory checklist and not part of this OpenStock/root-sidecar inventory.
- `archive/` records and historical report mentions.

## Reconciliation Summary

| Group | Exact active files | Router/menu owner | Direct importer status | Guard/test status | Lifecycle result |
| --- | ---: | --- | --- | --- | --- |
| OpenStock duplicate shells and shared child tree | 10 | No active router/menu owner | Root and demo shells import the same OpenStock child tree | `src/views/demo` package gate plus OpenStock style-source specs | `absorb-assets` / decision-required |
| Examples | 5 | No active router/menu owner | README and example config references | `examples-mainline-gate` plus style-source specs | `retain-as-demo` until example relocation decision |
| Freqtrade parent and tabs | 7 | No active router/menu owner | Root `FreqtradeDemo.vue` imports all tab files | `freqtrade-demo-mainline-gate` plus demo style guard | parent-child decision required |
| Tdxpy parent and tabs | 6 | No active router/menu owner | Root `TdxpyDemo.vue` imports all tab files | `tdxpy-demo-mainline-gate` plus demo style guard | parent-child decision required |
| Root demo/test/sandbox singletons | 9 | No active router/menu owner | Mostly no runtime importer; several have direct specs/package guards | package file-level token targets, root-demo specs, workflow guards | mixed `retain-as-demo` / `absorb-assets` / `archive-candidate` candidates |

No active file in this inventory is archive-approved by this document.

## Truth Inputs

Router and menu truth:

- `web/frontend/src/router/index.ts` has no current dynamic import for `views/OpenStockDemo.vue`, `views/demo/OpenStockDemo.vue`, `views/examples/*`, `views/freqtrade-demo/*`, `views/tdxpy-demo/*`, or the root demo/test/sandbox pages in this inventory.
- `web/frontend/src/layouts/MenuConfig.ts` has no current menu owner for the same set.
- `web/frontend/src/views/TradingDashboard.vue` remains excluded because it is the active `/trade/terminal` route owner.

Direct importer truth:

- `web/frontend/src/views/OpenStockDemo.vue` imports `./demo/openstock/config` and `./demo/openstock/components`.
- `web/frontend/src/views/demo/OpenStockDemo.vue` imports `./openstock/config` and `./openstock/components`.
- `web/frontend/src/views/FreqtradeDemo.vue` imports all files in `views/freqtrade-demo/*.vue`.
- `web/frontend/src/views/TdxpyDemo.vue` imports all files in `views/tdxpy-demo/*.vue`.
- `web/frontend/src/config/pageConfigExtended.example.ts` references `@/views/examples/composables/useTradingDashboard.migrated` as example guidance.
- `views/examples/README.md` documents `PageConfigExample.vue` and example usage.

Guard and package truth:

- `web/frontend/package.json` includes `src/views/demo`, `src/views/examples`, `src/views/freqtrade-demo`, and `src/views/tdxpy-demo` in `lint:artdeco:changed`.
- `web/frontend/package.json` also includes file-level targets for root demo/test/sandbox pages such as `SkeletonUsage.vue`, `ArtDecoTest.vue`, `SmartDataSourceTest.vue`, `DataVisualizationShowcase.vue`, `Phase4Dashboard.vue`, `Wencai.vue`, `StockAnalysisDemo.vue`, and `PyprofilingDemo.vue`.
- Config specs directly guard OpenStock component style sources, example style sources, Freqtrade/Tdxpy directory coverage, root demo style entrypoints, and SkeletonUsage workflow/tokenization constraints.
- Reference scanning hit permission-denied noise in `.claude/edit_log.jsonl` sidecar logs; those files are non-runtime sidecars and are not used as page-routing evidence.

## Exact Inventory

### OpenStock Shells And Child Tree

| File | Route/menu | Direct importer | Guard/test | Lifecycle | Successor or next decision |
| --- | --- | --- | --- | --- | --- |
| `web/frontend/src/views/OpenStockDemo.vue` | none | none found as route/menu; imports shared OpenStock demo child tree | guard-map/package-history referenced | `absorb-assets` / duplicate-shell decision | Compare against `views/demo/OpenStockDemo.vue`; keep at most one demo shell or absorb into canonical market/watchlist/data pages |
| `web/frontend/src/views/demo/OpenStockDemo.vue` | none | none found as route/menu; imports local OpenStock child tree | `openstock-demo-style-source.spec.ts`; covered by `src/views/demo` gate | `retain-as-demo` / duplicate-shell decision | Preferred demo-directory owner if OpenStock remains as demo documentation |
| `web/frontend/src/views/demo/openstock/config.ts` | none | imported by both OpenStock shells through relative paths | covered by demo directory lifecycle | `absorb-assets` | Keep only with selected OpenStock shell or extract constants during absorption |
| `web/frontend/src/views/demo/openstock/components/index.ts` | none | imported by both OpenStock shells | covered by demo directory lifecycle | `absorb-assets` | Keep with child component tree until shell decision |
| `web/frontend/src/views/demo/openstock/components/FeatureStatus.vue` | none | exported by component barrel and rendered by OpenStock shells | `openstock-feature-status-style-source.spec.ts`; guard-map referenced | `absorb-assets` | Retain only if OpenStock demo remains; otherwise no canonical successor unless API-status demo is documented |
| `web/frontend/src/views/demo/openstock/components/HeatmapChart.vue` | none | OpenStock shell child component | `openstock-heatmap-style-source.spec.ts`; guard-map referenced | `absorb-assets` | Candidate successor: canonical market/heatmap surface if feature exists; otherwise demo-only |
| `web/frontend/src/views/demo/openstock/components/KlineChart.vue` | none | OpenStock shell child component | `openstock-kline-style-source.spec.ts`; guard-map referenced | `absorb-assets` | Candidate successor: canonical market/technical K-line route |
| `web/frontend/src/views/demo/openstock/components/StockNews.vue` | none | OpenStock shell child component | `openstock-stock-news-style-source.spec.ts`; guard-map referenced | `absorb-assets` | Candidate successor: canonical market/detail/news surface if retained |
| `web/frontend/src/views/demo/openstock/components/StockQuote.vue` | none | OpenStock shell child component | `openstock-stock-quote-style-source.spec.ts`; guard-map referenced | `absorb-assets` | Candidate successor: canonical market quote/detail surface |
| `web/frontend/src/views/demo/openstock/components/StockSearch.vue` | none | OpenStock shell child component | `openstock-stock-search-style-source.spec.ts`; guard-map referenced | `absorb-assets` | Candidate successor: canonical market search or watchlist add-stock flow |
| `web/frontend/src/views/demo/openstock/components/WatchlistManagement.vue` | none | OpenStock shell child component | `openstock-watchlist-style-source.spec.ts`; guard-map referenced | `absorb-assets` | Compare against canonical `/watchlist/manage`; do not confuse with archived monitoring Watchlist page |

### Examples

| File | Route/menu | Direct importer | Guard/test | Lifecycle | Successor or next decision |
| --- | --- | --- | --- | --- | --- |
| `web/frontend/src/views/examples/PageConfigExample.vue` | none | README example reference | `examples-page-config-style-source.spec.ts`; examples directory gate | `retain-as-demo` | Relocate to documentation examples or retire with `no-successor-needed` only after docs update |
| `web/frontend/src/views/examples/WebSocketConfigExample.vue` | none | README/doc example reference | `examples-websocket-style-source.spec.ts`; examples directory gate | `retain-as-demo` | Absorb useful WebSocket guidance into shared docs before archive |
| `web/frontend/src/views/examples/TradingDashboard.migrated.vue` | none | example-only | `examples-trading-dashboard-style-source.spec.ts`; examples directory gate | `retain-as-demo` | Keep as migration reference; do not merge into active `/trade/terminal` |
| `web/frontend/src/views/examples/composables/useTradingDashboard.migrated.ts` | none | imported by migrated example; referenced by example page config | examples directory lifecycle | `retain-as-demo` | Keep paired with migrated example or move both into docs/examples |
| `web/frontend/src/views/examples/README.md` | none | documentation sidecar | markdown/doc reference only | `sidecar-exclude` | Move or update with examples lifecycle, not as a Vue page |

### Freqtrade Parent And Tabs

| File | Route/menu | Direct importer | Guard/test | Lifecycle | Successor or next decision |
| --- | --- | --- | --- | --- | --- |
| `web/frontend/src/views/FreqtradeDemo.vue` | none | none found as route/menu; imports all Freq tabs | package file-level/history and demo style references | `retain-as-demo` / parent decision | Decide parent and child tabs together; likely retain as external bot demo docs or archive with `no-successor-needed` |
| `web/frontend/src/views/freqtrade-demo/FreqOverviewTab.vue` | none | imported by `FreqtradeDemo.vue` | `freqtrade-demo-mainline-gate.spec.ts` | `retain-as-demo` | Parent decision required |
| `web/frontend/src/views/freqtrade-demo/FreqStrategyTab.vue` | none | imported by `FreqtradeDemo.vue` | `freqtrade-demo-mainline-gate.spec.ts` | `retain-as-demo` | Parent decision required |
| `web/frontend/src/views/freqtrade-demo/FreqBacktestTab.vue` | none | imported by `FreqtradeDemo.vue` | `freqtrade-demo-mainline-gate.spec.ts` | `retain-as-demo` | Parent decision required |
| `web/frontend/src/views/freqtrade-demo/FreqConfigTab.vue` | none | imported by `FreqtradeDemo.vue` | `freqtrade-demo-mainline-gate.spec.ts` | `retain-as-demo` | Parent decision required |
| `web/frontend/src/views/freqtrade-demo/FreqWebuiTab.vue` | none | imported by `FreqtradeDemo.vue` | `freqtrade-demo-mainline-gate.spec.ts` | `retain-as-demo` | Parent decision required |
| `web/frontend/src/views/freqtrade-demo/FreqStatusTab.vue` | none | imported by `FreqtradeDemo.vue` | `freqtrade-demo-mainline-gate.spec.ts` | `retain-as-demo` | Parent decision required |

### Tdxpy Parent And Tabs

| File | Route/menu | Direct importer | Guard/test | Lifecycle | Successor or next decision |
| --- | --- | --- | --- | --- | --- |
| `web/frontend/src/views/TdxpyDemo.vue` | none | none found as route/menu; imports all Tdx tabs | package file-level/history and demo style references | `retain-as-demo` / parent decision | Decide parent and child tabs together; likely retain as integration docs or archive with `no-successor-needed` |
| `web/frontend/src/views/tdxpy-demo/TdxOverviewTab.vue` | none | imported by `TdxpyDemo.vue` | `tdxpy-demo-mainline-gate.spec.ts` | `retain-as-demo` | Parent decision required |
| `web/frontend/src/views/tdxpy-demo/TdxInstallTab.vue` | none | imported by `TdxpyDemo.vue` | `tdxpy-demo-mainline-gate.spec.ts` | `retain-as-demo` | Parent decision required |
| `web/frontend/src/views/tdxpy-demo/TdxApiTab.vue` | none | imported by `TdxpyDemo.vue` | `tdxpy-demo-mainline-gate.spec.ts` | `retain-as-demo` | Parent decision required |
| `web/frontend/src/views/tdxpy-demo/TdxExportTab.vue` | none | imported by `TdxpyDemo.vue` | `tdxpy-demo-mainline-gate.spec.ts` | `retain-as-demo` | Parent decision required |
| `web/frontend/src/views/tdxpy-demo/TdxStatusTab.vue` | none | imported by `TdxpyDemo.vue` | `tdxpy-demo-mainline-gate.spec.ts` | `retain-as-demo` | Parent decision required |

### Root Demo/Test/Sandbox Pages

| File | Route/menu | Direct importer | Guard/test | Lifecycle | Successor or next decision |
| --- | --- | --- | --- | --- | --- |
| `web/frontend/src/views/ArtDecoTest.vue` | none | none found | package file-level target; guard-map referenced | `archive-candidate` after guard retirement | Likely `no-successor-needed` if retained only as visual sandbox |
| `web/frontend/src/views/DataVisualizationShowcase.vue` | none | none found | package file-level target; `root-demo-style-entrypoints.spec.ts`; console cleanup guard | `absorb-assets` | Review chart/showcase ideas before any archive |
| `web/frontend/src/views/KLineDemo.vue` | none | none found | guard-map referenced | `absorb-assets` | Candidate successor: canonical market/technical K-line pages |
| `web/frontend/src/views/MarketDataDemo.vue` | none | none found | guard-map referenced | `absorb-assets` | Candidate successor: canonical market/data API demo or docs |
| `web/frontend/src/views/MinimalTest.vue` | none | none found | guard-map referenced; contains console-load test intent | `archive-candidate` after guard retirement | Likely `no-successor-needed` if only runtime smoke sandbox |
| `web/frontend/src/views/PyprofilingDemo.vue` | none | imports `views/composables/usePyprofilingDemo.ts` and `views/styles/PyprofilingDemo.css` | package file-level target; root demo style entrypoint | `retain-as-demo` / absorb-assets | Keep with profiling support assets until AI/strategy successor decision |
| `web/frontend/src/views/SkeletonUsage.vue` | none | none found | package file-level target; workflow and tokenization guards | `retain-as-demo` | Retain until skeleton usage docs/guard ownership is replaced |
| `web/frontend/src/views/SmartDataSourceTest.vue` | none | none found | package file-level target; `root-demo-style-entrypoints.spec.ts` | `absorb-assets` | Candidate successor: canonical data/source diagnostics if feature remains valuable |
| `web/frontend/src/views/StockAnalysisDemo.vue` | none | directly tested by `views/__tests__/StockAnalysisDemo.spec.ts` | package file-level target; root demo style entrypoint; legacy shell spec | `retain-as-demo` / absorb-assets | Keep until stock-analysis demo value is absorbed or test retired |
| `web/frontend/src/views/Test.vue` | none | none found | guard-map referenced | `archive-candidate` after guard retirement | Likely `no-successor-needed` if only sandbox shell |

## Archive Blocking Conditions

- OpenStock has two active source shells pointing to the same demo child tree; this must be resolved before any child component move.
- Freqtrade and Tdxpy child tabs are directly imported by root parent shells; parent and tabs must be decided together.
- Directory-level and file-level token gates still cover these assets through `lint:artdeco:changed`.
- Several direct style-source and workflow specs read the exact source files, so archive moves require same-batch guard retirement or migration.
- OpenStock, K-line, stock search, watchlist, market data, smart data source, and stock-analysis assets may contain reusable product ideas; they cannot be marked redundant until successor coverage or `no-successor-needed` rationale is recorded.

## Recommended Next Batch

```text
A4-openstock-demo-decision
```

Recommended scope:

- Compare `views/OpenStockDemo.vue` and `views/demo/OpenStockDemo.vue`.
- Decide whether OpenStock remains a retained demo, becomes an absorption plan for canonical market/watchlist/data pages, or becomes archive-prep.
- Do not archive OpenStock children independently from the selected shell.
- If archive-prep is selected, list every direct OpenStock style-source spec and package guard that must be retired in the same mutation batch.

## Governance Conclusion

The A4 inventory confirms the selected assets are outside current `MenuConfig.ts` and `router/index.ts` active truth, but they are not disposable by static non-routing evidence alone. The safe next step is a narrow OpenStock shell decision, not a bulk demo archive.

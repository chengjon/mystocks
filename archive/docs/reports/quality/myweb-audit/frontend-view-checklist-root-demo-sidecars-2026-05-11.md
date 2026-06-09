# Frontend View Checklist: Root Demo And Sidecar Assets

Date: 2026-05-11

Scope:
- `web/frontend/src/views/{ArtDecoTest,DataVisualizationShowcase,FreqtradeDemo,KLineDemo,MarketDataDemo,MinimalTest,OpenStockDemo,PageTitleDemo,PyprofilingDemo,SkeletonUsage,SmartDataSourceTest,StockAnalysisDemo,TdxpyDemo,Test}.vue`
- `web/frontend/src/views/TradingDashboard.vue`
- `web/frontend/src/views/__tests__/*`
- `web/frontend/src/views/.claude/*`
- `web/frontend/src/views/TASK.md`

This checklist closes the non-ArtDeco `views/` coverage gap left after the domain, root legacy, blank-layout, demo-directory, `views/composables`, and `views/styles` batches. It records read-only lifecycle evidence only. It does not approve archive movement, deletion, or Vue refactoring.

## Inventory Reconciliation

Current filesystem snapshot:

| Scope | Files | Notes |
| --- | ---: | --- |
| Non-ArtDeco `views/**` total | 380 | Excludes `views/artdeco-pages/**`, which is covered by the ArtDeco rollup. |
| Non-ArtDeco Vue pages/components | 183 | Business domains, top-level wrappers, demo shells, error shells, and test/demo assets. |
| Non-ArtDeco non-Vue support assets | 197 | Tests, composables, styles, data helpers, docs, configs, and sidecar files. |

Existing checklist coverage already handles:

- Business domains: `advanced-analysis`, `ai`, `announcement`, `data`, `market`, `monitoring`, `risk`, `settings`, `stocks`, `strategy`, `system`, `technical`, `trade`, `trade-management`, `trading`, `trading-decision`, `watchlist`.
- Special and support scopes: blank-layout/error pages, `examples`, `freqtrade-demo`, `tdxpy-demo`, `demo`, `views/components`, `views/composables`, and `views/styles`.
- Root legacy business wrappers/static shells: `frontend-view-checklist-top-level-legacy-2026-05-10.md`.

This leaves three expanded focus groups: root demo/test/sandbox Vue files, the active `/trade/terminal` top-level route owner, and root sidecar/test guard files.

## Truth Inputs

Router and menu truth:

- `web/frontend/src/router/index.ts` currently imports `TradingDashboard.vue` for `/trade/terminal`.
- Static search found no current router/menu import for the root demo/test/sandbox pages listed in this checklist.
- `Login.vue` and `NotFound.vue` are intentionally excluded here because they are already covered by the blank-layout checklist.

Guard and historical evidence:

- `frontend-view-governance-inventory-2026-05-10.md` classifies `ArtDecoTest.vue`, `DataVisualizationShowcase.vue`, `FreqtradeDemo.vue`, `KLineDemo.vue`, `MarketDataDemo.vue`, `MinimalTest.vue`, `OpenStockDemo.vue`, `PageTitleDemo.vue`, `SkeletonUsage.vue`, `SmartDataSourceTest.vue`, `StockAnalysisDemo.vue`, `TdxpyDemo.vue`, and `Test.vue` as top-level demo/deprecated inventory.
- `frontend-view-guard-map-2026-05-10.json` still contains references to these root demo/test/sandbox pages, so they are not archive-approved by inventory classification alone.
- `web/frontend/tests/unit/config/root-demo-style-entrypoints.spec.ts` directly guards `DataVisualizationShowcase.vue`, `SmartDataSourceTest.vue`, and `StockAnalysisDemo.vue`.
- `web/frontend/tests/unit/config/skeleton-usage-tokenization.spec.ts` and workflow guard tests directly reference `SkeletonUsage.vue`.
- `web/frontend/tests/unit/config/console-log-cleanup-batch-24.spec.ts` directly reads `DataVisualizationShowcase.vue`.
- `web/frontend/src/views/__tests__/StockAnalysisDemo.spec.ts` directly guards the root `StockAnalysisDemo.vue` static-shell truth.
- Root `FreqtradeDemo.vue` and `TdxpyDemo.vue` still own the child tab directories covered by `frontend-view-checklist-demo-examples-2026-05-10.md`.
- Root `PyprofilingDemo.vue` still owns `views/composables/usePyprofilingDemo.ts` and `views/styles/PyprofilingDemo.css` per the composables/styles checklist.

## Page Classification

| Page | Current classification | Route status | Asset/guard status | Decision |
| --- | --- | --- | --- | --- |
| `TradingDashboard.vue` | `special-route-active` | `/trade/terminal` | Owns active terminal UI; paired with `views/composables/useTradingDashboard.ts` and `views/styles/TradingDashboard.css` | Exclude from archive flow |
| `DataVisualizationShowcase.vue` | `candidate-review/demo-sandbox` | no active route | Direct style import plus cleanup/style guards | Not archive-approved |
| `SmartDataSourceTest.vue` | `candidate-review/demo-sandbox` | no active route | Direct style import plus root-demo style guard | Not archive-approved |
| `SkeletonUsage.vue` | `candidate-review/demo-sandbox` | no active route | Direct tokenization/workflow guards; package-script target-file evidence | Not archive-approved |
| `StockAnalysisDemo.vue` | `candidate-review/legacy-static-shell` | no active route | Historical secondary-batch-44 static-shell repair plus direct spec/style guards | Not archive-approved |
| `FreqtradeDemo.vue` | `candidate-review/demo-parent-shell` | no active route | Owns `views/freqtrade-demo/*` child tabs | Not archive-approved; child tabs must move with parent decision |
| `TdxpyDemo.vue` | `candidate-review/demo-parent-shell` | no active route | Owns `views/tdxpy-demo/*` child tabs | Not archive-approved; child tabs must move with parent decision |
| `PyprofilingDemo.vue` | `candidate-review/demo-research-shell` | no active route | Owns root composable/style support; partially overlaps `views/demo/pyprofiling/*` concepts | Not archive-approved |
| `ArtDecoTest.vue` | `candidate-review/demo-sandbox` | no active route | Inventory/guard-map referenced demo page | Not archive-approved |
| `KLineDemo.vue` | `candidate-review/demo-sandbox` | no active route | Inventory/guard-map referenced demo page; K-line concepts overlap market/technical canonical routes | Not archive-approved |
| `MarketDataDemo.vue` | `candidate-review/demo-sandbox` | no active route | Contains selector/API-demo/fallback-literal risk; successor likely `market`/`data` domains | Not archive-approved |
| `MinimalTest.vue` | `candidate-review/test-sandbox` | no active route | Inventory/guard-map referenced test page | Not archive-approved |
| `OpenStockDemo.vue` | `candidate-review/demo-sandbox` | no active route | Root demo page distinct from `views/demo/OpenStockDemo.vue`; inventory/guard-map referenced | Not archive-approved |
| `PageTitleDemo.vue` | `candidate-review/demo-sandbox` | no active route | Page-title/shared-composable demo; inventory/guard-map referenced | Not archive-approved |
| `Test.vue` | `candidate-review/test-sandbox` | no active route | Inventory/guard-map referenced test page | Not archive-approved |

## Sidecar And Guard Assets

| Asset group | Current classification | Reason | Decision |
| --- | --- | --- | --- |
| `views/__tests__/*` | `guard-asset/root-view-lifecycle` | Directly guards root wrappers, static shells, active route owners, and demo/test pages | Move/retire only with owning page decisions |
| `views/.claude/*` | `sidecar-agent-state` | Agent/task recorder state, not a Vue runtime page | Exclude from page archive decisions; handle under tooling hygiene only |
| `views/TASK.md` | `sidecar-task-note` | Worktree/task note, not a Vue runtime page | Exclude from page archive decisions; handle under documentation/tooling hygiene only |

## Archive Eligibility

Current eligibility: no file in this checklist is `archive-approved`.

Blocking conditions:

- `TradingDashboard.vue` is active route truth for `/trade/terminal`.
- Several demo/test/sandbox pages still have direct test, style, workflow, guard-map, or inventory references.
- Root demo parent shells own child tab/support assets; child directories cannot be archived independently from parent decisions.
- Some root demo pages contain potentially reusable concepts for `market`, `data`, `technical`, `strategy`, `system`, or demo documentation, but successor/no-successor proof has not been recorded per file.
- Root sidecar files are not page assets and must not be mixed into archive-candidate counts.

Required before any mutation batch:

- Split root demo/test/sandbox pages into `retain-as-demo`, `absorb-assets`, or `archive-candidate` with one explicit successor or `no-successor-needed` rationale per file.
- For parent shells such as `FreqtradeDemo.vue`, `TdxpyDemo.vue`, and `PyprofilingDemo.vue`, decide the parent and child support directories together.
- Retire or migrate direct specs, style-source specs, workflow guards, and guard-map references in the same approved mutation batch.
- Keep `TradingDashboard.vue`, `useTradingDashboard.ts`, `tradingDashboardActions.ts`, and `TradingDashboard.css` together unless a trade-terminal-specific extraction is separately approved and verified.

## Governance Conclusion

The remaining non-ArtDeco `views/` coverage gap is not a business-route gap. It is a mix of root demo/test/sandbox pages, one active special route owner, and non-page sidecars. The correct next action is not archive movement; it is root demo/test lifecycle triage plus explicit guard retirement planning. This closes `2b.97` as read-only evidence and leaves mutation work gated behind section 3 approval.

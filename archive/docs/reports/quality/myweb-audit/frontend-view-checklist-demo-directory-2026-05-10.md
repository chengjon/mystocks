# Frontend View Checklist: Demo Directory Batch

Date: 2026-05-10

Scope:
- `web/frontend/src/views/demo/*`
- `web/frontend/src/views/demo/openstock/*`
- `web/frontend/src/views/demo/pyprofiling/*`
- `web/frontend/src/views/demo/stock-analysis/*`
- `web/frontend/src/views/demo/styles/*`

This checklist records lifecycle evidence for the current `views/demo` directory. It does not approve any archive move or deletion.

## Summary

| Group | Files Reviewed | Route/Menu Status | Internal Owner | Guard Status | Lifecycle Result |
| --- | ---: | --- | --- | --- | --- |
| Demo shells | 5 Vue shells | Not in current router or menu | Demo-only shell pages | `demo-mainline-gate`, shell/style specs | `candidate-review/demo-shell-asset` |
| OpenStock demo | 7 components + config/export | Not in current router or menu | `OpenStockDemo.vue` | OpenStock style specs and directory gate | `candidate-review/demo-functional-asset` |
| Pyprofiling demo | 7 components + config/export | Not in current router or menu | `PyprofilingDemo.vue` | Pyprofiling style specs and directory gate | `candidate-review/demo-research-asset` |
| Stock analysis demo | 6 components + config/code examples/export | Not in current router or menu | `StockAnalysisDemo.vue` | Stock-analysis style specs and directory gate | `candidate-review/demo-research-asset` |
| Demo styles | 4 SCSS files | Not route-owned | Historical demo style support | Demo style-source specs | `candidate-review/demo-support-asset` |

No file in this batch is `archive-approved`.

## Evidence

### Directory Intent

`web/frontend/src/views/demo/README.md` explicitly describes this directory as demonstration, experimental, and research pages outside the main production application. It also states that demo pages require extraction, API standardization, error/loading states, relocation to a production directory, and E2E tests before conversion to production.

### Menu And Router

- `web/frontend/src/router/index.ts` has no active route import for `web/frontend/src/views/demo/*`.
- `web/frontend/src/layouts/MenuConfig.ts` has no active menu owner for `views/demo/*`.
- Historical docs mention old demo paths, but those historical references are not current router truth.

### Internal Ownership

- `OpenStockDemo.vue` owns `openstock/config.ts` and `openstock/components/*` through local imports.
- `PyprofilingDemo.vue` owns `pyprofiling/config.ts` and asynchronously imports `pyprofiling/components/*`.
- `StockAnalysisDemo.vue` owns `stock-analysis/config.ts`, `stock-analysis/code-examples*`, and asynchronously imports `stock-analysis/components/*`.
- `Phase4Dashboard.vue` owns `composables/usePhase4Dashboard.ts`, which calls `dashboardService` and `@/utils/echarts`.
- `Wencai.vue` imports `@/components/market/WencaiPanel.vue` and calls `/api/market/wencai/queries`; it is demo-only, but not isolated from shared market components.

### Guard And Test References

- `web/frontend/package.json` includes `--target-dir src/views/demo --changed-from-git` in `lint:artdeco:changed`.
- `demo-mainline-gate.spec.ts`, `openstock-components-mainline-gate.spec.ts`, `pyprofiling-mainline-gate.spec.ts`, `pyprofiling-components-mainline-gate.spec.ts`, `stock-analysis-components-mainline-gate.spec.ts`, and `demo-styles-mainline-gate.spec.ts` intentionally keep this directory under one directory-level gate.
- Multiple style-source specs directly guard demo shells, OpenStock components, Pyprofiling components, StockAnalysis components, and demo SCSS files.
- `root-demo-style-entrypoints.spec.ts` also references `src/views/demo/Phase4Dashboard.vue` and `src/views/demo/pyprofiling/components/Prediction.vue`.

## Asset Classification

| Asset Group | Files | Current Result | Absorption / Successor Hint |
| --- | --- | --- | --- |
| OpenStock shell and components | `OpenStockDemo.vue`, `openstock/*` | `candidate-review/demo-functional-asset` | Extract reusable stock search/quote/news/watchlist/K-line/heatmap ideas only through canonical market/watchlist/data pages; do not promote the demo shell directly |
| Phase4 dashboard demo | `Phase4Dashboard.vue`, `composables/usePhase4Dashboard.ts`, `styles/Phase4Dashboard.scss` | `candidate-review/demo-legacy-dashboard-asset` | Compare with current `/dashboard`, market, watchlist, portfolio, and risk canonical pages before any retirement |
| Pyprofiling demo | `PyprofilingDemo.vue`, `pyprofiling/*` | `candidate-review/demo-research-asset` | Treat ML/profiling concepts as documentation or future AI/strategy asset candidates, not active route truth |
| Stock analysis demo | `StockAnalysisDemo.vue`, `stock-analysis/*` | `candidate-review/demo-research-asset` | Review parsing/backtest/realtime snippets before any archive; some may inform strategy/data docs |
| Wencai demo | `Wencai.vue`, `styles/Wencai.scss` | `candidate-review/demo-functional-asset` | Current shared successor candidate is `@/components/market/WencaiPanel.vue`; do not archive until Wencai feature ownership is confirmed |
| Demo support docs/styles | `README.md`, `docs/web-dev/GUIDE.md`, `styles/*` | `candidate-review/demo-support-asset` | Keep coupled to demo lifecycle; retire only with their owning demo shells |

## Redundancy And Archive Eligibility

Current eligibility: not approved.

Blocking conditions:
- Directory-level guards and many style-source specs still directly reference this tree.
- Several demo assets still call real API endpoints or import shared application components/services.
- Demo shells own child component trees; child files cannot be judged independently from their shell.
- Some assets have plausible absorption value for canonical market, watchlist, strategy, data, AI/profiling, and Wencai functionality.
- The current governance task has not approved a mutation batch for demo relocation, guard retirement, or archive movement.

Required before any archive move:
- Split `views/demo` into reviewed sub-batches with one lifecycle decision per demo shell.
- For each shell, decide `absorb`, `retain-as-demo`, or `archive-candidate` with a successor or `no-successor-needed` rationale.
- Retire or migrate all relevant style-source specs and the `src/views/demo` directory-level gate in the same mutation batch.
- Verify no remaining docs, package scripts, tests, or dynamic imports refer to the moved path.

## Governance Conclusion

`views/demo` is outside the current canonical menu/router tree and is correctly classified as demo/research inventory. However, it is not cleanly disposable. It remains `candidate-review/demo-*` because it has active guard coverage, internal shell/component ownership, shared component/service references, and possible reusable business assets.

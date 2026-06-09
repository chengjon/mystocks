# Frontend View Governance A4 OpenStock Demo Decision

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: approval package for `A4-openstock-demo-decision`.

This package does not move files, edit runtime code, update routes, or retire tests.

## Decision Needed

OpenStock currently has two source shells for the same demo component family:

- `web/frontend/src/views/OpenStockDemo.vue`
- `web/frontend/src/views/demo/OpenStockDemo.vue`

Both are outside current `MenuConfig.ts` and `router/index.ts` active truth. Both import the same OpenStock component family under `web/frontend/src/views/demo/openstock/*`.

## Evidence Summary

| Evidence | Result |
| --- | --- |
| Router/menu owner | No active router or menu owner for either OpenStock shell |
| Shared child tree | Both shells render `StockSearch`, `StockQuote`, `StockNews`, `WatchlistManagement`, `KlineChart`, `HeatmapChart`, and `FeatureStatus` |
| Guard ownership | Active style-source guard directly reads `src/views/demo/OpenStockDemo.vue`; OpenStock child specs read `src/views/demo/openstock/components/*.vue` |
| Package gate | `lint:artdeco:changed` covers the whole `src/views/demo` directory |
| Root shell guard | Root `src/views/OpenStockDemo.vue` is referenced by historical guard-map/inventory, but no current direct style-source spec was found for it |
| UI maturity | `views/demo/OpenStockDemo.vue` has the newer ArtDeco-tokenized shell; root `views/OpenStockDemo.vue` still uses older token names and Element Plus shell controls |
| Runtime risk | OpenStock children call live-looking `/api` endpoints and use local token access; this is demo/runtime-adjacent code, not static documentation only |

## Proposed Decision Profile

```text
A4-openstock-demo-root-duplicate-archive-prep
```

Recommended approval:

- Treat `web/frontend/src/views/demo/OpenStockDemo.vue` as the temporary retained demo owner.
- Treat `web/frontend/src/views/OpenStockDemo.vue` as a root-level duplicate shell eligible for archive-prep only after one final hidden-reference check.
- Do not archive `web/frontend/src/views/demo/openstock/*` in this batch.
- Do not promote OpenStock child components into canonical business routes in this batch.
- Keep all OpenStock style-source specs intact unless a later approved mutation removes or relocates their exact source targets.

## Why This Profile

The root OpenStock shell is redundant as a page shell because it has no route/menu owner and delegates to the same demo child tree as the demo-directory shell. The demo-directory shell is the safer temporary owner because the existing guard suite already targets it and its styles are closer to the current ArtDeco token model.

The child components are not redundant yet. They contain reusable product ideas for stock search, quote lookup, news lookup, watchlist operations, K-line display, and heatmap display. Some of those overlap canonical market/watchlist/data pages, but no per-feature successor proof has been recorded in this decision package.

## Archive-Prep Candidate

| Candidate | Proposed lifecycle | Successor / rationale | Required same-batch guard action |
| --- | --- | --- | --- |
| `web/frontend/src/views/OpenStockDemo.vue` | `archive-candidate/root-duplicate-shell` | Successor: `web/frontend/src/views/demo/OpenStockDemo.vue` as retained demo owner | Final active-reference sweep; no direct guard retirement expected unless current guard-map-derived tests are found |

## Retained Assets

| Asset | Proposed lifecycle | Reason |
| --- | --- | --- |
| `web/frontend/src/views/demo/OpenStockDemo.vue` | `retain-as-demo` | Better aligned with demo directory ownership and direct style-source guard |
| `web/frontend/src/views/demo/openstock/config.ts` | `retain-as-demo-support` | Shared tab/API-status config for retained shell |
| `web/frontend/src/views/demo/openstock/components/index.ts` | `retain-as-demo-support` | Barrel export for retained child tree |
| `web/frontend/src/views/demo/openstock/components/StockSearch.vue` | `absorb-assets-later` | Candidate source for canonical stock search/watchlist add-stock patterns |
| `web/frontend/src/views/demo/openstock/components/StockQuote.vue` | `absorb-assets-later` | Candidate source for canonical quote/detail route ideas |
| `web/frontend/src/views/demo/openstock/components/StockNews.vue` | `absorb-assets-later` | Candidate source for canonical stock news/detail route ideas |
| `web/frontend/src/views/demo/openstock/components/WatchlistManagement.vue` | `absorb-assets-later` | Must be compared against canonical `/watchlist/manage`; distinct from archived monitoring Watchlist page |
| `web/frontend/src/views/demo/openstock/components/KlineChart.vue` | `absorb-assets-later` | Candidate source for canonical market/technical K-line ideas |
| `web/frontend/src/views/demo/openstock/components/HeatmapChart.vue` | `absorb-assets-later` | Candidate source for canonical market heatmap ideas; contains `Math.random` fallback/demo data risk |
| `web/frontend/src/views/demo/openstock/components/FeatureStatus.vue` | `retain-as-demo-support` | Demo-only API-status display; no canonical successor required yet |

## Non-Absorption Rules

- Do not copy OpenStock API endpoint strings into canonical routes as new truth.
- Do not import OpenStock child components directly from canonical market/watchlist/data pages without a separate TDD-backed absorption batch.
- Do not treat the OpenStock watchlist component as a replacement for canonical `/watchlist/manage`; canonical watchlist already has verified snapshot/stale-state semantics.
- Do not keep both OpenStock shells long-term after root duplicate archive-prep is approved and executed.

## Execution Plan If Approved

1. Run a final hidden-reference sweep for exact `views/OpenStockDemo.vue` references across `web/frontend/src`, `web/frontend/tests`, `web/frontend/package.json`, and current OpenSpec/docs governance artifacts.
2. If active runtime/test references are still clear, move only `web/frontend/src/views/OpenStockDemo.vue` into the governed archive.
3. Leave `web/frontend/src/views/demo/OpenStockDemo.vue` and `web/frontend/src/views/demo/openstock/**` in place.
4. Run targeted checks:
   - `openspec validate update-frontend-view-governance --strict`
   - `python scripts/compliance/markdown_governance_gate.py --root-dir /opt/claude/mystocks_spec --format text --path openspec/changes/update-frontend-view-governance/tasks.md docs/reports/quality/myweb-audit/<new-doc>.md`
   - `git diff --check -- <changed paths>`
   - `gitnexus_detect_changes(scope="staged")`

## Alternatives Rejected For Now

| Alternative | Reason not selected |
| --- | --- |
| Archive both OpenStock shells and child tree | Too broad; child components still have guard coverage and possible absorption value |
| Promote OpenStock into router/menu | Outside current menu truth and not requested; live-looking demo APIs need product validation first |
| Absorb all child components immediately into canonical pages | Too large and likely to duplicate existing canonical data/watchlist semantics |
| Keep both shells indefinitely | Preserves root-level duplicate page debt and conflicts with single-truth cleanup goals |

## Approval Question

Approve `A4-openstock-demo-root-duplicate-archive-prep` as the next mutation-prep direction?

If approved, the next batch should prepare the exact archive runbook for only `web/frontend/src/views/OpenStockDemo.vue`; it should not move the child OpenStock component tree.

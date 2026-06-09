# Frontend View Checklist: `views/artdeco-pages/portfolio-tabs/*`

> Date: 2026-05-10
> Scope: `web/frontend/src/views/artdeco-pages/portfolio-tabs/*`
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence batch, no file moves, no runtime code changes.

## Scope Inventory

| Path | Type | Route/Menu Owner | Runtime Import | Guard/Test Evidence | Classification | Archive Status |
| --- | --- | --- | --- | --- | --- | --- |
| `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` | Vue wrapper page | `/risk/pnl`, route name `risk-pnl` | dynamic import in `router/index.ts` | risk/trade checklist docs, E2E references, wrapper-retention references | `canonical-active/risk-pnl-wrapper` | `not-archive-approved` |
| `web/frontend/src/views/artdeco-pages/portfolio-tabs/portfolioOverviewData.ts` | data mapper/helper | n/a | imported by `web/frontend/src/views/trade/Portfolio.vue` | `portfolioOverviewData.spec.ts`, trade portfolio tests | `active-canonical-helper` | `not-archive-approved` |
| `web/frontend/src/views/artdeco-pages/portfolio-tabs/__tests__/portfolioOverviewData.spec.ts` | helper regression test | n/a | tests `portfolioOverviewData.ts` directly | live positions payload mapping and rebalance-policy truth | `active-helper-test` | `not-archive-approved` |

## Route And Menu Truth

- `router/index.ts` routes `/risk/pnl` to `@/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`.
- `PortfolioOverviewTab.vue` is currently a thin wrapper over `@/views/trade/Portfolio.vue`.
- `web/frontend/src/views/trade/Portfolio.vue` is the canonical trade portfolio implementation and imports `portfolioOverviewData.ts`.
- Existing trade/risk checklist docs already state that `/risk/pnl` inherits `trade/Portfolio.vue` truth through this wrapper.

## Hidden Reference And Guard Evidence

- `web/frontend/src/views/trade/Portfolio.vue` imports `portfolioOverviewData.ts` for positions payload extraction and portfolio overview derivation.
- `web/frontend/src/views/artdeco-pages/portfolio-tabs/__tests__/portfolioOverviewData.spec.ts` guards mapper behavior for direct payloads, nested payloads, invalid payloads, and missing target-weight policy.
- `web/frontend/tests/e2e/risk-pnl.spec.ts` references the risk PnL route behavior.
- `web/frontend/tests/unit/views/trade-wrapper-retention.spec.ts` references the legacy path `src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`.
- Existing myweb-audit trade/risk reports identify this file family as part of the verified trade portfolio and risk PnL truth chain.

## Functional Asset Assessment

- `PortfolioOverviewTab.vue` is not a standalone business truth owner. It is a route wrapper that keeps `/risk/pnl` attached to the canonical trade portfolio surface.
- `portfolioOverviewData.ts` is still an active helper used by the canonical trade portfolio page, not a stale leftover.
- The helper encodes payload-shape tolerance for `/v1/trade/positions`: direct `positions[]`, nested `data.positions[]`, numeric parsing, derived totals, and rebalance policy readiness.
- The helper test remains valuable because it protects portfolio PnL and rebalance policy semantics shared by trade and risk routes.

## Redundant Page Decision

No file in this batch is archive-approved.

- `PortfolioOverviewTab.vue` is an active `/risk/pnl` route wrapper and must not be archived while router truth still points to it.
- `portfolioOverviewData.ts` is imported by canonical `views/trade/Portfolio.vue`; archiving it would break active portfolio logic.
- `portfolioOverviewData.spec.ts` is active helper coverage and must move only if the helper itself is deliberately relocated.

## Follow-Up Notes

- If the project later wants to eliminate `artdeco-pages/portfolio-tabs`, first move `/risk/pnl` to an approved canonical wrapper under `views/risk/` and relocate `portfolioOverviewData.ts` beside the true owner or into an approved shared data-mapper layer.
- Do not classify `PortfolioOverviewTab.vue` as redundant just because the implementation is a thin wrapper; the wrapper is currently route truth.
- Any future mutation in this family should verify both `/trade/portfolio` and `/risk/pnl` because they share the same portfolio data truth.

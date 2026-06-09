# Frontend View Governance 2.4 Compatibility Retention Disposition

Date: 2026-05-12
Change: `update-frontend-view-governance`
Task: `2.4 Mark pages requiring compatibility retention.`

## Decision

Close task 2.4 as a read-only compatibility-retention ledger. Existing checklists identify the pages and support assets that must remain because they still preserve route truth, legacy wrapper chains, active canonical targets, historical entrypoints, or guard expectations.

No compatibility layer is retired in this batch.

## Retention Classes

| Retention class | Examples from evidence | Required disposition |
| --- | --- | --- |
| Active route truth | `/dashboard` via `ArtDecoDashboard.vue`, `/risk/pnl` via `PortfolioOverviewTab.vue`, `/trade/terminal` via `TradingDashboard.vue`, `/login`, 404, and `/detail/news/:symbol`. | Exclude from archive flow while router truth points to these files. |
| Canonical route wrappers | Strategy route wrappers such as `views/strategy/List.vue`, `Parameters.vue`, `Backtest.vue`, and `Optimization.vue`. | Retain as current route entrypoints even when implementation delegates to canonical bodies. |
| Legacy compatibility wrappers | Market/data/risk/trade/system ArtDeco wrappers, `views/market/CapitalFlow.vue`, `views/market/Concepts.vue`, `views/strategy/StrategyList.vue`, trading/trading-decision thin wrappers. | Retain until compatibility consumers, wrapper-retention tests, function-tree references, and successor mappings are retired together. |
| Canonical targets referenced by wrappers | Data, market, system, risk, and trade canonical pages that are imported by compatibility wrappers. | Retain as canonical owners; wrapper references are additional retention evidence, not archive evidence. |
| Compatibility support assets | Wrapper-local composables, styles, helper mappers, and data normalizers tied to retained wrappers. | Govern with the owning wrapper or canonical route owner; do not archive independently. |
| Guarded legacy/static shells | Settings, monitoring, advanced-analysis, technical, root legacy, demo, and trade-management shells with specs or mainline guards. | Not product-route truth, but still compatibility or historical-contract assets until guards and successor/no-successor decisions are explicit. |

## Evidence Inputs

- `docs/reports/quality/myweb-audit/frontend-view-governance-2b-readonly-closeout-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-artdeco-coverage-rollup-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-artdeco-root-pages-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-artdeco-market-data-tabs-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-artdeco-risk-tabs-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-market-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-strategy-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-trading-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-trading-decision-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-stocks-2026-05-10.md`

## Boundary

- This record marks retention categories only; it does not approve wrapper retirement.
- This record does not remove any compatibility import, alias, test, route, package target, style entrypoint, or documentation reference.
- Retained compatibility does not mean the file is canonical business truth; it means the file is blocked from archive until the compatibility contract is explicitly closed.
- Candidate-review pages outside these retention classes still require their own hidden-reference, reusable-asset, successor, and redundant-page eligibility checks before any archive-candidate status.

# Frontend View Checklist: ArtDeco Coverage Rollup

> Date: 2026-05-11
> Scope: coverage rollup for `web/frontend/src/views/artdeco-pages/**`
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence rollup, no file moves, no runtime code changes.

## Coverage Summary

Current filesystem count: 186 files under `web/frontend/src/views/artdeco-pages/**`.

| Top-Level Group | File Count | Checklist Coverage | Rollup Result |
| --- | ---: | --- | --- |
| root files | 12 | root pages, backups | covered |
| `__tests__` | 1 | local tests | covered |
| `_templates` | 8 | templates, local tests | covered |
| `analysis-tabs` | 3 | analysis-tabs, local tests | covered |
| `components` | 24 | components, coverage delta | covered |
| `composables` | 5 | composables, dashboard-fetchers | covered |
| `market-data-tabs` | 22 | market-data-tabs, local tests | covered |
| `market-tabs` | 12 | market-tabs, local tests | covered |
| `portfolio-tabs` | 3 | portfolio-tabs, local tests | covered |
| `risk-tabs` | 19 | risk-tabs, local tests | covered |
| `settings` | 5 | settings | covered |
| `stock-management-tabs` | 6 | stock-management-tabs, local tests | covered |
| `strategy-tabs` | 37 | strategy-tabs, local tests, coverage delta | covered |
| `styles` | 4 | styles | covered |
| `system-tabs` | 12 | system-tabs, local tests | covered |
| `technical-tabs` | 1 | technical-tabs | covered |
| `trading-tabs` | 12 | trading-tabs, local tests | covered |
| empty directories | 0 files | empty-dirs | covered as directory hygiene, not page archive |

## Checklist Index

- `frontend-view-checklist-artdeco-analysis-tabs-2026-05-10.md`
- `frontend-view-checklist-artdeco-backups-2026-05-10.md`
- `frontend-view-checklist-artdeco-components-2026-05-10.md`
- `frontend-view-checklist-artdeco-composables-2026-05-10.md`
- `frontend-view-checklist-artdeco-coverage-delta-2026-05-10.md`
- `frontend-view-checklist-artdeco-dashboard-fetchers-2026-05-10.md`
- `frontend-view-checklist-artdeco-empty-dirs-2026-05-10.md`
- `frontend-view-checklist-artdeco-local-tests-2026-05-10.md`
- `frontend-view-checklist-artdeco-market-data-tabs-2026-05-10.md`
- `frontend-view-checklist-artdeco-market-tabs-2026-05-10.md`
- `frontend-view-checklist-artdeco-portfolio-tabs-2026-05-10.md`
- `frontend-view-checklist-artdeco-risk-tabs-2026-05-10.md`
- `frontend-view-checklist-artdeco-root-pages-2026-05-10.md`
- `frontend-view-checklist-artdeco-settings-2026-05-10.md`
- `frontend-view-checklist-artdeco-stock-management-tabs-2026-05-10.md`
- `frontend-view-checklist-artdeco-strategy-tabs-2026-05-10.md`
- `frontend-view-checklist-artdeco-styles-2026-05-10.md`
- `frontend-view-checklist-artdeco-system-tabs-2026-05-10.md`
- `frontend-view-checklist-artdeco-technical-tabs-2026-05-10.md`
- `frontend-view-checklist-artdeco-templates-2026-05-10.md`
- `frontend-view-checklist-artdeco-trading-tabs-2026-05-10.md`

## Lifecycle Distribution

The covered files fall into these governance classes:

- Active canonical route support: dashboard, data advanced, strategy backtest/repo/optimization, risk center, trade portfolio/signals, system/data/settings, and related helper modules.
- Compatibility-retained wrappers: market/data/risk/trade/system wrappers that still bridge old ArtDeco consumers to canonical domain views.
- Candidate-review legacy assets: inactive static panels, legacy shell parents, historical local-data components, and embedded parent-dependent tabs.
- Temporary backup candidates: `ArtDecoMarketData.vue.backup` and `ArtDecoMarketData.vue.backup.20260130`.
- Guard assets: local Vitest and Node test files under `__tests__` and `__node_tests__`.
- Empty placeholder directories: `market/`, `ml-tabs/`, `risk/`, and `trade/`.

## Archive Decision

No ArtDeco file is archive-approved by this rollup.

- Active support assets are excluded from archive flow.
- Compatibility wrappers require coordinated guard retirement and successor mapping.
- Candidate-review assets require per-file successor or explicit `no-successor-needed` rationale before any mutation.
- Backup files require temp-backup governance and explicit owner decision.
- Test files must follow the production asset lifecycle and should not be removed independently.
- Empty directories contain no page assets; if removed later, treat that as directory hygiene, not page archive.

## Next Phase Gate

The read-only ArtDeco evidence phase is sufficiently covered for mutation planning. Before entering mutation batches, require:

- A user-approved mutation batch scope.
- Exact files to move, absorb, or retire.
- Successor mapping for every candidate asset.
- Guard/test update plan in the same batch.
- Verification commands appropriate to the affected route family.

## Recommended Next Step

Start with a small approved mutation proposal, not bulk archive. The safest first candidates are non-runtime temp backup handling or a single static-shell retirement where tests and successor/no-successor rationale can be updated together.

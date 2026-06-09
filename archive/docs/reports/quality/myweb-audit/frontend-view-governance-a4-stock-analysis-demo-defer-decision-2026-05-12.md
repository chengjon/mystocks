# Frontend View Governance A4 StockAnalysisDemo Defer Decision

> **Scope**: `openspec/changes/update-frontend-view-governance`
> **Decision date**: 2026-05-12

## Decision

Select `A4-stock-analysis-demo-defer`.

Do not execute a `StockAnalysisDemo.vue` archive move in the current repo-local micro-batch.

## Reason

`web/frontend/src/views/StockAnalysisDemo.vue` is not an active routed business page, but it is still a deliberate legacy static-shell guard anchor.

Current guard owners:

- `web/frontend/package.json` includes `--target-file src/views/StockAnalysisDemo.vue` in `lint:artdeco:changed`.
- `web/frontend/src/views/__tests__/StockAnalysisDemo.spec.ts` imports and verifies the static shell directly.
- `web/frontend/tests/unit/config/root-demo-style-entrypoints.spec.ts` tracks `src/views/StockAnalysisDemo.vue` as a root demo style entrypoint.
- `web/frontend/tests/unit/config/stock-analysis-style-normalization.spec.ts` verifies the old tab orchestrator and local style remain retired.

Historical evidence in `docs/reports/quality/myweb-audit/audit-20260426-02/pages/stock-analysis-demo-legacy-static-shell-truth-audit.md` already downgraded this page to an honest static shell after removing the old child tabs and style. Archiving the remaining shell safely requires a separate decision to retire or migrate those static-shell guards.

## Boundary

This decision does not move files, edit runtime code, retire package/test guards, or reintroduce any stock-analysis tab orchestrator behavior.

`StockAnalysisDemo.vue` remains `candidate-review/legacy-static-shell` and `retain-as-static-shell-guard-anchor`.

This decision does not claim global frontend lint is clean.

## Next Valid Step

Prepare a separate approval package if the team wants to retire the static-shell guard. That package must choose a successor or removal path for:

- the direct component spec
- the root demo style-entrypoint guard
- the stock-analysis style-normalization guard
- the package-level ArtDeco target-file guard

Until then, no archive execution is approved for `StockAnalysisDemo.vue`.

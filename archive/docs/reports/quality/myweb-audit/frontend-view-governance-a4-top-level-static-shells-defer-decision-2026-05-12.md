# Frontend View Governance A4 Top-Level Static Shells Defer Decision

> **Scope**: `openspec/changes/update-frontend-view-governance`
> **Decision date**: 2026-05-12

## Decision

Select `A4-top-level-static-shells-defer`.

Do not execute archive moves for these top-level legacy pages in the current repo-local micro-batch:

- `web/frontend/src/views/EnhancedDashboard.vue`
- `web/frontend/src/views/RealTimeMonitor.vue`
- `web/frontend/src/views/StockDetail.vue`
- `web/frontend/src/views/Stocks.vue`
- `web/frontend/src/views/TaskManagement.vue`
- `web/frontend/src/views/TdxMarket.vue`
- `web/frontend/src/views/TechnicalAnalysis.vue`

## Reason

These files are not current active route truth, but they still have deliberate owner specs or historical static-shell evidence. Archiving them safely requires a separate guard-retirement decision, not a documentation-only sweep.

Current direct guard evidence:

- `web/frontend/src/views/__tests__/EnhancedDashboard.spec.ts` verifies the legacy enhanced dashboard delegates to the canonical dashboard owner.
- `web/frontend/src/views/__tests__/RealTimeMonitor.spec.ts` verifies the old realtime monitor remains an honest static shell.
- `web/frontend/src/views/__tests__/StockDetail.spec.ts` verifies the old stock-detail workbench remains an honest static shell.
- `web/frontend/src/views/__tests__/Stocks.spec.ts` verifies the old stocks workbench remains an honest static shell.
- `web/frontend/src/views/__tests__/TaskManagement.spec.ts` verifies the old task-management workbench remains an honest static shell.
- `web/frontend/src/views/__tests__/TdxMarket.spec.ts` verifies the old TDX market workbench remains an honest static shell.
- `web/frontend/src/views/__tests__/TechnicalAnalysis.spec.ts` verifies the old top-level technical-analysis workbench remains an honest static shell.

Historical evidence:

- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/enhanced-dashboard-legacy-canonical-wrapper-truth-audit.md`
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/realtime-monitor-legacy-static-shell-truth-audit.md`
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/stock-detail-legacy-static-shell-truth-audit.md`
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/stocks-legacy-static-shell-truth-audit.md`
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/task-management-legacy-static-shell-truth-audit.md`
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/tdx-market-legacy-static-shell-truth-audit.md`
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/technical-analysis-legacy-static-shell-truth-audit.md`

`docs/reports/quality/myweb-audit/frontend-view-checklist-top-level-legacy-2026-05-10.md` classifies these entries as retained wrapper/static-shell candidates and not archive-approved. `docs/reports/quality/myweb-audit/frontend-view-checklist-view-styles-2026-05-10.md` also records coupled legacy style assets for several of these pages, so style retirement must remain page-lifecycle-driven.

## Boundary

This decision does not move files, edit runtime code, retire tests, or change wrapper/static-shell behavior.

Current classifications:

- `EnhancedDashboard.vue`: `candidate-review/legacy-canonical-wrapper`, retain as dashboard-wrapper guard anchor.
- `RealTimeMonitor.vue`: `candidate-review/legacy-static-shell`, retain as realtime-monitor static-shell guard anchor.
- `StockDetail.vue`: `candidate-review/legacy-static-shell`, retain as stock-detail static-shell guard anchor.
- `Stocks.vue`: `candidate-review/legacy-static-shell`, retain as stocks static-shell guard anchor.
- `TaskManagement.vue`: `candidate-review/legacy-static-shell`, retain as task-management static-shell guard anchor.
- `TdxMarket.vue`: `candidate-review/legacy-static-shell`, retain as TDX static-shell guard anchor.
- `TechnicalAnalysis.vue`: `candidate-review/legacy-static-shell`, retain as technical-analysis static-shell guard anchor.

This decision does not cover nested `web/frontend/src/views/technical/TechnicalAnalysis.vue` or ArtDeco technical shells; those remain governed by their own domain checklists.

This decision does not claim global frontend lint is clean.

## Next Valid Step

Prepare a separate approval package if the team wants to retire these top-level legacy pages. That package must decide for each page:

- whether the direct owner spec is still needed
- whether the proof should be retired or migrated to a canonical successor
- the successor or explicit `no-successor-needed` rationale
- any coupled legacy style asset disposition

Until then, no archive execution is approved for these top-level wrapper/static-shell pages.

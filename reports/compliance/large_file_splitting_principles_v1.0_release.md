# Large File Splitting Principles v1.0 Release Record

## Status
- Document: `large_file_splitting_principles.md`
- Version: v1.0
- Approved Date: 2026-02-13
- Effective Date: 2026-02-13
- Owner: Architecture Group / Tech Lead

## Scope of This Phase
- Finalize and approve the governance standard only.
- Align acceptance commands and execution context.
- Freeze policy baseline for future refactoring work.

## Explicitly Out of Scope (This Phase)
- No large-file code splitting implementation.
- No API/module/component refactor execution.
- No behavior changes in backend/frontend runtime code.

## Locked Baseline Decisions
- Vue/JS mandatory split threshold: `> 500` lines.
- TypeScript type file mandatory split threshold: `> 500` lines.
- Frontend validation commands run from repo root with explicit prefix:
  - `cd web/frontend && npm run test`
  - `cd web/frontend && npm run test:coverage`
  - `cd web/frontend && npm run lint`
  - `cd web/frontend && npm run type-check`
- Performance gate policy:
  - Mandatory: Playwright and Locust metrics.
  - Recommended: Lighthouse (only when script exists).

## Release Checklist
- [x] Governance metadata switched to Approved with concrete dates.
- [x] Threshold matrix aligned with current OpenSpec constraints.
- [x] Lint gate documented as read-only (`eslint . --max-warnings=0`).
- [x] Execution-context ambiguity removed for frontend commands.
- [x] Performance section split into mandatory vs recommended gates.
- [x] Minor wording issue fixed (`FPS` duplication removed).

## Next-Step Entry Criteria (When Implementation Starts)
- A dedicated split plan document is created and approved.
- Target file list is generated against v1.0 thresholds.
- Each target has acceptance tests and rollback path defined.
- Work is executed in small batches with regression checks.


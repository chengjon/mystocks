# Task Plan: Large File Splitting Campaign - Wave 3

## Goal
Split two large TypeScript files into modular directories to improve maintainability and keep file sizes under 500 lines, while maintaining backward compatibility through re-exports.

## Phases
- [ ] Phase 1: Analysis and Planning
    - [ ] Analyze `tests/helpers/page-objects.ts` structure and dependencies.
    - [ ] Analyze `web/frontend/src/api/types/common.ts` for domain boundaries.
    - [ ] Create detailed implementation plan in `docs/plans/2026-02-16-large-file-splitting-wave-3.md`.
- [ ] Phase 2: Split `tests/helpers/page-objects.ts`
    - [ ] Create `tests/helpers/pages/` directory.
    - [ ] Extract `BasePage` and other page classes.
    - [ ] Create `index.ts` barrel file.
    - [ ] Update `page-objects.ts` to re-export.
    - [ ] Verify imports in tests.
- [ ] Phase 3: Split `web/frontend/src/api/types/common.ts`
    - [ ] Create `web/frontend/src/api/types/domains/` directory.
    - [ ] Extract `market-data.ts`.
    - [ ] Extract `trading-ops.ts`.
    - [ ] Extract `strategy-types.ts`.
    - [ ] Extract `system-base.ts`.
    - [ ] Update `common.ts` to re-export.
    - [ ] Verify type checking across frontend.
- [ ] Phase 4: Final Review and Cleanup
    - [ ] Run `lsp_diagnostics_directory` to ensure no breakages.
    - [ ] Create atomic commits for each split.

## Key Questions
1. How many classes are in `page-objects.ts`?
2. What are the specific types belonging to each domain in `common.ts`?
3. Are there internal dependencies between the split files (e.g., `DashboardPage` extending `BasePage`)?

## Decisions Made
- (None yet)

## Errors Encountered
- (None yet)

## Status
**Currently in Phase 1** - Analyzing file structures.

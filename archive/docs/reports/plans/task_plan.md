# Task Plan: Large File Splitting Campaign - Wave 3

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


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

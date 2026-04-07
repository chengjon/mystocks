# Large File Splitting Principles v1.0 Release Record

> **历史文档说明**:
> 本文件是某阶段的历史文档、过程记录或专题材料，不是当前基线、当前系统总览或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内描述、背景、结论和上下文如未重新复核，应视为历史快照，不得直接当作当前事实。


## Status
- Document: `architecture/standards/large_file_splitting_principles.md`
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

# Review: restructure-frontend-directory

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Scope

Local repo-truth review of the current `restructure-frontend-directory` execution state, focused on:

- router truth in `web/frontend/src/router/index.ts`
- generated page truth in `web/frontend/src/config/pageConfig.ts`
- canonical wrapper/cutover entrypoints under `web/frontend/src/views/{watchlist,strategy,trade,risk,system}/`
- change-ledger consistency across:
  - `openspec/changes/restructure-frontend-directory/tasks.md`
  - `openspec/changes/restructure-frontend-directory/MIGRATION_PROGRESS.md`
  - `docs/guides/frontend-structure.md`

## Evidence

- Targeted unit review command:
  - `cd web/frontend && npm run test -- tests/unit/config/router-full-path-uniqueness.spec.ts tests/unit/views/trade-wrapper-retention.spec.ts`
- Result:
  - `2` test files passed
  - `7` tests passed
- Manual source inspection confirmed:
  - active watchlist, strategy, trade, risk, and system route entries point at their current canonical targets
  - wrapper entrypoints such as `views/watchlist/*.vue` and `views/strategy/*.vue` remain thin forwarding layers
  - no active `@/views/shared/...` import chain remains in the restructure ledger truth

## Findings

### Resolved During Review

1. `openspec/changes/restructure-frontend-directory/MIGRATION_PROGRESS.md` still described Phase 2 as a scoped follow-up and Phase 9 as if local cleanup work were still pending.
   - Impact: documentation drift inside the change package; not a runtime regression.
   - Resolution: updated the phase table and notes to match the post-`8.5` repo truth and the current local closeout state.

## Open Findings

No open blocking code-review findings were identified in the reviewed restructure ledger and route-truth surface.

## Residual Risks

- Phase 6 is not fully complete until a real PR review thread and Architecture Board approval happen.
- Phases 7 through 9 still depend on merge, staging validation, archive timing, GitHub issue closure, and project-channel communication outside the local repo.

# Core Split Governance Reconciliation

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: blocked; refreshed against current checkout on `2026-05-20`; Batch 2 is not scheduled yet.

## Findings

| Item | Result |
|---|---|
| Current HEAD | `6530c88f3 docs(codebase): record openspec execution evidence`; does not contain `bbb399071` |
| Remote branch | `origin/wip/root-dirty-20260403` points at `bbb399071df53c2ae6a1001f0b65ebf3e8baddea` |
| OpenSpec task `3.2` | Still unchecked in `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/tasks.md`; an explicit non-execution note was added |
| `#83` evidence package | Not yet accepted for the next helper batch |
| issue15 | Remains unpublished and still blocked by `BLOCKED_BY_TODO: shared evidence package.` |
| Runtime-gate evidence | Commit-scoped evidence from `bbb399071`; not current-checkout evidence |
| Archive | Still disallowed |

## Decision

- Batch 2 cannot be scheduled yet.
- The task file note exists so later workers do not confuse governance reconciliation with implementation authorization.
- The current record stays in reconciliation mode, not execution mode.
- Task 9 remains blocked until `3.2`, `#83`, issue15, and archive readiness each have an accepted disposition.

## 2026-05-21 Supersession

The stale bare-import runtime blocker described below is no longer the current
first blocker. Later sequence-unblock evidence and the current validity review
show runtime smoke passing in clean current HEAD `f97f2eb57`. This does not
unblock Core Batch 2: Task `3.2`, `#83` evidence acceptance, issue15
disposition, and archive readiness still require explicit accepted decisions.

## Verification

- `git diff --check -- openspec/changes/split-backend-core-modules-with-compatibility-wrappers/tasks.md docs/reports/quality/backend-core-split-governance-reconciliation-2026-05-19.md`
- `python scripts/compliance/markdown_governance_gate.py --root-dir . --format json docs/reports/quality/backend-core-split-governance-reconciliation-2026-05-19.md`
- `openspec validate split-backend-core-modules-with-compatibility-wrappers --strict`

## Current Disposition

| Gate | Disposition |
|---|---|
| OpenSpec `3.2` | Unchecked; governance owner/scope note retained in `tasks.md`; not enough to archive |
| OpenSpec `4.3` / `4.4` / `4.5` | Accepted only as commit-scoped implementation-worktree evidence from `bbb399071` |
| Current checkout runtime | Runtime smoke now passes in clean current HEAD `f97f2eb57`, but Core Batch 2 still needs explicit gate acceptance |
| Batch 2 | Not schedulable |
| Archive | Not allowed |

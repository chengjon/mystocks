# Steward Tree Evidence Index

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active evidence index
- Prepared at: `2026-05-27T17:22:14+08:00`
- Base HEAD checked: `ba929aee2e7fc0de0278f80f30caa185fafa6b5c`

Boundary note: this index points to evidence artifacts. It does not promote
review input into accepted truth without a matching review, PR, or OpenSpec
state transition.

## Primary Evidence Artifacts

| Evidence | Role | Freshness policy |
|---|---|---|
| `.planning/codebase/steward-tree/archive/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.full-2026-05-27.md` | Full historical steward snapshot | Historical; refresh current state before using as execution truth |
| `.planning/codebase/CODEBASE-MAP-STEWARD-TREE-RETROSPECTIVE-2026-05-22.md` | Lessons and improvement opportunities | Historical; use as rationale for this split |
| `.planning/codebase/CODEBASE-MAP-STEWARD-TREE-PRACTICE-GUIDE-2026-05-24.md` | Reusable operating model for other projects | Historical; superseded for this repo by `steward-tree/README.md` |
| `.planning/codebase/steward-tree/steward-index.json` | Machine-readable active steward state | Current for this branch; stale if base HEAD or PR state changes |
| `.planning/codebase/steward-tree/current-next-gates.md` | Human-readable active gates | Current for this branch; stale if base HEAD changes |
| `.planning/codebase/generated/strategy-adapter-provider-closeout-2026-05-27.json` | G2.180 closeout and residual-refresh evidence | Current for HEAD `8bfb4dc74b06d6bb930e48ebf3d27bb28d908704` |
| `docs/reports/quality/backend-strategy-adapter-provider-closeout-2026-05-27.md` | G2.180 human-readable closeout report | Accepted by PR `#333`; superseded for residual next-gate selection by G2.181 |
| `.planning/codebase/generated/strategy-getter-residual-refresh-decision-2026-05-27.json` | G2.181 residual class refresh and next-gate decision evidence | Current for HEAD `ba929aee2e7fc0de0278f80f30caa185fafa6b5c` |
| `docs/reports/quality/backend-strategy-getter-residual-refresh-decision-2026-05-27.md` | G2.181 human-readable residual-refresh decision package | Review input until accepted |

## External State Inputs

| Input | Current state at split | Notes |
|---|---|---|
| GitHub PR `#331` | `MERGED` | G2.178 source implementation lane closed by merge commit `8bfb4dc74b06d6bb930e48ebf3d27bb28d908704` |
| `origin/wip/root-dirty-20260403` | `8bfb4dc74b06d6bb930e48ebf3d27bb28d908704` | Base used for this closeout branch |
| Root worktree | Dirty/stale relative to remote | Not used as the edit surface for this split |

## Evidence Recording Rules

- Evidence collected from context-mode must be summarized into repo files before
  it becomes durable project evidence.
- GitNexus risk results belong in implementation or authorization reports, not
  only in chat memory.
- GitHub PR state must include PR number, branch, base, and checked timestamp.
- Generated artifact references must include `generated_at`, `git_head` when
  available, `current_head_checked_at_review`, and a stale policy.
- Graphiti entries should record accepted milestone summaries after the repo or
  GitHub artifact exists.

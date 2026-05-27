# Steward Tree Current Next Gates

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active gate register
- Prepared at: `2026-05-27T15:32:41+08:00`
- Base HEAD checked: `3b8f95945fcb489316ddfaf919835d372122fa5f`

Boundary note: this file records gates. It does not authorize code changes,
issue label changes, OpenSpec proposal creation, PM2 commands, or PR merges.

## Gate Register

| Priority | Gate | Owner lane | Status | Next action |
|---|---|---|---|---|
| P0 | Keep PR `#331` separate from steward split | G/#79 service lifecycle DI | PR `#331` is open and mergeable; not included in this branch | Human decides whether to merge PR `#331`; reconcile only after a PR lands |
| P0 | Review steward-tree split | CODEBASE-MAP steward governance | In progress in `g2-179-steward-tree-governance-split` | Verify split files, JSON index, report, and task card |
| P1 | Preserve implementation authorization boundary | All lanes | Active | Every source lane still needs its own authorization packet |
| P1 | Keep Core Batch 2 blocked | Core split / compatibility wrappers | Blocked | Resolve Task 3.2 and shared evidence gate disposition before selecting Batch 2 |
| P1 | Use route/OpenAPI governance for route changes | Route/OpenAPI lane | Active | Route source changes require route ownership, OpenAPI exposure, and consumer-contract evidence |
| P2 | Keep Graphiti digest-only | Memory/governance | Active | Record accepted milestones after PR or decision package exists; do not use Graphiti as repo truth |
| P2 | Maintain machine-readable index | Steward governance | New | Update `steward-index.json` whenever an active gate changes |

## Immediate Review Questions

- Does the split preserve the full historical steward tree in archive?
- Is the root entrypoint short enough to serve as a daily navigation file?
- Does `steward-index.json` include enough fields for automated guards?
- Are PR `#331` and this governance split clearly separated?
- Are implementation, authorization, decision, and evidence lanes still distinct?

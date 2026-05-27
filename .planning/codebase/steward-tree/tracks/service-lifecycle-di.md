# Track: Service Lifecycle DI

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active track summary
- Prepared at: `2026-05-27T15:32:41+08:00`
- Base HEAD checked: `3b8f95945fcb489316ddfaf919835d372122fa5f`

Boundary note: this track summary does not authorize source changes. Each
implementation still needs a path-limited authorization package, GitNexus impact
analysis, tests, staged change detection, review, and PR merge.

## Track Role

This track owns the gradual replacement of route-body or service-body global
getter calls with explicit dependency providers or constructor/provider seams.
It proved a repeatable conveyor:

1. inventory or residual scan
2. candidate classification
3. decision package
4. implementation authorization
5. TDD implementation
6. closeout and residual refresh

## Current Strategy Residual State

| Node | State | Notes |
|---|---|---|
| G2.177 Strategy canonical adapter provider authorization | Accepted by human review in the current workstream; base snapshot still records it as ready for review | Authorized only a constructor-level Strategy service provider seam in canonical `strategy_adapter.py` and focused tests |
| G2.178 Strategy adapter provider implementation | Open PR `#331`, mergeable at split | Separate source implementation lane; not included in this governance split |
| Steward split | For review | Reorganizes steward files and index only |

## Next Gates

- Do not start another service source lane until PR `#331` is resolved or
  explicitly superseded.
- If PR `#331` merges first, update this track and `steward-index.json` to mark
  G2.178 as merged and create a closeout lane.
- If this governance split merges first, PR `#331` should reconcile steward file
  paths if it also edits the root steward tree.

## Forbidden Scope

This track summary forbids:

- backend source edits
- frontend edits
- test edits
- OpenSpec proposal creation
- issue label changes
- moving another service candidate directly to implementation
- treating service inventory counts as implementation backlogs

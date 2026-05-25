# Backend AdvancedAnalysis Compatibility Getter Phase 1 Closeout - 2026-05-25

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.89 AdvancedAnalysis compatibility getter Phase 1 closeout /
candidate refresh

Status: ready for review

## Purpose

Record the accepted G2.88 implementation, refresh the current-head getter
reference matrix, and decide the next governance gate.

This packet is closeout / candidate-refresh only. It does not edit source, tests,
routes, OpenAPI exposure, frontend clients, OpenSpec changes, PM2/runtime state,
or GitHub issue labels.

## Current Head

| Field | Value |
|---|---|
| Worktree | `.worktrees/g2-89-advanced-analysis-compat-getter-phase1-closeout` |
| Branch | `g2-89-advanced-analysis-compat-getter-phase1-closeout` |
| Current HEAD | `33c3d34dc00caa8b347e90d66084c1d001559186` |
| Parent PR | `#241` |
| Parent PR state | `MERGED` |
| Parent merge commit | `33c3d34dc00caa8b347e90d66084c1d001559186` |

## Reference Matrix

Current-head scan:

| Metric | Value |
|---|---:|
| Exact public getter hits | 1 |
| Public getter production scope | definition only |
| Route/API direct public getter hits | 0 |
| Service public getter hits | 1 |
| Test public mentions | 5 |
| Private initializer hits | 3 |
| Dependency-provider refs | 19 |
| Package export hits | 0 |

Interpretation:

- G2.88 closed the provider fallback dependency on the public compatibility
  getter.
- The public getter remains as a Phase 1 compatibility surface.
- The next possible source lane is not implementation. It is a separate
  final-retirement authorization packet that must explicitly decide whether to
  remove the public getter and update focused tests.

## Verification

| Gate | Result |
|---|---|
| Focused lifecycle tests | `4 passed in 3.60s` |
| `test_health_route_conflicts.py` | `120 passed in 67.35s` |
| OpenAPI smoke | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0`, warnings=`0` |

OpenAPI smoke loaded the root `.env` and imported `app.main`.

## Decision

G2.88 Phase 1 is ready to close once this closeout packet is accepted.

Next candidate:

`G2.90 AdvancedAnalysis public compatibility getter final-retirement authorization`

The G2.90 candidate must remain authorization-only until accepted. It must not
delete `get_advanced_analysis_service()` in the same packet.

## Boundary

Out of scope here:

- source or test edits;
- route/API edits;
- OpenAPI exposure changes;
- frontend or generated client edits;
- PM2/runtime execution;
- OpenSpec changes/spec updates;
- GitHub issue label changes;
- deleting, renaming, or privatizing `get_advanced_analysis_service()`.

## Rollback

Revert this governance-only packet. Reverting it does not revert PR `#241`; it
only restores the steward tree to the G2.88 implementation review state.

# Backend AdvancedAnalysis Compatibility Getter Final Retirement Closeout - 2026-05-25

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.92 AdvancedAnalysis public compatibility getter final-retirement
closeout

Status: ready for review

## Purpose

Record the accepted G2.91 implementation and close the AdvancedAnalysis public
compatibility getter lane.

This packet is closeout-only. It does not edit source, tests, routes, OpenAPI
exposure, frontend clients, OpenSpec changes, PM2/runtime state, or GitHub issue
labels.

## Current Head

| Field | Value |
|---|---|
| Worktree | `.worktrees/g2-92-advanced-analysis-compat-getter-final-retirement-closeout` |
| Branch | `g2-92-advanced-analysis-compat-getter-final-retirement-closeout` |
| Current HEAD | `1ebd0aeaf3f21fbaefd570955ca89b571207c18a` |
| Parent PR | `#244` |
| Parent PR state | `MERGED` |
| Parent merge commit | `1ebd0aeaf3f21fbaefd570955ca89b571207c18a` |

## Reference Matrix

Current-head scan:

| Metric | Value |
|---|---:|
| Exact public symbol mentions | 1 |
| Remaining public symbol scope | focused absence assertion string only |
| Route/API public mentions | 0 |
| Package export mentions | 0 |
| Private initializer hits | 2 |
| Dependency-provider refs | 19 |

Interpretation:

- G2.91 retired the public `get_advanced_analysis_service()` compatibility
  getter.
- Route/API continues to use `get_advanced_analysis_service_dependency()`.
- The lane should not proceed directly into another service without a fresh
  service lifecycle candidate refresh.

## Verification

| Gate | Result |
|---|---|
| Focused lifecycle tests | `5 passed in 4.79s` |
| `test_health_route_conflicts.py` | `120 passed in 77.16s` |
| OpenAPI smoke | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0`, warnings=`0` |

OpenAPI smoke loaded the root `.env` and imported `app.main`.

## Decision

AdvancedAnalysis public compatibility getter final retirement is ready to close
once this packet is accepted.

Next gate:

`Fresh service lifecycle candidate refresh`

Do not directly start another getter-retirement source branch from stale
candidate data.

## Boundary

Out of scope here:

- source or test edits;
- route/API edits;
- OpenAPI exposure changes;
- frontend or generated client edits;
- PM2/runtime execution;
- OpenSpec changes/spec updates;
- GitHub issue label changes.

## Rollback

Revert this governance-only packet. Reverting it does not revert PR `#244`; it
only restores the steward tree to the G2.91 implementation review state.

# Backend Wencai Compatibility Getter Retirement Closeout - 2026-05-25

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.96 Wencai getter-retirement closeout
Status: ready for review

## Purpose

Close out the Wencai public compatibility getter retirement lane after PR `#248`
merged.

This packet is closeout-only. It does not edit source, tests, routes, OpenAPI
exposure, PM2 state, OpenSpec content, frontend files, or issue labels.

## Parent Merge

| Field | Value |
|---|---|
| Parent PR | `#248` |
| Parent state | `MERGED` |
| Merge commit | `689d619c715ec521a3f5c1d967b0fc8eeb798293` |
| Merged at | `2026-05-25T11:54:51Z` |
| PR URL | `https://github.com/chengjon/mystocks/pull/248` |

## Current-Head Reference Scan

| Signal | Value |
|---|---:|
| `get_wencai_service` app refs | `0` |
| `get_wencai_service` route/API refs | `0` |
| `get_wencai_service` test refs | `1` |
| `get_wencai_service` package export refs | `0` |
| `WencaiService` app refs | `16` |
| `WencaiService` route/API refs | `9` |
| `WencaiService` test refs | `1` |

The remaining `get_wencai_service` test reference is the focused absence
assertion in `test_wencai_service_getter_retirement.py`.

## Verification Evidence

| Check | Result |
|---|---|
| Focused Wencai retirement test | `2 passed in 1.55s` |
| Health route conflicts | `120 passed in 71.43s` |
| Parent PR checks | PR `#248`: Mainline Governance Gate pass, check-compliance pass, weekly-full-scan skipped |

## Closed Scope

Closed:

- `get_wencai_service` public compatibility getter retirement.
- Focused absence/import regression coverage.
- Steward-tree implementation evidence for G2.95.

Still out of scope:

- deleting or renaming `WencaiService`;
- changing Wencai routes, tasks, or database service consumers;
- changing route/OpenAPI exposure;
- changing frontend, PM2, OpenSpec, or issue labels.

## Boundary

Out of scope here:

- source or test edits;
- route/API edits;
- OpenAPI exposure changes;
- frontend or generated client edits;
- PM2/runtime execution;
- OpenSpec changes/spec updates;
- GitHub issue label changes.

## Next Gate

Run a fresh service lifecycle candidate refresh before selecting another
getter-retirement lane.

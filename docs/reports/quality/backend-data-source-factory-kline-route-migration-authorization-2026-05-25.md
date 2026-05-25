# Backend DataSourceFactory Kline Route Migration Authorization - 2026-05-25

Workline: G2.72 candidate authorization packet

Current HEAD: `f4e3db66effa63ce37c94ad0f2b687a606ff8396`

> **历史索引说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: This document records a candidate-selection decision and its
evidence. It does not authorize backend source edits, route path changes,
OpenAPI exposure changes, response shape changes, frontend edits, PM2/runtime
operations, OpenSpec proposal publication, issue-label changes, compatibility
getter deletion, or migration of any DataSourceFactory consumer in this branch.

## Status

Ready for review.

G2.71 closeout has been accepted by PR `#221`, merged at
`f4e3db66effa63ce37c94ad0f2b687a606ff8396`. This packet selects the next
route/API DataSourceFactory direct consumer candidate before any further source
edit.

## Baseline Evidence

| Check | Result |
| --- | --- |
| `web/backend/tests/test_health_route_conflicts.py` | `117 passed` |
| `web/backend/tests/test_data_source_factory_lifecycle_di.py` | `4 passed` |
| Route/API direct `await get_data_source_factory()` refs | `6` |
| OpenAPI smoke | `routes=548`, `paths=500`, `operation_ids=536`, `duplicate_operation_ids=0`, `warning_count=0` |
| Git status before docs edits | clean |

OpenAPI smoke loaded the root `.env` into the isolated worktree without
recording any secret values.

## Candidate Matrix

| Candidate | LOC | Routes | Direct refs | Ruff | Black | GitNexus |
| --- | ---: | ---: | ---: | --- | --- | --- |
| `web/backend/app/api/data/kline.py` | 252 | 4 | 2 at lines `145`, `245` | `E701 x2` at lines `147`, `148` | would reformat | `LOW/1` |
| `web/backend/app/api/data/stocks.py` | 417 | 5 | 2 at lines `269`, `371` | `E701 x5` at lines `321`, `324`, `345`, `348`, `401` | would reformat | `LOW/1` |
| `web/backend/app/api/data/futures.py` | 123 | 2 | 2 at lines `91`, `114` | passed | would reformat | `CRITICAL/31` at `maxDepth=1` |

The remaining direct route/API refs are:

- `web/backend/app/api/data/stocks.py:269`
- `web/backend/app/api/data/stocks.py:371`
- `web/backend/app/api/data/kline.py:145`
- `web/backend/app/api/data/kline.py:245`
- `web/backend/app/api/data/futures.py:91`
- `web/backend/app/api/data/futures.py:114`

## Decision

Select `web/backend/app/api/data/kline.py` for the future G2.73
DataSourceFactory route migration.

Rationale:

- It has the same `LOW/1` GitNexus file-level risk as `stocks.py`, but a
  smaller route/source surface.
- It has only two same-file `E701` findings, while `stocks.py` has five.
- It avoids the `futures.py` `CRITICAL/31` file-level risk.
- It can move total route/API direct refs from `6 -> 4` and `kline.py` refs
  from `2 -> 0`.

## Deferred Candidates

`stocks.py` remains locked. It is `LOW/1`, but it has a larger source surface
and five current `E701` findings. It should not be selected until the kline
same-file style-normalization pattern has been reviewed.

`futures.py` remains locked. It is small and ruff-clean, but file-level
GitNexus impact is `CRITICAL/31`; it requires a separate narrower risk packet
before any source migration.

## Authorized Future Scope

If this packet is accepted, a future G2.73 implementation branch may be created
with source scope limited to:

- `web/backend/app/api/data/kline.py`
- a focused route dependency wiring test
- implementation evidence
- steward tree update
- mainline task card

The future G2.73 branch may normalize same-file `E701` and black formatting in
`web/backend/app/api/data/kline.py` only, if that normalization is required by
the route dependency migration diff.

No source edit is authorized by G2.72 itself.

## Next Gate

Human review / PR merge decision for this authorization packet. If accepted,
create a separate G2.73 path-limited implementation branch for `kline.py` only.

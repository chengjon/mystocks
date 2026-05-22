# Backend Watchlist Helper Cleanup Next-Lane Decision - 2026-05-23

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: decision-packet-prepared-for-review

Boundary note: This packet selects the next governance lane only. It does not
authorize backend source edits, tests, OpenSpec changes, issue label changes, or
runtime behavior changes.

## Context

G2.11 closed the third route-surface service lifecycle DI pilot:

- PR `#150` merged the `watchlist_service.py` route-surface implementation.
- PR `#151` merged the closeout report at
  `3caeea24dafb02748c92d58b2809e893ce761d5e`.
- The route-surface implementation intentionally kept the watchlist adapter/data
  helper callers out of scope.

The G2.11 closeout left one explicit decision gate:

1. select a fourth service lifecycle DI candidate,
2. create an adapter-aware watchlist helper cleanup packet, or
3. pause the service lifecycle DI sequence.

## Decision

Select option 2: prepare an adapter-aware watchlist helper cleanup authorization
packet as the next G2 lane.

Do not select a fourth route-surface service DI candidate yet.

## Rationale

The accepted service lifecycle DI sequence has completed three route-surface
pilots:

| Pilot | Surface | Result |
|---|---|---|
| `email_service.py` | notification routes | merged and closed |
| `announcement_service.py` | announcement routes | merged and closed |
| `watchlist_service.py` | seven watchlist group route handlers | merged and closed |

The remaining known watchlist lifecycle seam is not another route handler. It is
the compatibility/helper surface intentionally excluded from G2.9 and G2.10:

- `web/backend/app/services/data_adapters/watchlist.py`
- `web/backend/app/services/adapters/watchlist_adapter.py`

Earlier G2.8 evidence classified these files as adapter/data helper surfaces, not
FastAPI route dependency surfaces. Folding them into G2.10 would have expanded
the approved pilot. Leaving them unmodeled while selecting a fourth service
candidate would make the service lifecycle sequence wider without closing the
known residual seam from the third pilot.

`tradingview_widget_service.py` remains reference evidence only because it
already has the provider/app-state pattern. The accepted candidate evidence does
not identify a clean fourth route-surface service with lower governance risk
than closing the watchlist adapter-aware seam.

## Future Authorization Candidate

If this decision packet is accepted, the next packet should be a separate
implementation authorization packet, not immediate implementation.

Recommended future packet name:

- `backend-watchlist-helper-cleanup-implementation-authorization-2026-05-23.md`

Recommended future scope to evaluate:

| Area | Candidate path | Default disposition |
|---|---|---|
| Service provider seam | `web/backend/app/services/watchlist_service.py` | Inspect only unless a helper-safe seam is required |
| Data adapter helper | `web/backend/app/services/data_adapters/watchlist.py` | Candidate for adapter-aware cleanup |
| Service adapter helper | `web/backend/app/services/adapters/watchlist_adapter.py` | Candidate for adapter-aware cleanup |
| Route layer | `web/backend/app/api/watchlist.py` | Out of scope unless a regression is proven |
| Tests | focused watchlist helper lifecycle tests | Required in future authorization |

The future authorization packet must define:

- exact write scope,
- TDD red/green target,
- GitNexus pre-edit impact targets,
- whether helper seams should use explicit service injection, factory injection,
  or compatibility-retention,
- rollback plan that restores current helper behavior,
- proof that route-level G2.10 behavior remains unchanged,
- prohibition on unrelated service DI expansion.

## Non-Goals

- Do not edit backend source in this packet.
- Do not edit tests in this packet.
- Do not open a fourth route-surface service implementation lane in this packet.
- Do not delete `get_watchlist_service()` compatibility behavior.
- Do not move issue `#79` labels.
- Do not create or modify OpenSpec change files.
- Do not touch `email_service.py`, `announcement_service.py`, or
  `tradingview_widget_service.py`.

## Acceptance Evidence

| Evidence | Status |
|---|---|
| G2.11 closeout PR `#151` | merged |
| Base commit | `3caeea24dafb02748c92d58b2809e893ce761d5e` |
| Prior watchlist route-surface implementation | PR `#150`, merged at `b14ef8421d8ccd6dfd4a714b2a17d4e1ae971419` |
| Adapter/data helper files | intentionally excluded from G2.9/G2.10 |
| Backend source edits in this packet | none |

## Next Gate

Human review of this G2.12 decision packet.

If accepted, prepare a separate G2.13 adapter-aware watchlist helper cleanup
implementation authorization packet. G2.13 should still be authorization-only;
source edits remain locked until that packet is reviewed and explicitly accepted.

# Backend Realtime Socket Baseline Blocker Routing Decision

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: ready for review

Date: 2026-05-26

Workline: G2.147 realtime socket baseline blocker routing decision

Boundary: this is a decision-only routing package. It does not edit backend source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or service getter implementations.

## Purpose

G2.146 closed the G2.145 Socket.IO manager consumer-injection lane. The remaining failures are not part of that implementation. They are baseline blocker candidates that need separate ownership before broader Socket.IO/realtime suites can be used as clean regression gates.

This package routes those blockers into separate decision tracks.

## Parent Closeout

| Evidence | Value |
|---|---|
| Parent task | G2.146 Realtime socket manager consumer-injection closeout |
| Parent PR | #299 |
| Parent state | merged |
| Parent merge commit | `e42f4b11524da98cbf22f45807459f8984c9ebed` |
| Parent evidence | `docs/reports/quality/backend-realtime-socket-manager-consumer-injection-closeout-2026-05-26.md` |
| Current HEAD checked for this package | `e42f4b11524da98cbf22f45807459f8984c9ebed` |

## Current Positive Gate

The G2.145 focused regression test remains green:

```bash
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_realtime_socket_manager_streaming_dependency.py -q --no-cov --tb=short
```

Result:

- `2 passed in 0.83s`

This confirms the consumer-injection lane remains intact after PR #299.

## Blocker Evidence

### Socket.IO Legacy Export Contract

Current source scan:

| Symbol | Count in `socketio_manager.py` |
|---|---:|
| `get_socketio_manager` | 0 |
| `reset_socketio_manager` | 0 |

Current test import scan:

| Test file | `get_socketio_manager` tokens | `reset_socketio_manager` tokens |
|---|---:|---:|
| `web/backend/tests/test_socketio_manager.py` | 8 | 5 |
| `web/backend/tests/test_socketio_streaming_integration.py` | 0 | 18 |

Collect-only results:

- `web/backend/tests/test_socketio_manager.py`: cannot import `get_socketio_manager`
- `web/backend/tests/test_socketio_streaming_integration.py`: cannot import `reset_socketio_manager`

Interpretation:

The source/test contract is inconsistent. This should not be fixed inside G2.147 because doing so would require either source compatibility exports, test modernization, or both.

### Realtime Streaming Datetime Test Debt

Current command:

```bash
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_realtime_streaming_service.py -q --no-cov --tb=short
```

Result:

- `42 passed, 1 failed`
- Failure: `TypeError` comparing offset-naive and offset-aware datetimes

Relevant test lines:

| Line | Text |
|---:|---|
| 46 | `old_time = subscriber.subscribed_at` |
| 50 | `assert subscriber.subscribed_at >= old_time` |

Interpretation:

This is a realtime streaming timestamp/test-contract issue. It should not be mixed with Socket.IO legacy export alignment or G2.145 closeout.

## Routing Decision

G2.145 remains closed.

Do not reopen G2.145 to repair these blockers.

Split the remaining work into two independent downstream decision packages:

| Track | Candidate gate | Scope |
|---|---|---|
| Socket.IO legacy export contract alignment | G2.148 | Decide whether to restore thin compatibility exports, modernize legacy tests, or split source/test work |
| Realtime streaming datetime test debt | G2.149 | Decide whether this is test-only timezone consistency work or requires source timestamp contract review |

## G2.148 Candidate: Socket.IO Legacy Export Contract

Problem:

Existing tests expect `get_socketio_manager` and `reset_socketio_manager`, but current source does not expose them.

Decision options for the next gate:

- Restore thin `get_socketio_manager` / `reset_socketio_manager` compatibility exports and keep existing tests.
- Update legacy tests to instantiate `MySocketIOManager` directly and drop obsolete export expectations.
- Split test-only modernization from source compatibility if both are needed.

Required evidence before any source or test edit:

- GitNexus impact for `socketio_manager.py` and `MySocketIOManager`.
- Import consumer matrix for `get_socketio_manager` / `reset_socketio_manager`.
- Explicit decision on whether these symbols are public compatibility surface or obsolete test-only helpers.
- TDD plan and rollback for the approved option.

## G2.149 Candidate: Realtime Streaming Datetime Test Debt

Problem:

`test_realtime_streaming_service.py` compares timestamps across timezone awareness boundaries.

Decision options for the next gate:

- Fix the test to compare timezone-aware timestamps consistently.
- Adjust the source timestamp contract only if a separate source impact review proves the current contract is wrong.
- Mark as separate test debt if broader realtime source semantics are intentionally unchanged.

Required evidence before any source or test edit:

- Current `RealtimeStreamingService` timestamp contract review.
- Focused failing test or current failing test capture.
- Decision whether the fix is test-only or source+test.
- TDD plan and rollback for the selected scope.

## Explicit Non-Authorization

G2.147 does not authorize:

- Editing backend source or tests.
- Restoring `get_socketio_manager` or `reset_socketio_manager`.
- Changing realtime streaming timestamp behavior.
- Deleting `get_streaming_service`, `reset_streaming_service`, or `RealtimeStreamingService`.
- Changing route/API, OpenAPI, frontend, PM2, OpenSpec, or issue-label state.

## Recommended Next Step

Review G2.147.

If accepted, start G2.148 as a Socket.IO legacy export contract authorization package. Treat G2.149 as a separate later lane so datetime test debt does not contaminate the Socket.IO export contract decision.

# Backend Realtime Streaming Timezone-Aware Timestamps

Date: 2026-05-26  
Task: G2.153 realtime streaming timezone-aware timestamps  
Branch: `g2-153-realtime-streaming-timezone-aware-timestamps`  
Base HEAD: `58bdc319c3ca00819b6b4fe7fefa59a5a321ba9d`  
Parent: G2.149, merged by PR `#305`

> **历史文档说明**: This report records a narrow approved G2.153 implementation result and verification evidence. It does not authorize additional backend source changes, route/API changes, OpenAPI exposure changes, frontend changes, PM2 workflow changes, OpenSpec changes, issue-state changes, or compatibility wrapper deletion.

## Scope

This implementation closes the realtime streaming datetime inconsistency authorized by G2.149.

Allowed files:

- `web/backend/app/services/realtime_streaming_service.py`
- `web/backend/tests/test_realtime_streaming_service.py`
- G2.153 governance evidence, task card, and steward-tree updates

Non-goals:

- No Socket.IO manager behavior change.
- No route/API, OpenAPI, frontend, PM2, OpenSpec, config, script, or issue-label change.
- No compatibility wrapper deletion.

## Problem

`StreamSubscriber.subscribed_at` was initialized with `datetime.utcnow`, which produces an offset-naive datetime. `StreamSubscriber.update_activity()` already assigns `datetime.now(timezone.utc)`, which is offset-aware. The focused suite therefore failed when comparing the initial timestamp with the updated timestamp:

```text
TypeError: can't compare offset-naive and offset-aware datetimes
```

`StreamData.created_at` used the same naive `datetime.utcnow` default factory and was included in this lane to keep realtime streaming message timestamps on the same contract.

## Impact Check

GitNexus impact before source edit:

| Target | Direction | Risk | Impacted | Direct | Processes |
|---|---:|---:|---:|---:|---:|
| `StreamSubscriber` | upstream | LOW | 0 | 0 | 0 |
| `StreamData` | upstream | LOW | 0 | 0 | 0 |

No HIGH or CRITICAL impact was reported.

## Implementation

`web/backend/app/services/realtime_streaming_service.py` now defines `_utc_now()` and uses it for both dataclass default factories:

- `StreamSubscriber.subscribed_at`
- `StreamData.created_at`

`web/backend/tests/test_realtime_streaming_service.py` now asserts that both timestamp surfaces are timezone-aware before validating ordering or serialization behavior.

## TDD Evidence

Initial reproduction:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_realtime_streaming_service.py -q --no-cov --tb=short
1 failed, 42 passed
```

Explicit assertion red after adding timezone-awareness checks:

```text
3 failed, 40 passed
```

Green after implementation:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_realtime_streaming_service.py -q --no-cov --tb=short
43 passed
```

## Regression Evidence

| Check | Result |
|---|---|
| `web/backend/tests/test_socketio_streaming_integration.py` | 20 passed |
| `web/backend/tests/test_socketio_manager.py` | 26 passed, 1 existing warning |
| `web/backend/tests/test_realtime_socket_manager_streaming_dependency.py` | 2 passed |
| `ruff check web/backend/app/services/realtime_streaming_service.py web/backend/tests/test_realtime_streaming_service.py` | All checks passed |

The Socket.IO manager warning is the existing `RuntimeWarning` for un-awaited `asyncio.sleep` in `test_update_activity`; it is not introduced or modified by this lane.

## Decision

G2.153 is ready for review as a narrow source plus focused-test fix. The realtime streaming timestamp contract now consistently uses timezone-aware UTC datetimes for the covered dataclass defaults and update path.

Next gate: review and merge this PR, then update the steward tree to decide whether the realtime/socket subtrack has more remaining high-risk getter work or returns to the broader G2 service getter queue.

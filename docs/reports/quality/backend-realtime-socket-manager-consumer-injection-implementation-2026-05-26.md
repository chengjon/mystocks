# Backend Realtime Socket Manager Consumer-Injection Implementation

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: ready for review

Date: 2026-05-26

Workline: G2.145 realtime socket manager consumer-injection implementation

Boundary: this is the narrow source lane authorized by G2.144. It edits only `web/backend/app/core/socketio_manager.py`, adds one focused test file, and updates governance artifacts. It does not delete `get_streaming_service`, does not edit `realtime_streaming_service.py`, does not edit `aggregation_streaming_bridge.py`, and does not change route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, or GitHub issue labels.

## Purpose

G2.144 authorized the first implementation slice for the realtime streaming/socket track: reduce direct Socket.IO consumer coupling to `get_streaming_service` without retiring the realtime streaming service getter.

This implementation gives `MySocketIOManager` a manager-level streaming service dependency and routes namespace/manager streaming operations through that dependency.

## Parent Authorization

| Evidence | Value |
|---|---|
| Parent task | G2.144 Realtime streaming/socket authorization package |
| Parent PR | #297 |
| Parent state | merged |
| Parent merge commit | `3c27963c86bc095f7f28129d5b47d9257367a31f` |
| Parent evidence | `docs/reports/quality/backend-realtime-streaming-socket-authorization-package-2026-05-26.md` |
| Current HEAD before implementation | `3c27963c86bc095f7f28129d5b47d9257367a31f` |

## Pre-Edit Gates

`architecture/STANDARDS.md` was read before source edits.

GitNexus impact before edits:

| Symbol | Risk | Impacted | Direct | Processes |
|---|---:|---:|---:|---:|
| `get_streaming_service` | HIGH | 9 | 9 | 0 |
| `MySocketIOManager` | LOW | 0 | 0 | 0 |

The HIGH risk was accepted only because G2.144 explicitly authorized the first Socket.IO manager consumer-injection slice. The implementation stayed inside that authorized slice.

## Implementation

Modified source:

- `web/backend/app/core/socketio_manager.py`

Added focused test:

- `web/backend/tests/test_realtime_socket_manager_streaming_dependency.py`

Behavioral change:

- `MySocketIOManager` now accepts an optional `streaming_service` dependency.
- If no dependency is provided, it still falls back to `get_streaming_service()`.
- Socket.IO namespace streaming event handlers use `self.sio.streaming_service`.
- Socket.IO manager streaming stats and stream data emission use `self.streaming_service`.

Preserved behavior and compatibility:

- `RealtimeStreamingService` remains unchanged.
- `get_streaming_service` remains unchanged.
- `reset_streaming_service` remains unchanged.
- `web/backend/app/services/realtime_streaming_service.py` was not edited.
- `web/backend/app/services/aggregation_streaming_bridge.py` was not edited.
- No route/API, OpenAPI, frontend, PM2, OpenSpec, or issue-label state changed.

## TDD Evidence

Red:

Command:

```bash
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_realtime_socket_manager_streaming_dependency.py -q --no-cov --tb=short
```

Result:

- `2 failed`
- Failure reason: `MySocketIOManager.__init__() got an unexpected keyword argument 'streaming_service'`

Green:

Command:

```bash
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_realtime_socket_manager_streaming_dependency.py -q --no-cov --tb=short
```

Result:

- `2 passed in 0.83s`

## Token Scan

After implementation, `socketio_manager.py` contains only two `get_streaming_service` references:

| Line | Reference |
|---:|---|
| 38 | import |
| 583 | constructor fallback |

Handler-level `get_streaming_service` references: 0.

This satisfies the G2.144 target: remove repeated direct handler-level getter lookup while keeping compatibility fallback intact.

## Verification

Passed:

| Check | Result |
|---|---|
| Focused new test | `2 passed in 0.83s` |
| Ruff touched files | `All checks passed` |
| Black check touched files | `2 files would be left unchanged` |
| Token scan | total refs 2, handler-level refs 0 |

Blocked or baseline failures observed:

| Check | Result | Interpretation |
|---|---|---|
| `web/backend/tests/test_socketio_manager.py` | collection error: cannot import `get_socketio_manager` | Baseline mismatch. Parent and current `socketio_manager.py` both contain zero `get_socketio_manager` tokens. |
| `web/backend/tests/test_socketio_streaming_integration.py` | collection error: cannot import `reset_socketio_manager` | Baseline mismatch. Parent and current `socketio_manager.py` both contain zero `reset_socketio_manager` tokens. |
| `web/backend/tests/test_realtime_streaming_service.py` | `42 passed, 1 failed` | Baseline datetime issue: naive/aware datetime comparison in `test_subscriber_update_activity`; realtime service source was not edited in G2.145. |

These baseline failures were not fixed here because G2.144 explicitly forbids expanding this lane into realtime service getter deletion, aggregation bridge edits, or unrelated Socket.IO export restoration.

## Rollback

Revert the G2.145 PR to restore prior `socketio_manager.py` direct getter usage and remove the focused test and governance artifacts.

Because `get_streaming_service`, `reset_streaming_service`, and `RealtimeStreamingService` were preserved, rollback does not require route/API, OpenAPI, frontend, PM2, or OpenSpec changes.

## Next Gate

G2.146 should be closeout-only:

- Verify the G2.145 PR merge state.
- Re-run the focused test.
- Re-run the token scan.
- Record the persistent baseline test blockers separately from this implementation lane.
- Do not delete `get_streaming_service`.

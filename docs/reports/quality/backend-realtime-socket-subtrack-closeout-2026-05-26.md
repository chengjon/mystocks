# Backend Realtime Socket Subtrack Closeout

Date: 2026-05-26  
Task: G2.154 realtime/socket subtrack closeout  
Branch: `g2-154-realtime-socket-subtrack-closeout`  
Base HEAD: `bc795386313b40c4d87602fd80a09ad2d275f9d4`  
Parent: G2.153, merged by PR `#306`

> **历史文档说明**: This report records the G2.154 governance closeout result for the realtime/socket subtrack. It does not authorize backend source changes, backend test changes, route/API changes, OpenAPI exposure changes, frontend changes, PM2 workflow changes, OpenSpec changes, issue-state changes, compatibility wrapper deletion, or the next service getter implementation lane.

## Scope

G2.154 is closeout-only. It records the accepted sequence from high-risk getter strategy selection through realtime/socket implementation, follow-up routing, and timestamp fix.

Allowed files:

- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `.planning/codebase/generated/realtime-socket-subtrack-closeout-2026-05-26.json`
- `docs/reports/quality/backend-realtime-socket-subtrack-closeout-2026-05-26.md`
- `governance/mainline/task-cards/pr-307.yaml`

## Closed Sequence

| Task | PR | Result |
|---|---:|---|
| G2.143 | #296 | High-risk service getter strategy decision selected realtime streaming/socket as a dedicated track. |
| G2.144 | #297 | Authorized the realtime streaming socket lane. |
| G2.145 | #298 | Injected the Socket.IO streaming service dependency at manager level. |
| G2.146 | #299 | Closed the realtime socket injection lane and routed baseline blockers. |
| G2.147 | #300 | Split baseline blockers into legacy export contract and datetime debt lanes. |
| G2.148 | #301 | Authorized Socket.IO legacy export contract routing. |
| G2.150 | #302 | Aligned Socket.IO legacy test imports. |
| G2.151 | #303 | Triaged the stream-error emission failure as patch-target drift. |
| G2.152 | #304 | Aligned the stream-error test patch target. |
| G2.149 | #305 | Authorized realtime streaming timezone timestamp implementation. |
| G2.153 | #306 | Implemented timezone-aware realtime streaming dataclass defaults. |

## Post-Merge Verification

Focused post-merge regression on the merged base:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_realtime_streaming_service.py web/backend/tests/test_socketio_streaming_integration.py web/backend/tests/test_socketio_manager.py web/backend/tests/test_realtime_socket_manager_streaming_dependency.py -q --no-cov --tb=short
91 passed, 1 warning
```

The warning is the existing `RuntimeWarning` for un-awaited `asyncio.sleep` in `test_socketio_manager.py::TestConnectionManager::test_update_activity`; it is not introduced or modified by this closeout.

Static scan on the closeout base:

| Surface | Observation | Interpretation |
|---|---|---|
| `web/backend/app/core/socketio_manager.py` | `datetime.utcnow=0`, `get_streaming_service=2` | Remaining getter references are import plus constructor fallback; repeated handler-level direct calls remain removed. |
| `web/backend/app/services/realtime_streaming_service.py` | `datetime.utcnow=0`, `_utc_now=3`, `get_streaming_service=1` | Realtime streaming timestamp defaults are timezone-aware; remaining getter is the singleton provider itself. |
| `web/backend/tests/test_socketio_manager.py` | `get_socketio_manager=8`, `reset_socketio_manager=5` | Tests use the explicit singleton helper module contract restored by G2.150. |
| `web/backend/tests/test_socketio_streaming_integration.py` | `reset_socketio_manager=18` | Streaming integration tests use the aligned reset helper and manager-level patch target. |

## Decision

The realtime/socket subtrack is closed for now.

This closeout does not mean every high-risk getter in the project is retired. It means the dedicated realtime/socket slice has completed its authorized sequence:

- manager-level streaming service dependency injection is merged;
- legacy Socket.IO helper import/test compatibility is aligned;
- stream-error patch-target drift is resolved in tests;
- realtime streaming timestamp inconsistency is fixed;
- the focused merged-base regression suite is green.

The broader G2 high-risk service getter queue remains active. The next implementation lane should not start from this closeout. It should be selected by a separate decision or authorization package from the remaining G2.143 tracks:

- Dashboard/TDX
- Indicator/Data
- Strategy adapter
- root facade compatibility
- route dependency/provider governance

## Next Gate

Review and merge this closeout package. After acceptance, create a separate next-track decision or authorization package before any new backend source implementation starts.

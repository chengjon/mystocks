# Backend Socket.IO Test Import Alignment

Date: 2026-05-26

Branch: `g2-150-socketio-test-import-alignment`

Base: `wip/root-dirty-20260403` at `deb182e7f3ba7e50d0cc982c51248826e522dacd`

Status: implementation complete, ready for review

> **历史实施说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary: this is a test-only implementation package. It does not edit backend runtime source, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or service getter implementations.

## Purpose

G2.148 decided that the Socket.IO baseline blocker was stale test imports, not a
missing runtime provider. Runtime composition already consumes
`get_socketio_manager()` from `app.core._socketio_manager_singleton`.

This package applies that decision by aligning the legacy Socket.IO tests to the
canonical singleton helper import path.

## Pre-Edit Evidence

GitNexus pre-edit impact:

- `web/backend/tests/test_socketio_manager.py`: LOW, impacted count 0, affected
  processes 0.
- `web/backend/tests/test_socketio_streaming_integration.py`: LOW, impacted
  count 0, affected processes 0.

Red evidence:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_socketio_manager.py --collect-only -q --no-cov --tb=short
ImportError: cannot import name 'get_socketio_manager' from 'app.core.socketio_manager'
```

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_socketio_streaming_integration.py --collect-only -q --no-cov --tb=short
ImportError: cannot import name 'reset_socketio_manager' from 'app.core.socketio_manager'
```

Focused G2.145 regression baseline:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_realtime_socket_manager_streaming_dependency.py -q --no-cov --tb=short
2 passed in 1.02s
```

## Changes

Edited only:

- `web/backend/tests/test_socketio_manager.py`
- `web/backend/tests/test_socketio_streaming_integration.py`

Applied changes:

- Kept `ConnectionManager` / `MySocketIOManager` imports on
  `app.core.socketio_manager`.
- Moved `get_socketio_manager` / `reset_socketio_manager` imports to
  `app.core._socketio_manager_singleton`.
- Renamed unused `AsyncMock` patch context variables to `_mock_emit` where the
  variable is intentionally not asserted.

No runtime source was changed.

## Verification

Collection blockers are resolved:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_socketio_manager.py --collect-only -q --no-cov --tb=short
26 tests collected in 1.13s
```

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_socketio_streaming_integration.py --collect-only -q --no-cov --tb=short
20 tests collected in 1.05s
```

Focused regression remains green:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_realtime_socket_manager_streaming_dependency.py -q --no-cov --tb=short
2 passed in 1.02s
```

Touched test lint:

```text
ruff check web/backend/tests/test_socketio_manager.py web/backend/tests/test_socketio_streaming_integration.py
All checks passed
```

Additional focused suite evidence:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_socketio_manager.py -q --no-cov --tb=short
26 passed, 1 warning in 1.17s
```

The streaming integration suite now collects but exposes a separate behavior
debt:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_socketio_streaming_integration.py -q --no-cov --tb=short
1 failed, 19 passed in 2.45s
FAILED test_exception_during_subscription
```

The failure expects a `stream_error` emission during a patched subscription
exception. This is outside the import-alignment scope and should be triaged as a
separate Socket.IO streaming error-emission behavior package.

## Non-Goals

- No `app.core.socketio_manager` helper alias restoration.
- No edit to `web/backend/app/core/socketio_manager.py`.
- No edit to `web/backend/app/core/_socketio_manager_singleton.py`.
- No edit to `web/backend/app/services/realtime_streaming_service.py`.
- No realtime datetime debt fix.
- No route/API, OpenAPI, frontend, PM2, OpenSpec, issue-label, or GitHub issue
  state change.

## Next Gate

Review and merge this G2.150 package. After acceptance, decide whether the next
step is:

- G2.151 Socket.IO streaming error-emission behavior triage, or
- G2.149 realtime datetime test authorization.

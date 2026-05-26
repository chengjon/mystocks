# Backend Socket.IO Stream Error Test Patch Alignment

Date: 2026-05-26

Branch: `g2-152-socketio-stream-error-test-patch-alignment`

Base: `wip/root-dirty-20260403` at `9288c3a7cdb8428c5ef984b9ba79e7e8fb2135dc`

Status: implementation complete, ready for review

> **历史实施说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary: this is a test-only implementation package. It does not edit backend runtime source, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or service getter implementations.

## Purpose

G2.151 classified
`test_socketio_streaming_integration.py::TestStreamingErrorHandling::test_exception_during_subscription`
as test patch-target drift after Socket.IO manager consumer injection.

This package applies the test-only alignment. It changes the stale patch target
from the old accessor to the current manager-level streaming dependency.

## Pre-Edit Evidence

GitNexus pre-edit impact:

- `web/backend/tests/test_socketio_streaming_integration.py`: LOW, impacted
  count 0, affected processes 0.

Red evidence:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_socketio_streaming_integration.py::TestStreamingErrorHandling::test_exception_during_subscription -q --no-cov --tb=short
1 failed because stream_error was not observed
```

Baseline checks:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_socketio_manager.py -q --no-cov --tb=short
26 passed, 1 warning in 1.01s
```

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_realtime_socket_manager_streaming_dependency.py -q --no-cov --tb=short
2 passed in 0.98s
```

## Change

Edited only:

- `web/backend/tests/test_socketio_streaming_integration.py`

Implementation:

- Replaced the stale
  `patch("app.core.socketio_manager.get_streaming_service", ...)` target.
- Patched `manager.streaming_service.subscribe`, which is the current call path
  used by `on_subscribe_market_stream()`.
- Kept runtime source unchanged.

## Verification

Single regression:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_socketio_streaming_integration.py::TestStreamingErrorHandling::test_exception_during_subscription -q --no-cov --tb=short
1 passed in 0.85s
```

Streaming integration focused suite:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_socketio_streaming_integration.py -q --no-cov --tb=short
20 passed in 0.92s
```

Socket.IO manager focused suite:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_socketio_manager.py -q --no-cov --tb=short
26 passed, 1 warning in 0.90s
```

Consumer-injection focused regression:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_realtime_socket_manager_streaming_dependency.py -q --no-cov --tb=short
2 passed in 0.83s
```

Touched test lint:

```text
ruff check web/backend/tests/test_socketio_streaming_integration.py
All checks passed
```

## Non-Goals

- No backend runtime source edit.
- No Socket.IO manager behavior change.
- No restoration of `socketio_manager.py` helper aliases.
- No realtime datetime debt fix.
- No route/API, OpenAPI, frontend, PM2, OpenSpec, issue-label, or GitHub issue
  state change.

## Next Gate

Review and merge this G2.152 package. After acceptance, return to the already
split G2.149 realtime datetime test authorization.

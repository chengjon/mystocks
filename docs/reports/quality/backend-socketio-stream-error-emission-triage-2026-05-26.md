# Backend Socket.IO Stream Error Emission Triage

Date: 2026-05-26

Branch: `g2-151-socketio-stream-error-emission-triage`

Base: `wip/root-dirty-20260403` at `34bb3873149aee0b2e4cd06e63a45484a33a068f`

Status: triage complete, ready for review

> **历史决策说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary: this is a triage-only package. It does not edit backend runtime source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or service getter implementations.

## Purpose

G2.150 resolved the Socket.IO legacy import collection blocker and exposed a
separate behavior failure in:

```text
web/backend/tests/test_socketio_streaming_integration.py::TestStreamingErrorHandling::test_exception_during_subscription
```

This package investigates that failure and decides the next implementation lane.
It does not apply the fix.

## Reproduction

Command:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_socketio_streaming_integration.py::TestStreamingErrorHandling::test_exception_during_subscription -q --no-cov --tb=short
```

Result:

```text
FAILED test_exception_during_subscription
assert any("stream_error" in str(call) for call in calls)
```

## Root Cause

The test still patches the old accessor path:

```python
patch("app.core.socketio_manager.get_streaming_service", side_effect=Exception("Service error"))
```

That patch no longer affects the handler. After the G2.145 Socket.IO manager
consumer-injection change, `on_subscribe_market_stream()` calls:

```python
self.sio.streaming_service.subscribe(sid, symbol, user_id, fields)
```

So the handler uses the manager-level injected dependency, not a fresh
`get_streaming_service()` call. The test patch target is stale.

## Diagnostics

Stale patch-target diagnostic:

- Patched: `app.core.socketio_manager.get_streaming_service`
- Observed emission: `stream_subscribed`
- `stream_error`: not emitted
- Meaning: the patch no longer affects the subscription call path.

Current call-path diagnostic:

- Patched: `manager.streaming_service.subscribe`
- Observed emission: `stream_error`
- Error payload: `{"error_code": "INTERNAL_ERROR", "message": "Server error during subscription"}`
- Meaning: the runtime error-emission branch still works when the current call
  path is patched.

## Decision

Classification: test patch-target drift after Socket.IO manager consumer
injection.

Runtime bug: no evidence from this triage package.

Recommended next lane: G2.152 Socket.IO stream-error test patch-target
alignment.

Recommended implementation scope:

- Edit only `web/backend/tests/test_socketio_streaming_integration.py`.
- Keep runtime source unchanged.
- Patch `manager.streaming_service.subscribe` or inject a fake streaming service
  into `MySocketIOManager`.
- Run the single failing test, the full streaming integration focused suite,
  the Socket.IO manager focused suite, the G2.145 regression test, and ruff on
  the touched test file.

## Non-Goals

- No backend runtime source edit.
- No Socket.IO manager behavior change.
- No restoration of `socketio_manager.py` helper aliases.
- No realtime datetime debt fix.
- No route/API, OpenAPI, frontend, PM2, OpenSpec, issue-label, or GitHub issue
  state change.

## Next Gate

Review and merge this G2.151 triage package. After acceptance, start G2.152 as
a separate test-only implementation lane.

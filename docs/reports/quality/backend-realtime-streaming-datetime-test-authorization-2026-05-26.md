# Backend Realtime Streaming Datetime Test Authorization

Date: 2026-05-26

Branch: `g2-149-realtime-datetime-test-authorization`

Base: `wip/root-dirty-20260403` at `6ca7c1860ff3f1c1a87f094a016bef3d296fff6d`

Status: authorization package ready for review

> **历史决策说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary: this is an authorization-only package. It does not edit backend runtime source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or service getter implementations.

## Purpose

G2.147 split the remaining realtime/socket baseline debt into two independent
tracks:

- Socket.IO legacy export / error-emission debt, now handled through G2.148,
  G2.150, G2.151, and G2.152.
- Realtime streaming datetime debt, handled here as G2.149.

This package authorizes the next implementation lane for the realtime streaming
datetime failure. It does not implement the fix.

## Reproduction

Command:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_realtime_streaming_service.py -q --no-cov --tb=short
```

Result:

```text
1 failed, 42 passed in 0.97s
FAILED web/backend/tests/test_realtime_streaming_service.py::TestStreamSubscriber::test_subscriber_update_activity
TypeError: can't compare offset-naive and offset-aware datetimes
```

The failing assertion is:

```python
old_time = subscriber.subscribed_at
subscriber.update_activity()
assert subscriber.subscribed_at >= old_time
```

## Root Cause

`StreamSubscriber.subscribed_at` starts as an offset-naive datetime:

```python
subscribed_at: datetime = field(default_factory=datetime.utcnow)
```

`StreamSubscriber.update_activity()` then assigns an offset-aware datetime:

```python
self.subscribed_at = datetime.now(timezone.utc)
```

Diagnostic result:

```text
old_tz=None
new_tz=UTC
```

The failure is therefore a runtime timestamp contract inconsistency exposed by
the test, not a pure test assertion problem.

Related inconsistency:

```python
StreamData.created_at: datetime = field(default_factory=datetime.utcnow)
```

`StreamData.created_at` is not the current failing assertion, but it belongs to
the same realtime streaming timestamp surface and uses the same offset-naive
factory.

## GitNexus Evidence

Pre-authorization impact checks:

- `StreamSubscriber`: LOW, impacted count 0, affected processes 0.
- `StreamData`: LOW, impacted count 0, affected processes 0.

## Decision

Authorize G2.153: realtime streaming timezone-aware timestamps.

Recommended scope:

- `web/backend/app/services/realtime_streaming_service.py`
- `web/backend/tests/test_realtime_streaming_service.py`
- focused governance artifacts

Recommended implementation shape:

- Make realtime streaming dataclass timestamp defaults consistently
  timezone-aware UTC.
- Cover `StreamSubscriber.subscribed_at`.
- Include `StreamData.created_at` unless implementation review finds a concrete
  reason to keep it offset-naive.
- Add or preserve focused assertions that these dataclass timestamps are
  offset-aware UTC.

This should be a small source plus focused-test lane, not a Socket.IO route,
OpenAPI, frontend, PM2, or OpenSpec lane.

## Required G2.153 Gates

- Run GitNexus impact for `StreamSubscriber` and `StreamData` before editing
  source.
- Use the current `test_realtime_streaming_service.py` failure as red evidence.
- Run the full `test_realtime_streaming_service.py` focused suite after the
  implementation.
- Run the Socket.IO regression suites from G2.152 if the touched service could
  affect them.
- Run ruff on touched source and test files.
- Run staged GitNexus detect_changes before commit.
- Run mainline scope gate after commit.

## Non-Goals

- No implementation is performed by this authorization package.
- No Socket.IO manager or Socket.IO test edit is included here.
- No route/API, OpenAPI, frontend, PM2, OpenSpec, issue-label, or GitHub issue
  state change is included here.

## Next Gate

Review and merge this G2.149 authorization package. After acceptance, start
G2.153 as a separate implementation lane.

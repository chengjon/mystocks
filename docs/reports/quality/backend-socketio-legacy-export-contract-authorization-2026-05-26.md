# Backend Socket.IO Legacy Export Contract Authorization

Date: 2026-05-26

Branch: `g2-148-socketio-legacy-export-contract-authorization`

Base: `wip/root-dirty-20260403` at `3b1d67ceb52a5c3ccbbbafb534895c6a70aa6d2e`

Status: reviewable decision package

> **历史决策说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary: this is a decision-only authorization package. It does not edit backend source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or service getter implementations.

## Purpose

G2.147 split the remaining realtime/socket baseline blockers into two tracks:

- G2.148: Socket.IO legacy export contract authorization.
- G2.149: realtime streaming datetime test authorization.

This document covers only G2.148. It decides how the missing
`get_socketio_manager` / `reset_socketio_manager` imports should be routed. It
does not edit backend source or tests.

## Fresh Evidence

Focused consumer-injection regression remains clean:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_realtime_socket_manager_streaming_dependency.py -q --no-cov --tb=short
2 passed in 1.04s
```

The legacy Socket.IO manager suite still fails at collection:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_socketio_manager.py --collect-only -q --no-cov --tb=short
ImportError: cannot import name 'get_socketio_manager' from 'app.core.socketio_manager'
```

The legacy Socket.IO streaming integration suite still fails at collection:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_socketio_streaming_integration.py --collect-only -q --no-cov --tb=short
ImportError: cannot import name 'reset_socketio_manager' from 'app.core.socketio_manager'
```

## Current Contract Shape

The missing helper names are not absent from the repository. They live in the
canonical helper module:

- `web/backend/app/core/_socketio_manager_singleton.py`
  - `get_socketio_manager()`
  - `reset_socketio_manager()`

Runtime composition already consumes that canonical module:

- `web/backend/app/main.py`
- `web/backend/app/app_factory.py`

The failing tests still import the helper names from
`app.core.socketio_manager`, while runtime composition imports them from
`app.core._socketio_manager_singleton`.

## Decision

Selected path: authorize a follow-up test-only import-alignment lane.

Do not restore `get_socketio_manager` or `reset_socketio_manager` as exports
from `app.core.socketio_manager` unless a later review proves they are a real
public compatibility contract rather than stale test imports.

Reasoning:

- The canonical helper module already exists and is used by runtime composition
  roots.
- The baseline blocker is a stale test import path, not a missing runtime
  provider.
- Re-exporting the helpers from `socketio_manager.py` would make the manager
  facade wider again and weaken the getter-reduction direction from the service
  lifecycle workline.
- A test-only import alignment is narrower and keeps the runtime contract as-is.

## Authorized Next Lane

Next lane: G2.150 Socket.IO test import alignment.

Allowed implementation scope:

- `web/backend/tests/test_socketio_manager.py`
- `web/backend/tests/test_socketio_streaming_integration.py`
- focused reports, generated governance artifacts, task card, and steward-tree
  update

Expected implementation shape:

- Keep `MySocketIOManager` imported from `app.core.socketio_manager`.
- Import `get_socketio_manager` and `reset_socketio_manager` from
  `app.core._socketio_manager_singleton`.
- Do not edit runtime source.
- Do not restore helper aliases in `socketio_manager.py`.

Required verification for G2.150:

- Current red evidence from the two collect-only failures.
- Post-change collect-only for both legacy Socket.IO suites.
- Focused G2.145 regression test:
  `web/backend/tests/test_realtime_socket_manager_streaming_dependency.py`.
- Ruff check for touched test files.
- Staged GitNexus detect_changes.
- Mainline scope gate after commit.

If either legacy suite collects successfully but exposes unrelated behavioral
failures, G2.150 must record those as separate baseline debt instead of
expanding the lane.

## Non-Goals

- No backend source edit is authorized by this package.
- No test edit is performed by this package.
- No realtime streaming datetime fix is included here.
- No route/API, OpenAPI, frontend, PM2, OpenSpec, issue-label, or GitHub issue
  state change is included here.
- No deletion of Socket.IO singleton helpers is included here.

## Next Gate

Review and merge this G2.148 authorization package. After acceptance, start
G2.150 as a separate test-only implementation lane.

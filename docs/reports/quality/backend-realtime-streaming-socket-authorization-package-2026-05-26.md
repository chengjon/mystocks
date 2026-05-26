# Backend Realtime Streaming/Socket Authorization Package

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: ready for review

Date: 2026-05-26

Workline: G2.144 realtime streaming/socket authorization package

Boundary: this is an authorization package only. It does not edit backend source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or service getter implementations.

## Purpose

G2.143 split the remaining HIGH/CRITICAL service getter work into explicit tracks and selected Realtime streaming/socket as the preferred first downstream design track. This package turns that decision into a narrow authorization candidate for the next implementation lane.

The goal is to avoid jumping directly from a high-risk getter inventory to source edits. This package defines the smallest acceptable first implementation slice, the files it may touch, the files it must not touch, and the verification required before any future commit.

## Parent State

| Evidence | Value |
|---|---|
| Parent task | G2.143 High-risk service getter strategy decision package |
| Parent PR | #296 |
| Parent state | merged |
| Parent merge commit | `4b361b6c73972ad3b3d9b02bc0488946c5271882` |
| Parent evidence | `docs/reports/quality/backend-high-risk-service-getter-strategy-decision-2026-05-26.md` |
| Current HEAD checked for this package | `4b361b6c73972ad3b3d9b02bc0488946c5271882` |

## Target Seam

Primary getter: `get_streaming_service`

Service file: `web/backend/app/services/realtime_streaming_service.py`

Service class: `RealtimeStreamingService`

GitNexus impact:

| Metric | Value |
|---|---:|
| Risk | HIGH |
| Impacted symbols | 9 |
| Direct callers | 9 |
| Affected processes | 0 |
| Affected modules | 4 |

Direct callers:

- `web/backend/app/services/aggregation_streaming_bridge.py::__init__`
- `web/backend/app/core/socketio_manager.py::get_stats`
- `web/backend/app/core/socketio_manager.py::on_connect`
- `web/backend/app/core/socketio_manager.py::on_disconnect`
- `web/backend/app/core/socketio_manager.py::on_subscribe_market_stream`
- `web/backend/app/core/socketio_manager.py::on_unsubscribe_market_stream`
- `web/backend/app/core/socketio_manager.py::on_stream_filter_update`
- `web/backend/app/core/socketio_manager.py::emit_stream_data`
- `web/backend/app/core/socketio_manager.py::get_streaming_stats`

## Source Shape

| File | Observed shape | G2.145 authorization status |
|---|---|---|
| `web/backend/app/services/realtime_streaming_service.py` | 436 lines; owns `RealtimeStreamingService`, `get_streaming_service`, and `reset_streaming_service` | Do not edit in first implementation lane |
| `web/backend/app/services/aggregation_streaming_bridge.py` | 207 lines; constructor already accepts optional `streaming_service` and falls back to `get_streaming_service` | Observe only in first implementation lane |
| `web/backend/app/core/socketio_manager.py` | 688 lines; Socket.IO handlers call `get_streaming_service` directly | Candidate first implementation lane |

## Authorization Decision

This G2.144 package itself does not authorize source edits.

If this package is reviewed and approved, the next source lane may be:

G2.145 realtime socket manager consumer-injection implementation.

Authorized goal for G2.145:

Convert `MySocketIOManager` streaming consumers from repeated direct `get_streaming_service` calls to an explicit manager-level `streaming_service` dependency while preserving runtime behavior and the legacy service getter.

This is intentionally not a getter deletion lane. The first implementation should reduce direct consumer coupling inside `socketio_manager.py`, not retire the service singleton.

## G2.145 Allowed Paths If Approved

Source:

- `web/backend/app/core/socketio_manager.py`

Tests:

- `web/backend/tests/test_socketio_manager.py`
- `web/backend/tests/test_socketio_streaming_integration.py`
- `web/backend/tests/test_realtime_socket_manager_streaming_dependency.py`

Governance:

- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `.planning/codebase/generated/realtime-socket-manager-consumer-injection-implementation-2026-05-26.json`
- `docs/reports/quality/backend-realtime-socket-manager-consumer-injection-implementation-2026-05-26.md`
- `governance/mainline/task-cards/pr-298.yaml`

## G2.145 Forbidden Paths If Approved

- `web/backend/app/services/realtime_streaming_service.py`
- `web/backend/app/services/aggregation_streaming_bridge.py`
- `web/backend/app/api/**`
- `web/backend/app/schemas/**`
- `web/frontend/**`
- `src/**`
- `config/**`
- `scripts/**`
- `openspec/changes/**`
- `openspec/specs/**`

## Required G2.145 TDD And Verification If Approved

Before source edits:

- Read `architecture/STANDARDS.md`.
- Run fresh GitNexus impact for `get_streaming_service`.
- Run fresh GitNexus context or impact for `MySocketIOManager`.
- Record current `get_streaming_service` token count in `socketio_manager.py`.

TDD:

- Write a focused failing test proving `MySocketIOManager` can use an injected streaming service without direct per-handler getter lookup.
- Keep the failing red result in the implementation report.
- Make the minimal `socketio_manager.py` change to satisfy the test.
- Keep `RealtimeStreamingService`, `get_streaming_service`, and `reset_streaming_service` import compatibility intact.

Verification:

- Run the focused new test.
- Run relevant existing socket manager and streaming integration tests when import-safe.
- Run Ruff and Black checks for touched backend files.
- Run a scripted token scan proving `socketio_manager.py` no longer has handler-level `get_streaming_service` calls.
- Run staged GitNexus `detect_changes` before commit.
- Run the mainline scope gate after commit.
- Run `gitnexus analyze --with-gitignore` after commit.

## Explicit Non-Authorization

G2.144 does not authorize:

- Editing source or tests in this PR.
- Deleting `get_streaming_service`, `_streaming_service`, or `reset_streaming_service`.
- Editing `web/backend/app/services/realtime_streaming_service.py`.
- Editing `web/backend/app/services/aggregation_streaming_bridge.py`.
- Changing route/API, OpenAPI, frontend, PM2, OpenSpec, or issue-label state.
- Touching Dashboard/TDX, Indicator/Data, Strategy adapter, root facade, or route dependency/provider tracks.

## Rollback Model

If G2.144 is rejected, revert only this authorization package.

If a future G2.145 implementation is rejected, revert one socket-manager-focused implementation PR. Runtime getter compatibility must remain available after that rollback.

## Verification

Fresh checks performed for this package:

- PR #296 verified merged at `4b361b6c73972ad3b3d9b02bc0488946c5271882`.
- Current worktree HEAD: `4b361b6c73972ad3b3d9b02bc0488946c5271882`.
- GitNexus context found `get_streaming_service` in `web/backend/app/services/realtime_streaming_service.py`.
- GitNexus context found `RealtimeStreamingService` in `web/backend/app/services/realtime_streaming_service.py`.
- GitNexus impact for `get_streaming_service`: HIGH, impacted 9, direct 9, processes 0.
- Source shape scan found `socketio_manager.py` has 9 `get_streaming_service` tokens and is the only authorized first implementation source file.

## Next Gate

Review G2.144.

If approved, start G2.145 as a single-file `socketio_manager.py` consumer-injection implementation lane with focused tests and fresh GitNexus impact. Do not delete the realtime service getter in G2.145.

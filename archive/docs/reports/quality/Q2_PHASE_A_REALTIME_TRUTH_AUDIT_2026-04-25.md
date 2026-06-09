# Q2 Phase A Realtime Truth Audit

Date: 2026-04-25
Scope: `plan-q2-optimization-closure-program` Phase A
Mode: single-CLI sequential audit

## Documents And Code Surfaces Examined
- `docs/reports/quality/MYSTOCKS_PHASE_EVALUATION_2026Q2.md`
- `docs/reports/quality/Q2_CLOSURE_PROGRAM_SPEC_REVIEW.md`
- `openspec/changes/plan-q2-optimization-closure-program/proposal.md`
- `openspec/changes/plan-q2-optimization-closure-program/design.md`
- `openspec/changes/plan-q2-optimization-closure-program/tasks.md`
- `web/backend/app/main.py`
- `web/backend/app/app_factory.py`
- `web/backend/app/router_registry.py`
- `web/backend/app/api/websocket.py`
- `web/backend/app/api/realtime_market.py`
- `web/backend/app/api/notification.py`
- `web/backend/app/api/risk/v31.py`
- `web/backend/app/core/socketio_manager.py`
- `web/backend/app/core/_socketio_manager_singleton.py`
- `web/backend/app/services/websocket_manager.py`
- `web/backend/app/services/realtime_streaming_service.py`
- `web/backend/tests/test_socketio_streaming_integration.py`

## Executive Summary
Current repo truth does not support treating Socket.IO as the externally canonical realtime path.

The active runtime path is `app.main:app`, and the currently exposed realtime transport is native FastAPI WebSocket through mounted routers. Socket.IO exists as an initialized internal capability with tests and status reporting, but no verified ASGI mount or runtime attachment was found in the main application entrypoint.

## Composition Truth Findings

### Canonical backend composition source-of-truth
- `web/backend/app/main.py` is the runtime composition truth.
- Evidence:
  - `web/backend/ecosystem.config.js` starts `app.main:app`
  - `web/backend/Dockerfile` starts `uvicorn app.main:app`
  - `web/backend/start_backend.sh` starts `web.backend.app.main:app`
  - multiple scripts and deployment helpers point to `app.main:app`

### Current role of `app_factory.py`
- `web/backend/app/app_factory.py:create_app()` is not the main runtime assembly path.
- Current observed usage is primarily test-facing.
- Strong evidence found in `web/backend/tests/test_csrf_protection.py`, which repeatedly imports and instantiates `create_app()`.

## Realtime Transport Findings

### Active externally exposed native WebSocket paths
- `web/backend/app/api/websocket.py`
  - `/ws/events`
  - generic event channels via `app.services.websocket_manager.manager`
- `web/backend/app/api/realtime_market.py`
  - `/api/ws/market`
  - `/api/ws/portfolio`
  - plus supporting HTTP MTM/realtime quote endpoints
- `web/backend/app/api/notification.py`
  - `/api/notification/ws/notifications`
- `web/backend/app/api/risk/v31.py`
  - `/api/v31/ws/risk-updates`
- These routes are included through `web/backend/app/router_registry.py`, which is invoked by `web/backend/app/main.py`.

### Socket.IO path status
- `web/backend/app/core/socketio_manager.py` defines `MySocketIOManager`, namespace handlers, and streaming-specific handlers.
- `web/backend/app/main.py` and `web/backend/app/app_factory.py` both initialize `get_socketio_manager()`.
- No verified `socketio.ASGIApp(...)`, `app.mount(...)`, or equivalent runtime attachment for Socket.IO was found in the main runtime path.
- Conclusion: Socket.IO is present as an internal or compatibility-retained capability, not as the externally canonical realtime transport.

## Realtime Registry Recommendation

| Capability | Current path | Current status | Recommended registry state |
|---|---|---|---|
| generic backend event push | `/ws/events` | active | canonical |
| market quote push | `/api/ws/market` | active | canonical |
| MTM / portfolio push | `/api/ws/portfolio` | active | canonical |
| user notification push | `/api/notification/ws/notifications` | active | canonical |
| risk push | `/api/v31/ws/risk-updates` | active | canonical |
| Socket.IO streaming namespace `/` | internal `MySocketIOManager` | initialized but not mounted as verified public transport | compatibility-retained / non-canonical |

## Key Risks Found

### 1. Realtime connection managers are fragmented
Different realtime surfaces keep separate connection-management implementations:
- `app.services.websocket_manager.ConnectionManager`
- `api.realtime_market.WebSocketConnectionManager`
- `api.notification_support.connection_manager`
- `api.risk.v31.ConnectionManager`
- `api.backtest_ws.ConnectionManager`
- `app.core.socketio_manager.ConnectionManager`

This confirms the Q2 evaluation concern that realtime truth is split and difficult to govern as one chain.

### 2. Socket.IO streaming is not yet runtime-truth
The repo contains tests and code for Socket.IO market streaming, but the runtime application does not show a verified public mount. Promoting Socket.IO to canonical before that gap is closed would be false governance.

### 3. Realtime market route contains an internal inconsistency
`web/backend/app/api/realtime_market.py` defines `broadcast_to_subscribers()` using `self.symbol_subscribers`, but the manager stores subscriptions in `self.symbol_subscriptions`.

This is an implementation defect candidate and should be handled in a later implementation wave, not by changing the registry conclusion.

### 4. Two backend assembly entrypoints still create ambiguity
Even though runtime evidence strongly favors `main.py`, the existence of `app_factory.py` as a second assembly path still creates governance ambiguity and should be explicitly classified in Phase B.

## Canonicalization Decision For Phase A
- Backend composition truth:
  - canonical: `web/backend/app/main.py`
  - non-canonical current role: `web/backend/app/app_factory.py` as test-oriented compatibility factory
- Realtime transport truth:
  - canonical current transport family: native FastAPI WebSocket routes registered via `router_registry`
  - non-canonical current transport family: Socket.IO manager and streaming service until public runtime mount and ownership are formally closed

## Recommended Next Steps
1. Enter Phase B and formally codify `main.py` as runtime composition truth in implementation-facing docs and governance artifacts.
2. Keep Socket.IO classified as compatibility-retained until the project either mounts it as a real public transport or removes the ambiguity.
3. In later implementation waves, consolidate connection-management ownership to reduce duplicated realtime infrastructure.

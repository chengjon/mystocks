# Q2 Wave 1 Follow-Up Debt Capture

Date: 2026-04-26
Wave: `Wave 1 / Backend Composition And Realtime Truth Convergence`
Mode: single-CLI execution follow-up capture
Related artifacts:
- `docs/reports/quality/Q2_WAVE1_BACKEND_REALTIME_CLOSURE_BATCH_PLAN_2026-04-25.md`
- `docs/reports/quality/Q2_WAVE1_IMPLEMENTATION_PROGRESS_2026-04-26.md`
- `docs/reports/quality/Q2_PHASE_A_REALTIME_TRUTH_AUDIT_2026-04-25.md`
- `docs/reports/quality/Q2_PHASE_B_BACKEND_COMPOSITION_CLOSURE_2026-04-25.md`

## Purpose

This document records what Wave 1 intentionally did not solve. It prevents the completed truth-locking work from being misread as full backend composition unification or full realtime infrastructure cleanup.

## Deferred Items

### 1. Realtime connection-manager consolidation
Status: deferred

Current issue:
- multiple realtime surfaces still maintain separate connection-manager implementations

Examples:
- `app.services.websocket_manager.ConnectionManager`
- `api.realtime_market.WebSocketConnectionManager`
- `api.notification_support.connection_manager`
- `api.risk.v31.ConnectionManager`
- `api.backtest_ws.ConnectionManager`
- `app.core.socketio_manager.ConnectionManager`

Why deferred:
- this is structural runtime refactoring, not truth-locking work
- it carries broader regression risk than Wave 1 was allowed to absorb

### 2. `realtime_market.py` internal inconsistency
Status: deferred

Current issue:
- `broadcast_to_subscribers()` references `self.symbol_subscribers`
- the manager stores subscriptions in `self.symbol_subscriptions`

Why deferred:
- this is an implementation defect candidate
- Wave 1 only locked registry truth and explicitly did not claim realtime bug cleanup

### 3. `app_factory.py` long-term disposition
Status: deferred decision

Current issue:
- `app_factory.py` is now explicitly classified as compatibility-retained / test-scoped
- its final structural endpoint is still undecided

Allowed future directions:
1. thin delegation wrapper over canonical runtime composition
2. clearly bounded test factory with intentional deviations documented
3. retirement after callers migrate

Why deferred:
- Wave 1 only needed to stop dual-truth drift
- choosing the final endpoint affects test strategy and composition evolution

### 4. Socket.IO future decision
Status: deferred decision

Current issue:
- Socket.IO remains present as a compatibility-retained capability
- no verified public runtime mount exists in the canonical runtime path

What Wave 1 closed:
- Socket.IO is not the current public canonical transport truth

What remains open:
- whether Socket.IO should later be:
  - formally mounted and verified as a public transport
  - retained only for compatibility/internal use
  - retired if the FastAPI WebSocket route family remains sufficient

### 5. Test/runtime drift reduction beyond role labeling
Status: deferred

Current issue:
- tests still bootstrap via `create_app()` while production boots `app.main:app`
- Wave 1 added role labels and scope constraints, but did not unify behavior

Why deferred:
- deeper convergence would change middleware, exception, lifecycle, or route-assembly behavior
- `create_app` already showed HIGH upstream impact through the CSRF suite

## What Wave 1 Does Claim

Wave 1 now defensibly claims:
- canonical backend composition truth is explicit
- compatibility-retained `app_factory.py` scope is explicit
- canonical public realtime transport wording is explicit
- high-signal docs and references no longer overstate Socket.IO or dual runtime truth

## What Wave 1 Does Not Claim

Wave 1 does not claim:
- backend composition unification is complete
- realtime implementation defects are fixed
- connection-manager duplication is resolved
- Socket.IO runtime mounting is verified
- test/runtime behavior is fully converged

## Recommended Next Step

Wave 1 may now be treated as implementation-closed at the truth-locking level.

Subsequent work should move to:
- Wave 2 ownership closure
- or a separately approved backend/realtime cleanup batch if the team wants to reduce Wave 1 debt before moving on

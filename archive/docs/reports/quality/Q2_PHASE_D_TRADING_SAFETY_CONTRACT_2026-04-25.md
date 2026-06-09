# Q2 Phase D Trading Safety Contract Audit

Date: 2026-04-25
Scope: `plan-q2-optimization-closure-program` Phase D
Mode: single-CLI sequential audit

## Documents And Code Surfaces Examined
- `docs/reports/quality/MYSTOCKS_PHASE_EVALUATION_2026Q2.md`
- `docs/reports/quality/Q2_CLOSURE_PROGRAM_SPEC_REVIEW.md`
- `openspec/changes/plan-q2-optimization-closure-program/design.md`
- `openspec/changes/plan-q2-optimization-closure-program/tasks.md`
- `src/application/trading/order_mgmt_service.py`
- `src/application/dto/trading_dto.py`
- `src/domain/trading/model/order.py`
- `src/domain/trading/model/position.py`
- `src/domain/trading/repository/iorder_repository.py`
- `src/infrastructure/persistence/repository_impl.py`
- `src/trading/live_trading_engine.py`
- `src/trading/realtime_strategy_executor.py`
- `src/interfaces/api/trading_router.py`
- `src/governance/risk_management/services/stop_loss_execution_service.py`
- `src/governance/risk_management/services/stop_loss_history_service.py`
- `src/governance/risk_management/services/alert_service.py`
- `src/infrastructure/logging/audit_system.py`
- `src/interfaces/business_data_source.py`
- `src/interfaces/relational_data_source.py`

## Executive Summary
Current repo truth does not support classifying any trading execution path as `production-eligible`.

The project has:
- domain modeling for orders and positions
- an application service for placing orders
- live trading orchestration scaffolding
- stop-loss and risk-alert services
- a reusable audit infrastructure

But it does not yet have a closed production safety contract across:
- idempotent submission
- pre-execution risk gates
- explicit confirmation policy enforcement
- execution-path audit binding
- real external broker execution closure

## Current Trading Path

### Modeled path
- `RealtimeStrategyExecutor`
- `LiveTradingEngine`
- `OrderManagementService`
- `Order` aggregate
- `OrderRepositoryImpl`

### What this path currently does
- creates domain orders
- moves order state from `CREATED` to `SUBMITTED`
- persists order state to repository
- handles fill reports if they are supplied later

### What this path currently does not prove
- actual broker or exchange submission
- durable idempotency protection
- pre-execution risk threshold enforcement
- mandatory confirmation before sensitive execution
- durable order audit record tied to every submission decision

## Classification Decision

### Simulated
- DDD trading API at `src/interfaces/api/trading_router.py` is not wired and returns `501`
- this path is not even execution-complete

### Experimental
- `LiveTradingEngine` and `RealtimeStrategyExecutor` are best classified as experimental
- evidence:
  - executor creates `OrderManagementService(None)` by default in one path
  - comments explicitly note mock/default assumptions
  - strategy watchlists use default placeholder symbols
  - code demonstrates orchestration intent rather than production-grade execution proof

### Production-eligible
- no inspected path qualifies

## Key Findings

### 1. No idempotent submission contract is enforced
`CreateOrderRequest` does not carry any of:
- client request id
- idempotency key
- deduplication scope
- replay protection token

`OrderManagementService.place_order()` always creates a fresh `Order` via a new UUID and saves it. There is no duplicate-intent detection before persistence.

### 2. No explicit pre-execution risk gate exists in the order placement path
`LiveTradingConfig` defines:
- `max_positions`
- `max_position_size`
- `max_daily_loss`
- `max_drawdown`
- `risk_per_trade`

But these are not enforced as a blocking pre-order gate inside `OrderManagementService.place_order()`.

The strongest current risk logic is:
- position/stop-loss behavior in domain position model
- stop-loss execution service after monitoring
- alerting and monitoring services

These are valuable, but they are not the same as a mandatory pre-submission risk gate.

### 3. Confirmation policy is not enforced in the trading path
There is evidence of a preference flag example:
- `confirm_before_trade: True`

But this appears only as preference/interface documentation and not as a hard control in the order placement workflow.

No inspected trading execution path required:
- user confirmation token
- second-factor approval
- policy-based bypass justification

### 4. Audit infrastructure exists, but trading execution is not bound to it
`src/infrastructure/logging/audit_system.py` provides:
- async audit queue
- durable `audit_logs` insertion
- `request_id` support
- cleanup of old audit logs with a default 90-day retention helper

However:
- `OrderManagementService.place_order()` does not emit audit events into that system
- `OrderRepositoryImpl.save()` persists order state but does not create trade audit records
- stop-loss monitoring records signals, but signal recording is not the same as a complete trading submission audit contract

### 5. Real broker execution closure is missing
The inspected trading path ends at repository save and internal state transitions. No canonical external broker execution adapter was verified in the main execution chain.

This aligns with the Q2 evaluation concern that the system should not imply production-grade real trading readiness.

### 6. Stop-loss execution is useful but still not a production safety proof
`StopLossExecutionService` can create a market sell order request and invoke `order_service.place_order(...)`.

That helps confirm trading components can be orchestrated together, but it still lacks:
- idempotent liquidation protection
- explicit confirmation/bypass policy
- hard binding to durable audit logs
- proof of actual external execution semantics

## Canonical Safety Contract For Phase D

The Q2 closure program should adopt this interpretation:

| Concern | Required contract meaning | Current state |
|---|---|---|
| path classification | simulated / experimental / production-eligible | partially modeled, not yet formalized in code |
| idempotent submission | duplicate effective order intents must be blocked or deduped | missing |
| pre-execution risk gate | threshold breach blocks order before placement | missing in canonical placement path |
| confirmation policy | sensitive actions require confirmation or approved bypass | missing as enforced control |
| trading audit | every submit/reject/confirm/dedup decision is durably recorded | infrastructure exists, path binding missing |
| production eligibility | only allowed when all above are true | not satisfied |

## Minimum Blocking Conditions Before Any Production Claim
The project must not claim `production-eligible` trading until at least:

1. order submission carries a stable idempotency identity
2. pre-execution risk thresholds are enforced in the canonical placement path
3. confirmation policy is enforced for safety-sensitive actions
4. submit/reject/dedup/confirm decisions are durably audited
5. the external execution adapter path is explicit and verified

## Recommended Next Steps
1. Bind the OpenSpec trading-execution-safety capability to the actual canonical placement path rather than generic aspirations.
2. Treat all currently inspected execution paths as `experimental` unless proven otherwise.
3. Add explicit audit-binding and idempotency requirements before any implementation wave extends live trading claims.
4. Keep stop-loss and risk monitoring as supporting controls, not as substitutes for pre-execution safety gates.

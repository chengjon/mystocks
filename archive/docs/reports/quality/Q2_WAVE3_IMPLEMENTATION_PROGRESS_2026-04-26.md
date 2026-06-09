# Q2 Wave 3 Implementation Progress

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-26
Wave: `Wave 3 / Trading Safety Blocking Controls`
Mode: single-CLI execution
Related plan:
- `docs/reports/quality/Q2_WAVE3_TRADING_SAFETY_CLOSURE_BATCH_PLAN_2026-04-26.md`

## Summary

Wave 3 implementation is being closed conservatively at the safety-contract and governance layer.

The current implementation line does not make live trading production-ready. It locks the canonical placement path, safety classification, idempotency contract, pre-execution blocking semantics, audit binding requirements, and residual non-claims so later work cannot overstate execution readiness.

## Batch Status

### Batch 1: Safety Classification And Canonical Path Lock
Status: complete at documentation layer

Completed outcomes:
- the canonical order-placement path is explicitly identified as:
  - `RealtimeStrategyExecutor`
  - `LiveTradingEngine`
  - `OrderManagementService.place_order()`
  - `OrderRepository`
- currently execution-capable paths are explicitly classified as `experimental`
- no inspected path is allowed to imply `production-eligible`

Updated files:
- `docs/reports/quality/Q2_WAVE3_CANONICAL_PATH_AND_CLASSIFICATION_2026-04-26.md`

### Batch 2: Idempotency And Deduplication Contract
Status: complete at contract/documentation layer

Completed outcomes:
- a canonical idempotency identity and deduplication scope is now documented for the placement path
- duplicate effective trade intent is now explicitly modeled as an auditable dedup outcome rather than a second blind submission
- the current repo is explicitly documented as not yet enforcing this contract in code

Updated files:
- `docs/reports/quality/Q2_WAVE3_IDEMPOTENCY_AND_DEDUP_CONTRACT_2026-04-26.md`

### Batch 3: Pre-Execution Risk Gate And Confirmation Policy
Status: complete at policy/documentation layer

Completed outcomes:
- pre-execution blocking conditions are now documented for capital, concentration, exposure, and session-safety checks
- high-risk actions are now explicitly modeled as requiring confirmation or approved bypass
- stop-loss and monitoring are now explicitly classified as supporting controls rather than substitutes for a pre-order gate

Updated files:
- `docs/reports/quality/Q2_WAVE3_RISK_GATE_AND_CONFIRMATION_POLICY_2026-04-26.md`

### Batch 4: Durable Audit Binding And Retention Closure
Status: complete at audit-contract/documentation layer

Completed outcomes:
- submit, reject, confirm, bypass, and dedup decisions are now explicitly mapped to durable audit expectations
- audit identity requirements are now attached to the decision point rather than only downstream execution artifacts
- retention expectations are now documented for the experimental trading path

Updated files:
- `docs/reports/quality/Q2_WAVE3_AUDIT_BINDING_AND_RETENTION_2026-04-26.md`

### Batch 5: Residual Gap Capture
Status: complete at gap-capture/documentation layer

Completed outcomes:
- unresolved broker-path, stronger execution semantics, and promotion-criteria gaps are now explicitly preserved
- Wave 3 closure language now has a hard non-claim boundary against `production-eligible` readiness

Updated files:
- `docs/reports/quality/Q2_WAVE3_RESIDUAL_GAP_CAPTURE_2026-04-26.md`

## Risk Posture

Wave 3 intentionally avoids order-placement behavior changes in this pass.

It does not yet:
- prove a real external broker execution path
- provide centralized or distributed audit durability
- provide durable reservation state or broker-reconciled positions

This keeps the current line safe from false-readiness claims while preserving the next implementation target.

## Verification Notes

### Verified
- the Phase D audit and Wave 3 plan now have concrete closure artifacts for each required batch
- current execution-capable paths are still classified conservatively as `experimental`
- the trading safety contract now distinguishes blocking controls from supporting controls
- unresolved broker and production-readiness gaps remain explicit

### Runtime Batch 1 Follow-Up

A first runtime-hardening micro-batch is now also landed:

- `CreateOrderRequest` now carries optional request identity fields:
  - `idempotency_key`
  - `request_id`
  - `actor_id`
  - `source_id`
- `OrderManagementService` now performs narrow in-memory idempotency deduplication on `idempotency_key`
- `OrderManagementService` now emits decision-point audit payloads for:
  - `submitted`
  - `deduplicated`
  - `rejected`

Related artifact:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH1_IDEMPOTENCY_AUDIT_2026-04-26.md`

Targeted validation result:
- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `4 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: the targeted trading-service behavior passed, but the repository-level coverage gate still requires broader scope to report green

### Runtime Batch 2 Follow-Up

A second runtime-hardening micro-batch is now also landed:

- `OrderManagementService` now supports an injectable `pre_submit_gate`
- the canonical placement path now distinguishes these additional decision outcomes:
  - `blocked_by_risk_gate`
  - `awaiting_confirmation`
  - `approved_bypass`
- `CreateOrderRequest` now carries:
  - `confirmation_token`
  - `bypass_reason`
- confirmation-required requests are now stopped before persistence unless:
  - a confirmation token is present, or
  - a bounded bypass reason plus actor identity is present

Related artifact:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH2_RISK_GATE_CONFIRMATION_2026-04-26.md`

Targeted validation result:
- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `7 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: the targeted trading-service behavior passed, while the repository-level coverage gate remains a separate baseline issue

### Runtime Batch 3 Follow-Up

A third runtime-hardening micro-batch is now also landed:

- a default append-only JSONL durable sink now exists for trading decision audits
- default `OrderManagementService` construction in:
  - `src/application/bootstrap.py`
  - `src/governance/risk_management/services/stop_loss_execution_service.py`
  now binds decision audits to that sink
- the canonical placement path now has a local durable reconstruction trail instead of only an injectable callback hook

Related artifact:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH3_DURABLE_AUDIT_SINK_2026-04-26.md`

Targeted validation result:
- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: targeted tests include durable JSONL audit persistence coverage
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: the runtime batch behavior passed in the targeted scope, while repository-wide coverage remains a separate gate

### Runtime Batch 4 Follow-Up

A fourth runtime-hardening micro-batch is now also landed:

- a local SQLite ledger now exists for trading decision audits:
  - `SqliteTradingDecisionAuditSink`
- the default trading decision audit sink is now a composite local sink that writes to:
  - JSONL
  - SQLite
- the canonical placement path therefore gains both:
  - append-only local durability
  - local queryability for recent decision records

Related artifact:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH4_LOCAL_QUERYABLE_AUDIT_LEDGER_2026-04-26.md`

Targeted validation result:
- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `10 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: the new local ledger behavior passed in the targeted scope, while repository-wide coverage remains a separate gate
- `pytest tests/unit/core/test_runtime_config_governance.py::test_app_container_uses_role_aware_redis_kwargs -q`
  - functional result: `1 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: the default application wiring remains behaviorally compatible in the targeted scope

### Runtime Batch 5 Follow-Up

A fifth runtime-hardening micro-batch is now also landed:

- `CreateOrderRequest` now carries:
  - `portfolio_id`
- a new synchronous portfolio-aware gate now exists:
  - `build_portfolio_pre_submit_gate()`
- default `OrderManagementService` construction now binds that gate in:
  - `src/application/bootstrap.py`
  - `src/governance/risk_management/services/stop_loss_execution_service.py`
- the canonical placement path now blocks before persistence when:
  - portfolio context is missing
  - portfolio cash is insufficient for the requested BUY notional
  - projected single-symbol concentration breaches the configured limit
  - requested SELL quantity exceeds currently held quantity
- the stop-loss execution path now emits canonical uppercase sell requests plus `portfolio_id` to stay compatible with the same gate

Related artifact:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH5_PORTFOLIO_AWARE_RISK_GATE_2026-04-26.md`

Targeted validation result:
- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `15 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: the portfolio-aware risk gate behavior passed in the targeted scope, while repository-wide coverage remains a separate gate
- `pytest tests/unit/core/test_runtime_config_governance.py::test_app_container_uses_role_aware_redis_kwargs -q`
  - functional result: `1 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: default container wiring remains behaviorally compatible in the targeted scope

### Runtime Batch 6 Follow-Up

A sixth runtime-hardening micro-batch is now also landed:

- `OrderManagementService` now maintains a local pending BUY cash reservation ledger keyed by:
  - `portfolio_id`
  - `order_id`
- the portfolio-aware pre-submit gate now supports a reservation-aware cash check through:
  - `pending_buy_notional_getter`
- default runtime builders now bind that getter so the canonical placement path evaluates:
  - raw portfolio cash
  - minus pending BUY reservations
- execution reports now reconcile those pending BUY reservations in the same service-local runtime

Related artifact:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH6_PENDING_BUY_CASH_RESERVATION_2026-04-26.md`

Targeted validation result:
- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `17 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: reservation-aware capital checks passed in the targeted scope, while repository-wide coverage remains a separate gate
- `pytest tests/unit/core/test_runtime_config_governance.py::test_app_container_uses_role_aware_redis_kwargs -q`
  - functional result: `1 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: default container wiring remains behaviorally compatible in the targeted scope

### Runtime Batch 7 Follow-Up

A seventh runtime-hardening micro-batch is now also landed:

- a dedicated cash reservation store module now exists:
  - `InMemoryPortfolioCashReservationStore`
  - `SqlitePortfolioCashReservationStore`
- `OrderManagementService` now reads and writes pending BUY reservations through an injectable store
- default runtime builders now bind a local SQLite reservation ledger in:
  - `src/application/bootstrap.py`
  - `src/governance/risk_management/services/stop_loss_execution_service.py`
- the canonical single-process trading path can now recover pending BUY reservations across service recreation on the same host

Related artifact:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH7_DURABLE_CASH_RESERVATION_STORE_2026-04-26.md`

Targeted validation result:
- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `19 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: durable local reservation recovery passed in the targeted scope, while repository-wide coverage remains a separate gate
- `pytest tests/unit/core/test_runtime_config_governance.py::test_app_container_uses_role_aware_redis_kwargs -q`
  - functional result: `1 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because the same global threshold applies
  - interpretation: default container wiring remains behaviorally compatible in the targeted scope

### Runtime Batch 8 Follow-Up

A eighth runtime-hardening micro-batch is now also landed:

- reservation stores now support stale-record inspection through:
  - `fetch_stale(max_age_seconds)`
- `OrderManagementService` now exposes portfolio-level stale reservation detection
- the portfolio-aware pre-submit gate now supports conservative BUY blocking when:
  - stale pending BUY reservations remain unresolved for the same portfolio
- default runtime builders now bind that stale-reservation checker with a local conservative threshold:
  - `86400` seconds (`24h`)

Related artifact:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH8_STALE_RESERVATION_REVIEW_GATE_2026-04-26.md`

Targeted validation result:
- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `20 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: stale-reservation review blocking passed in the targeted scope, while repository-wide coverage remains a separate gate
- `pytest tests/unit/core/test_runtime_config_governance.py::test_app_container_uses_role_aware_redis_kwargs -q`
  - functional result: `1 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because the same global threshold applies
  - interpretation: default container wiring remains behaviorally compatible in the targeted scope

### Runtime Batch 9 Follow-Up

A ninth runtime-hardening micro-batch is now also landed:

- a dedicated trading runtime config helper now exists:
  - `src/utils/trading_runtime_config.py`
- default path resolution for:
  - trading decision audit JSONL
  - trading decision audit SQLite
  - trading cash reservation SQLite
  is now centralized instead of hardcoded in builders
- default stale reservation threshold resolution is now centralized instead of hardcoded in composition roots
- current runtime env overrides now include:
  - `TRADING_RUNTIME_DIR`
  - `TRADING_DECISION_AUDIT_JSONL_PATH`
  - `TRADING_DECISION_AUDIT_SQLITE_PATH`
  - `TRADING_CASH_RESERVATION_SQLITE_PATH`
  - `TRADING_STALE_CASH_RESERVATION_MAX_AGE_SECONDS`

Related artifact:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH9_RUNTIME_CONFIG_EXTERNALIZATION_2026-04-26.md`

Targeted validation result:
- `pytest tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: trading runtime config externalization passed in the targeted scope, while repository-wide coverage remains a separate gate
- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `20 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because the same global threshold applies
  - interpretation: previously landed trading safety runtime behavior remains intact after config externalization
- GitNexus note:
  - several impact queries for newly added or recently changed builder symbols timed out in this session, so targeted file-scope control plus focused tests were used as fallback evidence

### Runtime Batch 10 Follow-Up

A tenth runtime-hardening micro-batch is now also landed:

- a dedicated operator-facing runtime CLI now exists:
  - `scripts/runtime/trading_cash_reservations.py`
- the local reservation CLI now supports:
  - listing all reservations
  - listing stale reservations
  - optional portfolio filtering
  - explicit single-order manual release
  - `text` and `json` output
- cleanup remains intentionally manual and explicit:
  - no bulk auto-release
  - no automatic stale sanitation

Related artifact:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH10_STALE_RESERVATION_OPERATOR_TOOLING_2026-04-26.md`

Targeted validation result:
- `pytest tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `4 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: operator-facing stale reservation inspection and single-order release passed in the targeted scope
- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `20 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because the same global threshold applies
  - interpretation: previously landed trading safety runtime behavior remains intact after adding the operator CLI

### Runtime Batch 11 Follow-Up

A eleventh runtime-hardening micro-batch is now also landed:

- the reservation operator CLI now requires explicit operator identity for release:
  - `--actor-id`
- manual release actions are now durably bound to the existing local trading audit sink:
  - JSONL
  - SQLite
- both successful and unsuccessful manual release attempts now emit explicit audit outcomes:
  - `manual_reservation_release`
  - `manual_reservation_release_not_found`

Related artifact:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH11_MANUAL_RELEASE_AUDIT_TRAIL_2026-04-26.md`

Targeted validation result:
- `pytest tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `4 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: manual release audit persistence passed in the targeted scope
- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `20 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because the same global threshold applies
  - interpretation: previously landed trading safety runtime behavior remains intact after manual release audit binding

### Runtime Batch 12 Follow-Up

A twelfth runtime-hardening micro-batch is now also landed:

- the reservation release CLI no longer treats dual control as the only valid governance path
- release behavior is now risk-tiered from local ledger facts:
  - stale reservation -> `auto_release`
  - fresh reservation without explicit review path -> `review_required`
  - fresh reservation with `--allow-single-operator` -> `single_operator_with_audit`
  - fresh reservation with `--approved-by` -> `dual_control`
- same-person actor / approver combinations are still rejected when dual control is requested
- local audit records now preserve release-governance context:
  - `approval_mode`
  - `review_required`
  - `reservation_age_seconds`
  - `stale_age_seconds`
  - `approved_by`
  - `approval_note`

Related artifact:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH12_RISK_TIERED_RELEASE_GATE_2026-04-26.md`

Targeted validation result:
- `pytest tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `8 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: the release CLI now supports automatic stale release plus bounded single-operator and dual-control review paths in the targeted scope
- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `20 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because the same global threshold applies
  - interpretation: previously landed trading safety runtime behavior remains intact after the Batch 12 release-governance change

### Runtime Batch 13 Follow-Up

A thirteenth runtime-hardening micro-batch is now also landed:

- a durable local order-state evidence store now exists:
  - `InMemoryTradingOrderStateStore`
  - `SqliteTradingOrderStateStore`
- default runtime wiring now binds that store into the canonical placement path in:
  - `src/application/bootstrap.py`
  - `src/governance/risk_management/services/stop_loss_execution_service.py`
- `OrderManagementService` now records last-known local order state on:
  - successful submit
  - execution report handling
- the reservation release CLI now uses that local evidence to refine fresh reservation handling:
  - terminal local order state -> `terminal_order_state_auto_release`
  - active local order state -> `active_order_state_requires_review`
  - no local order-state evidence -> fall back to the Batch 12 policy
- local audit records now preserve order-state evidence context:
  - `order_state_status`
  - `order_state_updated_at`
  - `order_state_symbol`
  - `order_state_portfolio_id`

Related artifact:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH13_LOCAL_ORDER_STATE_EVIDENCE_2026-04-26.md`

Targeted validation result:
- `pytest tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: the release CLI now distinguishes fresh terminal local order evidence from fresh active local order evidence in the targeted scope
- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `22 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because the same global threshold applies
  - interpretation: the canonical application path now persists local order-state evidence without regressing previously landed trading safety runtime behavior
- `pytest tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because the same global threshold applies
  - interpretation: the new local order-state runtime path remains externally configurable without regressing current composition-root behavior

### Runtime Batch 14 Follow-Up

A fourteenth runtime-hardening micro-batch is now also landed:

- `OrderManagementService` now exposes local lifecycle entrypoints for:
  - `cancel_order(...)`
  - `reject_order(...)`
- the canonical application path now releases pending BUY reservations when local order status becomes terminal through:
  - `CANCELLED`
  - `REJECTED`
  - `EXPIRED`
  - `FILLED`
- the local order-state evidence store now persists additional terminal lifecycle outcomes:
  - `CANCELLED`
  - `REJECTED`
- local decision audits now distinguish post-submit lifecycle outcomes:
  - `cancelled`
  - `rejected_after_submission`

Related artifact:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH14_CANCEL_REJECT_LIFECYCLE_EVIDENCE_2026-04-26.md`

Targeted validation result:
- `pytest tests/ddd/test_phase_7_application.py -k "cancel_order or reject_order" -q`
  - functional result: `2 passed`
  - interpretation: the new cancel / reject lifecycle paths behave correctly in the narrowest targeted scope
- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `24 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: the canonical application path now persists cancel / reject terminal evidence without regressing previously landed trading safety runtime behavior
- `pytest tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because the same global threshold applies
  - interpretation: reservation-operator tooling remains behaviorally compatible after the terminal lifecycle release change
- `pytest tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because the same global threshold applies
  - interpretation: current runtime config and composition-root wiring remain compatible after the Batch 14 service change

### Runtime Batch 15 Follow-Up

A fifteenth runtime-hardening micro-batch is now also landed:

- the trading aggregate now rejects invalid local reject transitions unless the order is still in:
  - `CREATED`
  - `SUBMITTED`
- the canonical application path now refuses to rewrite local lifecycle evidence from:
  - `PARTIALLY_FILLED -> REJECTED`
  - `CANCELLED -> REJECTED`
- failed reject attempts now preserve the prior valid local evidence shape:
  - reservation state remains unchanged
  - order-state evidence remains unchanged
  - no successful `rejected_after_submission` audit is emitted for the denied path

Related artifact:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH15_REJECT_TRANSITION_GUARDS_2026-04-27.md`

Targeted validation result:
- `pytest tests/ddd/test_phase_7_application.py -k "reject_order_disallows" -q`
  - functional result: `2 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: the canonical local path now blocks invalid reject transitions in the narrowest targeted scope
- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `26 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: the reject-transition guard does not regress previously landed trading safety runtime behavior
- `pytest tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because the same global threshold applies
  - interpretation: reservation-operator tooling remains behaviorally compatible after the reject-transition guard
- `pytest tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because the same global threshold applies
  - interpretation: current runtime config and composition-root wiring remain compatible after the Batch 15 domain-state guard

### Runtime Batch 16 Follow-Up

A sixteenth runtime-hardening micro-batch is now also landed:

- the canonical application path now emits explicit denial audit outcomes when local lifecycle mutations are refused:
  - `cancel_denied`
  - `reject_denied`
- denial audit records now preserve extra local review context:
  - `requested_reason`
  - `current_order_status`
- denied local lifecycle attempts still keep the prior valid local evidence unchanged:
  - reservation state remains unchanged
  - order-state evidence remains unchanged
  - previously successful lifecycle history remains intact

Related artifact:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH16_DENIAL_AUDIT_EVIDENCE_2026-04-27.md`

Targeted validation result:
- `pytest tests/ddd/test_phase_7_application.py -k "reject_order_disallows or cancel_order_audits_denied_lifecycle_attempt" -q`
  - functional result: `3 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: invalid local cancel / reject attempts now leave explicit denial audit evidence in the narrowest targeted scope
- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `27 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: the denial-audit extension does not regress previously landed trading safety runtime behavior
- `pytest tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because the same global threshold applies
  - interpretation: reservation-operator tooling remains behaviorally compatible after the denial-audit extension
- `pytest tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because the same global threshold applies
  - interpretation: current runtime config and composition-root wiring remain compatible after the Batch 16 audit-path change

### Runtime Batch 17 Follow-Up

A seventeenth runtime-hardening micro-batch is now also landed:

- the canonical application path now emits explicit missing-order lifecycle audit outcomes for operator/runtime actions:
  - `cancel_not_found`
  - `reject_not_found`
- missing-order audit records now preserve bounded attempt context:
  - requested order id as `request_identity`
  - requested order id as `order_id`
  - `requested_reason`
- missing-order lifecycle attempts still preserve prior control-flow semantics:
  - the same `ValueError` is raised
  - no false success path is introduced

Related artifact:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH17_NOT_FOUND_LIFECYCLE_AUDIT_2026-04-27.md`

Targeted validation result:
- `pytest tests/ddd/test_phase_7_application.py -k "audits_not_found_lifecycle_attempt" -q`
  - functional result: `2 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: missing-order cancel / reject attempts now leave local audit evidence in the narrowest targeted scope
- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `29 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: the missing-order audit extension does not regress previously landed trading safety runtime behavior
- `pytest tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because the same global threshold applies
  - interpretation: reservation-operator tooling remains behaviorally compatible after the Batch 17 not-found audit change
- `pytest tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because the same global threshold applies
  - interpretation: current runtime config and composition-root wiring remain compatible after the Batch 17 not-found audit change

### Runtime Batch 18 Follow-Up

An eighteenth runtime-hardening micro-batch is now also landed:

- the canonical application path now normalizes lifecycle refusal reasons into stable machine-readable codes:
  - `order_not_found`
  - `invalid_order_status_transition`
- action-specific lifecycle audit outcomes remain unchanged:
  - `cancel_not_found`
  - `reject_not_found`
  - `cancel_denied`
  - `reject_denied`
- lifecycle refusal audit records now preserve original exception text separately as:
  - `decision_reason_detail`
- the durable sink scope remains intentionally unchanged:
  - JSONL still preserves extra payload fields
  - SQLite still preserves extra payload fields in `payload_json`

Related artifact:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH18_LIFECYCLE_REASON_TAXONOMY_2026-04-27.md`

Targeted validation result:
- `pytest tests/ddd/test_phase_7_application.py -k "audits_not_found_lifecycle_attempt or disallows_partial_fill_transition or disallows_reject_after_cancelled_terminal_state or audits_denied_lifecycle_attempt_after_filled_state" -q`
  - functional result: `5 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: denied and missing-order lifecycle audits now expose stable reason taxonomy without losing raw local evidence
- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `29 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: the reason-taxonomy normalization does not regress previously landed trading safety runtime behavior
- `pytest tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because the same global threshold applies
  - interpretation: reservation-operator tooling remains behaviorally compatible after the lifecycle reason-taxonomy change
- `pytest tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because the same global threshold applies
  - interpretation: current runtime config and composition-root wiring remain compatible after the Batch 18 normalization change

### Runtime Batch 19 Follow-Up

A nineteenth runtime-hardening micro-batch is now also landed:

- the canonical application path now emits explicit missing-order audit evidence for execution-report misses:
  - `execution_report_not_found`
- the same stable reason taxonomy from Batch 18 is now reused on this runtime entrypoint:
  - `decision_reason = order_not_found`
  - `decision_reason_detail = Order not found: ...`
- execution-report miss audit records now preserve bounded report input context:
  - `reported_filled_quantity`
  - `reported_fill_price`
- missing-order execution-report attempts still preserve prior control-flow semantics:
  - the same `ValueError` is raised
  - no false fill or synthetic order-recovery path is introduced

Related artifact:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH19_EXECUTION_REPORT_NOT_FOUND_AUDIT_2026-04-27.md`

Targeted validation result:
- `pytest tests/ddd/test_phase_7_application.py -k "handle_execution_report_audits_missing_order_attempt" -q`
  - functional result: `1 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: execution-report misses now leave bounded local audit evidence in the narrowest targeted scope
- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `30 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: the execution-report miss audit extension does not regress previously landed trading safety runtime behavior
- `pytest tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because the same global threshold applies
  - interpretation: reservation-operator tooling remains behaviorally compatible after the Batch 19 execution-report audit change
- `pytest tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because the same global threshold applies
  - interpretation: current runtime config and composition-root wiring remain compatible after the Batch 19 execution-report audit change

### Runtime Batch 20 Follow-Up

A twentieth runtime-hardening micro-batch is now also landed:

- the canonical application path now emits explicit denial audit evidence when a loaded local order rejects execution input:
  - `execution_report_denied`
- execution-report denials now reuse a bounded stable reason taxonomy instead of leaking only raw exception text:
  - `invalid_order_status_transition`
  - `fill_quantity_exceeds_remaining_quantity`
  - `invalid_fill_quantity`
- denial audit records now preserve the minimal troubleshooting payload needed for local replay analysis:
  - `current_order_status`
  - `decision_reason_detail`
  - `reported_filled_quantity`
  - `reported_fill_price`
- denied execution reports still preserve prior control-flow and state semantics:
  - the same domain exception is re-raised
  - no synthetic fill recovery path is introduced
  - local order-state evidence and cash reservation evidence remain unchanged on denied fill

Related artifact:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH20_EXECUTION_REPORT_DENIAL_AUDIT_2026-04-27.md`

Targeted validation result:
- `pytest tests/ddd/test_phase_7_application.py -k "denied_fill_after_cancelled_terminal_state or denied_overfill_attempt_and_preserves_partial_state" -q`
  - functional result: `2 passed`
  - repo-wide coverage gate still fails for this narrow test invocation because total project coverage remains below the configured global threshold
  - interpretation: denied execution reports now leave bounded local audit evidence for terminal-state fills and overfill attempts
- `pytest --no-cov tests/ddd/test_phase_7_application.py -q`
  - functional result: `32 passed`
  - interpretation: the execution-report denial audit extension does not regress the current Wave 3 trading safety application suite
- `pytest --no-cov tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - interpretation: reservation-operator tooling remains behaviorally compatible after the Batch 20 denial-audit change
- `pytest --no-cov tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - interpretation: current runtime config and composition-root wiring remain compatible after the Batch 20 denial-audit change

### Broker Batch 1 Follow-Up

Wave 3 has now also switched from local-only runtime hardening into the broker acknowledgement
and reconciliation line.

The first broker batch is documentation and governance only:

- the canonical local control anchor for later broker-truth work is explicitly locked as:
  - `src/application/trading/order_mgmt_service.py`
- non-canonical adjacent trading surfaces are explicitly classified as:
  - `stub`
  - `demo`
  - `experimental` upstream orchestration
- a dedicated broker execution truth registry now exists

Related artifacts:

- `docs/guides/quant-trading/broker-execution-truth-registry.md`
- `docs/reports/quality/Q2_WAVE3_BROKER_BATCH1_TRUTH_REGISTRY_SEED_2026-04-27.md`

Validation result:

- `openspec validate add-broker-acknowledgement-reconciliation-contract --strict`
  - result: `valid`
  - interpretation: the next-layer broker truth contract is now explicit instead of being
    implied through local runtime hardening notes

### Broker Batch 2 Follow-Up

A second broker-truth micro-batch is now also landed:

- a dedicated local broker correlation ledger now exists:
  - `src/application/trading/broker_order_correlation.py`
- the canonical application path now persists explicit awaiting-acknowledgement identity
  evidence at order placement time
- external broker order identity can now be attached later through:
  - `record_broker_acknowledgement(order_id, external_order_id=...)`
- current bounded semantics remain intentionally honest:
  - adapter path is explicit
  - account scope remains `unscoped`
  - no broker lifecycle ingestion is claimed
  - no replay suppression is introduced
  - no local order state mutation occurs during acknowledgement binding

Related artifact:

- `docs/reports/quality/Q2_WAVE3_BROKER_BATCH2_LOCAL_EXTERNAL_IDENTITY_PERSISTENCE_2026-04-28.md`

Targeted validation result:

- `pytest --no-cov tests/ddd/test_phase_7_application.py -q -k "broker_order_correlation or broker_acknowledgement"`
  - functional result: `3 passed`
  - interpretation: submission correlation creation, durable lookup, and later external-id
    binding now exist on the canonical local path
- `pytest --no-cov tests/ddd/test_phase_7_application.py -q`
  - functional result: `36 passed`
  - interpretation: Batch 2 does not regress the current Wave 3 trading-safety application suite
- `pytest --no-cov tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - interpretation: reservation-operator tooling remains compatible after correlation-ledger
    introduction
- `pytest --no-cov tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - interpretation: runtime path governance now covers the local broker-correlation ledger

### Broker Batch 3 Follow-Up

A third broker-truth micro-batch is now also landed:

- a dedicated broker lifecycle event envelope and durable local ledger now exist:
  - `src/application/trading/broker_lifecycle_event.py`
- correlation lookup now supports `local_submission_id` so acknowledgement events can bind
  broker identity before only-external matching is possible
- the canonical application path can now ingest broker lifecycle events through:
  - `record_broker_lifecycle_event(event)`
- current bounded semantics remain intentionally narrow:
  - acknowledgement events may bind external identity
  - execution/cancel/reject events are preserved as local evidence only
  - no broker event mutates local order status in this batch
  - missing identity and missing sequencing metadata are classified explicitly
  - replay suppression remains blocked

Related artifact:

- `docs/reports/quality/Q2_WAVE3_BROKER_BATCH3_LIFECYCLE_EVENT_ENVELOPE_2026-04-28.md`

Targeted validation result:

- `pytest --no-cov tests/ddd/test_phase_7_application.py -q -k "broker_lifecycle_event"`
  - functional result: `4 passed`
  - interpretation: durable broker lifecycle event persistence and bounded identity-resolution
    semantics now exist on the canonical local path
- `pytest --no-cov tests/ddd/test_phase_7_application.py -q`
  - functional result: `40 passed`
  - interpretation: Batch 3 does not regress the current Wave 3 trading-safety application suite
- `pytest --no-cov tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - interpretation: reservation-operator tooling remains compatible after lifecycle-event
    envelope introduction
- `pytest --no-cov tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - interpretation: runtime path governance now covers the broker lifecycle event ledger

### Broker Batch 4 Follow-Up

A fourth broker-truth micro-batch is now also landed:

- a dedicated durable divergence ledger now exists:
  - `src/application/trading/broker_divergence.py`
- the canonical application path can now persist review-required divergence incidents after
  broker lifecycle event ingestion
- current bounded machine-readable categories now include:
  - `awaiting_broker_acknowledgement`
  - `unmatched_external_order`
  - `locally_terminal_externally_open`
  - `externally_terminal_locally_open`
  - `quantity_or_fill_divergence`
- current bounded semantics remain intentionally narrow:
  - divergence evidence is durable and queryable
  - order state is not rewritten from broker lifecycle events in this batch
  - replay suppression remains blocked
  - automatic resolution remains deferred

Related artifact:

- `docs/reports/quality/Q2_WAVE3_BROKER_BATCH4_DIVERGENCE_LEDGER_REVIEW_SURFACE_2026-04-28.md`

Targeted validation result:

- `pytest --no-cov tests/ddd/test_phase_7_application.py -q -k "broker_divergence or unmatched_external_order_divergence or locally_terminal_externally_open_divergence or externally_terminal_locally_open_divergence or quantity_or_fill_divergence_without_mutating_local_state"`
  - functional result: `5 passed`
  - interpretation: durable review-required divergence incidents now exist on the canonical
    local path
- `pytest --no-cov tests/ddd/test_phase_7_application.py -q`
  - functional result: `45 passed`
  - interpretation: Batch 4 does not regress the current Wave 3 trading-safety application suite
- `pytest --no-cov tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `10 passed`
  - interpretation: reservation-operator tooling remains compatible after divergence evidence
    introduction
- `pytest --no-cov tests/unit/core/test_runtime_config_governance.py -q`
  - functional result: `22 passed`
  - interpretation: runtime path governance now covers the broker divergence ledger

## Next Recommended Step

Wave 3 should continue outward, not back into local-only runtime micro-fixes.

Recommended next step:
- implement `Batch 5: Bounded Auto-Resolution And Replay-Suppression Gate`
- keep replay suppression blocked until the policy names the broker-side identity or sequencing
  basis explicitly
- allow stronger behavior only for explicitly authorized divergence classes
- keep unsupported cases as durable review-required incidents

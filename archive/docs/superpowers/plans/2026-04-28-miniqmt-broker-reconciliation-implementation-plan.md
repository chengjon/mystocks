# MiniQMT Broker Reconciliation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish `miniQMT` as the first canonical broker-truth path for trading execution, while keeping Tongdaxin semi-manual trading as a supplemental operator-assisted path with explicit reconciliation boundaries.

**Architecture:** Build outward from the existing local trading anchor in `src/application/trading/order_mgmt_service.py` and its adjacent correlation, lifecycle-event, and divergence ledgers. Do not invent a second trading core. Instead, add a broker-truth registry, explicit adapter-path/account/session identity, and a two-lane reconciliation policy: `miniQMT` may evolve toward bounded auto-resolution, while Tongdaxin remains review-first unless it can emit equivalent external identity and sequencing facts.

**Tech Stack:** Python 3.12, Pydantic v2, repository-local SQLite ledgers, existing application-layer trading services, Windows bridge provider integration for `qmt`, OpenSpec change `add-broker-acknowledgement-reconciliation-contract`.

---

## Current Anchors

- Canonical local anchor: `src/application/trading/order_mgmt_service.py`
- Local-to-external correlation ledger: `src/application/trading/broker_order_correlation.py`
- Broker lifecycle event envelope and ledger: `src/application/trading/broker_lifecycle_event.py`
- Divergence incident ledger: `src/application/trading/broker_divergence.py`
- Governance registry: `docs/guides/quant-trading/broker-execution-truth-registry.md`
- Current OpenSpec contract: `openspec/changes/add-broker-acknowledgement-reconciliation-contract/`
- Existing Windows bridge surface for `qmt`: `web/backend/app/services/windows_bridge_adapter.py`

## Target Operating Model

### Truth Registry

| Path | Role | Truth Level | Default Reconciliation Policy |
| --- | --- | --- | --- |
| `miniQMT` via Windows bridge / dedicated broker adapter | Primary automated execution path | canonical broker-truth candidate | correlation required, lifecycle ledger required, divergence policy may later allow bounded auto-resolution |
| Tongdaxin semi-manual execution | Supplemental operator-assisted path | non-canonical supplemental truth | correlation required, lifecycle capture best effort, divergence stays review-required by default |
| Upstream strategy/runtime orchestrators | local orchestration only | non-truth | never mutate broker-truth state directly |

### Required Correlation Fields

Every broker-facing submission record must preserve:

- `local_order_id`
- `local_submission_id`
- `adapter_path`
- `broker_channel`
- `account_scope`
- `session_scope`
- `acknowledgement_status`
- `external_order_id` when available
- `source_name`

Recommended `broker_channel` enum for the first batch:

- `miniqmt`
- `tdx_manual`

### Required Lifecycle Event Fields

Every ingested broker event must preserve:

- `event_type`
- `source_timestamp`
- `source_name`
- `external_order_id` when available
- `local_submission_id` when available
- `local_order_id` when available
- `event_id` when available
- `sequence_id` when available
- `reason_code` / `reason_detail` when applicable
- `fill_quantity` / `fill_price` when applicable

## State Machine Boundaries

### Local Order State

Local order state remains centered on the existing domain statuses:

- `created`
- `submitted`
- `partially_filled`
- `filled`
- `cancelled`
- `rejected`
- `expired`

### Broker-Truth Overlay State

Broker-truth handling should be modeled as an overlay, not as a second replacement order state machine:

- `awaiting_broker_acknowledgement`
- `acknowledged`
- `lifecycle_event_recorded`
- `divergence_review_required`
- `auto_resolved` for explicitly allowed `miniQMT` cases only

### Hard Boundaries

- Do not treat local submission success as broker acknowledgement.
- Do not allow replay suppression unless external identity or sequence evidence exists.
- Do not auto-match unmatched external executions by price and quantity coincidence alone.
- Do not allow Tongdaxin supplemental events to overwrite local state automatically unless that path later proves stable external identity and sequencing.
- Do not let one local order fan out across both `miniQMT` and Tongdaxin without an explicit operator decision and separate correlation trail.

## Execution Policy by Channel

### MiniQMT Primary Path

- `miniQMT` is the intended first canonical broker-truth path.
- A successful broker submission must either:
  - keep the order in `awaiting_broker_acknowledgement`, or
  - bind `external_order_id` immediately if the provider emits it synchronously.
- Subsequent `acknowledgement`, `reject`, `cancel`, and `execution` events must resolve through the correlation ledger before any stronger lifecycle claim is made.
- Only after stable event identity and sequencing are verified should `miniQMT` become eligible for bounded auto-resolution or replay suppression.

### Tongdaxin Supplemental Path

- Tongdaxin remains a valid supplemental execution surface.
- Its default role is operator-assisted execution, not canonical broker truth.
- If it can emit stable external order identifiers, it may share the same correlation and lifecycle ledger formats.
- Until that proof exists, every Tongdaxin-originated divergence should remain `review_required`.
- Tongdaxin should never silently inherit `miniQMT` replay or auto-resolution privileges.

## OpenSpec Closure Path

### Batch 1: Registry and Vocabulary Closure

- [ ] Update `docs/guides/quant-trading/broker-execution-truth-registry.md` to name `miniQMT` as the first canonical broker-truth candidate.
- [ ] Register Tongdaxin as `supplemental/operator-assisted`, not as equivalent canonical truth.
- [ ] Add `broker_channel` vocabulary and channel-specific policy statements to the active OpenSpec change if current deltas do not already make the distinction explicit.

### Batch 2: Correlation Ledger Expansion

- [ ] Extend correlation records to preserve `broker_channel`, concrete `adapter_path`, `account_scope`, and `session_scope` for both channels.
- [ ] Ensure a `miniQMT` submission and a Tongdaxin submission cannot collide in identity space.
- [ ] Add durable tests covering per-channel correlation binding and acknowledgement transition.

### Batch 3: MiniQMT Event Ingestion

- [ ] Introduce the first verified `miniQMT` broker-facing ingestion surface, likely behind the existing Windows bridge or a dedicated adapter.
- [ ] Convert provider payloads into `BrokerLifecycleEvent`.
- [ ] Record acknowledgement, reject, cancel, and execution events into the lifecycle ledger before any downstream mutation claims.

### Batch 4: Tongdaxin Supplemental Ingestion

- [ ] Add a separate supplemental ingestion path for Tongdaxin manual or semi-manual events.
- [ ] Persist whatever identity fields are available without overstating truth strength.
- [ ] Force unmatched or weak-identity incidents into divergence review instead of automatic mutation.

### Batch 5: Divergence Policy Enforcement

- [ ] Keep the current stable divergence categories as the minimum baseline.
- [ ] Add channel-aware review policy:
  - `miniQMT`: eligible for future bounded auto-resolution once evidence is strong enough.
  - `tdx_manual`: review-required by default.
- [ ] Add audit fields that make the chosen resolution authority explicit.

### Batch 6: Verification and Governance Closure

- [ ] Add or extend DDD tests for both channels, including unmatched external execution, externally terminal locally open, and quantity/fill divergence.
- [ ] Update `docs/FUNCTION_TREE.md` under `05-投资组合与交易` to reflect the new broker-truth boundary and channel roles.
- [ ] Close the relevant OpenSpec tasks only after current repo truth proves:
  - registry updated
  - per-channel correlation exists
  - lifecycle ingestion exists
  - divergence review boundary is enforced

## Acceptance Rules

The work should only be considered meaningfully closed when all of the following are true:

- `miniQMT` is explicitly named as the primary broker-truth path in the registry and docs.
- Tongdaxin is explicitly named as supplemental/operator-assisted unless stronger evidence exists.
- One local order can be traced to one broker-facing correlation record without cross-channel ambiguity.
- Broker lifecycle events are durably recorded before reconciliation claims are made.
- Divergence incidents record owner, next action, and required evidence.
- Any auto-resolution rule is limited to channel-specific, evidence-backed cases and is auditable.

## Not In Scope for the First Closeout

- Full production-readiness certification for live trading
- Exactly-once distributed delivery semantics
- Multi-broker smart routing across channels
- Automatic Tongdaxin truth promotion without identity proof
- Replacing the existing local trading application core

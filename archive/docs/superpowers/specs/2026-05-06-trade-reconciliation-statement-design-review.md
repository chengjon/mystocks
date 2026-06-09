# Review: 2026-05-06-trade-reconciliation-statement-design.md

**Type**: md / spec (design specification) | **Perspective**: auto | **Date**: 2026-05-06

## Summary

Well-scoped design for a trade reconciliation statement feature targeting FUNCTION_TREE `5.2 对账单`. All referenced existing files exist, scope boundaries are disciplined, and the matching model is sound. The critical gap: the design ignores `src/application/trading/broker_reconciliation.py` (500+ lines of existing broker-lifecycle reconciliation) and the OpenSpec `add-broker-acknowledgement-reconciliation-contract` capability, creating a naming collision that will confuse implementers. Several contract details are underspecified.

## Verified

- A1 Component boundaries: History.vue stays trade-history; Reconciliation.vue is a dedicated new page. Backend extends trade route family.
- A3 Coupling: Reconciliation imports from CSV and matches against internal truth; no coupling to execution tracking.
- A5 Scalability: One-to-one matching is bounded; future broker adapters normalize to same `BrokerStatementRow`.
- A7 Backward compatibility: No changes to existing endpoints; additive-only design.
- A9 Named entities: `History.vue` exists, `routes.py` exists, `Reconciliation.vue` correctly marked as proposed. `UnifiedResponse` confirmed in both backend (`web/backend/app/core/responses.py`) and frontend (`web/frontend/src/types/unified-api.ts`).
- C1 Required sections: All expected sections present (Context, Goals, Non-Goals, Data Contract, Matching, Testing, Governance, Risks).
- C4 Acceptance criteria: Governance Closeout section provides verifiable closeout checklist; e2e steps are concrete.
- N1-N5 Consistency: Terminology, naming, formatting, and style are internally consistent.
- F1 Technical risk: Deterministic matching is low-risk; miniQMT parser scoped to fixed header mapping.
- F2 Dependencies: No new external dependencies; CSV parsing uses stdlib.
- F5 Rollback: Additive-only design; reverting means removing new endpoints and page.

## Issues

- [ ] **[HIGH]** Existing `broker_reconciliation.py` module not acknowledged — Context, Capability Boundary
      Evidence: `src/application/trading/broker_reconciliation.py` (500+ lines) already implements broker-lifecycle reconciliation with matched/unmatched identities, divergence categories, and auto-resolution. OpenSpec `add-broker-acknowledgement-reconciliation-contract` also exists. This design proposes a different "reconciliation" (trade-statement CSV matching) using the same term with no documented relationship.

- [ ] **[MED]** Internal statement data source unspecified — Data Contract: InternalStatementRow
      Evidence: Doc says "derived from current trade-domain history sources" without naming the source. Current `/trades` endpoint (routes.py:641) uses `symbol` + date range, not `account_id` + `trade_time` range. The `account_id` field in `InternalStatementRow` has no existing query path.

- [ ] **[MED]** Endpoint contracts underspecified — Backend Contract: Endpoints
      Evidence: 5 endpoints listed with single-line descriptions but no request/response schemas, error codes, file upload mechanics for `POST /import`, or response headers for `GET /export`.

- [ ] **[MED]** Implementation surface not decomposed into files — Backend Contract, Capability Boundary
      Evidence: `web/backend/app/api/trade/routes.py` is already 740+ lines. Adding 5 reconciliation endpoints without file decomposition would approach the project's 800-line limit (STANDARDS.md). Doc does not specify whether new routes go into existing file or separate module.

- [ ] **[MED]** Time tolerance threshold unspecified — Matching Rules: Time tolerance
      Evidence: Line 218: "small normalization tolerance" with no concrete value. Matching priority 2 uses `trade_time` as a key, so implementer must guess the tolerance.

- [ ] **[MED]** Multi-account support assumes account model that may not exist — Frontend Design: Primary controls, Data Contract
      Evidence: Design proposes account switcher as first control. Current `/trades` endpoint has no `account_id` parameter. No account model found in existing trade routes. Either account model creation should be in scope, or multi-account should be deferred.

- [ ] **[LOW]** `InternalStatementRow` and `BrokerStatementRow` share 10 identical fields but no base model — Data Contract
      Evidence: Both models contain `account_id`, `trade_id`, `order_id`, `symbol`, `direction`, `trade_time`, `price`, `quantity`, `amount`, `commission`. A shared base would prevent field drift.

- [ ] **[LOW]** Export response headers unspecified — Export Rules
      Evidence: `GET /api/trade/reconciliation/export` returns CSV but no mention of `Content-Type: text/csv` or `Content-Disposition: attachment`.

- [ ] **[LOW]** Unrecognized `source_type` error behavior undefined — CSV Import Model
      Evidence: Import endpoint accepts "a declared source type" but does not specify what happens for unrecognized types. Should return `422` with valid source types listed.

## Suggestions

- Add a "Relationship to Existing Reconciliation Code" subsection distinguishing trade-statement CSV matching from `broker_reconciliation.py` runtime lifecycle correlation. Consider renaming the module to `trade_statement_matching` or `statement_reconciliation` to avoid collision.
- Specify the internal statement data source: name the query path, confirm `account_id` filtering is available, and document any required data model changes.
- Add a file decomposition subsection mapping each responsibility to a file path (e.g., `reconciliation_routes.py`, `reconciliation_models.py`, `services/reconciliation/matcher.py`, `services/reconciliation/parsers/`).
- Lock the time tolerance value (e.g., "timestamps normalized to whole seconds; matches require exact equality after normalization").
- Expand endpoint contracts with request parameters, response shapes, and error codes consistent with existing `UnifiedResponse` patterns.

## Verdict

**NEEDS_REVISION** -- Must resolve the existing `broker_reconciliation.py` naming collision and specify the internal statement data source before implementation can proceed. File decomposition is needed to avoid bloating `routes.py`. The medium items (endpoint contracts, time tolerance, account model) should also be addressed for deterministic acceptance testing.

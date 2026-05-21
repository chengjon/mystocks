# Design: Backend Route/OpenAPI Governance Refresh

## Context

The backend route surface is now healthy enough for governance work: `app.main`
imports, route table generation is available, OpenAPI generation reports no
duplicate operationIds, and probe consumers have a current evidence matrix.

The same evidence also shows that route governance should not be collapsed into
a single implementation batch. The route surface contains multiple categories:

- Business API routes.
- Trading-owned and trading-adjacent routes.
- Control-plane routes such as health, readiness, metrics, status, OpenAPI
  docs, and probe-facing endpoints.
- Backup and recovery routes that need a dedicated ownership proposal.
- Runtime-only compatibility routes that may be hidden from OpenAPI.
- Schema-visible routes whose docs and consumer contract require review before
  mutation.

## Decision

Create `refresh-backend-route-openapi-governance` as a proposal-only OpenSpec
change. Its job is to classify ownership, evidence freshness, schema exposure,
and consumer impact before any route/OpenAPI mutation is authorized.

## Governance Rules

1. Evidence must be current-head or explicitly marked stale.
2. Route ownership must be classified before route mutation.
3. OpenAPI exposure must be treated separately from runtime route existence.
4. Compatibility states must be explicit:
   - active and documented
   - runtime-only and hidden from schema
   - retired by a later approved change
5. Trading route governance belongs under unified route/OpenAPI governance, not
   a trading-only implementation lane.
6. Backup route ownership remains a dedicated D2.4 candidate.
7. Control-plane docs/probe stabilization remains a dedicated D2.5 candidate.
8. PM2 stateful workflow execution remains a D2.6 approval-only gate.

## Evidence Model

Each accepted evidence packet must record:

- artifact path
- generated timestamp, if available
- captured git head
- current head checked at review
- stale-if-head-mismatch policy
- route table count
- OpenAPI path and operation counts
- duplicate operationId count
- warning count
- probe matrix scope
- consumer categories
- explicit note when a route exists at runtime but is hidden from schema

## Workstream Shape

### F1 Current-Head Evidence Refresh

Refresh route table, OpenAPI snapshot, duplicate operationId warnings, and probe
consumer matrix against the branch being reviewed.

### F2 Ownership Classification

Classify route candidates into business, trading-owned, trading-adjacent,
control-plane, backup, compatibility, and unknown. The D2.3 trading package is
input evidence, not automatic ownership truth.

### F3 OpenAPI Exposure Policy

Classify each route or route group as schema-visible, runtime-only hidden from
schema, intentionally absent, or retired by a later approved change.

### F4 Consumer Contract Matrix

For any route group considered for later mutation, record consumer path, query
parameter, response shape, caller parser, OpenAPI example, and minimum
regression-test expectations.

### F5 Decision Split

After evidence is accepted, decide whether each follow-up belongs in:

- a narrow route/OpenAPI implementation issue
- D2.4 backup route ownership
- D2.5 control-plane OpenAPI docs stabilization
- D2.6 PM2 stateful gate approval
- no action

## Rollback

Because this change is proposal-only, rollback is a documentation revert. Any
future route mutation must have its own rollback plan in a separate approved
implementation lane.

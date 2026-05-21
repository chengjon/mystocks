# Change: Refresh Backend Route/OpenAPI Governance

## Why

Issue `#92` accepted the downstream decision split and folded trading route
ownership into the unified route/OpenAPI governance track. The D2.3 planning
package and the refreshed route/OpenAPI/probe evidence now show that route
governance has enough current-head evidence to become an explicit OpenSpec
change, but not enough authority to mutate runtime routes or OpenAPI exposure.

Current evidence records:

- Runtime route table: `548` routes.
- OpenAPI snapshot: `500` paths, `536` operations, duplicate operationIds `0`.
- Probe consumer matrix: `5782` scanned files, `188` hit files, `611` hit lines.
- Trading route governance candidates: `41` runtime routes across core trade,
  runtime trading, TradingView/widget, v1 trading, and one trading-adjacent
  advanced-analysis endpoint.
- Control-plane duplicate route taxonomy item: `/metrics` GET exists both as a
  hidden runtime route and as a schema-visible exporter route.

Without a dedicated governance change, later workers can confuse evidence
refresh with permission to move routes, hide schema paths, rewrite probes, or
open trading-specific implementation lanes. This change turns the route/OpenAPI
governance lane into an explicit approval and classification gate.

## What Changes

- Add an architecture-governance requirement that route/OpenAPI taxonomy and
  evidence acceptance must precede route mutation.
- Define the route governance work as evidence-first and proposal-only until a
  later approved implementation issue or change explicitly authorizes runtime
  edits.
- Require route ownership classification for trading, trading-adjacent,
  control-plane, backup, compatibility, and schema-exposure cases.
- Require current-head freshness metadata for route table, OpenAPI, and probe
  consumer evidence before using those artifacts as decision input.
- Preserve D2.4 backup route ownership, D2.5 control-plane OpenAPI docs
  stabilization, and D2.6 PM2 stateful gate as separate lanes unless a later
  approved decision explicitly folds a subset into this change.

## Non-Goals

- No backend source, frontend source, test, generated client, or runtime
  behavior changes.
- No route path, method, prefix, router registration, operationId,
  `include_in_schema`, response contract, or probe URL changes.
- No deletion or retirement of compatibility wrappers or shim routes.
- No trading-only implementation issue creation.
- No movement of issue `#92` to `ready-for-agent`.
- No PM2 stateful workflow execution.

## Impact

- Affected spec: `architecture-governance`.
- Primary inputs:
  - `docs/reports/quality/backend-trading-route-openapi-governance-planning-package-2026-05-21.md`
  - `docs/reports/quality/backend-route-openapi-probe-refresh-2026-05-20.md`
  - `docs/reports/quality/backend-route-openapi-probe-refresh-2026-05-20-review.md`
  - `docs/reports/quality/backend-openspec-issue92-next-child-lane-selection-2026-05-21.md`
  - `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- New artifacts prepared by this PR:
  - `openspec/changes/refresh-backend-route-openapi-governance/`
  - `docs/reports/quality/backend-route-openapi-governance-openspec-proposal-2026-05-21.md`
  - `governance/mainline/task-cards/pr-116.yaml`

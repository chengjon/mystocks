# Change: Stabilize Backend Control-Plane OpenAPI Docs

## Why

D2.5 identified a residual control-plane documentation and probe governance
lane after health/status consolidation, route/OpenAPI refresh, D2.3 trading
route planning, and D2.4 backup route ownership planning.

Current evidence shows the backend route surface is stable enough for a
proposal, but not authorized for mutation:

- Runtime routes: `548`.
- OpenAPI paths: `500`.
- Broad control/status candidate routes: `128`.
- Broad control/status schema-exposed routes: `124`.
- Broad control/status hidden routes: `4`.
- Focused control-plane duplicate operationIds: `0`.
- `/health/readiness` is intentionally absent.
- `/metrics` GET is a duplicate runtime path/method across one hidden runtime
  route and one schema-visible exporter route.

Control-plane endpoints do not always follow ordinary business API flow. They
serve CI, PM2, runtime liveness/readiness, observability, frontend smoke,
OpenAPI docs, schema retrieval, and compatibility consumers. A dedicated
proposal is needed before docs/API changes, probe rewrites, route exposure
changes, or endpoint retirement are considered.

## What Changes

- Add an API documentation requirement for control-plane OpenAPI documentation
  stabilization.
- Require a current-head route table, OpenAPI snapshot, and probe consumer
  matrix before using control-plane documentation evidence.
- Require an explicit taxonomy for liveness, readiness, service health,
  detailed health, status summary, metrics scrape, docs UI, schema retrieval,
  and runtime-only compatibility routes.
- Preserve `/health/readiness` as intentionally absent unless a later approved
  change says otherwise.
- Require `/metrics` GET to be documented as a control-plane taxonomy item
  before any route registration or schema exposure change.
- Keep backup/recovery route ownership in D2.4 and route/OpenAPI mutation in
  D2.3/F unless a later approved decision explicitly narrows the scope.

## Non-Goals

- No backend source, frontend source, test, generated client, docs/API, or
  runtime behavior changes.
- No route path, route registration, alias, operationId, response contract,
  probe URL, OpenAPI docs UI route, OpenAPI schema route, or
  `include_in_schema` changes.
- No adding `/health/readiness`.
- No retiring `/api/health/ready`.
- No changing `/metrics` runtime registration.
- No PM2 stateful workflow execution.
- No movement of issue `#92` to `ready-for-agent`.

## Impact

- Affected spec: `api-documentation`.
- Primary inputs:
  - `docs/reports/quality/backend-control-plane-openapi-docs-planning-package-2026-05-21.md`
  - `docs/reports/quality/backend-route-openapi-probe-refresh-2026-05-20.md`
  - `docs/reports/quality/backend-route-openapi-probe-refresh-2026-05-20-review.md`
  - `docs/reports/quality/backend-route-openapi-governance-openspec-proposal-2026-05-21.md`
  - `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- New artifacts prepared by this PR:
  - `openspec/changes/stabilize-backend-control-plane-openapi-docs/`
  - `docs/reports/quality/backend-control-plane-openapi-docs-openspec-proposal-2026-05-21.md`
  - `governance/mainline/task-cards/pr-117.yaml`

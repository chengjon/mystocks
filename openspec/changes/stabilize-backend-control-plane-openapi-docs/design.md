# Design: Control-Plane OpenAPI Docs Stabilization

## Context

Control-plane endpoints are not ordinary business routes. They are consumed by
deployment checks, PM2 workflows, CI, frontend smoke tests, monitoring, docs UI,
OpenAPI schema retrieval, and compatibility clients. Several surfaces are
runtime-only or intentionally hidden from operation schema.

The D2.5 planning package records a focused taxonomy that includes:

- `GET /health` as platform liveness.
- `GET /health/ready` as canonical readiness.
- `GET /api/health/ready` as compatibility readiness.
- `/health/readiness` as intentionally absent.
- `GET /api/health/services` as service-health contract surface.
- `GET /api/health/detailed` as diagnostic health surface.
- `GET /api/status` as status summary.
- `GET /metrics` as a duplicate runtime path/method requiring docs taxonomy.
- `/api/docs`, `/api/redoc`, and `/openapi.json` as docs/schema surfaces, not
  business API operations.
- `/api/strategy-mgmt/{path:path}` as runtime-only hidden compatibility route.

## Decision

Create `stabilize-backend-control-plane-openapi-docs` as a proposal-only
OpenSpec change. It authorizes documentation and evidence planning only. It
does not authorize docs/API edits or runtime route changes by itself.

## Documentation Model

Each accepted control-plane documentation packet must record:

- route class
- method and path, or intentionally absent path
- endpoint module and operation name when applicable
- runtime existence
- `include_in_schema` state
- OpenAPI schema exposure state
- probe consumer categories
- compatibility state
- whether the endpoint is a platform probe, diagnostics surface, docs/schema
  surface, metrics scrape surface, or business-domain health/status endpoint

## Workstream Shape

### CP1 Evidence Freshness

Refresh route table, OpenAPI snapshot, duplicate operationId warnings, and probe
consumer matrix before changing documentation or probe contracts.

### CP2 Taxonomy

Classify liveness, readiness, service health, detailed health, status, metrics,
OpenAPI docs UI, schema retrieval, and runtime-only compatibility endpoints.

### CP3 Documentation Acceptance

Prepare a docs/API implementation packet only after taxonomy is accepted. That
packet must list exact docs/API files, wording boundaries, examples, consumer
matrix evidence, and rollback plan.

### CP4 Explicit Exclusions

Keep backup/recovery route ownership in D2.4. Keep route mutation and schema
exposure changes in D2.3/F. Keep PM2 stateful execution in D2.6.

## Rollback

This proposal is rollback-safe by revert. Any later documentation or route
implementation must provide its own rollback plan.

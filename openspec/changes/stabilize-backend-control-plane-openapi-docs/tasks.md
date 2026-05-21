# Tasks: Stabilize Backend Control-Plane OpenAPI Docs

## 0. Proposal Preparation

- [x] Create OpenSpec proposal, design note, task list, and API documentation
  spec delta.
- [x] Link D2.5 planning package, route/OpenAPI/probe refresh evidence, D2.3
  route governance proposal, and steward tree context.
- [x] Keep this change proposal-only and explicitly exclude backend source,
  route behavior, OpenAPI schema, docs/API, generated client, probe, PM2, and
  test edits.
- [x] Obtain human approval for this OpenSpec change before starting the
  execution tasks below.
  Approval recorded in the current review thread at
  `2026-05-22T00:32:45+08:00`; scope is governance/evidence tasks only and
  does not authorize implementation, docs/API edits, route behavior, OpenAPI
  schema/exposure, generated client, probe URL, PM2, source, or test changes.

## 1. Evidence Freshness Gate

- [ ] Refresh FastAPI route table and record route count, endpoint module,
  method, path, operation name, and `include_in_schema`.
- [ ] Refresh `app.openapi()` and record path count, operation count, schema
  count, duplicate operationId warnings, warning count, generated timestamp,
  git head, and stale-if-head-mismatch policy.
- [ ] Refresh probe consumer matrix for GitHub workflows, config, scripts, PM2,
  Docker/package config, frontend smoke references, and approved docs/schema
  consumers.
- [ ] Stop and return to review if `app.main` import, route table generation, or
  OpenAPI generation fails.

## 2. Control-Plane Taxonomy

- [ ] Classify `GET /health` as platform liveness.
- [ ] Classify `GET /health/ready` as canonical readiness.
- [ ] Classify `GET /api/health/ready` as compatibility readiness and retain
  consumer matrix evidence before any retirement discussion.
- [ ] Keep `/health/readiness` documented as intentionally absent unless a later
  approved change explicitly creates it.
- [ ] Classify `GET /api/health/services` as service-health contract surface.
- [ ] Classify `GET /api/health/detailed` as diagnostic health surface, not a
  platform liveness probe.
- [ ] Classify `GET /api/status` as status summary.
- [ ] Classify `GET /metrics` duplicate runtime path/method as a control-plane
  metrics scrape taxonomy item before any route registration or schema exposure
  change.
- [ ] Classify `/api/docs`, `/api/redoc`, and `/openapi.json` as docs/schema
  surfaces, not business API operations.
- [ ] Classify `/api/strategy-mgmt/{path:path}` as runtime-only hidden
  compatibility route when it is present at runtime and hidden from OpenAPI.

## 3. Documentation Decision Package

- [ ] Produce a docs/API implementation decision package with exact target files,
  proposed wording categories, examples, consumer matrix evidence, verification
  commands, rollback plan, and non-goals.
- [ ] Keep backup/recovery routes in D2.4 unless an approved decision narrows a
  control-plane docs subset.
- [ ] Keep route mutation, schema exposure changes, operationId changes, and
  response contract changes in D2.3/F unless an approved implementation lane
  explicitly narrows the scope.
- [ ] Keep PM2 stateful workflow execution in D2.6.

## 4. Steward Tree

- [ ] Update the codebase-map task tree after the control-plane docs decision
  package is reviewed.
- [ ] Do not create implementation issues or edit docs/API until the accepted
  decision package identifies the owner, write scope, checks, and rollback plan.

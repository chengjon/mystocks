# Tasks: Define Backend Backup Route Ownership

## 0. Proposal Preparation

- [x] Create OpenSpec proposal, design note, task list, and architecture
  governance spec delta.
- [x] Link D2.4 planning package, route/OpenAPI/probe refresh evidence, D2.3
  route governance proposal, D2.5 control-plane docs proposal, and steward tree
  context.
- [x] Keep this change proposal-only and explicitly exclude backend source,
  route behavior, OpenAPI schema, docs/API, generated client, probe, PM2, and
  test edits.
- [x] Obtain human approval for this OpenSpec change before starting the
  execution tasks below.
  Approval recorded in the current review thread at
  `2026-05-22T00:32:45+08:00`; scope is governance/evidence tasks only and
  does not authorize implementation, backup route behavior, OpenAPI schema,
  docs/API, generated client, probe URL, PM2, source, infrastructure, or test
  changes.

## 1. Evidence Freshness Gate

- [x] Refresh FastAPI route table and record backup candidate route count,
  endpoint module, method, path, operation name, and `include_in_schema`.
- [x] Refresh `app.openapi()` and record backup OpenAPI path count, operation
  count, warnings, duplicate operationIds, generated timestamp, git head, and
  stale-if-head-mismatch policy.
- [x] Refresh consumer matrix covering frontend, backend, tests, scripts, PM2,
  Docker, CI, docs, and generated artifacts.
- [x] Stop and return to review if `app.main` import, route table generation, or
  OpenAPI generation fails.
  Current evidence package passed all three gates; no stop condition triggered.

## 2. Backup Ownership Taxonomy

- [x] Classify backup execution routes under `/api/backup-recovery/backup/*`.
- [x] Classify backup listing route `/api/backup-recovery/backups`.
- [x] Classify recovery execution routes under `/api/backup-recovery/recovery/*`
  as destructive restore surfaces.
- [x] Classify scheduler control routes under `/api/backup-recovery/scheduler/*`
  as operational control surfaces.
- [x] Classify integrity verification route
  `/api/backup-recovery/integrity/verify/{backup_id}`.
- [x] Classify cleanup and health routes:
  `/api/backup-recovery/cleanup/old-backups` and
  `/api/backup-recovery/health`.
- [x] Decide whether `/api/backup-recovery/health` belongs to service health,
  backup ownership, or control-plane docs before any route or docs/API change.
- [x] Record explicit ownership of `cleanup_old_backups.py`,
  `cleanup_old_backups`, and `backup_service_health`.

## 3. Safety and Contract Matrix

- [x] Record auth dependency, admin permission, security logging, rate-limit,
  audit, rollback, and restore-safety expectations for each ownership class.
- [x] Record request body, query/path parameters, response shape, caller parser
  expectations, OpenAPI examples, and minimum regression checks for each route
  group.
- [x] Distinguish active route consumers from historical `.backup` files,
  archived reports, infrastructure backup code, and generated artifacts.

## 4. Decision Package

- [x] Produce a backup route ownership decision package with exact future write
  scopes, owner, implementation lane, tests, and rollback plan.
- [x] Keep D2.3 route/OpenAPI mutation, D2.5 control-plane docs stabilization,
  and D2.6 PM2 stateful execution separate unless an approved decision narrows a
  specific overlap.
- [x] Update the codebase-map task tree after the decision package is reviewed.
- [x] Do not create implementation issues or edit source until the accepted
  decision package identifies the lane, owner, write scope, tests, and rollback
  plan.

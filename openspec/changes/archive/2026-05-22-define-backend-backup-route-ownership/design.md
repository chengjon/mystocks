# Design: Backend Backup Route Ownership

## Context

Backup and recovery routes are high-risk operational surfaces. They include
backup execution, recovery execution, scheduler control, integrity verification,
cleanup, and health checks. Some operations can be destructive or stateful and
therefore need a stronger ownership and permission model than ordinary route
cleanup.

The D2.4 planning package identifies these ownership classes:

- backup execution: `/api/backup-recovery/backup/*`
- backup listing: `/api/backup-recovery/backups`
- recovery execution: `/api/backup-recovery/recovery/*`
- scheduler control: `/api/backup-recovery/scheduler/*`
- integrity verification: `/api/backup-recovery/integrity/verify/{backup_id}`
- cleanup and health:
  `/api/backup-recovery/cleanup/old-backups` and `/api/backup-recovery/health`

## Decision

Create `define-backend-backup-route-ownership` as a proposal-only OpenSpec
change. It defines the ownership and evidence gate before any backup route
mutation, docs/API edit, schema exposure change, or implementation issue is
opened.

## Evidence Model

Each accepted backup route ownership packet must record:

- route class
- endpoint module
- method and path
- operation name
- `include_in_schema` state
- OpenAPI path and operation counts
- duplicate operationId count
- frontend, backend, test, script, PM2, Docker, CI, and docs consumers
- auth dependency and admin permission behavior
- audit/logging expectations
- stateful/destructive risk level
- rollback and restore safety expectations

## Ownership Boundaries

Backup route ownership must distinguish:

- backup/recovery orchestration from route wrapper code
- cleanup routes from backup execution routes
- `backup_service_health` from platform liveness/readiness
- historical `.backup` files from active route consumers
- infrastructure backup code from route ownership unless an approved proposal
  explicitly includes it

## Rollback

This proposal is rollback-safe by revert. Any future backup route implementation
must include its own rollback plan, including stateful operation protections and
restore safety checks.

# Change: Define Backend Backup Route Ownership

## Why

Issue `#92` accepted backup route ownership as a dedicated downstream proposal
candidate. The D2.4 planning package confirms that backup routes should not be
folded into general route cleanup, trading route governance, or control-plane
docs stabilization.

Current evidence records:

- Runtime routes: `548`.
- OpenAPI paths: `500`.
- Backup candidate routes: `13`.
- Backup schema-exposed routes: `13`.
- Backup OpenAPI paths: `13`.
- Backup OpenAPI operations: `13`.
- Backup duplicate operationIds: `0`.
- `cleanup_old_backups.py` owns cleanup plus backup health routes and needs an
  explicit ownership decision before any route movement or deletion discussion.

Backup and recovery endpoints include stateful and potentially destructive
surfaces. They require an ownership proposal before any module move, route path
change, schema exposure change, consumer rewrite, or cleanup/retirement work.

## What Changes

- Add an architecture governance requirement for backup route ownership and
  mutation gates.
- Require backup route candidates to be classified by ownership class before
  implementation work begins.
- Require explicit ownership of `cleanup_old_backups.py` and
  `backup_service_health`.
- Require security, permission, audit, rollback, consumer, and OpenAPI evidence
  before any backup route mutation.
- Keep D2.3 route/OpenAPI governance and D2.5 control-plane docs stabilization
  separate unless a later approved decision narrows a specific overlap.

## Non-Goals

- No backend source, frontend source, test, generated client, docs/API, or
  runtime behavior changes.
- No moving backup route modules.
- No renaming, adding, retiring, or hiding backup paths.
- No `include_in_schema`, operationId, response contract, probe URL, or OpenAPI
  schema changes.
- No editing `src/infrastructure/backup_recovery/**`.
- No broad backup implementation issue creation.
- No PM2 stateful workflow execution.
- No movement of issue `#92` to `ready-for-agent`.

## Impact

- Affected spec: `architecture-governance`.
- Primary inputs:
  - `docs/reports/quality/backend-backup-route-ownership-planning-package-2026-05-21.md`
  - `docs/reports/quality/backend-route-openapi-probe-refresh-2026-05-20.md`
  - `docs/reports/quality/backend-route-openapi-governance-openspec-proposal-2026-05-21.md`
  - `docs/reports/quality/backend-control-plane-openapi-docs-openspec-proposal-2026-05-21.md`
  - `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- New artifacts prepared by this PR:
  - `openspec/changes/define-backend-backup-route-ownership/`
  - `docs/reports/quality/backend-backup-route-ownership-openspec-proposal-2026-05-21.md`
  - `governance/mainline/task-cards/pr-118.yaml`

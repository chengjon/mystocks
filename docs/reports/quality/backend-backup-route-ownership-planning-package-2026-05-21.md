# Backend Backup Route Ownership Planning Package

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

- Date: 2026-05-21
- Status: D2.4 planning package prepared; no route implementation authorized
- Parent issue: <https://github.com/chengjon/mystocks/issues/92>
- Track: D2.4 backup route ownership dedicated proposal candidate
- Base HEAD: `553e71a90c833a3f9a2ffbec2342d67816baa2ad`
- Prepared at: `2026-05-21T04:18:21Z`

## Boundary

This package is planning and evidence only.

It does not modify backend route modules, does not change route registration,
does not change OpenAPI schema exposure, does not edit frontend consumers, does
not edit tests, does not create or modify OpenSpec change/spec files, does not
run PM2, and does not move issue `#92` or any downstream child to
`ready-for-agent`.

## Decision Question

Should backup route ownership be handled as a dedicated proposal candidate
instead of being folded into the general trading or route cleanup lanes?

Recommended answer for this package: yes. Backup routes should remain a
dedicated proposal candidate because they combine destructive operations,
restore workflows, scheduler control, security logging, integrity checks, and
health/status semantics.

## Why This Exists

Issue `#92` downstream splitting accepted that backup route ownership becomes a
dedicated proposal candidate and that `cleanup_old_backups.py` is owned by that
lane.

D2.4 records the backup decision as a planning package. It converts the decision
into a concrete route/OpenAPI evidence shape without approving route edits.

## Current Route Evidence Snapshot

The current FastAPI route table and `app.openapi()` snapshot were collected by
importing `app.main` with local placeholder environment variables.

| Evidence | Result |
|---|---|
| Current HEAD | `553e71a90c833a3f9a2ffbec2342d67816baa2ad` |
| App import smoke | `app.main` imported with placeholder local env |
| Runtime routes | `548` |
| OpenAPI paths | `500` |
| Backup candidate routes | `13` |
| Backup schema-exposed routes | `13` |
| Backup OpenAPI paths | `13` |
| Backup OpenAPI operations | `13` |
| Backup duplicate operationIds | `0` |

## Classification Heuristic

The D2.4 backup candidate count is reproducible from the loaded FastAPI route
table by including route rows whose endpoint module contains
`app.api.backup_recovery_secure` or whose path contains `/api/backup-recovery`.

The current matching modules are:

- `app.api.backup_recovery_secure.log_security_event`: `11` routes
- `app.api.backup_recovery_secure.cleanup_old_backups`: `2` routes

Do not treat every repository file with `backup` in its name as backup-route
ownership. Historical `.backup` files, archived reports, infrastructure backup
managers, and operational scripts need separate classification before any
implementation proposal uses them as active route consumers.

## Candidate Ownership Classes

| Class | Current path group | Routes | Planning treatment |
|---|---|---:|---|
| Backup execution | `/api/backup-recovery/backup/*` | 3 | High-risk stateful operations; require permission, rate-limit, logging, and rollback review |
| Backup listing | `/api/backup-recovery/backups` | 1 | Consumer contract and pagination/filter semantics need review |
| Recovery execution | `/api/backup-recovery/recovery/*` | 4 | Destructive restore surface; keep separate from ordinary route cleanup |
| Scheduler control | `/api/backup-recovery/scheduler/*` | 2 | Operational control-plane surface; requires run-state and permission gates |
| Integrity verification | `/api/backup-recovery/integrity/verify/{backup_id}` | 1 | Verification surface tied to backup identity and audit history |
| Cleanup and health | `/api/backup-recovery/cleanup/old-backups`, `/api/backup-recovery/health` | 2 | Owned by `cleanup_old_backups.py`; needs dedicated security/ops classification |

## Current Route Snapshot

| Method | Path | Endpoint module | Endpoint name |
|---|---|---|---|
| `POST` | `/api/backup-recovery/backup/tdengine/full` | `app.api.backup_recovery_secure.log_security_event` | `backup_tdengine_full` |
| `POST` | `/api/backup-recovery/backup/tdengine/incremental` | `app.api.backup_recovery_secure.log_security_event` | `backup_tdengine_incremental` |
| `POST` | `/api/backup-recovery/backup/postgresql/full` | `app.api.backup_recovery_secure.log_security_event` | `backup_postgresql_full` |
| `GET` | `/api/backup-recovery/backups` | `app.api.backup_recovery_secure.log_security_event` | `list_backups` |
| `POST` | `/api/backup-recovery/recovery/tdengine/full` | `app.api.backup_recovery_secure.log_security_event` | `restore_tdengine_full` |
| `POST` | `/api/backup-recovery/recovery/tdengine/pitr` | `app.api.backup_recovery_secure.log_security_event` | `restore_tdengine_pitr` |
| `POST` | `/api/backup-recovery/recovery/postgresql/full` | `app.api.backup_recovery_secure.log_security_event` | `restore_postgresql_full` |
| `GET` | `/api/backup-recovery/recovery/objectives` | `app.api.backup_recovery_secure.log_security_event` | `get_recovery_objectives` |
| `POST` | `/api/backup-recovery/scheduler/control` | `app.api.backup_recovery_secure.log_security_event` | `scheduler_control` |
| `GET` | `/api/backup-recovery/scheduler/jobs` | `app.api.backup_recovery_secure.log_security_event` | `get_scheduled_jobs` |
| `GET` | `/api/backup-recovery/integrity/verify/{backup_id}` | `app.api.backup_recovery_secure.log_security_event` | `verify_backup_integrity` |
| `POST` | `/api/backup-recovery/cleanup/old-backups` | `app.api.backup_recovery_secure.cleanup_old_backups` | `cleanup_old_backups` |
| `GET` | `/api/backup-recovery/health` | `app.api.backup_recovery_secure.cleanup_old_backups` | `backup_service_health` |

All `13` routes are currently schema-exposed.

## `cleanup_old_backups.py` Ownership Note

`web/backend/app/api/backup_recovery_secure/cleanup_old_backups.py` owns two
runtime routes:

- `POST /api/backup-recovery/cleanup/old-backups`
- `GET /api/backup-recovery/health`

The cleanup route depends on `get_current_user`, calls `verify_admin_permission`,
logs security events, and delegates to `backup_manager.cleanup_old_backups()`.
That makes it a state-changing operations endpoint, not a generic route cleanup
candidate.

Any future implementation proposal must keep this file inside the dedicated
backup route ownership lane unless a human reviewer explicitly approves a
different ownership split.

## Consumer Matrix Snapshot

Tracked-file string scans found the following planning surface.

| Pattern | Backend source | Frontend source | Tests | Scripts | Docs/governance | Other | Planning impact |
|---|---:|---:|---:|---:|---:|---:|---|
| `/api/backup-recovery` | 3 files / 23 hits | 0 / 0 | 2 / 25 | 0 / 0 | 13 / 44 | 0 / 0 | Active path consumers appear concentrated in backend source, tests, and docs |
| `backup_recovery_secure` | 6 / 9 | 0 / 0 | 2 / 4 | 1 / 1 | 50 / 137 | 3 / 123 | Includes module-level, historical, and generated references; needs classification |
| `cleanup_old_backups` | 2 / 11 | 0 / 0 | 2 / 2 | 1 / 2 | 23 / 54 | 4 / 20 | Dedicated cleanup ownership evidence; not deletion authorization |
| `backup_service_health` | 2 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 3 | 0 / 0 | Health/status semantics need separate treatment from destructive cleanup |

This matrix is a planning snapshot. It is not enough to authorize route edits
because it has not yet classified active runtime callers, historical references,
generated artifacts, stale snapshots, or operational scripts.

## Required Future Evidence Before Any Backup Route Mutation

A future backup route implementation proposal or issue must include:

- current FastAPI route table with endpoint module, method, path, and
  `include_in_schema`;
- current `app.openapi()` snapshot with path count, operation count, warnings,
  and duplicate operationId check;
- backup ownership taxonomy for backup, recovery, scheduler, integrity,
  cleanup, and health routes;
- explicit ownership of `cleanup_old_backups.py` and its `backup_service_health`
  endpoint;
- `router_registry`, `VERSION_MAPPING`, and `docs/FUNCTION_TREE.md` status;
- frontend, backend, test, script, PM2, Docker, CI, and docs consumer matrix;
- security matrix covering auth dependency, admin permission, backup/recovery
  permission, rate limit, and security audit logging;
- contract parity matrix covering path, query/body parameters, response shape,
  caller parser expectations, OpenAPI examples, and minimal regression tests;
- rollback and compatibility strategy for any renamed, hidden, or retired route;
- explicit decision on whether `/api/backup-recovery/health` remains a service
  health endpoint, a backup route endpoint, or a control-plane endpoint.

## Governance Recommendation

Backup route ownership should remain a dedicated proposal candidate, currently
referred to by the future candidate name `define-backend-backup-route-ownership`.

No git branch, GitHub issue, or OpenSpec change with that name exists or is
required by this D2.4 package. If future implementation begins, the actual git
branch, OpenSpec change-id, and issue identifier must be created and recorded at
that time.

D2.4 should not be folded into the D2.3 trading route planning package and
should not be treated as a generic route cleanup batch.

## Explicit Non-Authorizations

D2.4 does not authorize:

- moving any backup route module;
- renaming or retiring any backup path;
- changing `include_in_schema`;
- changing operationIds;
- editing `web/backend/app/api/**`;
- editing `src/infrastructure/backup_recovery/**`;
- editing `web/frontend/**`;
- editing tests or fixtures;
- editing `docs/api/**`;
- opening a broad backup implementation issue;
- moving issue `#92` or any downstream item to `ready-for-agent`.

## Next Gate

Human review of this D2.4 package.

If accepted, the maintainer should decide whether to create a separate backup
route ownership OpenSpec proposal or a narrower implementation issue. Until that
decision exists, backup route behavior remains locked.

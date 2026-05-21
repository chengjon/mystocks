# Backend Backup Route Ownership Decision Package - 2026-05-22

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

## Status

- Status: decision-package-prepared-for-review
- OpenSpec change: `define-backend-backup-route-ownership`
- Parent decision issue: GitHub issue `#92`
- Current HEAD: `e6d576ccc26f7d2baa89b77f74da6b09bb57c103`
- Evidence generated at: `2026-05-21T18:46:13.961529Z`
- Execution mode: governance/evidence only

This package executes the D2.4 evidence tasks for backup route ownership. It
refreshes current-head route, OpenAPI, consumer, ownership, security, and
rollback evidence before any backup route mutation is considered.

It does not authorize or perform backend source edits, frontend edits, tests,
generated client changes, `docs/api` edits, route behavior changes, OpenAPI
schema or exposure changes, probe URL changes, PM2 commands, infrastructure
backup implementation changes, implementation issue creation, or movement of
issue `#92` to `ready-for-agent`.

## Evidence Artifacts

| Artifact | Role | Notes |
|---|---|---|
| `.planning/codebase/generated/backup-route-ownership-evidence-2026-05-22.json` | Current-head route/OpenAPI/consumer/static evidence | Generated from `app.main` and `app.openapi()` with placeholder governance env; no server or PM2 process was started |
| `openspec/changes/define-backend-backup-route-ownership/tasks.md` | D2.4 task checklist | Updated only for evidence and decision-package tasks that are complete |
| `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md` | Steward tree | Updated to mark D2.4 as decision-package-prepared-for-review |

## Authorization Boundary

The evidence was collected with placeholder environment values needed for
importing the FastAPI application in a governance snapshot. No production
secret, service credential, runtime process, PM2 workflow, external backup
operation, restore operation, cleanup operation, or live probe was used.

The following remain explicitly out of scope:

- adding, removing, renaming, moving, hiding, or retiring backup routes;
- changing `include_in_schema`, operationIds, response models, request models,
  or OpenAPI exposure;
- editing `web/backend/app/api/backup_recovery_secure/**`;
- editing `src/infrastructure/backup_recovery/**`;
- editing frontend callers, generated clients, `docs/api`, or tests;
- executing backup, recovery, cleanup, scheduler, PM2, Docker, or service
  restart commands;
- treating this package as a broad backup implementation issue.

## Freshness Gate

| Gate | Result | Evidence |
|---|---:|---|
| `app.main` import | Passed | `app_import_error=null` |
| FastAPI route table generation | Passed | `total_routes=548` |
| `app.openapi()` generation | Passed | `openapi_error=null` |
| OpenAPI path count | `500` | Based on current router registration and `include_in_schema` policy |
| OpenAPI operation count | `536` | Same snapshot as route table |
| OpenAPI schema count | `301` | Same snapshot as route table |
| Duplicate operationIds | `0` | `duplicate_operation_id_count=0` |
| OpenAPI warning count | `0` | `warning_count=0` |
| Stop condition | Not triggered | Import, route table, and OpenAPI generation all succeeded |

Route table summary:

| Metric | Count |
|---|---:|
| Runtime routes | `548` |
| Schema-visible routes | `536` |
| Hidden runtime routes | `12` |
| Endpoint modules | `99` |
| Duplicate runtime path/methods excluding HEAD/OPTIONS | `1` |

Backup route summary:

| Metric | Count |
|---|---:|
| Backup candidate routes | `13` |
| Backup schema-visible routes | `13` |
| Backup hidden runtime routes | `0` |
| Backup OpenAPI paths | `13` |
| Backup OpenAPI operations | `13` |
| Backup duplicate operationIds | `0` |

The only duplicate runtime path/method in the overall route table remains
`GET /metrics`. It is a D2.3/D2.5 route/OpenAPI and control-plane taxonomy item,
not a D2.4 backup route ownership issue.

## Backup Ownership Taxonomy

| Ownership class | Routes | Owner | Decision |
|---|---:|---|---|
| `backup-execution` | `3` | D2.4 backup route ownership | Backup creation or backup job execution surfaces |
| `backup-listing` | `1` | D2.4 backup route ownership | Backup inventory/listing surface |
| `recovery-execution` | `4` | D2.4 backup route ownership | Restore-capable recovery surfaces; treat as destructive unless a later implementation proves otherwise |
| `scheduler-control` | `2` | D2.4 backup route ownership | Operational scheduler control/listing surfaces |
| `integrity-verification` | `1` | D2.4 backup route ownership | Backup integrity validation surface |
| `cleanup-control` | `1` | D2.4 backup route ownership | State-changing backup cleanup surface |
| `backup-service-health` | `1` | D2.4 backup route ownership with D2.5 docs cross-reference | Backup subsystem health/status surface, not platform liveness/readiness |

Focused route list:

| Method | Path | Class | Endpoint | File |
|---|---|---|---|---|
| `POST` | `/api/backup-recovery/backup/postgresql/full` | `backup-execution` | `backup_postgresql_full` | `web/backend/app/api/backup_recovery_secure/log_security_event.py` |
| `POST` | `/api/backup-recovery/backup/tdengine/full` | `backup-execution` | `backup_tdengine_full` | `web/backend/app/api/backup_recovery_secure/log_security_event.py` |
| `POST` | `/api/backup-recovery/backup/tdengine/incremental` | `backup-execution` | `backup_tdengine_incremental` | `web/backend/app/api/backup_recovery_secure/log_security_event.py` |
| `GET` | `/api/backup-recovery/backups` | `backup-listing` | `list_backups` | `web/backend/app/api/backup_recovery_secure/log_security_event.py` |
| `POST` | `/api/backup-recovery/cleanup/old-backups` | `cleanup-control` | `cleanup_old_backups` | `web/backend/app/api/backup_recovery_secure/cleanup_old_backups.py` |
| `GET` | `/api/backup-recovery/health` | `backup-service-health` | `backup_service_health` | `web/backend/app/api/backup_recovery_secure/cleanup_old_backups.py` |
| `GET` | `/api/backup-recovery/integrity/verify/{backup_id}` | `integrity-verification` | `verify_backup_integrity` | `web/backend/app/api/backup_recovery_secure/log_security_event.py` |
| `GET` | `/api/backup-recovery/recovery/objectives` | `recovery-execution` | `get_recovery_objectives` | `web/backend/app/api/backup_recovery_secure/log_security_event.py` |
| `POST` | `/api/backup-recovery/recovery/postgresql/full` | `recovery-execution` | `restore_postgresql_full` | `web/backend/app/api/backup_recovery_secure/log_security_event.py` |
| `POST` | `/api/backup-recovery/recovery/tdengine/full` | `recovery-execution` | `restore_tdengine_full` | `web/backend/app/api/backup_recovery_secure/log_security_event.py` |
| `POST` | `/api/backup-recovery/recovery/tdengine/pitr` | `recovery-execution` | `restore_tdengine_pitr` | `web/backend/app/api/backup_recovery_secure/log_security_event.py` |
| `POST` | `/api/backup-recovery/scheduler/control` | `scheduler-control` | `scheduler_control` | `web/backend/app/api/backup_recovery_secure/log_security_event.py` |
| `GET` | `/api/backup-recovery/scheduler/jobs` | `scheduler-control` | `get_scheduled_jobs` | `web/backend/app/api/backup_recovery_secure/log_security_event.py` |

`/api/backup-recovery/health` is backup-owned for behavior and route/OpenAPI
ownership. It may be cross-referenced by D2.5 control-plane documentation, but
it is not the platform liveness endpoint and should not be moved to generic
service-health ownership without an explicit D2.4/D2.5 overlap decision.

## Cleanup And Health Ownership

`web/backend/app/api/backup_recovery_secure/cleanup_old_backups.py` currently
owns both:

- `POST /api/backup-recovery/cleanup/old-backups` via `cleanup_old_backups`;
- `GET /api/backup-recovery/health` via `backup_service_health`.

The cleanup route depends on `get_current_user`, calls
`verify_admin_permission`, calls `log_security_event`, and calls
`backup_manager`. It is therefore a state-changing operations endpoint, not a
generic route cleanup candidate.

The health route calls backup manager / backup recovery service logic and is a
backup subsystem health surface. Any future behavior change belongs in a D2.4
backup ownership lane; any wording-only cross-reference belongs in a separately
approved D2.5 docs lane.

## Safety And Contract Matrix

| Class | Auth evidence | Admin/security evidence | Stateful risk | Contract evidence | Minimum future regression checks |
|---|---|---|---|---|---|
| `backup-execution` | `get_current_user`; request body present | `log_security_event`; rate-limit terms present | State-changing backup execution | body params, `POST`, OpenAPI operation present | focused route tests for accepted body, auth, failure response, and OpenAPI operation |
| `backup-listing` | `get_current_user`; query params `database`, `backup_type`, `status` | `log_security_event` | Read/list | query params and response shape in OpenAPI | query filter contract and caller parser tests |
| `recovery-execution` | `get_current_user` on restore routes; objectives route has no dependency in route metadata | restore routes call `verify_admin_permission` and `log_security_event` | Restore-capable/destructive | body params for `POST` restore routes, OpenAPI operation present | restore request validation, admin failure, and no-live-restore smoke using test doubles |
| `scheduler-control` | `get_current_user`; control body present | control route calls `verify_admin_permission`; jobs route logs security event | Operational scheduler mutation/listing | body/query response shape in OpenAPI | scheduler control permission tests and jobs listing parser tests |
| `integrity-verification` | `get_current_user`; path param `backup_id` | no admin marker in current static source terms | Read/validation | path param and OpenAPI operation present | backup_id path validation and integrity response tests |
| `cleanup-control` | `get_current_user`; request body present | `verify_admin_permission`, `log_security_event` | State-changing deletion/cleanup | body params and OpenAPI operation present | cleanup dry-run/permission/failure tests; no live deletion in normal CI |
| `backup-service-health` | no auth dependency in route metadata | no admin/security marker in current static source terms | Read/status | OpenAPI operation present | backup subsystem health response test; not platform liveness/readiness |

Security gaps or intentionally unauthenticated surfaces should not be changed by
this package. They are decision inputs for a later, narrower implementation
proposal with explicit compatibility, rollback, and testing strategy.

## Consumer Matrix

The refreshed consumer scan covered workflows, config, scripts, frontend source,
backend and root tests, docs, Docker compose files, package config, and PM2
config files.

| Metric | Count |
|---|---:|
| Scanned files | `5781` |
| Files with hits | `500` |
| Hit lines | `3634` |

Category counts:

| Category | Hit lines |
|---|---:|
| `backup_route` | `94` |
| `backup_keyword` | `1202` |
| `restore_keyword` | `2500` |
| `scheduler_keyword` | `1269` |

Consumer class counts:

| Consumer class | Hit lines |
|---|---:|
| `docs_governance` | `2369` |
| `frontend` | `85` |
| `ops_config_ci` | `114` |
| `scripts` | `265` |
| `tests` | `801` |

This scan intentionally separates active route consumers from historical docs,
tests, generated artifacts, and infrastructure backup code. A future
implementation lane must narrow these hits to exact active callers before route
or response changes.

## Registry And Documentation State

| Artifact | State |
|---|---|
| `web/backend/app/router_registry.py` | exists; backup mentions=`2`; `VERSION_MAPPING` mentions=`9` |
| `web/backend/app/api/VERSION_MAPPING.py` | exists; backup mentions=`0`; `VERSION_MAPPING` mentions=`1` |
| `docs/FUNCTION_TREE.md` | exists; backup mentions=`10` |

The current evidence confirms `docs/FUNCTION_TREE.md` is the path that should be
used in follow-up records. Do not use a bare `FUNCTION_TREE.md` path in future
D2.4 acceptance criteria.

## Future Implementation Packet

If this reviewed D2.4 package is accepted and a later implementation lane is
approved, the future write scope should be narrow:

| Future scope | Current decision |
|---|---|
| `web/backend/app/api/backup_recovery_secure/log_security_event.py` | Candidate source scope for backup, recovery, scheduler, integrity, listing route behavior only |
| `web/backend/app/api/backup_recovery_secure/cleanup_old_backups.py` | Candidate source scope for cleanup and backup-service health route behavior only |
| `tests/api/file_tests/test_backup_recovery_api.py` | Candidate regression test surface |
| `tests/api/file_tests/test_backup_recovery_secure_api.py` | Candidate regression test surface |
| `tests/api/test_backup_recovery_file.py` | Candidate regression test surface |
| `tests/unit/api/test_backup_recovery_integrity_verification.py` | Candidate integrity verification regression surface |

The future packet must not include `src/infrastructure/backup_recovery/**`,
frontend callers, `docs/api`, generated clients, PM2 workflows, or route
registration changes unless a separate approval explicitly adds those paths.

Required future checks:

- current route table and `app.openapi()` freshness;
- focused route tests for every changed ownership class;
- OpenAPI path/operationId diff for backup paths;
- consumer contract matrix for active callers;
- security/admin/audit evidence for destructive routes;
- rollback plan that restores previous route behavior and OpenAPI exposure;
- explicit no-live-restore and no-live-cleanup guard for normal CI.

## Decision Routing

| Topic | Routing decision |
|---|---|
| Backup route behavior | D2.4 backup ownership only |
| Backup OpenAPI exposure or operationId changes | D2.4 plus D2.3/F route/OpenAPI governance overlap approval |
| `/api/backup-recovery/health` wording | D2.4 owns behavior; D2.5 may cross-reference docs wording in a separate docs lane |
| Generic route/OpenAPI mutation | D2.3/F, not this package alone |
| Control-plane docs stabilization | D2.5, not this package alone |
| PM2 stateful workflow execution | D2.6, not this package |
| Infrastructure backup implementation | Separate infrastructure proposal, not this package |

## OpenSpec Task Status

Completed in this package:

- Evidence freshness gate
- Backup ownership taxonomy
- Cleanup and backup-service health ownership classification
- Safety and contract matrix
- Decision package creation
- Explicit no-implementation boundary

Still pending:

- Human review of this D2.4 decision package
- Steward tree update after review acceptance
- Any implementation lane, write scope, tests, or rollback plan for future
  backup route changes

## Verification Commands

The following commands are intended for the PR that records this package:

```bash
openspec validate define-backend-backup-route-ownership --strict
python scripts/compliance/markdown_governance_gate.py --root-dir . --format json \
  .planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md \
  docs/reports/quality/backend-backup-route-ownership-decision-package-2026-05-22.md
git diff --cached --check
python governance/mainline/scripts/mainline_scope_gate.py \
  --task-card governance/mainline/task-cards/pr-125.yaml
```

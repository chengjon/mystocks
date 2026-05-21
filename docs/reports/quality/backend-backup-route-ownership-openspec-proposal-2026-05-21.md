# Backend Backup Route Ownership OpenSpec Proposal

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: review-ready proposal-only record

Date: 2026-05-21

Branch: `d2-4-backup-route-ownership-openspec`

OpenSpec change: `define-backend-backup-route-ownership`

## Purpose

This report records the D2.4 handoff from backup route ownership planning into
an explicit OpenSpec proposal. It is a governance record only. It does not
authorize backend source edits, route behavior changes, OpenAPI schema changes,
docs/API edits, generated client changes, probe rewiring, PM2 execution, or
issue `#92` movement to `ready-for-agent`.

## Inputs

| Input | Role |
|---|---|
| `docs/reports/quality/backend-backup-route-ownership-planning-package-2026-05-21.md` | D2.4 planning package for backup route ownership |
| `docs/reports/quality/backend-route-openapi-probe-refresh-2026-05-20.md` | Current route table, OpenAPI snapshot, and probe consumer matrix evidence |
| `docs/reports/quality/backend-route-openapi-governance-openspec-proposal-2026-05-21.md` | D2.3/F route/OpenAPI governance proposal that keeps backup ownership separate |
| `docs/reports/quality/backend-control-plane-openapi-docs-openspec-proposal-2026-05-21.md` | D2.5 docs/probe proposal that keeps backup ownership separate |
| `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md` | Steward task tree and branch register |

## Evidence Snapshot

| Evidence | Value | Source |
|---|---:|---|
| Runtime routes | `548` | `backend-backup-route-ownership-planning-package-2026-05-21.md` |
| OpenAPI paths | `500` | `backend-backup-route-ownership-planning-package-2026-05-21.md` |
| Backup candidate routes | `13` | `backend-backup-route-ownership-planning-package-2026-05-21.md` |
| Backup schema-exposed routes | `13` | `backend-backup-route-ownership-planning-package-2026-05-21.md` |
| Backup OpenAPI paths | `13` | `backend-backup-route-ownership-planning-package-2026-05-21.md` |
| Backup OpenAPI operations | `13` | `backend-backup-route-ownership-planning-package-2026-05-21.md` |
| Backup duplicate operationIds | `0` | `backend-backup-route-ownership-planning-package-2026-05-21.md` |
| Cleanup route owner candidate | `cleanup_old_backups.py` | `backend-backup-route-ownership-planning-package-2026-05-21.md` |

## Proposal Outcome

The OpenSpec proposal creates a backup route ownership gate with these accepted
boundaries:

1. Backup route ownership remains a dedicated proposal lane, not a generic route
   cleanup lane.
2. Backup execution, listing, recovery execution, scheduler control, integrity
   verification, cleanup, and health routes must be classified before mutation.
3. `cleanup_old_backups.py`, `cleanup_old_backups`, and
   `backup_service_health` require explicit ownership decisions.
4. Destructive/stateful backup and recovery operations require security,
   permission, audit, consumer, OpenAPI, regression, and rollback evidence.
5. D2.3 route/OpenAPI governance, D2.5 control-plane docs stabilization, and
   D2.6 PM2 stateful execution remain separate lanes.

## Artifacts Added

| Artifact | Purpose |
|---|---|
| `openspec/changes/define-backend-backup-route-ownership/proposal.md` | Proposal summary, impact, non-goals, and evidence links |
| `openspec/changes/define-backend-backup-route-ownership/design.md` | Backup ownership model, evidence model, boundaries, and rollback |
| `openspec/changes/define-backend-backup-route-ownership/tasks.md` | Approval and execution checklist for later backup ownership work |
| `openspec/changes/define-backend-backup-route-ownership/specs/architecture-governance/spec.md` | Architecture governance spec delta |
| `governance/mainline/task-cards/pr-118.yaml` | Mainline PR task card and path-limited scope |

## Authorization Boundary

This proposal does not authorize implementation. Any future backup route module
move, path rename, route retirement, OpenAPI exposure change, route-contract
edit, docs/API edit, generated-client change, probe rewrite, compatibility-route
retirement, infrastructure backup change, or PM2 gate execution requires a later
accepted decision package and a separate approved implementation lane with a
write scope, tests, and rollback plan.

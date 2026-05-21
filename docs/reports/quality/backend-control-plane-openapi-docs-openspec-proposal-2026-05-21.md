# Backend Control-Plane OpenAPI Docs OpenSpec Proposal

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: review-ready proposal-only record

Date: 2026-05-21

Branch: `d2-5-control-plane-openapi-docs-openspec`

OpenSpec change: `stabilize-backend-control-plane-openapi-docs`

## Purpose

This report records the D2.5 handoff from control-plane OpenAPI docs planning
into an explicit OpenSpec proposal. It is a governance record only. It does not
authorize backend source edits, route behavior changes, OpenAPI schema changes,
docs/API edits, generated client changes, probe rewiring, PM2 execution, or
issue `#92` movement to `ready-for-agent`.

## Inputs

| Input | Role |
|---|---|
| `docs/reports/quality/backend-control-plane-openapi-docs-planning-package-2026-05-21.md` | D2.5 planning package for control-plane OpenAPI docs and probe taxonomy |
| `docs/reports/quality/backend-route-openapi-probe-refresh-2026-05-20.md` | Current route table, OpenAPI snapshot, and probe consumer matrix evidence |
| `docs/reports/quality/backend-route-openapi-probe-refresh-2026-05-20-review.md` | Review feedback confirming `/metrics` duplicate as taxonomy item |
| `docs/reports/quality/backend-route-openapi-governance-openspec-proposal-2026-05-21.md` | D2.3/F route/OpenAPI governance proposal that keeps D2.5 separate |
| `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md` | Steward task tree and branch register |

## Evidence Snapshot

| Evidence | Value | Source |
|---|---:|---|
| Runtime routes | `548` | `backend-control-plane-openapi-docs-planning-package-2026-05-21.md` |
| OpenAPI paths | `500` | `backend-control-plane-openapi-docs-planning-package-2026-05-21.md` |
| Broad control/status candidate routes | `128` | `backend-control-plane-openapi-docs-planning-package-2026-05-21.md` |
| Broad control/status schema-exposed routes | `124` | `backend-control-plane-openapi-docs-planning-package-2026-05-21.md` |
| Broad control/status hidden routes | `4` | `backend-control-plane-openapi-docs-planning-package-2026-05-21.md` |
| Focused control-plane duplicate operationIds | `0` | `backend-control-plane-openapi-docs-planning-package-2026-05-21.md` |
| Intentionally absent readiness alias | `/health/readiness` | `backend-control-plane-openapi-docs-planning-package-2026-05-21.md` |
| Focused duplicate runtime path/method | `GET /metrics` | `backend-control-plane-openapi-docs-planning-package-2026-05-21.md` |

## Proposal Outcome

The OpenSpec proposal creates a control-plane documentation gate with these
accepted boundaries:

1. Control-plane docs/probe work must refresh current-head route/OpenAPI/probe
   evidence before docs/API or route decisions.
2. Health/readiness documentation must distinguish liveness, canonical
   readiness, compatibility readiness, service health, diagnostics, and
   intentionally absent aliases.
3. Metrics scrape, docs UI, schema retrieval, and runtime-only hidden
   compatibility surfaces must be classified separately from business API
   operations.
4. `/metrics` duplicate runtime path/method remains a taxonomy item, not an
   authorized route registration change.
5. `/health/readiness` remains intentionally absent unless a later approved
   change explicitly creates it.
6. D2.4 backup ownership, D2.3/F route mutation, and D2.6 PM2 stateful execution
   remain separate lanes.

## Artifacts Added

| Artifact | Purpose |
|---|---|
| `openspec/changes/stabilize-backend-control-plane-openapi-docs/proposal.md` | Proposal summary, impact, non-goals, and evidence links |
| `openspec/changes/stabilize-backend-control-plane-openapi-docs/design.md` | Control-plane docs model, taxonomy, workstream shape, and rollback |
| `openspec/changes/stabilize-backend-control-plane-openapi-docs/tasks.md` | Approval and execution checklist for later docs/probe governance work |
| `openspec/changes/stabilize-backend-control-plane-openapi-docs/specs/api-documentation/spec.md` | API documentation spec delta |
| `governance/mainline/task-cards/pr-117.yaml` | Mainline PR task card and path-limited scope |

## Authorization Boundary

This proposal does not authorize implementation. Any future docs/API edit,
runtime route mutation, OpenAPI exposure change, route-contract edit, probe
rewrite, generated-client change, compatibility-route retirement, or PM2 gate
execution requires a later accepted decision package and a separate approved
implementation lane with a write scope, tests, and rollback plan.

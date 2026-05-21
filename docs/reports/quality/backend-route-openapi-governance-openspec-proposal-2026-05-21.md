# Backend Route/OpenAPI Governance OpenSpec Proposal

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: review-ready proposal-only record

Date: 2026-05-21

Branch: `d2-3-route-openapi-governance-openspec`

OpenSpec change: `refresh-backend-route-openapi-governance`

## Purpose

This report records the D2.3 handoff from trading route/OpenAPI governance
planning into an explicit OpenSpec proposal. It is a governance record only. It
does not authorize backend source edits, route behavior changes, OpenAPI schema
changes, generated client changes, tests, probe rewiring, or issue `#92`
movement to `ready-for-agent`.

## Inputs

| Input | Role |
|---|---|
| `docs/reports/quality/backend-trading-route-openapi-governance-planning-package-2026-05-21.md` | D2.3 planning package for folding trading route ownership into unified route/OpenAPI governance |
| `docs/reports/quality/backend-route-openapi-probe-refresh-2026-05-20.md` | Current route table, OpenAPI snapshot, and probe consumer matrix evidence |
| `docs/reports/quality/backend-route-openapi-probe-refresh-2026-05-20-review.md` | Review feedback for route/OpenAPI/probe refresh evidence |
| `docs/reports/quality/backend-openspec-issue92-next-child-lane-selection-2026-05-21.md` | Recommendation that D2.3 is the next child lane after D2.1a closeout |
| `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md` | Steward task tree and branch register |

## Evidence Snapshot

| Evidence | Value | Source |
|---|---:|---|
| Runtime routes | `548` | `backend-route-openapi-probe-refresh-2026-05-20.md` |
| OpenAPI paths | `500` | `backend-route-openapi-probe-refresh-2026-05-20.md` |
| OpenAPI operations | `536` | `backend-route-openapi-probe-refresh-2026-05-20.md` |
| Duplicate operationIds | `0` | `backend-route-openapi-probe-refresh-2026-05-20.md` |
| OpenAPI warnings | `0` | `backend-route-openapi-probe-refresh-2026-05-20.md` |
| Probe matrix scanned files | `5782` | `backend-route-openapi-probe-refresh-2026-05-20.md` |
| Probe matrix hit files | `188` | `backend-route-openapi-probe-refresh-2026-05-20.md` |
| Probe matrix hit lines | `611` | `backend-route-openapi-probe-refresh-2026-05-20.md` |
| Trading route candidates | `41` | `backend-trading-route-openapi-governance-planning-package-2026-05-21.md` |
| Trading schema path count | `32` | `backend-trading-route-openapi-governance-planning-package-2026-05-21.md` |

## Proposal Outcome

The OpenSpec proposal creates a route/OpenAPI governance gate with these
accepted boundaries:

1. Current-head route, OpenAPI, and probe evidence must be refreshed before
   route governance is used as decision input.
2. Trading route ownership remains under unified route/OpenAPI governance, not a
   standalone trading implementation lane.
3. `/api/v1/advanced-analysis/trading-signals` remains trading-adjacent until an
   explicit owner decision is accepted.
4. `/metrics` GET duplicate path/method remains a control-plane taxonomy item
   until D2.5 or an explicitly approved narrow route-governance lane handles it.
5. Backup and recovery routes remain D2.4 ownership candidates.
6. Runtime route existence and OpenAPI schema exposure must be recorded as
   separate facts for compatibility routes.

## Artifacts Added

| Artifact | Purpose |
|---|---|
| `openspec/changes/refresh-backend-route-openapi-governance/proposal.md` | Proposal summary, impact, non-goals, and evidence links |
| `openspec/changes/refresh-backend-route-openapi-governance/design.md` | Governance model, evidence model, workstream shape, and rollback |
| `openspec/changes/refresh-backend-route-openapi-governance/tasks.md` | Approval and execution checklist for later route/OpenAPI governance work |
| `openspec/changes/refresh-backend-route-openapi-governance/specs/architecture-governance/spec.md` | Architecture governance spec delta |
| `governance/mainline/task-cards/pr-116.yaml` | Mainline PR task card and path-limited scope |

## Authorization Boundary

This proposal does not authorize implementation. Any future route mutation,
OpenAPI exposure change, route-contract edit, probe rewrite, generated-client
change, or compatibility-route retirement requires a later accepted decision
package and a separate approved implementation lane with a write scope, tests,
and rollback plan.

# Backend PM2 Stateful Gate OpenSpec Proposal

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: review-ready proposal-only record

Date: 2026-05-21

Branch: `d2-6-pm2-stateful-gate-openspec`

OpenSpec change: `approve-backend-pm2-stateful-gate`

## Purpose

This report records the D2.6 handoff from PM2 stateful gate approval governance
into an explicit OpenSpec proposal. It is a governance record only. It does not
authorize PM2 workflow execution, `pm2 stop all`, `pm2 delete all`, service
restart, backend source edits, route behavior changes, OpenAPI schema changes,
docs/API edits, generated client changes, probe rewiring, or issue `#92`
movement to `ready-for-agent`.

## Inputs

| Input | Role |
|---|---|
| `docs/reports/quality/backend-pm2-stateful-gate-approval-governance-2026-05-21.md` | D2.6 approval strategy and residual gate governance package |
| `docs/reports/quality/backend-health-status-pm2-gate-2026-05-18.md` | Historical passing PM2 gate evidence for health/status task `4.7` |
| `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md` | Steward task tree and branch register |

## Prior PM2 Evidence

The health/status consolidation line already has passing PM2 gate evidence:

| Evidence | Value |
|---|---|
| Workflow command | `./scripts/run_pm2_integration_workflow.sh gate` |
| PM2 E2E command | `bash scripts/run_e2e_pm2.sh` |
| PM2 E2E result | `14 passed` |
| Service restore command | `pm2 start ecosystem.test.config.js` |
| `/health` probe | HTTP 200 |
| `/api/health/ready` probe | HTTP 200 |

This proposal does not rerun that workflow. It preserves the evidence as
historical input and requires future worklines to justify whether existing PM2
evidence is sufficient, a named equivalent is sufficient, or a fresh stateful
run is explicitly approved.

## Proposal Outcome

The OpenSpec proposal creates a PM2 stateful gate approval policy with these
boundaries:

1. `gate`, `regression`, and `all` remain stateful PM2 workflows.
2. A full PM2 workflow requires explicit human approval and a rollback/restore
   plan before execution.
3. A named equivalent must list exact commands, substitution rationale, and what
   full PM2 evidence remains unproven.
4. Read-only PM2 sampling requires an explicit command list and no-mutation
   statement.
5. Issue `#92` remains a decision issue and does not authorize PM2 execution by
   implication.
6. Health/status task `4.7` remains closed unless new current-HEAD evidence
   contradicts the 2026-05-18 PM2 gate report.

## Artifacts Added

| Artifact | Purpose |
|---|---|
| `openspec/changes/approve-backend-pm2-stateful-gate/proposal.md` | Proposal summary, impact, non-goals, and evidence links |
| `openspec/changes/approve-backend-pm2-stateful-gate/design.md` | Approval dispositions, required fields, and rollback model |
| `openspec/changes/approve-backend-pm2-stateful-gate/tasks.md` | Approval and execution-boundary checklist |
| `openspec/changes/approve-backend-pm2-stateful-gate/specs/architecture-governance/spec.md` | Architecture governance spec delta |
| `governance/mainline/task-cards/pr-119.yaml` | Mainline PR task card and path-limited scope |

## Authorization Boundary

This proposal does not authorize implementation or PM2 execution. Any future
PM2 workflow run, named equivalent, read-only PM2 sampling, service restart,
process deletion/recreation, runtime route mutation, OpenAPI exposure change,
route-contract edit, docs/API edit, generated-client change, probe rewrite, or
compatibility-route retirement requires a later accepted approval record and the
specific write or execution scope named in that record.

# Backend PM2 Stateful Gate Approval Governance

Date: 2026-05-21
Parent issue: `#92`
Track: D2.6 PM2 stateful gate approval strategy
Base HEAD: `ca215767b4bbc04b237a408a409ac63cb799bf80`
Prepared at: `2026-05-21T04:50:03Z`
Status: approval governance package prepared; no PM2 workflow executed

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Boundary

This D2.6 package is governance and evidence alignment only.

It does not authorize or perform:

- PM2 workflow execution.
- `pm2 stop all`, `pm2 delete all`, or service restart operations.
- Backend runtime code changes.
- Route registration changes.
- OpenAPI schema exposure changes.
- Frontend, test, fixture, or docs/API changes.
- OpenSpec change/spec creation or modification.
- Moving issue `#92` or any downstream item to `ready-for-agent`.

The candidate name `approve-backend-pm2-stateful-gate` is a future approval-track
placeholder. It is not a created GitHub issue, git branch, or OpenSpec change.

## Current State

| Item | State | Evidence |
|---|---|---|
| Issue `#92` | `OPEN`; labels: `enhancement`, `ready-for-downstream`, `ready-for-human`; no `ready-for-agent` | GitHub issue query on 2026-05-21 |
| Health/status OpenSpec task `4.7` | Closed historically | `docs/reports/quality/backend-health-status-pm2-gate-2026-05-18.md` |
| Earlier PM2 residual blocker report | Superseded by the passing PM2 gate evidence | `docs/reports/quality/backend-health-status-residual-blockers-2026-05-18.md` |
| Current D2.6 action | Approval strategy and residual gate governance only | This report |

## Stateful Gate Classification

The script `scripts/run_pm2_integration_workflow.sh` has multiple modes:

| Mode | Stateful? | Why | D2.6 disposition |
|---|---:|---|---|
| `gate` | Yes | Calls `clean_pm2`, which runs `pm2 stop all` and `pm2 delete all`; then runs frontend type-check, frontend tests, and PM2-backed E2E | Requires explicit human approval or a named equivalent approved by the owning issue |
| `regression` | Yes | Starts PM2 with `ecosystem.test.config.js`, probes backend health/readiness, runs E2E and backend pytest, and inspects PM2 logs | Requires explicit human approval and an explicit rollback/restore plan |
| `all` | Yes | Runs `gate` and `regression` | Requires explicit human approval; should not be the default for small governance closeout |

D2.6 does not run any of these modes.

## Prior Closure Evidence

The health/status consolidation line already has passing stateful PM2 evidence:

- Command: `./scripts/run_pm2_integration_workflow.sh gate`
- Result: `PASS`
- Frontend type-check exit code: `0`
- Frontend test exit code: `0`
- Frontend unit result: `378 passed (378)` test files, `1415 passed (1415)` tests
- PM2 E2E command: `bash scripts/run_e2e_pm2.sh`
- PM2 E2E exit code: `0`
- PM2 E2E result: `14 passed`
- Services restored with `pm2 start ecosystem.test.config.js`
- Post-restore service checks:
  - `mystocks-backend`: `online`
  - `mystocks-frontend`: `online`
  - `http://localhost:8020/health`: HTTP 200
  - `http://localhost:8020/api/health/ready`: HTTP 200
  - `http://localhost:3020/`: HTTP 200

This means D2.6 should not reopen health/status task `4.7`. Its purpose is to
prevent future agents from running stateful PM2 gates from a broad planning issue
without an explicit approval record.

## Approval Strategy

Future PM2 stateful gate execution should use one of these dispositions.

| Disposition | Allowed by D2.6? | Required approval record | Suitable use |
|---|---:|---|---|
| No PM2 execution | Yes | Report records why prior evidence is sufficient | Documentation, taxonomy, route/OpenAPI evidence, and decision packages |
| Read-only PM2 status/probe sampling | Only if explicitly requested | Issue comment or report with command list, no service mutation, service owner, and timestamp | Checking current service state without restart fidelity |
| Named equivalent | Only if explicitly approved | Owning issue must name the equivalent command set, why it substitutes for the stateful workflow, and what it cannot prove | Small runtime-adjacent batches where full PM2 reset is disproportionate |
| Full `run_pm2_integration_workflow.sh gate` | Only with explicit human approval | Approval comment/report naming `gate`, service impact, rollback/restore, target branch/HEAD, and evidence destination | PM2/frontend gate closure, runtime-sensitive archive reviews |
| Full `run_pm2_integration_workflow.sh regression` or `all` | Only with explicit human approval and expanded owner plan | Approval comment/report naming services, ports, logs, restore command, timeout, and acceptance owner | High-risk runtime release validation |

## Required Fields for Any Future Stateful Approval

An approval record must include:

- Approval source: GitHub issue comment, review-thread approval, or approved runbook.
- Approval timestamp.
- Requesting lane or issue.
- Target branch and HEAD.
- Exact command mode: `gate`, `regression`, `all`, or named equivalent.
- Services and ports affected.
- Expected state mutation, including whether `pm2 stop all` / `pm2 delete all` will run.
- Rollback and service-restore command.
- Evidence artifact path.
- Owner who validates post-run service state.
- Statement that approval is not reusable for unrelated branches or future HEADs.

## Named Equivalent Minimum Bar

A named equivalent must state both what it proves and what it does not prove.

Minimum fields:

- Command list.
- Read-only or stateful classification.
- Probe URLs, if any.
- Whether route table or OpenAPI smoke is included.
- Whether frontend E2E is included.
- Whether PM2 process deletion/recreation is included.
- Why the equivalent is sufficient for the owning issue.
- Which full PM2 workflow evidence remains unproven.

Examples of possible components:

- Backend import smoke: `PYTHONPATH=web/backend python -c "from app.main import app; print(len(app.routes))"`
- Route/OpenAPI smoke using placeholder required environment, when applicable.
- Read-only `pm2 list`, when explicitly approved.
- HTTP probes for `/health` and `/api/health/ready`, when services are already running and probe execution is approved.

This report does not approve any of those commands for immediate execution.

## Routing Rules

| Situation | Route |
|---|---|
| Health/status task `4.7` review | Use the existing 2026-05-18 PM2 gate evidence; do not rerun by default |
| Issue `#92` downstream decision work | Keep PM2 execution out of `#92`; record D2.6 as an approval strategy package |
| Future runtime-sensitive implementation issue | Create a dedicated approval record before PM2 execution |
| Future OpenSpec archive requiring PM2 evidence | Cite existing evidence if still applicable; otherwise approve a new run with branch/HEAD scoping |
| Agent sees `run_pm2_integration_workflow.sh` in a task list | Stop unless the task includes explicit approval or an approved named equivalent |

## Residual Risks

- A broad planning issue could be misread as permission to run a stateful PM2 gate.
- Historical reports can look contradictory because the residual blocker report was
  later superseded by passing PM2 evidence.
- A named equivalent can be overused if it does not clearly state which restart or
  E2E fidelity it does not cover.
- PM2 gate evidence is branch/HEAD-sensitive; old evidence should not be silently
  treated as current runtime proof for unrelated changes.

## Recommended Next Gate

D2.6 should be reviewed as a decision-only package.

If accepted:

1. Keep issue `#92` as the parent decision issue, not an execution issue.
2. Do not create `approve-backend-pm2-stateful-gate` as an implementation issue unless a future workline requires a fresh PM2 run.
3. If a future workline needs PM2 execution, create a small approval issue or approved runbook using the required fields above.
4. Keep prior health/status `4.7` closed unless new current-HEAD evidence contradicts the 2026-05-18 gate report.

## Verification for This Package

Expected verification is document/governance only:

- Markdown governance gate on this report and the steward task tree.
- YAML parse for the PR task card.
- `git diff --check`.
- Mainline scope gate for the task card.
- GitNexus staged change detection before commit.

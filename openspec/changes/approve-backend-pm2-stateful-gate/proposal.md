# Change: Approve Backend PM2 Stateful Gate Policy

## Why

D2.6 recorded that PM2-backed validation is stateful and must not be executed
from broad planning or governance issues. The script
`scripts/run_pm2_integration_workflow.sh` can run `pm2 stop all` and
`pm2 delete all`, recreate services, run frontend checks, run PM2-backed E2E,
and inspect PM2 logs. That is useful evidence for runtime-sensitive work, but
it is not a read-only check.

The health/status line already has historical passing PM2 gate evidence:

- `./scripts/run_pm2_integration_workflow.sh gate`
- PM2 E2E command: `bash scripts/run_e2e_pm2.sh`
- PM2 E2E result: `14 passed`
- services restored with `pm2 start ecosystem.test.config.js`
- `/health`: HTTP 200
- `/api/health/ready`: HTTP 200

D2.6 should therefore not reopen health/status task `4.7`. Its job is to define
the approval policy that future agents must satisfy before running a stateful
PM2 workflow or a named equivalent.

## What Changes

- Add an architecture-governance requirement for PM2 stateful workflow approval.
- Define stateful PM2 modes: `gate`, `regression`, and `all`.
- Define allowed dispositions: no PM2 execution, read-only sampling, named
  equivalent, full `gate`, full `regression`, and full `all`.
- Require a complete approval record before any stateful PM2 workflow runs.
- Require named equivalents to state what they prove and what they do not prove.
- Keep issue `#92` as a decision issue and prevent it from authorizing PM2
  execution by implication.

## Non-Goals

- No PM2 command execution.
- No `pm2 stop all`, `pm2 delete all`, service restart, or process recreation.
- No backend source, frontend source, test, docs/API, generated client, route,
  OpenAPI, probe URL, or runtime behavior changes.
- No reopening health/status task `4.7` without new current-HEAD contradictory
  evidence.
- No movement of issue `#92` to `ready-for-agent`.
- No implementation issue creation.

## Impact

- Affected spec: `architecture-governance`.
- Primary inputs:
  - `docs/reports/quality/backend-pm2-stateful-gate-approval-governance-2026-05-21.md`
  - `docs/reports/quality/backend-health-status-pm2-gate-2026-05-18.md`
  - `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- Related lane boundaries:
  - D2.3 route/OpenAPI governance remains separate.
  - D2.4 backup route ownership remains separate.
  - D2.5 control-plane OpenAPI docs stabilization remains separate.
- New artifacts prepared by this PR:
  - `openspec/changes/approve-backend-pm2-stateful-gate/`
  - `docs/reports/quality/backend-pm2-stateful-gate-openspec-proposal-2026-05-21.md`
  - `governance/mainline/task-cards/pr-119.yaml`

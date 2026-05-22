# Tasks: Approve Backend PM2 Stateful Gate Policy

## 0. Proposal Preparation

- [x] Create OpenSpec proposal, design note, task list, and architecture
  governance spec delta.
- [x] Link D2.6 PM2 stateful gate approval governance, historical health/status
  PM2 evidence, and steward tree context.
- [x] Keep this change proposal-only and explicitly exclude PM2 execution,
  backend source, frontend source, tests, docs/API, generated client, route,
  OpenAPI, probe, and runtime edits.
- [x] Obtain human approval for this OpenSpec policy before treating it as the
  PM2 stateful gate approval contract.
  Approval recorded in the current review thread at
  `2026-05-22T00:32:45+08:00`; scope is governance/evidence tasks only and
  does not authorize PM2 command execution, service restart/recreation, route
  behavior, OpenAPI schema, docs/API, generated client, source, or test
  changes.

## 1. Approval Policy Acceptance

- [x] Confirm `gate`, `regression`, and `all` remain classified as stateful PM2
  workflows.
- [x] Confirm issue `#92` remains a decision issue and does not authorize PM2
  execution by implication.
- [x] Confirm health/status task `4.7` remains closed unless new current-HEAD
  evidence contradicts the 2026-05-18 PM2 gate report.
- [x] Confirm future agents must stop when they see
  `scripts/run_pm2_integration_workflow.sh` in a task list without explicit
  approval or an approved named equivalent.

## 2. Future Approval Record Template

- [x] Record approval source, timestamp, approving human, target branch, target
  commit, command mode, service impact, rollback/restore commands, evidence
  destination, timeout, stop rule, and acceptance owner.
- [x] For named equivalents, record the exact command set, substitution reason,
  and what full PM2 workflow evidence remains unproven.
- [x] For read-only sampling, record exact commands and confirm that no service
  mutation is expected.

## 3. Execution Boundary

- [x] Do not run PM2 commands from this proposal.
- [x] Do not create implementation issues from this proposal.
- [x] If a future workline needs PM2 execution, create a narrow approval issue,
  issue comment, or approved runbook before execution.
- [x] Update the codebase-map task tree after the PM2 approval policy is
  reviewed.

Evidence:

- `docs/reports/quality/backend-pm2-stateful-gate-approval-decision-package-2026-05-22.md`
- `docs/reports/quality/backend-pm2-stateful-gate-approval-decision-package-2026-05-22-review.md`
- `.planning/codebase/generated/pm2-stateful-gate-approval-evidence-2026-05-22.json`
- PR `#127` task card:
  `governance/mainline/task-cards/pr-127.yaml`

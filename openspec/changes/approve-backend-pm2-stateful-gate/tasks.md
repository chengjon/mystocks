# Tasks: Approve Backend PM2 Stateful Gate Policy

## 0. Proposal Preparation

- [x] Create OpenSpec proposal, design note, task list, and architecture
  governance spec delta.
- [x] Link D2.6 PM2 stateful gate approval governance, historical health/status
  PM2 evidence, and steward tree context.
- [x] Keep this change proposal-only and explicitly exclude PM2 execution,
  backend source, frontend source, tests, docs/API, generated client, route,
  OpenAPI, probe, and runtime edits.
- [ ] Obtain human approval for this OpenSpec policy before treating it as the
  PM2 stateful gate approval contract.

## 1. Approval Policy Acceptance

- [ ] Confirm `gate`, `regression`, and `all` remain classified as stateful PM2
  workflows.
- [ ] Confirm issue `#92` remains a decision issue and does not authorize PM2
  execution by implication.
- [ ] Confirm health/status task `4.7` remains closed unless new current-HEAD
  evidence contradicts the 2026-05-18 PM2 gate report.
- [ ] Confirm future agents must stop when they see
  `scripts/run_pm2_integration_workflow.sh` in a task list without explicit
  approval or an approved named equivalent.

## 2. Future Approval Record Template

- [ ] Record approval source, timestamp, approving human, target branch, target
  commit, command mode, service impact, rollback/restore commands, evidence
  destination, timeout, stop rule, and acceptance owner.
- [ ] For named equivalents, record the exact command set, substitution reason,
  and what full PM2 workflow evidence remains unproven.
- [ ] For read-only sampling, record exact commands and confirm that no service
  mutation is expected.

## 3. Execution Boundary

- [ ] Do not run PM2 commands from this proposal.
- [ ] Do not create implementation issues from this proposal.
- [ ] If a future workline needs PM2 execution, create a narrow approval issue,
  issue comment, or approved runbook before execution.
- [ ] Update the codebase-map task tree after the PM2 approval policy is
  reviewed.

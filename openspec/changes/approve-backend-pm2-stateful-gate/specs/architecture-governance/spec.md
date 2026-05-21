## ADDED Requirements

### Requirement: Stateful PM2 Workflow Execution Requires Explicit Approval

Stateful PM2 validation SHALL require an explicit approval record before any
workflow can stop, delete, recreate, or restart services.

#### Scenario: PM2 workflow mode is classified

- **WHEN** `scripts/run_pm2_integration_workflow.sh` is referenced by a task
  list, proposal, runbook, or issue
- **THEN** the work item SHALL classify the intended mode as no execution,
  read-only sampling, named equivalent, full `gate`, full `regression`, or full
  `all` before any PM2 command is run.

#### Scenario: Stateful PM2 gate requires an approval record

- **WHEN** a future work item requests full `gate`, `regression`, or `all`
  execution
- **THEN** the approval record SHALL name the approving source, approval
  timestamp, approving human or owner, target branch, target commit, exact
  command mode, expected state mutation, service impact, rollback and restore
  commands, evidence destination, timeout, stop rule, and acceptance owner.

#### Scenario: Named equivalent is not full PM2 evidence

- **WHEN** a named equivalent is approved instead of a full PM2 workflow
- **THEN** the approval record SHALL name the exact command set, explain why it
  substitutes for the stateful workflow, and state which full PM2 workflow
  evidence remains unproven.

#### Scenario: Existing PM2 evidence is cited without rerun

- **WHEN** existing PM2 gate evidence is used for a later governance or archive
  decision
- **THEN** the decision packet SHALL record the evidence path, captured branch or
  commit if known, freshness limits, and why no new PM2 execution is required.

#### Scenario: Proposal-only PM2 approval work remains locked

- **WHEN** a PM2 approval-policy change is in proposal or evidence-only state
- **THEN** it SHALL NOT authorize PM2 command execution, `pm2 stop all`,
  `pm2 delete all`, service restart, process recreation, backend source edits,
  frontend source edits, tests, generated client changes, docs/API edits, route
  changes, OpenAPI schema changes, probe URL changes, or movement of a decision
  issue to implementation-ready state.

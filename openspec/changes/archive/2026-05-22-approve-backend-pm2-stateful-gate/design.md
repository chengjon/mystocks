# Design: Backend PM2 Stateful Gate Approval Policy

## Context

PM2-backed validation can mutate service state. `gate`, `regression`, and `all`
modes are not equivalent to lint, import smoke, route table generation, or
OpenAPI generation. They can stop, delete, recreate, probe, and inspect running
services.

The policy must keep three facts separate:

- Previous health/status PM2 evidence may be cited when still applicable.
- A named equivalent may be approved for a narrower runtime-adjacent batch.
- A fresh stateful PM2 workflow requires an explicit approval record before
  execution.

## Decision

Create `approve-backend-pm2-stateful-gate` as a proposal-only OpenSpec change.
It defines the approval contract for future PM2 stateful gate execution. It does
not approve any current PM2 run.

## Approval Dispositions

### No PM2 Execution

Allowed for documentation, taxonomy, route/OpenAPI evidence, decision packages,
and proposal-only governance work when prior evidence or non-stateful checks are
sufficient.

### Read-Only Sampling

Allowed only when explicitly requested. The approval record must name the exact
commands, confirm no service mutation, record service owner, and include a
timestamp.

### Named Equivalent

Allowed only when explicitly approved. The owning issue or runbook must name the
equivalent command set, explain why it substitutes for the stateful workflow,
and state which full PM2 workflow evidence remains unproven.

### Full `gate`

Allowed only with explicit human approval. The approval record must name
`gate`, expected service impact, rollback/restore plan, target branch and HEAD,
and evidence destination.

### Full `regression` Or `all`

Allowed only with explicit human approval and an expanded owner plan naming
services, ports, logs, restore command, timeout, acceptance owner, and rollback
plan.

## Required Approval Fields

Any future stateful approval record must include:

- approval source
- approval timestamp
- approving human or owner
- target branch and commit
- exact command mode or named equivalent
- expected state mutation
- service impact and ports
- rollback and restore commands
- evidence destination
- timeout and stop rule
- acceptance owner
- statement of what remains unproven, if using a named equivalent

## Rollback

This proposal is rollback-safe by revert. Any future PM2 execution must include
its own rollback and service restoration plan.

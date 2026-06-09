# Backend Core Split Line Summary And Next Plan

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Recorded at: `2026-05-19`

## Purpose

This document summarizes the current backend Core split line after the runtime
gate reconciliation, and defines the next reviewable work plan before any new
Core split batch starts.

It is intended for human review. It does not persist database passwords, JWT
secrets, or monitoring credentials.

## Current Status

The backend Core split line is now in a **runtime-gate reconciled / not yet
fully closed** state.

Meaning:

- the first low-risk Core helper split evidence exists;
- the contract / route import blockers that prevented backend startup have been
  unblocked in the implementation worktree;
- OpenSpec verification tasks `4.3`, `4.4`, and `4.5` have fresh runtime
  evidence and are checked off;
- OpenSpec task `3.2` remains open and must be reviewed before this change can
  be considered fully complete;
- no next Core split batch should start until the remaining governance
  reconciliation is accepted.

## Completed Work

### 1. Boundary And Execution Discipline

- Reviewed
  `docs/reports/quality/backend-core-split-other-line-next-work-boundary-2026-05-19.md`.
- Kept the publication / governance checkout separate from backend
  implementation continuation.
- Continued runtime verification in the isolated worktree:
  `/opt/claude/mystocks_spec/.worktrees/contract-startup-unblock`.
- Did not mix issue publication artifacts, route changes, Core implementation,
  PM2 runtime evidence, or generated evidence into one uncontrolled batch.
- Created the execution plan:
  `docs/superpowers/plans/2026-05-19-backend-core-split-runtime-gate-plan.md`.

### 2. Startup Blocker Follow-Up

The implementation worktree had already restored the backend startup import
chain through these pushed commits:

```text
71d29d3b7 fix(contract): restore drift incident response schemas
2d6682e81 fix(api): restore extracted route module imports
```

These commits unblocked the runtime path that previously prevented PM2 and
health/readiness evidence collection.

### 3. Runtime Environment Preflight

Using session-provided runtime environment values only, the following dependency
reachability was checked:

| Dependency | Endpoint | Result |
|---|---:|---|
| PostgreSQL / TimescaleDB | `192.168.123.104:5438` | reachable |
| TDengine native | `192.168.123.104:6030` | reachable |
| TDengine REST | `192.168.123.104:6041` | reachable |
| Redis | `localhost:6379` | reachable |
| Prometheus | `192.168.123.104:9090` | connection refused |
| Grafana | `192.168.123.104:3000` | connection refused |

Prometheus and Grafana were treated as non-blocking for this backend startup
gate because backend PM2 startup and readiness did not depend on those UI /
scrape services.

### 4. PM2 Backend Startup Gate

The backend was started with PM2 in the implementation worktree using the
session runtime environment.

Observed state before cleanup:

```text
process: mystocks-backend
status: online
restarts: 0
backend URL: http://localhost:8020
```

After verification, the temporary PM2 process was removed:

```text
pm2_processes=0
```

OpenSpec task closed:

```text
4.3 Run PM2 backend startup smoke
```

### 5. Health And Readiness Smoke

Observed backend smoke results:

| Endpoint | HTTP | success |
|---|---:|---|
| `/health` | `200` | `True` |
| `/api/health/services` | `200` | `True` |
| `/health/ready` | `200` | `True` |
| `/api/health/ready` | `200` | `True` |

OpenSpec task closed:

```text
4.4 Run /api/health/services, /health/ready, and /api/health/ready smoke
```

### 6. OpenAPI / Route Drift Check

Current runtime OpenAPI generation completed from `app.main` using the same PM2
runtime environment.

Current snapshot:

```text
paths=499
operations=535
duplicate_operation_ids=0
```

A read-only comparison against the existing root-worktree reference baseline
showed non-zero path diff:

```text
baseline_paths=501
current_paths=499
added=8
removed=10
duplicate_operation_ids=0
```

Classification:

- the path delta is not attributed to the Core validation helper split;
- the added / removed paths align with known health, data-quality, and
  strategy-mgmt compatibility governance surfaces;
- no duplicate `operationId` warning remains in the current runtime schema;
- no unexplained route or OpenAPI drift attributable to this Core split line was
  found.

OpenSpec task closed:

```text
4.5 Confirm no unintended route or OpenAPI drift
```

### 7. Evidence And Commit

Evidence report added in the implementation worktree:

```text
docs/reports/quality/backend-core-split-runtime-gates-2026-05-19.md
```

OpenSpec tasks updated:

```text
openspec/changes/split-backend-core-modules-with-compatibility-wrappers/tasks.md
```

Verification and risk checks:

```text
openspec validate split-backend-core-modules-with-compatibility-wrappers --strict
result: valid

GitNexus staged detect_changes
result: low risk, affected processes: 0
```

Committed and pushed:

```text
bbb399071 docs(core): record runtime gate evidence
remote: origin/wip/root-dirty-20260403
```

## Remaining Open Items

### R1. OpenSpec Task 3.2 Is Still Open

Current task:

```text
3.2 Introduce same-name packages with __init__.py re-exports.
```

Why it remains open:

- batch 1 introduced `app.core.validation` package re-exports;
- task wording may describe a broader same-name package strategy beyond the
  validation messages batch;
- marking it complete without scope review could overstate migration closure.

Required decision:

```text
Does the current validation package re-export satisfy 3.2 for this OpenSpec
change, or should 3.2 stay open until the broader package strategy is applied?
```

### R2. Issue #83 Evidence Must Be Reconciled

Issue `#83` should absorb the completed first-batch evidence and the runtime
gate evidence, but should not be moved forward only because one implementation
batch landed.

Required action:

- attach or cite the helper split evidence;
- attach or cite the runtime gate evidence;
- rerun or update the triage gate against the current state;
- keep status honest if the broader Core split still has unresolved task scope.

### R3. Unpublished Issue15 Draft Must Be Revised

The issue15 draft must stop asking for the already-completed first Core split
batch.

Required revision:

- cite the completed validation messages split;
- cite the runtime gate evidence report;
- ask for next-batch selection or wrapper retirement criteria instead of
  reopening batch 1.

### R4. OpenSpec Archive Is Not Yet Allowed

Do not archive
`split-backend-core-modules-with-compatibility-wrappers` until:

- task `3.2` is explicitly resolved;
- task status and evidence links are internally consistent;
- issue `#83` and issue15 are reconciled;
- `openspec validate ... --strict` still passes after any final task edits.

## Next Work Plan

### Step 1. Review And Decide Task 3.2

Owner lane:

```text
backend Core split governance / implementation coordination
```

Actions:

1. Re-read the OpenSpec proposal and task wording for
   `split-backend-core-modules-with-compatibility-wrappers`.
2. Inspect current package re-export evidence for `app.core.validation`.
3. Decide one of two outcomes:
   - mark `3.2` complete with a note that this change's same-name package scope
     is limited to batch 1;
   - keep `3.2` open and rewrite the next-batch work to include the broader
     same-name package strategy.

Acceptance:

```text
Task 3.2 has a defensible status and does not overclaim migration completion.
```

### Step 2. Prepare Issue #83 Evidence Reconciliation

Owner lane:

```text
backend OpenSpec issue governance
```

Actions:

1. Summarize the completed helper split evidence.
2. Summarize runtime gate evidence from
   `backend-core-split-runtime-gates-2026-05-19.md`.
3. State that 4.3 / 4.4 / 4.5 are closed by runtime evidence, not by unit tests.
4. State the remaining 3.2 decision explicitly.
5. Keep issue status gated by current triage criteria.

Acceptance:

```text
Issue #83 has a current evidence packet and no longer depends on stale PM2 /
health / OpenAPI blocker language.
```

### Step 3. Revise Issue15 Draft

Owner lane:

```text
backend OpenSpec publication governance
```

Actions:

1. Remove or reframe language asking to select the first low-risk Core split
   batch.
2. Cite the completed validation messages split and runtime gate evidence.
3. Convert issue15 into either:
   - a next-batch selection request; or
   - a wrapper retirement criteria request; or
   - a broader Core split continuation proposal.

Acceptance:

```text
Issue15 no longer duplicates completed work and has a clear post-batch1 purpose.
```

### Step 4. Select The Next Core Split Batch Only After Governance Reconciliation

Owner lane:

```text
backend Core implementation
```

Preconditions:

- Step 1 is complete;
- issue `#83` is reconciled;
- issue15 is revised or explicitly deferred;
- no unreviewed runtime blocker is being carried forward.

Candidate selection rules:

- prefer low-risk pure helpers with narrow import surfaces;
- avoid database, security, socketio, logger, and lifecycle-owned modules unless
  separate coordination evidence exists;
- define canonical target path, compatibility wrapper, rollback command, and
  wrapper retirement criteria before moving code;
- run GitNexus impact before editing symbols;
- use a clean implementation worktree.

Acceptance:

```text
The next batch has a bounded file set, expected import diff, expected OpenAPI
impact, rollback path, and verification commands before implementation starts.
```

### Step 5. Archive Only After All OpenSpec Tasks Are Fully Resolved

Owner lane:

```text
OpenSpec change owner
```

Actions:

1. Confirm all task checkboxes are accurate.
2. Run strict validation.
3. Archive only after the capability delta and task evidence are consistent.

Acceptance:

```text
OpenSpec archive is performed only after real completion, not after partial
runtime gate closure.
```

## Explicit Non-Goals For The Next Batch

- Do not start another Core split before resolving task `3.2`.
- Do not delete compatibility wrappers only because references appear low.
- Do not treat OpenAPI path count changes as harmless without path-level
  classification.
- Do not commit generated OpenAPI artifacts unless the batch explicitly requires
  them.
- Do not persist runtime secrets into tracked files.
- Do not use Prometheus / Grafana connection refusal as a blocker for backend
  startup unless the next task explicitly targets observability deployment.

## Review Questions

1. Should OpenSpec task `3.2` be scoped to the completed validation package
   re-export, or remain open for a broader same-name package strategy?
2. Should issue `#83` stay in triage until 3.2 is resolved, or can it move with
   a clearly documented remaining task?
3. Should issue15 become the next Core split batch selector, a wrapper
   retirement criteria issue, or a broader continuation proposal?
4. Is the OpenAPI path diff classification acceptable as unrelated to this Core
   split line, or should a separate route governance issue cite it explicitly?

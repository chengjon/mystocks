# Backend Core Split Runtime Gates

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Recorded at: `2026-05-19`

## Purpose

This report records the runtime evidence needed to reconcile OpenSpec tasks
`4.3`, `4.4`, and `4.5` for
`split-backend-core-modules-with-compatibility-wrappers`.

It follows the boundary in
`docs/reports/quality/backend-core-split-other-line-next-work-boundary-2026-05-19.md`:

- do not use import smoke or unit tests alone to close runtime gates;
- do not mix publication / governance artifacts with backend implementation;
- do not start the next Core split batch until runtime evidence is reconciled.

No database passwords, JWT secrets, or monitoring credentials are persisted in
this report. Runtime checks used session-provided environment values only.

## Worktree And Revision

```text
worktree: /opt/claude/mystocks_spec/.worktrees/contract-startup-unblock
branch: contract-startup-unblock
HEAD: 2d6682e81 fix(api): restore extracted route module imports
remote target: origin/wip/root-dirty-20260403
```

## Runtime Environment Preflight

TCP reachability was checked before accepting the runtime gate evidence.

| Dependency | Endpoint | Result | Interpretation |
|---|---:|---|---|
| PostgreSQL / TimescaleDB | `192.168.123.104:5438` | `tcp=ok` | available for backend runtime |
| TDengine native | `192.168.123.104:6030` | `tcp=ok` | available for backend runtime |
| TDengine REST | `192.168.123.104:6041` | `tcp=ok` | available for backend runtime |
| Redis | `localhost:6379` | `tcp=ok` | available for backend runtime |
| Prometheus | `192.168.123.104:9090` | `ConnectionRefusedError` | monitoring UI scrape target not required for this backend startup gate |
| Grafana | `192.168.123.104:3000` | `ConnectionRefusedError` | dashboard service not required for this backend startup gate |

## Task 4.3 Evidence: PM2 Backend Startup

Command class:

```text
pm2 backend-only startup using ecosystem.test.config.js with session-provided runtime DB environment
```

Observed PM2 state:

```text
name=mystocks-backend
status=online
restarts=0
pid=3258026
```

Result:

```text
OpenSpec task 4.3 is closed for this implementation line.
```

Post-run cleanup:

```text
pm2 delete all
pm2_processes=0
```

## Task 4.4 Evidence: Health And Readiness Smoke

Backend base URL during smoke:

```text
http://localhost:8020
```

Observed endpoint results:

| Endpoint | HTTP | success |
|---|---:|---|
| `/health` | `200` | `True` |
| `/api/health/services` | `200` | `True` |
| `/health/ready` | `200` | `True` |
| `/api/health/ready` | `200` | `True` |

Result:

```text
OpenSpec task 4.4 is closed for this implementation line.
```

## Task 4.5 Evidence: Route / OpenAPI Drift

Current runtime OpenAPI generation completed from `app.main` using the same PM2
runtime environment.

Observed current schema snapshot:

```text
paths=499
operations=535
duplicate_operation_ids=0
```

The isolated implementation worktree did not contain the generated
`docs/reports/quality/generated/openapi-before.json` baseline artifact. A
read-only comparison was therefore run against the existing root-worktree
baseline artifact for classification only.

Reference comparison:

```text
reference baseline: /opt/claude/mystocks_spec/docs/reports/quality/generated/openapi-before.json
baseline_paths=501
current_paths=499
added=8
removed=10
current_operations=535
duplicate_operation_ids=0
```

Added paths:

```text
/api/alerts
/api/alerts/{alert_id}/acknowledge
/api/alerts/{alert_id}/resolve
/api/config/mode
/api/metrics/trends
/api/mock/strategy/strategies
/api/status/overview
/api/test/quality
```

Removed paths:

```text
/api/data-quality/alerts
/api/data-quality/alerts/{alert_id}/acknowledge
/api/data-quality/alerts/{alert_id}/resolve
/api/data-quality/config/mode
/api/data-quality/health
/api/data-quality/metrics
/api/data-quality/metrics/trends
/api/data-quality/status/overview
/api/data-quality/test/quality
/api/strategy-mgmt/{path}
```

Classification:

- The non-zero path delta is not attributed to the Core validation helper split.
- The delta matches known route governance surfaces from the health /
  data-quality / strategy-mgmt compatibility work.
- The current schema has no duplicate `operationId` warnings.
- No additional route or OpenAPI drift attributable to the Core helper split or
  the startup import fixes was identified in this runtime gate.

Result:

```text
OpenSpec task 4.5 is closed for this implementation line, scoped to no
unexplained drift attributable to the Core helper split lane.
```

## Known Non-Blocking Runtime Warnings

These observations appeared during runtime import or startup and are not treated
as blockers for tasks `4.3`, `4.4`, or `4.5`:

- GPU / Numba compatibility warning: GPU backtest falls back to CPU/mock mode.
- Capital flow clustering reports GPU libraries unavailable and falls back to
  CPU.
- Prometheus and Grafana TCP checks refused connection; backend health and
  readiness did not depend on those services for this gate.

## Remaining Open Work For This Line

Do not start the next Core split batch until these are explicitly handled:

1. Review OpenSpec task `3.2` wording and decide whether the existing
   `app.core.validation` package re-export satisfies only batch 1 or the broader
   same-name package strategy.
2. Reconcile issue `#83` with the first-batch evidence and keep its triage
   status honest.
3. Revise the unpublished issue15 draft so it references the completed
   validation messages split instead of asking for that first split again.
4. Select the next Core split batch only after the evidence reconciliation above
   is accepted.

# G2.259 Signal History Postgres Async Provider Implementation

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: for review
- Prepared at: `2026-05-31T01:32:04+08:00`
- Branch: `g2-259-signal-history-postgres-provider`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `a58cf6490af4e4cd51e9b98543fa286244fdb78f`
- Parent authorization: G2.258, PR `#411`, merged at `a58cf6490af4e4cd51e9b98543fa286244fdb78f`
- OpenSpec lane: `migrate-backend-singletons-to-lifecycle-di`

Boundary note: this report records the G2.259 path-limited implementation. It
does not authorize broader `signal_monitoring/*` migrations, route contract
changes, OpenAPI exposure changes, frontend/config/script edits, PM2 commands,
or OpenSpec source/spec edits.

## Authorized Scope

G2.259 used the scope approved by G2.258:

- `web/backend/app/api/signal_monitoring/signal_history_response.py`
- `tests/api/file_tests/test_signal_monitoring_api.py`
- `web/backend/tests/test_signal_history_response_regressions.py`

The following remained out of scope:

- `web/backend/app/api/signal_monitoring/get_signal_statistics.py`
- other `web/backend/app/api/signal_monitoring/*` files
- infrastructure provider implementation under `src/**`
- route paths, route registration, or OpenAPI exposure policy
- frontend, config, scripts, PM2, and OpenSpec source/spec edits

## Implementation

G2.259 added one route-local provider:

- `get_signal_history_postgres_async`

The provider remains a thin FastAPI dependency wrapper around:

- `src.monitoring.infrastructure.postgresql_async_v3.get_postgres_async`

The following four authorized handlers now receive the postgres async provider
through `Depends(get_signal_history_postgres_async)`:

- `get_signal_history`
- `get_signal_quality_report`
- `get_strategy_realtime_monitoring`
- `health_check`

The four target route bodies no longer call `get_postgres_async()` directly.
The provider contains the single backing call. Route paths, response models,
summaries, response examples, and `include_in_schema` state were not changed.

## Test-Driven Development Evidence

RED was established before production source changes:

```text
PYTHONPATH=. pytest -q tests/api/file_tests/test_signal_monitoring_api.py::TestSignalMonitoringAPIFile::test_signal_history_handlers_use_postgres_dependency_provider -n 0 --tb=short --no-cov
```

Result:

- `1 failed`
- Failure reason: `get_signal_history_postgres_async` was missing.

GREEN after implementation:

```text
PYTHONPATH=. pytest -q tests/api/file_tests/test_signal_monitoring_api.py::TestSignalMonitoringAPIFile::test_signal_history_handlers_use_postgres_dependency_provider -n 0 --tb=short --no-cov
```

Result:

- `1 passed`

Focused verification:

```text
PYTHONPATH=. pytest -q tests/api/file_tests/test_signal_monitoring_api.py web/backend/tests/test_signal_history_response_regressions.py -n 0 --tb=short --no-cov
```

Result:

- `15 passed`

The file-level test also removed the pre-existing direct fixture import that
caused `F811` under `ruff --no-fix`. The regression test now supplies
`postgres_async=_FakePostgres()` directly and asserts the current dict response
shape returned by `create_success_response(...).dict(exclude_unset=True)`.

## Static And Contract Checks

Ruff:

```text
ruff check --no-fix web/backend/app/api/signal_monitoring/signal_history_response.py tests/api/file_tests/test_signal_monitoring_api.py web/backend/tests/test_signal_history_response_regressions.py
```

Result:

- `All checks passed!`

Residual scan:

| Metric | Result |
|---|---:|
| Provider `get_postgres_async()` calls | 1 |
| Target route-body direct `get_postgres_async()` calls | 0 |
| Target `postgres_async=Depends(...)` parameters | 4 |

OpenAPI smoke with placeholder environment:

| Metric | Result |
|---|---:|
| `app.routes` | 548 |
| `app.openapi()["paths"]` | 500 |
| Target route count | 4 |
| Target paths present in schema | 4 |
| Target `include_in_schema` | `true` |

Non-blocking OpenAPI smoke note:

- First smoke attempt failed because the placeholder environment omitted
  `BACKEND_BACKUP_PORT`; the rerun included that placeholder and passed.
- Import emitted the existing GPU warning:
  `Numba needs NumPy 2.2 or less. Got NumPy 2.4.`

OpenSpec:

```text
openspec validate migrate-backend-singletons-to-lifecycle-di --strict
```

Result:

- `Change 'migrate-backend-singletons-to-lifecycle-di' is valid`

## GitNexus Evidence

Pre-edit GitNexus MCP impact calls failed with `Transport closed`. The lane
used the GitNexus CLI fallback before source edits:

- `get_signal_history`: LOW risk, zero impacted execution flows
- `get_signal_quality_report`: LOW risk, zero impacted execution flows
- `get_strategy_realtime_monitoring`: LOW risk, zero impacted execution flows
- `health_check`: exact UID context review was used because the symbol name is
  ambiguous across the codebase

This degradation is recorded as tool availability evidence, not as a pass from
the MCP transport.

Staged `detect_changes` MCP failed with `Transport closed`. CLI fallback:

```text
npx gitnexus verify-staged -r mystocks --cwd /opt/claude/mystocks_spec/.worktrees/g2-259-signal-history-postgres-provider --json
```

Result:

- `ok: true`
- `status: stale`
- `risk_level: low`
- `changed_count: 13`
- `affected_count: 0`
- `changed_files: 12`
- stale reason: `current_commit_differs_from_indexed_commit`

Detailed staged verification is recorded in the generated evidence artifact:

- `.planning/codebase/generated/postgres-async-signal-history-provider-implementation-2026-05-31.json`

Mainline scope gate after commit:

```text
python governance/mainline/scripts/mainline_scope_gate.py --task-card governance/mainline/task-cards/pr-412.yaml --schema governance/mainline/schemas/ai-task-card.schema.json --base-sha a58cf6490af4e4cd51e9b98543fa286244fdb78f --head-sha HEAD --report /tmp/pr412-mainline-governance-report.json
```

Result:

- `pass=True`
- `problem_count=0`
- `changed_files_count=12`

## Review Checklist

- [ ] Scope remains limited to the G2.258 authorized files.
- [ ] The new provider is route-local and does not alter infrastructure backing behavior.
- [ ] The four authorized handlers use `Depends(get_signal_history_postgres_async)`.
- [ ] Direct route-body `get_postgres_async()` calls in the four target handlers are `0`.
- [ ] Route/OpenAPI contract remains unchanged at `548` routes and `500` OpenAPI paths.
- [ ] `get_signal_statistics.py` remains deferred.
- [ ] G2.260 is the next no-source closeout / residual-refresh gate, not a source lane.

## Next Gate

If this PR is accepted and merged, start G2.260 as a no-source closeout /
residual refresh:

- verify the G2.259 provider migration remains closed
- refresh active app-route `get_postgres_async()` residuals
- choose the next authorization candidate or declare the queue closed
- do not edit source from G2.260

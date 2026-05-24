# Backend Data Source Factory Provider Seam Implementation - 2026-05-24

> **历史总结说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: ready for review

Workline: G2.61a data-source factory provider seam implementation

Base branch: `wip/root-dirty-20260403`

Current HEAD before this branch: `ae6ba4e43b1470b524110fe506929df675bd8b93`

## Scope Boundary

G2.61a implements the provider-seam-only source batch authorized by G2.60.

This batch changes only:

- `web/backend/app/services/data_source_factory/data_source_factory.py`
- `web/backend/tests/test_data_source_factory_lifecycle_di.py`
- This implementation evidence report
- The generated evidence artifact
- The mainline task card
- The steward tree

This batch does not migrate route consumers, does not change route paths,
response contracts, OpenAPI exposure, generated clients, OpenSpec files, issue
labels, runtime process state, PM2 state, or compatibility getter cleanup.

## GitNexus Pre-Edit Evidence

GitNexus was refreshed from a temporary non-linked checkout:

- Checkout: `.worktrees/g2-61a-gitnexus-index-checkout`
- `.git` kind: `directory`
- HEAD: `ae6ba4e43b14`
- `gitnexus analyze` exit: `0`
- Nodes: `62636`
- Edges: `145807`
- Clusters: `3296`
- Flows: `300`

GitNexus context resolved `get_data_source_factory` to:

```text
web/backend/app/services/data_source_factory/data_source_factory.py
lines 294-300
```

Pre-edit upstream impact:

```text
risk=CRITICAL
impactedCount=22
direct=21
processes_affected=15
modules_affected=3
```

The CRITICAL risk is expected for this seam and is why G2.61a is limited to a
provider seam with `0` route calls migrated.

## Implementation

`data_source_factory.py` now exposes:

- `DATA_SOURCE_FACTORY_STATE_KEY`
- `install_data_source_factory(app, factory=None)`
- `get_data_source_factory_dependency(request)`

The existing compatibility getter remains unchanged in purpose:

- `get_data_source_factory()` still owns `_global_factory` fallback creation.
- `_global_factory` is preserved.
- Existing convenience functions still call `get_data_source_factory()`.

`get_data_source_factory_dependency(request)` reads an installed app-state
factory when present and falls back to `install_data_source_factory(request.app)`
when missing.

No API route imports or route handler signatures were changed.

## TDD Evidence

Red:

```text
pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short
3 failed, 1 passed
```

Expected red failures:

- Missing `install_data_source_factory`
- Missing `DATA_SOURCE_FACTORY_STATE_KEY`
- Missing `get_data_source_factory_dependency`

Green:

```text
pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short
4 passed
```

Existing data-source factory regression:

```text
pytest -o addopts= web/backend/tests/test_data_source_factory.py -q --no-cov --tb=short
38 passed
```

Route-adjacent runtime fallback regression:

```text
pytest -o addopts= web/backend/tests/test_data_stocks_runtime_fallback.py -q --no-cov --tb=short
1 passed
```

## Static Route Guard

Post-implementation static scan confirms no route migration occurred:

- API files scanned: `219`
- Direct `get_data_source_factory()` API calls: `17`
- `get_data_source_factory_dependency` API refs: `0`

The `17` route/API direct call sites remain intentionally unchanged for future
route-specific batches.

## App And OpenAPI Smoke

Initial app smoke without test env values failed at the environment validation
gate:

```text
missing POSTGRESQL_HOST, POSTGRESQL_USER, POSTGRESQL_PASSWORD,
JWT_SECRET_KEY, BACKEND_PORT, BACKEND_BACKUP_PORT
```

With non-secret test env values injected, app/OpenAPI smoke passed:

```text
app_import=passed
routes=548
openapi_paths=500
operation_ids=536
duplicate_operation_ids=0
```

This confirms the provider seam did not change route registration or OpenAPI
shape.

## Formatting And Lint

```text
ruff check web/backend/app/services/data_source_factory/data_source_factory.py web/backend/tests/test_data_source_factory_lifecycle_di.py
All checks passed
```

```text
black --check web/backend/app/services/data_source_factory/data_source_factory.py web/backend/tests/test_data_source_factory_lifecycle_di.py
2 files would be left unchanged
```

## Known Existing Test Debt

`tests/backend/test_data_api_regression.py` still fails with three `404` route
expectations:

- `/api/v1/data/stocks/basic`
- `/api/v1/data/markets/overview`
- `/api/v1/data/stocks/daily?symbol=000001`

The same three failures reproduce in the unmodified G2.61a GitNexus checkout at
HEAD `ae6ba4e43b14`, so they are current baseline route-test debt and not caused
by this provider seam.

This batch does not fix those tests because G2.61a explicitly forbids route
migration and route contract changes.

## Residuals

- Package-level re-export from `web/backend/app/services/data_source_factory/__init__.py`
  is not changed in this batch because G2.60 limited the source scope to the
  implementation module and focused test.
- Future route migration packets may either import the provider from the
  implementation module directly or authorize a separate package export update.
- All `17` direct API route calls remain to be handled by later reviewed
  route-specific packets.

## Next Gate

Human review this implementation PR.

If accepted, create G2.61a closeout / current-head refresh before selecting the
first route migration batch. The currently recommended first route migration
candidate remains `web/backend/app/api/data_quality.py`, but it is not
authorized by this implementation PR.

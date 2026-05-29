# Backend Data-Source Config Manager Provider Injection

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2 lane: `G2.233`
- Status: for review
- Prepared at: `2026-05-29T16:50:00+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `1f63a46657858920a3df9799ffc0c45ccf3b3dd8`
- Parent: G2.232 / PR `#385`

Boundary: this implementation uses the G2.232 authorization. It changes only the
active data-source config route/provider seam and focused tests. It does not
authorize edits to the legacy `.old.py` file, response constants module,
route paths, OpenAPI exposure, frontend, config, scripts, or OpenSpec state.

## Parent Authorization

G2.232 was merged by PR `#385` at
`1f63a46657858920a3df9799ffc0c45ccf3b3dd8` and authorized a future path-limited
implementation for active `web/backend/app/api/data_source_config.py`
`get_config_manager()` route-body calls.

Authorized source/test scope:

| Scope | Paths |
|---|---|
| Source | `web/backend/app/api/data_source_config.py` |
| Tests | `tests/api/file_tests/test_data_source_config_api.py`, `web/backend/tests/test_data_source_config_provider_injection.py` |
| Explicitly out of scope | `web/backend/app/api/data_source_config.old.py`, `web/backend/app/api/_data_source_config_responses.py` |

## GitNexus Impact

Before source edits, GitNexus impact was run for `get_config_manager`:

| Metric | Value |
|---|---:|
| Target | `web/backend/app/api/_data_source_config_responses.py:get_config_manager` |
| Risk | HIGH |
| Impacted count | 9 |
| Direct callers | 9 |
| Affected processes | 3 |
| Affected modules | 1 (`Api`) |

This is why the implementation remains path-limited and does not alter the
backing getter or legacy compatibility file.

## Implementation

G2.233 adds route-local FastAPI dependency injection in
`web/backend/app/api/data_source_config.py`:

- Adds `get_config_manager_dependency()`.
- Injects `manager: Any = Depends(get_config_manager_dependency)` into all 9 active handlers.
- Removes direct route-body `manager = get_config_manager()` calls from those handlers.
- Keeps `get_config_manager()` as the default backing getter.
- Keeps `data_source_config.old.py` unchanged and classified as a legacy false-positive surface.
- Keeps `_data_source_config_responses.py` unchanged; response constants, `router`,
  `get_current_user`, and backing `get_config_manager` remain where they were.

Changed active handlers:

| Handler | Provider state |
|---|---|
| `create_data_source` | `manager` injected |
| `update_data_source` | `manager` injected |
| `delete_data_source` | `manager` injected |
| `get_data_source` | `manager` injected |
| `list_data_sources` | `manager` injected |
| `batch_operations` | `manager` injected |
| `get_version_history` | `manager` injected |
| `rollback_to_version` | `manager` injected |
| `reload_config` | `manager` injected |

## Before / After

| Metric | Before | After |
|---|---:|---:|
| Active route-body `get_config_manager()` calls | 9 | 0 |
| Active `manager` dependency parameters | 0 | 9 |
| Route-local provider wrapper definitions | 0 | 1 |
| Legacy `.old.py` calls | 8 | 8 |
| Legacy `.old.py` edited | No | No |
| Backing getter edited | No | No |

## TDD Evidence

RED:

```text
pytest -o addopts= web/backend/tests/test_data_source_config_provider_injection.py -q --no-cov --tb=short
2 failed
```

Failure reasons:

- `get_config_manager_dependency` was absent.
- 9 active route handlers still called `get_config_manager()` in route bodies.

GREEN:

```text
pytest -o addopts= web/backend/tests/test_data_source_config_provider_injection.py -q --no-cov --tb=short
2 passed
```

Focused contract regression:

```text
pytest -o addopts= tests/api/file_tests/test_data_source_config_api.py web/backend/tests/test_data_source_config_provider_injection.py -q --no-cov --tb=short
12 passed
```

## Verification

| Check | Result |
|---|---|
| `ruff check web/backend/app/api/data_source_config.py web/backend/tests/test_data_source_config_provider_injection.py tests/api/file_tests/test_data_source_config_api.py` | Passed |
| app/OpenAPI smoke | `routes=548`, `paths=500` |
| Direct getter scan | `route_body_direct_getter_calls=0`, `dependency_parameters=9` |

## Preserved Invariants

- Route paths remain unchanged.
- Router registration remains unchanged.
- Auth/current-user dependency behavior remains unchanged.
- Response models and `UnifiedResponse` shape remain unchanged.
- OpenAPI exposure remains unchanged.
- Default backing `get_config_manager()` behavior remains unchanged.
- Legacy `data_source_config.old.py` remains untouched.

## Next Gate

If this implementation is accepted, start G2.234 no-source data-source config
manager provider injection closeout / residual refresh. G2.234 should confirm
post-merge state, classify remaining residuals, and select the next gate without
opening source edits directly.

# Backend Watchlist Service Lifecycle DI Implementation - 2026-05-22

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: implementation-prepared-for-review
- Workline: G2.10 watchlist service lifecycle DI implementation
- Parent issue: https://github.com/chengjon/mystocks/issues/79
- Parent decision issue: https://github.com/chengjon/mystocks/issues/92
- Authorization PR: https://github.com/chengjon/mystocks/pull/149
- Authorization merge commit: `bddb764c79355e6c0c366fdd9a28d64a685700bf`
- Implementation branch: `g2-10-watchlist-service-di-implementation`
- Source implementation scope: route-surface-only

## Governance Boundary

This implementation follows the G2.9 authorization packet. It edits only the
watchlist service provider, seven watchlist group route handlers, focused tests,
this report, the steward tree, and the PR task card.

It does not modify watchlist adapter/data-layer helper files, route paths,
request models, response shapes, OpenAPI exposure policy, generated clients,
frontend source, OpenSpec changes/specs, PM2 scripts, runtime process state, or
issue labels.

## Pre-Edit Gates

`architecture/STANDARDS.md` was read before source edits. The applicable
constraints are:

- preserve compatibility surfaces during migration
- do not delete or retire shim/compatibility callers based only on static search
- keep route/API layer changes scoped to the authorized seam
- keep implementation tied to evidence, tests, and rollback boundaries

GitNexus pre-edit impact:

| Target | Risk | Impact summary |
|---|---:|---|
| `WatchlistService` | LOW | 0 impacted symbols, 0 direct callers, 0 affected processes |
| `get_watchlist_service` | MEDIUM | 15 impacted symbols, 9 direct callers, 0 affected processes |

The `get_watchlist_service` direct callers split into:

- seven `web/backend/app/api/watchlist.py` route handlers migrated in this PR
- two adapter/data helper callers intentionally retained as compatibility
  surfaces:
  - `web/backend/app/services/data_adapters/watchlist.py::_get_watchlist_service`
  - `web/backend/app/services/adapters/watchlist_adapter.py::_get_watchlist_service`

## TDD Evidence

New test:

- `web/backend/tests/test_watchlist_service_lifecycle_di.py`

Red run before implementation:

```text
3 failed
AttributeError: module 'app.services.watchlist_service' has no attribute 'get_watchlist_service_dependency'
AssertionError: 'service' not in get_user_groups signature
TypeError: get_user_groups() got an unexpected keyword argument 'service'
```

Green run after implementation:

```text
3 passed in 1.61s
```

Post-format rerun:

```text
3 passed in 1.64s
```

## Implementation Summary

`web/backend/app/services/watchlist_service.py` now provides:

- `WATCHLIST_SERVICE_STATE_KEY`
- `install_watchlist_service(app, service=None)`
- `get_watchlist_service_dependency(request)`

`get_watchlist_service()` remains unchanged as the compatibility singleton
getter for adapter/data-layer helper callers.

`web/backend/app/api/watchlist.py` now injects `WatchlistService` into these
seven route handlers:

| Function | Route surface | Change |
|---|---|---|
| `get_user_groups` | `GET /groups` | route receives injected `service` |
| `create_group` | `POST /groups` | route receives injected `service` |
| `update_group` | `PUT /groups/{group_id}` | route receives injected `service` |
| `delete_group` | `DELETE /groups/{group_id}` | route receives injected `service` |
| `get_watchlist_by_group` | `GET /group/{group_id}` | route receives injected `service` |
| `move_stock_to_group` | `PUT /move` | route receives injected `service` |
| `get_watchlist_with_groups` | `GET /with-groups` | route receives injected `service` |

## Compatibility Guard

Post-implementation static guard:

```text
web/backend/app/api/watchlist.py: get_watchlist_service()=0, dependency_tokens=8
web/backend/app/services/data_adapters/watchlist.py: get_watchlist_service()=9, dependency_tokens=0
web/backend/app/services/adapters/watchlist_adapter.py: get_watchlist_service()=9, dependency_tokens=0
```

All seven migrated route functions have the injected service parameter and no
route-body `get_watchlist_service()` call.

The two adapter/data helper files were not modified.

## Verification

| Check | Result |
|---|---|
| `ruff check web/backend/app/services/watchlist_service.py web/backend/app/api/watchlist.py web/backend/tests/test_watchlist_service_lifecycle_di.py` | passed |
| `black --check web/backend/app/services/watchlist_service.py web/backend/app/api/watchlist.py web/backend/tests/test_watchlist_service_lifecycle_di.py` | passed; 3 files unchanged after formatting |
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_watchlist_service_lifecycle_di.py -q --no-cov --tb=short` | 3 passed |
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_watchlist_service_lifecycle_di.py web/backend/tests/test_watchlist_service_logging.py tests/api/file_tests/test_watchlist_api.py tests/api/test_watchlist_file.py -q --no-cov --tb=short` | 42 passed |
| `app.main` import with required placeholder env | routes=548 |
| `app.openapi()` smoke with required placeholder env | paths=500, operations=536, duplicate_operation_ids=0 |

The initial `app.main` smoke without placeholder env failed because the checkout
lacked required environment variables:

```text
POSTGRESQL_HOST, POSTGRESQL_USER, POSTGRESQL_PASSWORD, JWT_SECRET_KEY,
BACKEND_PORT, BACKEND_BACKUP_PORT
```

The placeholder-env smoke passed and did not expose a route/OpenAPI regression.

## Rollback Plan

If review or CI rejects this implementation:

1. Revert this PR.
2. Restore the seven watchlist group route handlers to direct
   `get_watchlist_service()` calls.
3. Remove `get_watchlist_service_dependency`, `install_watchlist_service`, and
   `WATCHLIST_SERVICE_STATE_KEY` as one unit if the provider seam is reverted.
4. Remove `web/backend/tests/test_watchlist_service_lifecycle_di.py`.
5. Leave watchlist adapter/data helper files unchanged.

## Next Gate

PR review and merge decision for this route-surface-only implementation.

After merge, create a separate closeout packet that records the merge commit,
GitHub checks, and whether a fourth service DI candidate should be selected.

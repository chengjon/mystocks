# Backend MarketDataServiceV2 Dashboard Helper Provider Migration Implementation - 2026-05-23

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Workline: G2.32 `MarketDataServiceV2` dashboard helper provider migration
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `0b838356e51e11f2ad27f9d3c898583611520622`
- Parent approval: PR `#171` merged at `0b838356e51e11f2ad27f9d3c898583611520622`
- Scope: approved source implementation plus focused tests and evidence

Boundary note: this packet implements only the G2.31-approved dashboard helper
provider migration. It does not authorize broader backend refactors,
`market_v2.py` edits, route path changes, OpenAPI contract changes, OpenSpec
changes, issue label movement, PM2/frontend/docs/API changes, service
consolidation, or deletion/privatization of `get_market_data_service_v2()`.

## What Changed

`web/backend/app/api/dashboard_data_source.py`

- `RealBusinessDataSource` now accepts an optional `MarketDataServiceV2`
  instance and a narrow fallback provider callable.
- `_get_market_overview_data()` now gets the service from the instance-level
  provider path instead of directly calling `get_market_data_service_v2()`.
- `prewarm_dashboard_market_overview_cache()` can receive an explicit
  `MarketDataServiceV2` instance.
- `get_data_source(market_service=None)` preserves direct-call compatibility.
- `get_data_source_dependency()` provides the FastAPI dependency bridge through
  `get_market_data_service_v2_dependency`.

`web/backend/app/api/dashboard.py`

- `/summary` now receives the dashboard data source as a dependency parameter
  instead of calling `get_data_source()` inside the route body.
- `/market-overview` and `/health` now use `Depends(get_data_source_dependency)`.

`web/backend/app/main.py`

- Startup prewarm now installs/gets the app-state `MarketDataServiceV2` instance
  and passes it into `prewarm_dashboard_market_overview_cache()`.

`web/backend/tests/test_dashboard_data_source.py`

- Adds regression coverage for injected dashboard market service usage.
- Adds prewarm injection coverage.
- Adds dashboard summary route dependency coverage.
- Adds a static guard that `dashboard_data_source.py` no longer directly calls
  `get_market_data_service_v2()`.

## What Did Not Change

- `web/backend/app/api/market_v2.py` was not edited.
- `get_market_data_service_v2()` remains public and defined in
  `market_data_service_v2.py`.
- `install_market_data_service_v2()` still preserves fallback behavior.
- Route paths, HTTP methods, response models, OpenAPI examples, and operation
  IDs are unchanged.
- No OpenSpec files, frontend files, PM2 scripts, docs/API files, generated
  clients, or issue labels were changed.

## TDD Evidence

RED command:

`env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_dashboard_data_source.py -q --no-cov --tb=short`

Observed failures before implementation:

- `RealBusinessDataSource.__init__()` did not accept `market_service`
- `prewarm_dashboard_market_overview_cache()` did not accept an injected service
- `get_dashboard_summary()` did not accept injected `data_source`
- `dashboard_data_source.py` still contained direct
  `get_market_data_service_v2()` calls

GREEN command:

`env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_dashboard_data_source.py web/backend/tests/test_market_data_service_v2_lifecycle_di.py -q --no-cov --tb=short`

Result: `11 passed in 3.85s` after formatting.

## Verification Evidence

| Check | Result |
|---|---|
| Focused pytest | `11 passed in 3.85s` |
| Ruff touched files | `All checks passed!` |
| Black touched files | `5 files would be left unchanged` |
| `app.main` import smoke | `app.main import ok` |
| OpenAPI smoke | `paths=500`, `/api/v2/market` paths=`13`, duplicate operation IDs=`0` |
| `market_v2.py` direct getter calls | `0` |
| `dashboard_data_source.py` direct getter calls | `0` |
| `market_data_service_v2.py` getter definitions | `1` |
| `dashboard.py` direct `get_data_source()` route-body calls | `0` |

The `app.main` and OpenAPI smoke emitted an existing GPU dependency warning:
`Numba needs NumPy 2.2 or less. Got NumPy 2.4.` The smoke commands still exited
successfully and produced the expected results.

## GitNexus Pre-Edit Evidence

| Target | Risk | Interpretation |
|---|---:|---|
| `get_market_data_service_v2` | CRITICAL | Expected known compatibility surface; retained, not renamed, not privatized |
| `RealBusinessDataSource` | LOW | Safe to add constructor injection with focused tests |
| `dashboard_data_source.py` | MEDIUM | Direct import consumers include `dashboard.py`, `main.py`, focused tests, and dashboard integration tests |
| `web/backend/app/api/dashboard.py` | LOW | Route source edit only, no route/OpenAPI contract change intended |
| `web/backend/app/main.py` | CRITICAL | File-level import impact is broad, so change is limited to startup prewarm argument passing and verified with import/OpenAPI smoke |
| `prewarm_dashboard_market_overview_cache` | LOW | Narrow helper change covered by focused test |

## Rollback

Revert this PR as a unit. The rollback restores:

- dashboard helper direct compatibility getter calls
- `get_dashboard_summary()` route-body `get_data_source()` construction
- startup prewarm without an explicit service argument
- the focused tests and evidence added by this batch

Earlier PRs `#167` through `#171` remain valid unless separately reverted.

## Decision

G2.32 is ready for human review.

If accepted, the steward tree should record the dashboard helper provider
migration as implemented. The next service lifecycle DI lane should be selected
by a fresh candidate refresh rather than immediately deleting
`get_market_data_service_v2()`, because the compatibility getter remains an
intentional fallback for `install_market_data_service_v2()`.

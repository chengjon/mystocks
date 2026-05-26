# Backend Indicator/Data Design Authorization

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-27

Status: Ready for review

Scope: G2.159 design and authorization package only.

Base HEAD: `aef7e765b0c0472c2b2f907463345c964735b1f9`

Parent: G2.158, PR `#311`, merged as `aef7e765b0c0472c2b2f907463345c964735b1f9`.

Boundary: this is a design-authorization package only. It does not edit backend source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or service getter implementations. It does not perform implementation.

## Decision

Do not open Indicator/Data source implementation yet.

Authorize the next gate as G2.160: Indicator/Data test-contract alignment package.

Reason: the Indicator/Data getter seam is small enough for a future implementation lane, but current focused verification shows an existing v1 indicator regression test still expects `HTTPException`, while the current code raises the canonical `BusinessException` contract. That test-contract debt should be aligned before changing `get_data_service` consumers.

## GitNexus Evidence

| Symbol | Risk | Impacted | Direct callers | Processes |
|---|---:|---:|---:|---:|
| `get_data_service` | CRITICAL | 5 | 3 | 7 |
| `calculate_indicators` | LOW | 0 | 0 | 0 |
| `_calculate_single_indicator` | LOW | 3 | 1 | 0 |
| `calculate_single_request` | LOW | 2 | 1 | 0 |
| `limited_calculate` | LOW | 1 | 1 | 0 |

`get_data_service` direct callers:

- `web/backend/app/api/indicators/indicator_cache.py::calculate_indicators`
- `web/backend/app/api/indicators/indicator_cache.py::_calculate_single_indicator`
- `web/backend/app/api/v1/strategy/indicators.py::get_technical_indicators`

Downstream callers:

- `web/backend/app/api/indicators/indicator_cache.py::calculate_single_request`
- `web/backend/app/api/indicators/indicator_cache.py::limited_calculate`
- `web/backend/app/api/indicators/indicator_cache.py::calculate_indicators_batch`

`get_technical_indicators` is an ambiguous symbol name in GitNexus. This package used `context(name="get_technical_indicators", file_path="web/backend/app/api/v1/strategy/indicators.py")` to pin the intended route function.

## Current-Head Hit Classification

| File | Line | Classification | Text |
|---|---:|---|---|
| `web/backend/app/services/data_service.py` | 466 | definition | `def get_data_service() -> DataService:` |
| `web/backend/app/api/indicators/indicator_cache.py` | 40 | import | imports `get_data_service` |
| `web/backend/app/api/indicators/indicator_cache.py` | 343 | direct body call | `data_service = get_data_service()` |
| `web/backend/app/api/indicators/indicator_cache.py` | 613 | direct body call | `data_service = get_data_service()` |
| `web/backend/app/api/v1/strategy/indicators.py` | 17 | import | imports `get_data_service` |
| `web/backend/app/api/v1/strategy/indicators.py` | 201 | direct body call | `get_data_service().get_daily_ohlcv(...)` |
| `web/backend/tests/test_v1_indicators_regressions.py` | 39 | test monkeypatch | `module.get_data_service = lambda: _FakeDataService()` |
| `web/backend/tests/test_v1_indicators_regressions.py` | 56 | test monkeypatch | `module.get_data_service = lambda: _FakeDataService()` |
| `web/backend/tests/test_integration_e2e.py` | 198/201 | test import/reference | direct service smoke |
| `web/backend/tests/test_integration_e2e.py` | 233/235 | test import/reference | direct service smoke |

Direct application body calls: `3`.

## Consumer Contract Matrix

| Consumer | Surface | Current getter use | Contract to preserve |
|---|---|---|---|
| `calculate_indicators` | public indicator calculation flow | direct body call at `indicator_cache.py:343` | `UnifiedResponse[Dict]`, `create_success_response`, request validation, OHLCV retrieval, cache/accounting behavior, `InvalidDateRangeError -> ValidationException`, `StockDataNotFoundError -> NotFoundException`, `BusinessException` propagation |
| `_calculate_single_indicator` | helper used by single/batch calculation paths | direct body call at `indicator_cache.py:613` | result dict shape, symbol/date semantics, `calculate_single_request`, `limited_calculate`, and `calculate_indicators_batch` behavior |
| `get_technical_indicators` | v1 strategy indicator API flow | direct body call at `strategy/indicators.py:201` | indicator normalization, `get_daily_ohlcv` behavior, pagination payload, unsupported indicator `BusinessException 400`, missing data `BusinessException 404`, generic fetch failure `BusinessException 500` |

## Verification

| Check | Result |
|---|---|
| `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_indicator_registry_route_provider.py -q --no-cov --tb=short` | 2 passed in 2.05s |
| `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_v1_indicators_regressions.py -q --no-cov --tb=short` | 1 failed, 1 passed in 1.81s |
| indicator-related test discovery | 18 candidate files |

The failed test is `test_v1_indicators_rejects_unsupported_indicator`.

Observed failure:

- implementation raises `app.core.exceptions.BusinessException`;
- test attempts to catch `module.HTTPException`;
- module `app.api.v1.strategy.indicators` no longer exposes `HTTPException`.

This is consistent with the repository's canonical exception direction. It is a test-contract alignment blocker, not evidence that G2.159 should edit source code.

## G2.160 Authorization

G2.160 should be a narrow Indicator/Data test-contract alignment package.

Allowed G2.160 scope:

- `web/backend/tests/test_v1_indicators_regressions.py`
- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `.planning/codebase/generated/*indicator-data*.json`
- `docs/reports/quality/*indicator-data*.md`
- `governance/mainline/task-cards/pr-*.yaml`

G2.160 should align `test_v1_indicators_rejects_unsupported_indicator` with the canonical `BusinessException` contract or produce a review note explaining why the route-level HTTP translation should be tested differently.

G2.160 must not modify application source unless a separate review explicitly authorizes it.

## Eventual Source Lane Conditions

After G2.160 passes, a later Indicator/Data source lane may be considered, but it must still be separately reviewed and approved.

Potential source paths for that later lane:

- `web/backend/app/api/indicators/indicator_cache.py`
- `web/backend/app/api/v1/strategy/indicators.py`

Potential focused test paths:

- `web/backend/tests/test_v1_indicators_regressions.py`
- `web/backend/tests/test_indicator_registry_route_provider.py`
- `web/backend/tests/test_integration_e2e.py`
- `web/backend/tests/test_health_route_conflicts.py`

Required gates before any source edit:

- fresh GitNexus impact for `get_data_service` and the direct caller being edited;
- current-head hit classification;
- focused tests passing after G2.160 alignment;
- route/OpenAPI drift check if a public route dependency, response envelope, or documented example changes;
- staged GitNexus detect before commit.

Stop conditions:

- do not edit `web/backend/app/services/data_service.py` without a new review;
- do not delete or privatize `get_data_service()`;
- do not touch Strategy adapter, root facade compatibility, or route dependency/provider governance surfaces;
- do not change OpenAPI exposure or route paths from an Indicator/Data getter lane.

## Next Gate

Review this package. If accepted, start G2.160 as a narrow test-contract alignment package. Do not start Indicator/Data source implementation from G2.159.

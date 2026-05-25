# Backend MarketDataService Getter Retirement Closeout - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.113 MarketDataService getter-retirement closeout/current-head refresh
Status: ready for review

## Purpose

Close out the G2.111 -> G2.112 MarketDataService package-level getter retirement
lane after PR `#265` was merged.

This is a governance-only current-head refresh. It does not edit backend source,
tests, route/API contracts, OpenAPI exposure, frontend code, PM2 workflows,
OpenSpec changes, GitHub issue labels, or service lifecycle implementation
logic.

## Parent Gate

| Gate | Result |
|---|---|
| Parent implementation | G2.112 accepted in PR `#265` |
| Parent merge commit | `b5ca0c5fcf65de77e7bf336091c4ae3f220019ef` |
| Current closeout base | `b5ca0c5fcf65de77e7bf336091c4ae3f220019ef` |
| Closeout scope | current-head scan, regression evidence, steward tree update, generated artifact, and task card |

## Current-Head Scan

| Surface | Result |
|---|---|
| Backend app/test Python files scanned | `775` |
| `market_data_service/get_market_data_service.py:def get_market_data_service` | `0` |
| `market_data_service/get_market_data_service.py:_market_data_service` | `0` |
| `from app.services.market_data_service import get_market_data_service` | `0` |
| `market_data_adapter.py` calls to `get_market_data_service()` | `0` |
| Root-level `web/backend/app/services/__init__.py:get_market_data_service` | preserved |

The remaining test-file mention of `_market_data_service` is the retirement
assertion in `test_market_data_service_getter_retirement.py`.

## Verification

| Check | Command | Result |
|---|---|---|
| Focused market-data tests | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_market_data_service_getter_retirement.py web/backend/tests/test_market_data_service_lifecycle_di.py -q --no-cov --tb=short` | `7 passed` |
| Health route conflicts | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | `120 passed` |

## Boundary

This PR does not:

- modify backend source or tests
- modify route paths, response models, response shapes, or OpenAPI exposure
- modify frontend code
- modify PM2 workflows
- create or modify OpenSpec proposals/specs
- change GitHub issue labels or readiness state
- delete or rename any service symbol
- select the next service getter candidate

## Next Gate

Human review / PR merge decision for G2.113.

If accepted, run a fresh service lifecycle candidate refresh before selecting
another service getter candidate.

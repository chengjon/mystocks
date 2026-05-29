# Backend Monitoring Calculator Factory Provider Injection

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2: `G2.238`
- Status: implementation for review
- Prepared at: `2026-05-29T20:34:17+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `ef11ae6577bf62d15b814af732ba291696e5b084`
- Parent: G2.237, PR `#390`, merge commit `ef11ae6577bf62d15b814af732ba291696e5b084`

## Scope

G2.238 implements the path-limited provider injection authorized by G2.237:

- `web/backend/app/api/monitoring_analysis.py`
- `web/backend/app/api/_monitoring_portfolio_router.py`
- `tests/api/file_tests/test_monitoring_analysis_api.py`

No other runtime source or test file is in scope.

## Implementation

The implementation adds local FastAPI dependency providers named
`get_monitoring_calculator_factory` in both authorized API modules. The provider
keeps the domain import lazy and delegates to the existing
`src.monitoring.domain.calculator_factory.get_calculator_factory`.

Then the 8 active route handlers receive `calculator_factory` through
`Depends(get_monitoring_calculator_factory)` and assign it to the existing local
`factory` variable. This preserves the handler body behavior while moving the
factory lookup out of route-body execution.

## Route Consumer Result

| File | Provider line | Target handlers | Direct route-body calls after |
|---|---:|---:|---:|
| `web/backend/app/api/monitoring_analysis.py` | 46 | 5 | 0 |
| `web/backend/app/api/_monitoring_portfolio_router.py` | 102 | 3 | 0 |

Total:

- Provider functions: 2
- Target route handlers: 8
- Direct route-body `get_calculator_factory()` calls after: 0
- FastAPI dependency parameters after: 8

## TDD Evidence

RED:

```text
pytest -o addopts= tests/api/file_tests/test_monitoring_analysis_api.py::TestMonitoringAnalysisAPIFile::test_monitoring_calculator_factory_uses_route_dependency_provider -q --no-cov --tb=short
```

Result before implementation:

```text
AssertionError: get_monitoring_calculator_factory not found in module
```

GREEN:

```text
pytest -o addopts= tests/api/file_tests/test_monitoring_analysis_api.py::TestMonitoringAnalysisAPIFile::test_monitoring_calculator_factory_uses_route_dependency_provider -q --no-cov --tb=short
```

Result after implementation:

```text
1 passed
```

## Verification

| Check | Result |
|---|---|
| GitNexus impact before edit | HIGH, 9 impacted, 9 direct, 3 affected processes, 2 modules; MCP transport closed, CLI fallback used |
| Focused monitoring API tests | `17 passed` |
| Health route conflicts collect-only | `121 tests collected` |
| Ruff on authorized files | `All checks passed` |
| app/OpenAPI smoke | `routes=548`, `paths=500` |
| Static route-body guard | 2 providers, 8 target handlers, 0 direct route-body calls |

## Preserved Boundaries

G2.238 does not change:

- `src/monitoring/domain/calculator_factory.py`
- calculator construction behavior
- GPU/CPU/risk calculator selection semantics
- route paths
- OpenAPI path count
- response models
- `UnifiedResponse` contracts
- frontend code
- OpenSpec changes
- config or scripts

G2.238 also keeps `get_mock_data_manager`, `get_monitoring_db`, and
`get_postgres_async` outside the lane.

## Rollback

Revert the G2.238 PR. The two API modules return to route-body factory lookup
and the focused static guard test is removed.

## Next Gate

If accepted, start G2.239 as a no-source closeout / residual refresh for the
monitoring calculator factory provider injection lane. Do not use G2.238 to
expand into another source lane.

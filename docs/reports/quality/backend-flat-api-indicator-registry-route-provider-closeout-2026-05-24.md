# Backend Flat API IndicatorRegistry Route Provider Closeout - 2026-05-24

> **历史总结说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.55 closeout/current-head refresh after G2.54 flat API
`IndicatorRegistry` route-provider implementation.

Base branch: `wip/root-dirty-20260403`
Current HEAD: `5b12a3c08cac`
Generated at: `2026-05-24T17:38:30+08:00`

## Status

`READY_FOR_REVIEW`.

This packet is closeout evidence only. It does not change backend source, tests,
route paths, OpenAPI output, runtime behavior, or issue/OpenSpec state.

## Merge Evidence

| PR | State | Merge commit | Notes |
| --- | --- | --- | --- |
| `#195` | `MERGED` | `5b12a3c08cac3558c56af615ff14c05913d96f72` | G2.54 flat API `IndicatorRegistry` route-provider implementation |

PR `#195` remote checks were green before merge:

```text
Validate API Contracts=pass
Mainline Governance Gate=pass
check-compliance=pass
weekly-full-scan=skipping
```

## Current-Head Closeout Evidence

Provider surface is present in
`web/backend/app/services/indicator_registry.py`:

```text
line 631: INDICATOR_REGISTRY_STATE_KEY = "indicator_registry"
line 642: def install_indicator_registry(app: Any, registry: IndicatorRegistry | None = None) -> IndicatorRegistry:
line 649: def get_indicator_registry_dependency(request: Request) -> IndicatorRegistry:
line 651: registry = getattr(request.app.state, INDICATOR_REGISTRY_STATE_KEY, None)
```

Route dependency usage is present in
`web/backend/app/api/indicators/indicator_cache.py`:

```text
line 42: from app.services.indicator_registry import IndicatorCategory, IndicatorRegistry, get_indicator_registry_dependency
line 80: registry: IndicatorRegistry = Depends(get_indicator_registry_dependency),
line 201: registry: IndicatorRegistry = Depends(get_indicator_registry_dependency),
```

Route direct getter calls are closed:

```text
get_indicator_registry() references under web/backend/app/api: 0
```

Remaining `get_indicator_registry()` references are intentional compatibility
and non-route surfaces:

```text
web/backend/app/services/indicator_calculator.py:43 self.registry = get_indicator_registry()
web/backend/app/services/indicator_registry.py:634 def get_indicator_registry() -> IndicatorRegistry:
web/backend/app/services/indicator_registry.py:644 selected_registry = registry if registry is not None else get_indicator_registry()
web/backend/app/services/indicators/defaults.py:36 v2_registry = get_indicator_registry()
web/backend/app/services/indicators/talib_adapter.py:39 registry = get_indicator_registry()
unit tests for the package registry singleton behavior
```

The package registry and startup/jobs surface remain out of scope for this
route-provider batch.

## Runtime And Contract Evidence

Configured app/OpenAPI smoke used non-sensitive placeholder environment
variables only. It did not run PM2, intentionally connect to production
resources, or authorize runtime promotion.

```text
routes_total=548
openapi_paths_total=500
duplicate_operation_ids=0
warnings=0
selected_indicator_cache_routes=6
```

Selected route inventory remains unchanged:

```text
GET  /api/v1/indicators/registry
GET  /api/v1/indicators/registry/{category}
POST /api/v1/indicators/calculate
POST /api/v1/indicators/calculate/batch
GET  /api/v1/indicators/cache/stats
POST /api/v1/indicators/cache/clear
```

Focused checks:

```text
pytest -o addopts= web/backend/tests/test_indicator_registry_route_provider.py -q --tb=short --no-cov
2 passed in 1.68s

pytest -o addopts= web/backend/tests/test_health_route_conflicts.py::test_v1_indicator_endpoints_have_examples_parameter_docs_and_descriptions -q --tb=short --no-cov
1 passed in 11.87s
```

## Provider Inventory Refresh

Static provider scan at current HEAD:

```text
service provider/state-key records=29
```

This count includes state keys, install functions, and dependency functions
across existing service lifecycle DI surfaces. The new flat API indicator
registry provider contributes:

```text
INDICATOR_REGISTRY_STATE_KEY
install_indicator_registry
get_indicator_registry_dependency
```

## GitNexus Note

GitNexus context still resolved `get_indicator_registry()` to stale pre-merge
route callers and did not yet resolve the new `get_indicator_registry_dependency`
or `install_indicator_registry` symbols after PR `#195`.

For this closeout packet, current-head static code evidence and runtime/OpenAPI
smoke are treated as authoritative. Refresh the GitNexus index before using
graph impact results to select the next implementation lane.

## Residual Debt

Known residual test debt from G2.54 remains:

```text
web/backend/tests/test_indicators.py
legacy /api/indicators/* path assertions receive 404 while active routes are /api/v1/indicators/*
```

This closeout does not reopen that test debt or broaden the route-provider
implementation scope.

## Decision

G2.54 is closed as implemented and merged.

The flat API `IndicatorRegistry` route-provider migration is complete for the
two selected route consumers:

- `get_indicator_registry_endpoint`
- `get_indicators_by_category`

No additional `IndicatorRegistry` route-provider source work is authorized by
this closeout.

## Next Gate

Before selecting another service lifecycle DI implementation lane:

1. Refresh or explicitly discount stale GitNexus graph output.
2. Run a current-head candidate refresh that excludes already-closed provider
   surfaces.
3. Keep `IndicatorCalculator`, package registry startup/jobs, and legacy
   `/api/indicators/*` test path debt as separate decision lanes unless a future
   approved packet explicitly scopes them.

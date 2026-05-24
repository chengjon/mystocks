# Backend Flat API IndicatorRegistry Route Provider Implementation - 2026-05-24

> **历史实施说明**:
> 本文件是历史实施记录，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.54 flat API `IndicatorRegistry` route-provider implementation
after G2.53 consumer matrix.

Base branch: `wip/root-dirty-20260403`
Base HEAD: `71510bb02a84`
Generated at: `2026-05-24T16:49:54+08:00`

## Status

`READY_FOR_REVIEW`.

This implementation follows the G2.53 authorization candidate. It changes only
the flat API registry provider surface, the two selected registry read route
consumers, one focused regression test file, and governance records.

## Human Approval Chain

| Gate | State | Evidence |
| --- | --- | --- |
| G2.52 provider design | Accepted and merged | PR `#193`, merge commit `ec3dc2920886eb24e963a33488bd2e945e98e6c9` |
| G2.53 consumer matrix | Accepted and merged | PR `#194`, merge commit `71510bb02a845ec529c8c04f3a7288ca86b87b9c` |
| G2.54 implementation | Prepared for review | This report and PR task card `pr-195.yaml` |

## Pre-Edit GitNexus Evidence

Pre-edit graph checks were run before source changes.

Flat registry getter:

```text
Function:web/backend/app/services/indicator_registry.py:get_indicator_registry
direct callers:
- get_indicator_registry_endpoint
- get_indicators_by_category
- IndicatorCalculator.__init__
```

Selected route handlers:

```text
get_indicator_registry_endpoint
risk=LOW
impacted_count=0
direct=0
processes_affected=0

get_indicators_by_category
risk=LOW
impacted_count=0
direct=0
processes_affected=0
```

The generic same-name `get_indicator_registry` impact query still resolves to
the package registry, so this implementation used exact context and caller
evidence for the flat API registry surface.

## Implementation Scope

Modified source:

- `web/backend/app/services/indicator_registry.py`
- `web/backend/app/api/indicators/indicator_cache.py`

Added test:

- `web/backend/tests/test_indicator_registry_route_provider.py`

Governance records:

- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `.planning/codebase/generated/flat-api-indicator-registry-route-provider-implementation-2026-05-24.json`
- `docs/reports/quality/backend-flat-api-indicator-registry-route-provider-implementation-2026-05-24.md`
- `governance/mainline/task-cards/pr-195.yaml`

## Code Changes

`web/backend/app/services/indicator_registry.py` now exposes an app-state-backed
provider surface for the flat API registry:

```text
INDICATOR_REGISTRY_STATE_KEY = "indicator_registry"
install_indicator_registry(app, registry=None)
get_indicator_registry_dependency(request)
```

The existing compatibility getter remains intact:

```text
get_indicator_registry()
```

`web/backend/app/api/indicators/indicator_cache.py` now injects the provider into
only the two selected read endpoints:

```text
GET /api/v1/indicators/registry
GET /api/v1/indicators/registry/{category}
```

No calculate, batch, cache, `IndicatorCalculator`, package registry, TA-Lib
adapter, defaults, or jobs code was changed.

## TDD Evidence

RED:

```text
pytest -o addopts= web/backend/tests/test_indicator_registry_route_provider.py -q --tb=short --no-cov
2 failed in 1.77s

Failure 1:
assert dependency is not None

Failure 2:
TypeError: get_indicator_registry_endpoint() got an unexpected keyword argument 'registry'
```

GREEN:

```text
pytest -o addopts= web/backend/tests/test_indicator_registry_route_provider.py -q --tb=short --no-cov
2 passed in 1.60s
```

The focused test verifies:

- both registry read route handlers expose the FastAPI dependency provider;
- both handlers accept an injected fake registry;
- registry data still serializes through the existing response contract.

## Validation

Passed:

```text
black web/backend/app/services/indicator_registry.py \
      web/backend/app/api/indicators/indicator_cache.py \
      web/backend/tests/test_indicator_registry_route_provider.py

ruff check web/backend/app/services/indicator_registry.py \
           web/backend/app/api/indicators/indicator_cache.py \
           web/backend/tests/test_indicator_registry_route_provider.py

pytest -o addopts= web/backend/tests/test_indicator_registry_route_provider.py -q --tb=short --no-cov
2 passed in 1.68s

pytest -o addopts= web/backend/tests/test_health_route_conflicts.py::test_v1_indicator_endpoints_have_examples_parameter_docs_and_descriptions -q --tb=short --no-cov
1 passed in 10.62s

configured app/OpenAPI smoke:
routes_total=548
openapi_paths_total=500
duplicate_operation_ids=0
selected_indicator_cache_routes=6
```

Staged GitNexus scope check:

```text
gitnexus_detect_changes(scope=staged)
risk=MEDIUM
changed_files=7
changed_count=22
affected_count=2
affected_processes:
- Calculate_indicators -> Warning
- Calculate_indicators -> _dataframe_to_ohlcv_arrays
```

Manual staged diff review confirmed the actual source hunks are bounded to the
`indicator_cache.py` import/signature/call-site changes, the
`indicator_registry.py` provider addition, and the focused new regression test.
The calculate-flow hits come from file-level parser attribution in
`indicator_cache.py`; no calculate handler body was intentionally changed.

Known existing test debt observed:

```text
pytest -o addopts= web/backend/tests/test_indicators.py -q --tb=short --no-cov
8 failed, 8 passed in 11.96s
```

The failing assertions use legacy `/api/indicators/*` paths and receive `404`.
The active route table exposes `/api/v1/indicators/*`. This was not introduced
by G2.54 and is recorded here as residual test path debt, not an implementation
regression.

## Non-Goals Preserved

- No package registry migration.
- No `IndicatorCalculator.__init__` migration.
- No route path, OpenAPI visibility, response model, or operation ID change.
- No compatibility getter deletion.
- No PM2 or runtime promotion.
- No OpenSpec state movement.

## Next Gate

If accepted and merged, run a G2.55 closeout/current-head refresh before
selecting another service lifecycle DI implementation lane. The closeout should
verify that `indicator_cache.py` has zero direct route calls to
`get_indicator_registry()` while `IndicatorCalculator` and the package registry
remain intentionally outside this route-provider batch.

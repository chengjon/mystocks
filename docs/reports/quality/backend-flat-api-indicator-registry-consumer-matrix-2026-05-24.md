# Backend Flat API IndicatorRegistry Consumer Matrix - 2026-05-24

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.53 flat API registry consumer matrix / authorization candidate after
G2.52 `IndicatorRegistry` provider design.

Base branch: `wip/root-dirty-20260403`
Current HEAD: `ec3dc2920886`
Generated at: `2026-05-24T15:40:41+08:00`

## Status

`APPROVE_WITH_GUARDS` for a future implementation branch, pending human review of
this packet.

This packet is governance-only. It does not edit backend source, tests, API
contracts, OpenAPI output, or runtime behavior.

G2.52 is complete: PR `#193` was merged into `wip/root-dirty-20260403` at merge
commit `ec3dc2920886eb24e963a33488bd2e945e98e6c9`.

## Source Snapshot

| Surface | File | Current role | G2.53 disposition |
| --- | --- | --- | --- |
| Flat API registry | `web/backend/app/services/indicator_registry.py` | API-facing TA-Lib metadata registry with module-level singleton fallback | Candidate for future app-state provider addition |
| Indicator cache routes | `web/backend/app/api/indicators/indicator_cache.py` | Six `/api/v1/indicators/*` route handlers; two read endpoints call the flat registry directly | Candidate route consumer migration scope |
| Indicator calculator | `web/backend/app/services/indicator_calculator.py` | Service constructor calls the flat registry getter | Excluded from route-provider implementation |
| Package registry | `web/backend/app/services/indicators/indicator_registry.py` | Internal package registry for defaults, TA-Lib adapter, jobs, and unit tests | Excluded; requires separate startup/jobs design packet |

The flat registry singleton remains:

```text
web/backend/app/services/indicator_registry.py:628 _indicator_registry = None
web/backend/app/services/indicator_registry.py:631 def get_indicator_registry() -> IndicatorRegistry:
web/backend/app/services/indicator_registry.py:633 global _indicator_registry
web/backend/app/services/indicator_registry.py:634 if _indicator_registry is None:
web/backend/app/services/indicator_registry.py:635 _indicator_registry = IndicatorRegistry()
web/backend/app/services/indicator_registry.py:636 return _indicator_registry
```

## Consumer Matrix

### Flat API Registry Consumers

| Consumer | File | Current access | Migration decision |
| --- | --- | --- | --- |
| `get_indicator_registry_endpoint` | `web/backend/app/api/indicators/indicator_cache.py:86` | Calls `get_indicator_registry()` inside route handler | Future implementation may migrate to route dependency |
| `get_indicators_by_category` | `web/backend/app/api/indicators/indicator_cache.py:213` | Calls `get_indicator_registry()` inside route handler | Future implementation may migrate to route dependency |
| `IndicatorCalculator.__init__` | `web/backend/app/services/indicator_calculator.py:43` | Calls `get_indicator_registry()` during service construction | Keep untouched in the flat API route-provider batch |

Import evidence:

```text
web/backend/app/api/indicators/indicator_cache.py:42
from app.services.indicator_registry import IndicatorCategory, get_indicator_registry

web/backend/app/services/indicator_calculator.py:20
from .indicator_registry import get_indicator_registry
```

### Indicator Cache Route Inventory

| Method | Path | Handler | Registry relationship |
| --- | --- | --- | --- |
| GET | `/api/v1/indicators/registry` | `get_indicator_registry_endpoint` | Direct flat registry consumer |
| GET | `/api/v1/indicators/registry/{category}` | `get_indicators_by_category` | Direct flat registry consumer |
| POST | `/api/v1/indicators/calculate` | `calculate_indicators` | Uses calculation flow; no direct registry getter call in route handler |
| POST | `/api/v1/indicators/calculate/batch` | `calculate_indicators_batch` | Uses calculation flow; no direct registry getter call in route handler |
| GET | `/api/v1/indicators/cache/stats` | `get_cache_statistics` | Cache/control behavior; no direct registry getter call |
| POST | `/api/v1/indicators/cache/clear` | `clear_cache` | Cache/control behavior; no direct registry getter call |

Only the first two route handlers are candidates for a route-provider
implementation batch. The calculate and cache endpoints should remain out of the
initial migration unless a later source-level review proves an additional route
dependency is needed.

## GitNexus Evidence

GitNexus disambiguation confirms the flat API registry direct callers:

```text
get_indicator_registry_endpoint -> web/backend/app/api/indicators/indicator_cache.py
get_indicators_by_category      -> web/backend/app/api/indicators/indicator_cache.py
IndicatorCalculator.__init__    -> web/backend/app/services/indicator_calculator.py
```

The same-name package registry remains separate. A generic `impact` query on
`get_indicator_registry` resolves to the package registry and reports LOW risk,
impacted count `4`, and the `Run_daily_calculation -> Get_indicator_registry`
process. That evidence must not be used to authorize edits to the flat API
registry route handlers.

## Runtime And Contract Evidence

Configured app/OpenAPI smoke used non-sensitive placeholder environment
variables only. It did not run PM2, connect intentionally to production
resources, or authorize runtime promotion.

```text
routes_total=548
openapi_paths_total=500
duplicate_operation_ids=0
selected_indicator_cache_routes=6
selected_registry_route_consumers=2
```

Selected OpenAPI operations:

```text
GET  /api/v1/indicators/registry
GET  /api/v1/indicators/registry/{category}
POST /api/v1/indicators/calculate
POST /api/v1/indicators/calculate/batch
GET  /api/v1/indicators/cache/stats
POST /api/v1/indicators/cache/clear
```

Targeted collection checks:

```text
pytest -o addopts= web/backend/tests/test_indicators.py --collect-only -q --no-cov
16 tests collected in 11.20s

pytest -o addopts= web/backend/tests/test_health_route_conflicts.py --collect-only -q --no-cov
112 tests collected in 11.96s

pytest -o addopts= web/backend/tests/unit/services/indicators/test_indicator_registry.py --collect-only -q --no-cov
29 tests collected in 1.31s
```

## Authorization Candidate

If this packet is accepted, a future implementation branch may be created for a
narrow flat API registry route-provider migration.

Allowed source scope for that future branch:

- `web/backend/app/services/indicator_registry.py`
- `web/backend/app/api/indicators/indicator_cache.py`
- focused tests that directly cover indicator registry routes or app/OpenAPI
  route contract stability

Required implementation constraints:

- Add an app-state provider surface for the flat API registry only, for example
  `INDICATOR_REGISTRY_STATE_KEY`, `install_indicator_registry(app, registry=None)`,
  and `get_indicator_registry_dependency(request)`.
- Preserve `get_indicator_registry()` as a compatibility fallback.
- Convert only the two direct registry route consumers in
  `indicator_cache.py`.
- Do not edit `IndicatorCalculator.__init__` in the same batch.
- Do not edit `web/backend/app/services/indicators/indicator_registry.py`,
  `defaults.py`, `talib_adapter.py`, or indicator jobs.
- Do not merge the flat API registry and package registry surfaces.
- Do not change route paths, response models, OpenAPI visibility, or operation
  IDs.

Required pre-edit gates for the future implementation branch:

- Run GitNexus context for the exact flat registry getter and both selected
  route handlers.
- Run GitNexus impact or equivalent Cypher caller query before touching source.
- If impact or caller inventory shows HIGH/CRITICAL risk, stop and return to
  review.
- Start from current `wip/root-dirty-20260403`, not from this governance branch
  if it has become stale.

## Non-Goals

- No source implementation in G2.53.
- No backend route, service, test, OpenAPI, PM2, or generated client edits.
- No package registry startup/jobs design.
- No compatibility getter deletion.
- No route path or response contract change.
- No GitHub issue label or OpenSpec state movement.

## Decision

G2.53 authorizes only a future reviewable implementation candidate, not source
edits in this PR.

The next safe implementation lane is a narrow flat API registry route-provider
branch that touches the flat registry service and the two registry read
endpoints only. The package registry and `IndicatorCalculator` remain explicit
exclusions.

## Next Gate

If this packet is accepted, create G2.54 flat API registry route-provider
implementation branch with TDD and pre-edit GitNexus checks. The G2.54 branch
must carry its own task card and must not reuse this governance-only PR as
implementation authorization beyond the bounded scope above.

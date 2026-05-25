# Backend DataSourceFactory Compatibility Getter Retirement Authorization - 2026-05-25

Workline: G2.80 source-capable authorization packet

Current HEAD: `ac0fa318aa30262092d00219de18bd670bab26b2`

> **历史索引说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: This packet authorizes only a future, separate implementation
branch. It does not itself edit backend source, tests, routes, OpenAPI exposure,
frontend code, runtime processes, OpenSpec changes, issue labels, package
exports, or the `get_data_source_factory()` compatibility API.

## Status

Ready for review.

## Authorization Decision

Authorize a future G2.81 Phase 1 implementation to decouple service-internal
helper fallback paths from the public `get_data_source_factory()` compatibility
getter.

This is not deletion authorization. G2.81 may make the public getter delegate to
a private/internal initializer, and may move internal helper calls to that
private/internal initializer. G2.81 must keep the public function and package
exports in place.

## Current Evidence

| Metric | Current HEAD |
| --- | ---: |
| Route/API direct `get_data_source_factory()` calls | 0 |
| Python mentions of `get_data_source_factory` | 61 |
| Exact Python `get_data_source_factory()` parenthesized refs | 10 |
| Service-module exact refs | 6 |
| Package export mentions | 4 |
| OpenAPI routes | 548 |
| OpenAPI paths | 500 |
| Duplicate operation IDs | 0 |
| Duplicate operation ID warnings | 0 |

Focused verification:

| Check | Result |
| --- | --- |
| `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov` | 4 passed |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov` | 120 passed |
| OpenAPI smoke with `PYTHONPATH=web/backend` and root `.env` loaded | 548 routes, 500 paths, 536 operation IDs, duplicate operation IDs 0 |

Current service-module call sites:

| Location | Current role |
| --- | --- |
| `web/backend/app/services/data_source_factory/data_source_factory.py:300` | public compatibility getter definition |
| `web/backend/app/services/data_source_factory/data_source_factory.py:310` | `install_data_source_factory` fallback calls public getter |
| `web/backend/app/services/data_source_factory/data_source_factory.py:324` | `get_data_source` fallback calls public getter |
| `web/backend/app/services/data_source_factory/data_source_factory.py:330` | `get_market_data` fallback calls public getter |
| `web/backend/app/services/data_source_factory/data_source_factory.py:336` | `get_dashboard_data` fallback calls public getter |
| `web/backend/app/services/data_source_factory/data_source_factory.py:342` | `get_technical_analysis_data` fallback calls public getter |

Package export locations:

| Location | Current role |
| --- | --- |
| `web/backend/app/services/data_source_factory/__init__.py:12` | package re-export |
| `web/backend/app/services/data_source_factory/__init__.py:31` | package `__all__` export |

GitNexus currently reports CRITICAL impact for `get_data_source_factory()`: 22
impacted symbols, 21 direct dependents, 12 affected processes. The current graph
still lists historical route handlers that textual current-head scans show as
migrated. G2.80 therefore grants only a scoped stale-index waiver for Phase 1
service-internal decoupling; it does not waive full getter or package export
deletion risk.

## Future G2.81 Allowed Scope

Allowed source files:

- `web/backend/app/services/data_source_factory/data_source_factory.py`
- `web/backend/tests/test_data_source_factory_lifecycle_di.py`

Allowed governance files:

- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `.planning/codebase/generated/data-source-factory-compat-getter-retirement-phase1-implementation-*.json`
- `docs/reports/quality/backend-data-source-factory-compat-getter-retirement-phase1-implementation-*.md`
- `governance/mainline/task-cards/pr-*.yaml`

Allowed implementation intent:

1. Add or reuse a private/internal helper that owns lazy DataSourceFactory
   initialization.
2. Keep `get_data_source_factory()` as a compatibility wrapper.
3. Make `install_data_source_factory()` use the private/internal initializer
   when no explicit factory is provided.
4. Make `get_data_source`, `get_market_data`, `get_dashboard_data`, and
   `get_technical_analysis_data` stop calling the public compatibility getter
   directly.
5. Add TDD coverage proving service-internal helper fallback no longer depends
   on the public compatibility getter while the public getter still initializes
   correctly.

## Future G2.81 Forbidden Scope

The future implementation must not:

- delete `get_data_source_factory()`;
- remove package exports from
  `web/backend/app/services/data_source_factory/__init__.py`;
- edit route modules under `web/backend/app/api/**`;
- edit frontend files;
- edit route paths, response models, response shapes, or OpenAPI exposure;
- change app-state key `DATA_SOURCE_FACTORY_STATE_KEY`;
- change runtime/PM2 scripts or run stateful PM2 gates;
- create or archive OpenSpec changes;
- change GitHub issue labels.

## Future G2.81 Required Gates

Before source edits:

1. Read `architecture/STANDARDS.md`.
2. Run GitNexus impact/context for `get_data_source_factory`,
   `install_data_source_factory`, `get_data_source`, `get_market_data`,
   `get_dashboard_data`, and `get_technical_analysis_data`.
3. Record that this G2.80 packet is the stale-index waiver only for Phase 1
   service-internal decoupling.

Implementation gates:

1. TDD red test for internal helper fallback not depending on the public getter.
2. Green implementation.
3. `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov`.
4. `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov`.
5. `ruff check web/backend/app/services/data_source_factory/data_source_factory.py web/backend/tests/test_data_source_factory_lifecycle_di.py`.
6. `black --check web/backend/app/services/data_source_factory/data_source_factory.py web/backend/tests/test_data_source_factory_lifecycle_di.py`.
7. OpenAPI smoke: paths remain 500 and duplicate operation IDs remain 0.
8. Textual scan: route/API direct `get_data_source_factory()` calls remain 0.
9. Textual scan: service-module direct calls from helper functions to public
   `get_data_source_factory()` are removed, while the public getter definition
   remains.
10. Staged GitNexus `detect_changes(scope=staged)`.

## Stop Conditions

Stop and return to review if any of these occur:

- source edits need files outside the allowed source scope;
- deletion of the public getter or package export appears necessary;
- route/OpenAPI changes appear;
- GitNexus reports new HIGH/CRITICAL impact outside the known service-internal
  helper and stale-index route-handler set;
- focused tests or OpenAPI smoke fail for reasons unrelated to the planned
  helper decoupling.

## Next Gate

Human review / PR merge decision for this authorization packet. If accepted,
create a separate G2.81 implementation branch for Phase 1 service-internal
decoupling only.

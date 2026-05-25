# Backend DataSourceFactory Compatibility Getter Retirement Phase 1 Implementation - 2026-05-25

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.81 source implementation packet

Status: ready for review

Branch: `g2-81-data-source-factory-compat-getter-phase1-implementation`

Baseline HEAD: `b922db6b672f1084dcefb9ecba953b780ac8dbe3`

Prepared at: `2026-05-25T12:48:57+08:00`

## Purpose

Implement the G2.80 authorization boundary for Phase 1 retirement of the
`get_data_source_factory()` compatibility getter.

This packet decouples service-internal fallback helper paths from the public
compatibility getter while keeping the public getter and package exports intact.
It does not retire the compatibility API.

## Authorization Source

G2.80 was merged in PR `#233` at
`b922db6b672f1084dcefb9ecba953b780ac8dbe3`.

G2.80 authorized only this Phase 1 service-internal decoupling:

- source edits limited to
  `web/backend/app/services/data_source_factory/data_source_factory.py`;
- test edits limited to
  `web/backend/tests/test_data_source_factory_lifecycle_di.py`;
- public `get_data_source_factory()` must remain;
- package exports in `web/backend/app/services/data_source_factory/__init__.py`
  must remain;
- route/API modules, OpenAPI exposure, frontend, runtime/PM2, OpenSpec, and
  issue labels remain out of scope.

## Implementation Summary

Changed
`web/backend/app/services/data_source_factory/data_source_factory.py`:

- introduced private `_get_or_create_data_source_factory()`;
- changed public `get_data_source_factory()` into a compatibility wrapper around
  the private initializer;
- changed `install_data_source_factory()` fallback to call the private
  initializer;
- changed service convenience helpers to call the private initializer:
  - `get_data_source()`;
  - `get_market_data()`;
  - `get_dashboard_data()`;
  - `get_technical_analysis_data()`.

Changed
`web/backend/tests/test_data_source_factory_lifecycle_di.py`:

- updated the fallback dependency test to patch the private initializer;
- added coverage proving service convenience helpers no longer call the public
  compatibility getter;
- kept coverage proving the public compatibility getter still initializes a
  factory.

## TDD Evidence

RED:

```text
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short
2 failed, 3 passed
```

Expected failures:

- `AttributeError: ... has no attribute '_get_or_create_data_source_factory'`
  in `test_data_source_factory_dependency_installs_fallback_factory`;
- `AttributeError: ... has no attribute '_get_or_create_data_source_factory'`
  in `test_convenience_helpers_use_internal_factory_initializer`.

GREEN after implementation and formatting:

```text
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short
5 passed in 1.69s
```

## Verification

| Check | Result |
|---|---|
| `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short` | 5 passed |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | 120 passed |
| `ruff check web/backend/app/services/data_source_factory/data_source_factory.py web/backend/tests/test_data_source_factory_lifecycle_di.py` | passed |
| `black --check web/backend/app/services/data_source_factory/data_source_factory.py web/backend/tests/test_data_source_factory_lifecycle_di.py` | passed |
| OpenAPI smoke with root `.env` loaded | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0`, duplicate operation ID warnings=`0` |

Reference scan after implementation:

| Metric | Result |
|---|---:|
| Route/API direct `get_data_source_factory()` calls | 0 |
| Exact parenthesized `get_data_source_factory(` refs | 4 |
| Service-module exact refs | 1 |
| Service helper public getter calls | 0 |
| Package export mentions | 4 |
| Private initializer refs | 11 |

The remaining service-module exact ref is the public compatibility getter
definition itself. Package exports intentionally remain unchanged.

## GitNexus Evidence

Pre-edit GitNexus checks were run before source modification:

| Target | Result |
|---|---|
| `get_data_source_factory` impact | CRITICAL, 22 impacted symbols, 21 direct dependents, 12 affected processes |
| `get_data_source_factory` context | confirms public compatibility getter and historical/stale route-handler references |
| `get_data_source` impact | LOW, 0 impacted symbols |
| `get_market_data` context | exact service function located in `data_source_factory.py` |
| `get_dashboard_data` context | exact service function located in `data_source_factory.py` |
| `get_technical_analysis_data` impact | LOW, 0 impacted symbols |
| `install_data_source_factory` | not found in current GitNexus index |

The CRITICAL impact for `get_data_source_factory()` is handled under the G2.80
scoped stale-index waiver for Phase 1 service-internal decoupling only. This
packet does not rely on that waiver for public getter deletion or package export
removal.

Staged GitNexus `detect_changes(scope=staged)` result:

| Metric | Result |
|---|---|
| Changed files | 6 |
| Changed symbols | 20 |
| Affected symbols | 12 |
| Risk level | HIGH |
| Affected process families | `Get_system_status_overview`, `Get_sources_health` |

This matches the expected DataSourceFactory initialization blast radius and
does not introduce a new public getter deletion or package export removal path.

## Boundary Confirmation

This packet did not:

- delete public `get_data_source_factory()`;
- remove package exports from
  `web/backend/app/services/data_source_factory/__init__.py`;
- edit route modules under `web/backend/app/api/**`;
- edit route paths, response models, response shapes, or OpenAPI exposure;
- edit frontend files;
- edit runtime or PM2 scripts;
- edit OpenSpec changes;
- change GitHub issue labels;
- change `DATA_SOURCE_FACTORY_STATE_KEY`.

## Risk And Rollback

Risk level: MEDIUM because the public compatibility getter has a known
GitNexus CRITICAL/stale-index warning, but the implementation keeps the public
API and narrows only service-internal fallback calls.

Rollback: revert this packet to restore service helpers calling the public
compatibility getter directly. The rollback does not require route, OpenAPI,
frontend, runtime, or package export changes.

## Next Gate

Human review / PR merge decision for G2.81.

If accepted, create a separate closeout/current-head refresh before any further
retained-shim retirement decision. Full public getter deletion and package
export removal remain unauthorized.

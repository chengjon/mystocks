# Backend Indicator Registry Factory Provider Authorization - G2.314

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: for review
- Prepared at: `2026-06-02T01:46:33+08:00`
- Base HEAD checked: `75f6c63023bec35453892f63aaeaf193023e4881`
- Parent gate: G2.313 accepted / merged by PR `#466`
- Target: `web/backend/app/api/indicator_registry.py:get_factory`
- Source edit authority in this PR: none

Boundary note: this G2.314 package is no-source governance only. It authorizes only a future path-limited source PR after acceptance; it does not itself edit backend source, tests, route registration, route/OpenAPI contracts, docs/api, frontend/config/scripts, OpenSpec specs, PM2, or runtime state.

## Authorization Decision

G2.314 authorizes a future G2.315 path-limited implementation lane for `indicator_registry.get_factory` provider injection, but only after PR `#467` is accepted / merged. G2.315 must stop for human review before merge because it will modify backend source and tests.

## Future G2.315 Allowed Scope

| Category | Paths |
|---|---|
| Backend source | `web/backend/app/api/indicator_registry.py` |
| Focused tests | `tests/api/file_tests/test_indicator_registry_api.py` |

No other backend source, generated OpenAPI artifact, docs/api artifact, frontend, config, script, OpenSpec proposal/spec, PM2, or runtime-state change is authorized by this package.

## Required Implementation Shape

A future G2.315 implementation must:

1. Add a route-local provider dependency for `IndicatorFactory` without changing route paths, methods, response models, or OpenAPI path count.
2. Move `list_indicators`, `get_indicator_details`, and `calculate_indicator` away from route-body `get_factory()` calls.
3. Retain `get_factory()` as backing compatibility / singleton construction seam unless a later explicit retirement decision exists.
4. Add or update focused file-level tests proving provider wiring and preserving route/model contracts.
5. Run route/OpenAPI smoke and focused tests before PR.

## Current Evidence

| Item | Value |
|---|---|
| Direct route-body calls | 3 |
| Call lines | 159, 186, 201 |
| Registered indicator-registry routes | 3 |
| FastAPI route count | 548 |
| OpenAPI path count | 500 |
| Duplicate operation ID warnings | 0 |
| GitNexus CLI risk | LOW |
| GitNexus direct callers | 3 |
| GitNexus affected processes | 0 |

## Required Verification For Future Source PR

- `pytest -o addopts= tests/api/file_tests/test_indicator_registry_api.py --no-cov -q`
- `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py --collect-only -q --no-cov`
- `ruff check web/backend/app/api/indicator_registry.py tests/api/file_tests/test_indicator_registry_api.py`
- route/OpenAPI smoke confirming `548` routes, `500` paths, and `duplicate_operation_id_warnings=0`
- GitNexus impact before source edit
- GitNexus staged verification before commit

## Stop Rules

G2.314 itself remains no-source. If accepted, the next G2.315 implementation branch must stop at PR review and must not be automatically merged under the no-source autopilot rule.

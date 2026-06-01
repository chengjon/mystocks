# Backend Indicator Registry Factory Provider Implementation - G2.315

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: source implementation PR review required
- Prepared at: `2026-06-02T01:58:00+08:00`
- Base HEAD checked: `8d52fa0548fd200f0c9b606e5880e71286c07d10`
- Parent gate: G2.314 accepted / merged by PR `#467`
- Target: `web/backend/app/api/indicator_registry.py:get_factory`
- Automerge authority: none

Boundary note: this G2.315 package changes backend source and a focused test file. It must stop at PR review and must not be automatically merged under the no-source autopilot rule.

## Scope

| Category | Paths |
|---|---|
| Backend source | `web/backend/app/api/indicator_registry.py` |
| Focused tests | `tests/api/file_tests/test_indicator_registry_api.py` |
| Governance evidence | steward tree, generated evidence, quality report, task card |

No route registration, generated OpenAPI artifact, docs/api, frontend, config, script, OpenSpec proposal/spec, PM2, or runtime-state change is included.

## Implementation Summary

- Added `Depends` and route-local `get_indicator_factory()` provider.
- Moved `list_indicators`, `get_indicator_details`, and `calculate_indicator` to `Depends(get_indicator_factory)`.
- Retained `get_factory()` as the backing singleton compatibility seam.
- Added a file-level provider wiring test for all three indicator-registry routes.
- Updated the same file-level contract test to assert the current `UnifiedResponse[...]` response model contract.

## TDD Evidence

| Phase | Result |
|---|---|
| RED | `pytest -o addopts= tests/api/file_tests/test_indicator_registry_api.py --no-cov -q` produced the expected provider AttributeError; the same run also exposed an existing stale response_model assertion. Result: 2 failed, 9 passed. |
| GREEN | Same focused test command passed: 11 passed, 1 warning. |

## Verification

| Gate | Result |
|---|---|
| Focused test | `11 passed, 1 warning` |
| Health route collect-only | 121 tests collected without collection failure |
| Ruff | `All checks passed` for target source/test files |
| Route/OpenAPI smoke | 548 routes, 500 OpenAPI paths, duplicate operation ID warnings 0 |
| Indicator-registry dependencies | all 3 routes expose `get_indicator_factory` dependency |
| Provider scan | route-body direct `get_factory()` calls 0; provider backing calls 1; `Depends` bindings 3 |
| GitNexus pre-edit impact | MCP failed with `Transport closed`; CLI fallback LOW, 3 direct callers, affected processes 0 |

## Review Stop

PR `#468` must be manually reviewed. If accepted and merged, the next node should be G2.316 no-source indicator-registry factory provider closeout / residual refresh.

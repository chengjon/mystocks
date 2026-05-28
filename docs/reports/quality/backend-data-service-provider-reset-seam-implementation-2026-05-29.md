# Backend DataService Provider/Reset Seam Implementation - 2026-05-29

> **历史文档说明**: 本文件是 G2.217 执行证据快照，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Branch: `g2-217-data-service-provider-reset-seam`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `68ba10829b89095f8b907d249f59198995543ebc`
- Prepared at: `2026-05-29T00:46:30+08:00`
- OpenSpec lane: `migrate-backend-singletons-to-lifecycle-di`
- Source authority: path-limited by accepted G2.216 / PR `#369`

## Inputs

| Input | State |
|---|---|
| PR `#369` | Merged at `68ba10829b89095f8b907d249f59198995543ebc` |
| G2.216 report | `docs/reports/quality/backend-indicator-data-service-provider-authorization-2026-05-29.md` |
| G2.216 evidence | `.planning/codebase/generated/indicator-data-service-provider-authorization-2026-05-29.json` |

## Pre-Edit Impact

GitNexus was indexed for the isolated G2.217 worktree before editing `get_data_service`.

| Metric | Value |
|---|---:|
| GitNexus repo | `g2-217-data-service-provider-reset-seam` |
| Indexed at | `2026-05-28T16:41:52.531Z` |
| Target | `get_data_service` |
| Risk | `LOW` |
| Direct callers | 2 |
| Impacted symbols | 2 |
| Affected processes | 0 |
| Affected modules | 0 |

Direct callers remain route-local provider wrappers:

| Direct caller | File |
|---|---|
| `get_indicator_data_service` | `web/backend/app/api/indicators/indicator_cache.py` |
| `get_strategy_indicator_data_service` | `web/backend/app/api/v1/strategy/indicators.py` |

## Implementation

Changed source:

| File | Change |
|---|---|
| `web/backend/app/services/data_service.py` | Added `_data_service_provider`, `set_data_service_provider()`, and `reset_data_service_provider()` |

Added test:

| File | Coverage |
|---|---|
| `web/backend/tests/test_data_service_singleton_provider.py` | Provider override selection and reset-to-default singleton fallback |

Behavior preserved:

- `get_data_service()` remains import-compatible and runtime-compatible.
- Without a provider override, `get_data_service()` still lazily creates and caches a default `DataService`.
- With a provider override, `get_data_service()` returns the provider result.
- `reset_data_service_provider()` clears both the provider override and cached singleton state.

## TDD Evidence

Red:

| Command | Expected failure |
|---|---|
| `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_service_singleton_provider.py -q --no-cov --tb=short` | `ImportError: cannot import name 'reset_data_service_provider' from 'app.services.data_service'` |

Green:

| Command | Result |
|---|---|
| `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_service_singleton_provider.py -q --no-cov --tb=short` | `2 passed in 2.25s` |
| `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_indicator_registry_route_provider.py -q --no-cov --tb=short` | `3 passed in 4.11s` |
| `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_v1_indicators_regressions.py -q --no-cov --tb=short` | `3 passed in 2.98s` |

## GitNexus Staged Scope Note

`gitnexus_detect_changes(scope="staged")` reports `high` risk with 11 changed files, 15 changed symbols, and 12 affected processes. The high rating is retained as a review signal.

The cached source diff for `web/backend/app/services/data_service.py` is localized to:

- adding `Callable` to typing imports
- adding `_data_service_provider`
- adding `set_data_service_provider()`
- adding `reset_data_service_provider()`
- adding the provider override branch at the start of `get_data_service()`

No `DataService` method bodies, route handlers, OpenAPI contracts, adapters, or data loading flows are intentionally changed in this lane.

## Not Changed

- No route/OpenAPI contract changes.
- No route provider wrapper edits.
- No Strategy getter residual reopen.
- No data-quality monitor, trade execution evidence, cache prewarming, realtime streaming/socket, `adapter_split`, or `market_data_adapter.py` changes.

## Next Gate

If this implementation is accepted, start G2.218 as a no-source closeout and residual refresh package before selecting another source lane.

## Evidence Artifacts

| Artifact | Purpose |
|---|---|
| `.planning/codebase/generated/data-service-provider-reset-seam-implementation-2026-05-29.json` | Machine-readable G2.217 implementation evidence |
| `docs/reports/quality/backend-data-service-provider-reset-seam-implementation-2026-05-29.md` | Human-readable G2.217 implementation report |
| `governance/mainline/task-cards/pr-370.yaml` | Mainline governance task card |

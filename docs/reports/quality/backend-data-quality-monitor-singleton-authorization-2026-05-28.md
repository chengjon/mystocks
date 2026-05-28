# Backend Data-Quality Monitor Singleton Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Lane: G2.211 data-quality monitor singleton/backing API authorization
- Prepared at: `2026-05-28T22:18:21+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `619be9cac1f9516b3df42a41ca362ca9d42d5c9a`
- Parent lane: G2.210 data-quality monitor residual ownership decision
- Parent PR: `#363`
- Parent merge commit: `619be9cac1f9516b3df42a41ca362ca9d42d5c9a`
- Source edit authority in this PR: none

Boundary note: this report authorizes a future implementation lane only. It does
not edit backend source, delete getters, change route/OpenAPI behavior, change
frontend/config/script files, create OpenSpec proposals, change issue labels,
run PM2 workflows, or merge PRs.

## Parent State

G2.210 classified `get_data_quality_monitor()` as a CRITICAL impact root
ownership surface:

| Field | Value |
|---|---:|
| Impacted symbols | 24 |
| Direct dependents | 20 |
| Affected processes | 7 |
| Affected modules | 4 |

That finding means the next source lane must be narrow and compatibility-first.
It must not migrate routes, adapters, or `market_data_adapter.py` as part of the
singleton/backing API work.

## Current Consumer Matrix

| Surface | Current state | G2.212 authority |
|---|---|---|
| `web/backend/app/api/data_quality.py` | Already uses `get_data_quality_monitor_provider` and `Depends` | No source edits |
| `web/backend/app/services/adapters/dashboard_adapter.py` | Closed canonical adapter fallback | No source edits |
| `web/backend/app/services/adapters/data_adapter.py` | Closed canonical adapter fallback | No source edits |
| `web/backend/app/services/adapters_split/base_adapter.py` | Closed adapter-split fallback | No source edits |
| `web/backend/app/services/market_data_adapter.py` | Closed market-data adapter fallback | No source edits |
| `web/backend/app/services/_data_quality_monitor_singleton.py` | Singleton backing API | Authorized future source path |
| `web/backend/app/services/data_quality_monitor.py` | Public facade and re-export surface | Authorized future source path only for import/re-export maintenance |
| `web/backend/app/services/data_adapter.py.backup.20260130` | Historical backup | No source edits; repository hygiene only |

## Authorization Decision

This PR authorizes a future G2.212 implementation lane, but does not implement
it.

| Future lane | Authorized source paths | Authorized test path |
|---|---|---|
| G2.212 data-quality monitor singleton/backing API compatibility implementation | `web/backend/app/services/_data_quality_monitor_singleton.py`, `web/backend/app/services/data_quality_monitor.py` | `web/backend/tests/test_data_quality_monitor_singleton_provider.py` |

Future implementation must preserve these public imports:

- `from app.services.data_quality_monitor import get_data_quality_monitor`
- `from app.services.data_quality_monitor import monitor_data_quality`

## Authorized Future Shape

G2.212 may add a narrow compatibility/provider seam with these constraints:

- Preserve the existing `get_data_quality_monitor()` name, import path, return
  behavior, and default singleton fallback.
- Preserve `monitor_data_quality()` and keep it routed through the same monitor
  resolution policy.
- Allow only compatibility-oriented helper additions in
  `_data_quality_monitor_singleton.py`, such as explicit provider/reset hooks
  for tests or lifecycle wiring.
- Allow `data_quality_monitor.py` edits only to maintain facade imports and
  `__all__` re-exports.
- Do not change `DataQualityMonitor` class internals.
- Do not migrate routes, adapters, adapter-split constructors, or
  `market_data_adapter.py`.

## Required Future Tests

G2.212 must use TDD:

| Phase | Required evidence |
|---|---|
| RED | A focused singleton provider/reset test fails before implementation because no explicit test-safe override/reset hook exists |
| GREEN | The focused singleton provider/reset test passes after compatibility helpers are added |
| Regression | Existing route/provider and adapter compatibility tests remain passing |

Required future check set:

- `web/backend/tests/test_data_quality_monitor_singleton_provider.py`
- `web/backend/tests/test_data_quality_route_provider_regressions.py`
- `web/backend/tests/test_data_quality_canonical_service_adapter_provider.py`
- `web/backend/tests/test_adapter_split_data_quality_monitor_provider.py`
- `web/backend/tests/test_market_data_adapter_quality_monitor_provider.py`
- `web/backend/tests/test_logging_noise_regressions.py`
- `web/backend/tests/test_large_file_split_regressions.py`
- targeted ruff for the authorized source and test files
- OpenSpec strict validation for `migrate-backend-singletons-to-lifecycle-di`
- staged GitNexus change detection before commit

## Required Future GitNexus Gate

Before editing source in G2.212, run GitNexus impact/context for:

- `get_data_quality_monitor`
- `monitor_data_quality`
- `web/backend/app/services/_data_quality_monitor_singleton.py`

Known G2.210 impact is CRITICAL. G2.212 may proceed only if the future diff stays
inside the two authorized source files and the focused test path. Stop and
return to review if the implementation needs route, adapter, OpenAPI, frontend,
config, script, or OpenSpec edits.

## Explicit Non-Goals

This authorization does not grant:

- source edits in G2.211
- route/provider migration in G2.212
- adapter or adapter-split migration in G2.212
- `market_data_adapter.py` edits in G2.212
- `DataQualityMonitor` class internals
- historical backup cleanup
- `get_data_quality_monitor()` deletion or rename
- OpenAPI, frontend, config, script, or OpenSpec edits
- GitHub issue label changes

## Evidence Artifacts

- `.planning/codebase/generated/data-quality-monitor-singleton-authorization-2026-05-28.json`
- `docs/reports/quality/backend-data-quality-monitor-singleton-authorization-2026-05-28.md`
- `governance/mainline/task-cards/pr-364.yaml`

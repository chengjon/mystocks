# Backend WatchlistService Getter Retirement Implementation - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: implementation-prepared-for-review
- Workline: G2.131 WatchlistService getter-retirement implementation
- Current HEAD: `35dcc90cd9a242e8906107a01abf1649d77737ea`
- Parent PR: `#283` merged at `35dcc90cd9a242e8906107a01abf1649d77737ea`
- Generated artifact: `.planning/codebase/generated/watchlist-service-getter-retirement-implementation-2026-05-26.json`

This is the source-capable implementation authorized by G2.130. The scope stays
inside WatchlistService lifecycle code, two watchlist adapter fallback seams,
focused tests, this report, the generated artifact, the task card, and the
steward tree. It does not edit route handlers, route paths, response contracts,
OpenAPI exposure, frontend code, PM2 workflows, OpenSpec changes, or GitHub
issue labels.

## Source Changes

| File | Change |
|---|---|
| `web/backend/app/services/watchlist_service.py` | Removed module-level `_watchlist_service` and public `get_watchlist_service`; `install_watchlist_service()` now constructs `WatchlistService()` when no explicit service is supplied |
| `web/backend/app/services/adapters/watchlist_adapter.py` | Removed fallback import/call of `get_watchlist_service`; live mode without `watchlist_service_provider` now fails explicitly |
| `web/backend/app/services/data_adapters/watchlist.py` | Same fallback import/call retirement as the legacy adapter |
| `web/backend/tests/test_watchlist_service_lifecycle_di.py` | Updated app-state dependency fallback test to patch `WatchlistService` construction instead of the retired getter |
| `web/backend/tests/test_watchlist_helper_lifecycle_di.py` | Removed obsolete monkeypatch against the retired getter |
| `web/backend/tests/test_watchlist_service_getter_retirement.py` | Added regression coverage for getter/singleton absence, dependency preservation, and adapter fallback import retirement |

## Preserved Contracts

- `WatchlistService` remains importable.
- `install_watchlist_service` remains importable.
- `get_watchlist_service_dependency` remains importable.
- `web/backend/app/api/watchlist.py` was not edited.
- Route dependency handlers remain `7`.
- API direct `get_watchlist_service()` calls remain `0`.
- Route paths, response shapes, response models, and OpenAPI exposure were not
  changed.

## Cleanup Decision

Removed:

- `web/backend/app/services/watchlist_service.py:get_watchlist_service`
- module-level `_watchlist_service`
- fallback imports/calls from both watchlist adapter helper files

Retained:

- adapter-local `_watchlist_service` cache attributes in both adapter classes
- route dependency injection through `get_watchlist_service_dependency`
- explicit provider-based adapter injection

The adapter-local cache fields are retained because they cache injected
providers, not the retired module singleton.

## GitNexus Evidence

Before source edits:

- `get_watchlist_service`: MEDIUM, impacted `15`, direct `9`, processes `0`
- data adapter `_get_watchlist_service`: LOW, direct callers
  `_fetch_watchlist_data` and `health_check`
- legacy adapter `_get_watchlist_service`: direct callers
  `_fetch_watchlist_data` and `health_check`

No HIGH or CRITICAL warning was returned for the edited adapter helper symbols.

## TDD Evidence

Red:

- `web/backend/tests/test_watchlist_service_getter_retirement.py`:
  `2 failed, 1 passed`
- Failures proved the existing module still exposed `get_watchlist_service` and
  adapter helper source still imported the public getter.

Green:

- Focused watchlist suite:
  `web/backend/tests/test_watchlist_service_getter_retirement.py`
  `web/backend/tests/test_watchlist_service_lifecycle_di.py`
  `web/backend/tests/test_watchlist_helper_lifecycle_di.py`
  `web/backend/tests/test_adapter_mock_fallback_controls.py`
  `web/backend/tests/test_logging_noise_regressions.py`
  -> `28 passed`

## Verification

| Check | Result |
|---|---|
| Focused watchlist tests | `28 passed in 3.54s` |
| Health route conflicts | `120 passed in 83.70s` |
| Ruff touched files | `All checks passed` |
| Black check touched files | `8 files would be left unchanged` |
| Import smoke | `watchlist-import-ok` |
| Staged GitNexus detect changes | low risk, changed files `10`, changed symbols `45`, affected symbols `0`, affected processes `0` |

Exact scan:

| Metric | Result |
|---|---:|
| `watchlist_service.py` `get_watchlist_service` definitions | 0 |
| `watchlist_service.py` `_watchlist_service =` assignments | 0 |
| Adapter fallback imports of `get_watchlist_service` | 0 |
| Adapter public `get_watchlist_service()` calls | 0 |
| App/API public `get_watchlist_service()` calls | 0 |
| Route dependency refs | 8 |
| Route dependency handlers | 7 |

## Rollback

Revert this implementation commit to restore `get_watchlist_service`,
`_watchlist_service`, and both adapter fallback imports if focused tests, health
route conflicts, exact scans, staged GitNexus, or mainline scope fail.

## Non-Goals

- No route handler edits
- No route path, response model, response shape, or OpenAPI exposure changes
- No frontend, PM2, runtime workflow, or OpenSpec changes
- No GitHub issue label or readiness changes
- No deletion of `WatchlistService`, `install_watchlist_service`, or
  `get_watchlist_service_dependency`

## Next Gate

Human review / PR merge decision for G2.131. If accepted, close out the
WatchlistService getter-retirement lane and refresh the remaining service
lifecycle candidate pool before selecting another implementation lane.

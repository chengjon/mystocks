# Backend WatchlistService Getter Retirement Authorization - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: authorization-prepared-for-review
- Workline: G2.130 WatchlistService getter-retirement authorization
- Current HEAD: `cc32d0c2ba52cf7a9669ec1e9976740a84fd5be9`
- Parent PR: `#282` merged at `cc32d0c2ba52cf7a9669ec1e9976740a84fd5be9`
- Generated artifact: `.planning/codebase/generated/watchlist-service-getter-retirement-authorization-2026-05-26.json`

This packet authorizes only a future implementation branch after human review.
It does not change backend source, tests, route handlers, OpenAPI exposure,
frontend code, PM2 workflows, OpenSpec changes, or GitHub issue labels.

## Parent Decision

G2.129 selected `get_watchlist_service` only as a future authorization candidate.
It did not select a direct implementation lane because the WatchlistService getter
still crosses adapter fallback seams and seven route dependency handlers.

## Current Evidence

| Evidence | Current value |
|---|---:|
| `get_watchlist_service` definitions | 1 |
| `_watchlist_service` tokens | 74 |
| App/API direct `get_watchlist_service()` calls | 0 |
| API `get_watchlist_service_dependency` refs | 8 |
| Route dependency handlers | 7 |
| Adapter fallback files importing `get_watchlist_service` | 2 |
| Tests with getter refs | 4 |
| Focused watchlist baseline tests | 9 passed |

Adapter fallback files:

- `web/backend/app/services/adapters/watchlist_adapter.py`
- `web/backend/app/services/data_adapters/watchlist.py`

Tests with current getter references:

- `web/backend/tests/test_adapter_mock_fallback_controls.py`
- `web/backend/tests/test_logging_noise_regressions.py`
- `web/backend/tests/test_watchlist_helper_lifecycle_di.py`
- `web/backend/tests/test_watchlist_service_lifecycle_di.py`

## GitNexus Impact

| Target | Risk | Impacted | Direct | Processes | Modules |
|---|---:|---:|---:|---:|---:|
| `get_watchlist_service` | MEDIUM | 15 | 9 | 0 | 2 |

Direct d=1 callers that future work must account for:

- `web/backend/app/services/data_adapters/watchlist.py:_get_watchlist_service`
- `web/backend/app/services/adapters/watchlist_adapter.py:_get_watchlist_service`
- `web/backend/app/api/watchlist.py:get_user_groups`
- `web/backend/app/api/watchlist.py:create_group`
- `web/backend/app/api/watchlist.py:update_group`
- `web/backend/app/api/watchlist.py:delete_group`
- `web/backend/app/api/watchlist.py:get_watchlist_by_group`
- `web/backend/app/api/watchlist.py:move_stock_to_group`
- `web/backend/app/api/watchlist.py:get_watchlist_with_groups`

## Future Write Scope

If this authorization is accepted, the future implementation branch may edit
only these source/test files:

- `web/backend/app/services/watchlist_service.py`
- `web/backend/app/services/adapters/watchlist_adapter.py`
- `web/backend/app/services/data_adapters/watchlist.py`
- `web/backend/tests/test_watchlist_service_lifecycle_di.py`
- `web/backend/tests/test_watchlist_helper_lifecycle_di.py`
- `web/backend/tests/test_adapter_mock_fallback_controls.py`
- `web/backend/tests/test_logging_noise_regressions.py`
- `web/backend/tests/test_watchlist_service_getter_retirement.py`

The future implementation may also update its own report, generated artifact,
task card, and steward-tree record.

## Locked Scope

The future implementation must not edit:

- `web/backend/app/api/watchlist.py`
- other `web/backend/app/api/**` files
- frontend code
- `src/**`
- API docs or guides
- PM2, Docker, or runtime workflow files
- OpenSpec changes/specs
- GitHub issue labels or readiness state

Route paths, response shapes, response models, dependency handler count, and
OpenAPI exposure are locked unless a separate amendment authorizes route edits.

## Required Future Acceptance

The future implementation must:

1. Run GitNexus impact for `get_watchlist_service` before source edits.
2. Run GitNexus context/impact for any adapter helper symbol that will be
   changed.
3. Add a TDD red test proving `get_watchlist_service` and `_watchlist_service`
   are retired while `WatchlistService`, `install_watchlist_service`, and
   `get_watchlist_service_dependency` remain available.
4. Remove adapter fallback imports of `get_watchlist_service` or replace them
   with an explicitly authorized provider/app-state fallback.
5. Keep `web/backend/app/api/watchlist.py` route paths, response shapes, and
   dependency handlers unchanged.
6. Run focused tests:
   - `web/backend/tests/test_watchlist_service_getter_retirement.py`
   - `web/backend/tests/test_watchlist_service_lifecycle_di.py`
   - `web/backend/tests/test_watchlist_helper_lifecycle_di.py`
   - `web/backend/tests/test_adapter_mock_fallback_controls.py`
   - `web/backend/tests/test_logging_noise_regressions.py`
7. Run `web/backend/tests/test_health_route_conflicts.py`.
8. Run touched-file ruff and black checks.
9. Run exact scans for getter definitions, singleton tokens, adapter fallback
   imports, app/API direct getter calls, and route dependency handler count.
10. Run staged GitNexus detect changes and post-commit mainline scope gate.

## Rollback

If the future implementation fails route/helper tests, exact scans, GitNexus
staged scope, or mainline scope, revert the implementation commit and restore
`get_watchlist_service` plus adapter fallback imports.

## Authorization Packet Verification

- Parent PR `#282`: `MERGED`, merge commit
  `cc32d0c2ba52cf7a9669ec1e9976740a84fd5be9`
- Focused watchlist baseline:
  `web/backend/tests/test_watchlist_helper_lifecycle_di.py`
  and `web/backend/tests/test_watchlist_service_lifecycle_di.py`:
  `9 passed`
- GitNexus impact for `get_watchlist_service`: MEDIUM, impacted `15`,
  direct `9`, processes `0`
- Staged GitNexus detect changes for this authorization packet: low risk,
  changed files `4`, changed symbols `0`, affected symbols `0`, affected
  processes `0`

## Non-Goals

- No source or test edits in this authorization packet
- No direct implementation in this packet
- No route handler edits
- No route path, response model, response shape, or OpenAPI exposure changes
- No frontend, PM2, runtime workflow, or OpenSpec changes
- No GitHub issue label or readiness change

## Next Gate

Human review / PR merge decision for G2.130. If accepted, open G2.131 as the
source-capable WatchlistService getter-retirement implementation branch within
the scope above.

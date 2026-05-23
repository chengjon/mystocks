# Backend MarketDataServiceV2 Compatibility Getter Consumer Matrix - 2026-05-23

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: consumer-matrix-prepared-for-review
- Workline: G2.30 `MarketDataServiceV2` compatibility getter / dashboard
  helper consumer matrix
- Current HEAD: `04e2f7038386dbea1b8fc8bdcb24dd91dc7e9bb1`
- Parent issue: `#92`
- Service lifecycle issue: `#79`
- PR `#169`: MERGED at `2026-05-23T09:21:50Z`
- Execution mode: governance/evidence only
- Recorded at: `2026-05-23T17:25:26+08:00`

Boundary note: this packet classifies current `MarketDataServiceV2`
compatibility getter consumers only. It does not authorize backend source edits,
test edits, route edits, OpenAPI changes, OpenSpec changes, issue label
movement, `ready-for-agent` movement, PM2/runtime work, dashboard helper
migration, or compatibility getter deletion.

## Governance Boundary

This packet executes the G2.30 decision lane selected by G2.29. It is a
consumer matrix and authorization decision, not an implementation branch. It
does not create a source edit scope by itself.

The packet answers one narrow question: whether
`get_market_data_service_v2()` can be cleaned up after the `market_v2.py`
route-surface DI migration.

## Input State

PR `#169` was merged at
`04e2f7038386dbea1b8fc8bdcb24dd91dc7e9bb1`. That merge recorded:

- 152 service Python files scanned.
- 20 narrow service lifecycle candidate files.
- 5 completed route-surface DI seams.
- `market_v2.py` direct route getter calls remain `0`.
- `dashboard_data_source.py` still has two non-route helper compatibility
  calls.
- No direct next source implementation candidate was selected.
- This G2.30 consumer-matrix lane before any `MarketDataServiceV2`
  compatibility getter or dashboard helper source edit.

## Consumer Matrix Summary

The scan looked for:

- `get_market_data_service_v2`
- `get_market_data_service_v2_dependency`
- `install_market_data_service_v2`
- `MARKET_DATA_SERVICE_V2_STATE_KEY`
- `MarketDataServiceV2`

Scope:

| Area | Files with matches | Interpretation |
|---|---:|---|
| Route/API files | 2 | `market_v2.py` uses provider refs; `dashboard_data_source.py` still uses compatibility getter |
| Service files | 1 | Definition, installer, provider, state key, and compatibility getter surface |
| Test files | 3 | Provider lifecycle, runtime fallback, and file-level API integration references |
| Governance docs | 23 | Historical/planning evidence only; not runtime consumers |

Runtime and test token totals, excluding governance docs:

| Token | Count | Meaning |
|---|---:|---|
| `get_market_data_service_v2` | 6 | Dashboard helper calls, service definition/fallback, and lifecycle test monkeypatch |
| `get_market_data_service_v2_dependency` | 16 | Route provider refs, provider definition, and lifecycle test |
| `install_market_data_service_v2` | 3 | Installer definition, provider fallback, and lifecycle test |
| `MARKET_DATA_SERVICE_V2_STATE_KEY` | 5 | App-state key used by provider/tests |
| `MarketDataServiceV2` | 25 | Route type annotations, service class, runtime fallback tests, and API integration mention |

## Route And API Consumers

| File | Consumers | Direct compatibility getter calls | Dependency provider refs | Decision |
|---|---|---:|---:|---|
| `web/backend/app/api/market_v2.py` | `get_fund_flow`, `refresh_fund_flow`, `get_etf_list`, `refresh_etf_spot`, `get_lhb_detail`, `refresh_lhb_detail`, `get_sector_fund_flow`, `refresh_sector_fund_flow`, `get_stock_dividend`, `refresh_stock_dividend`, `get_stock_blocktrade`, `refresh_stock_blocktrade`, `refresh_all_market_data` | 0 | 14 | Keep provider refs; route-surface DI is complete |
| `web/backend/app/api/dashboard_data_source.py` | module import, `_get_market_overview_data`, `prewarm_dashboard_market_overview_cache` | 2 calls plus import | 0 | Keep as active dashboard-helper compatibility surface until a separate provider-migration packet is approved |

Route conclusion: there are no direct route-local calls to
`get_market_data_service_v2()` in `market_v2.py`. The route surface now depends
on `get_market_data_service_v2_dependency`, which is the canonical DI provider
for this lane. The dependency provider is not a cleanup target.

Dashboard conclusion: the two `dashboard_data_source.py` helper calls are active
non-route compatibility consumers. Treating them as cleanup leftovers would
exceed the G2.27/G2.28 route-provider boundary.

## Service Surface

| File | Current role | Decision |
|---|---|---|
| `web/backend/app/services/market_data_service_v2.py` | Defines `MarketDataServiceV2`, module-level compatibility getter, app-state installer, app-state dependency provider, and state key | Keep all current symbols as active compatibility/provider surface |

The module-level `get_market_data_service_v2()` is still used as the default
fallback by `install_market_data_service_v2(app, service=None)`. Removing it
would change the current app-state fallback behavior and would require a
separate implementation authorization with route/dashboard/test updates.

## Test Consumers

| File | Current role | Direct getter calls | Decision |
|---|---|---:|---|
| `web/backend/tests/test_market_data_service_v2_lifecycle_di.py` | App-state provider/installer lifecycle test; monkeypatches `get_market_data_service_v2` and asserts provider/installer behavior | 1 monkeypatch | Keep; it proves fallback and explicit service injection |
| `web/backend/tests/services/test_market_data_service_v2_runtime_fallback.py` | Runtime fallback tests instantiate `MarketDataServiceV2` directly | 0 | Keep; class-level service behavior coverage |
| `tests/api/file_tests/test_market_v2_api.py` | File-level API integration test mention of `MarketDataServiceV2` | 0 | Historical/file-level test reference; no getter cleanup implication |

## GitNexus Evidence

| Target | Result | Interpretation |
|---|---|---|
| `get_market_data_service_v2` | CRITICAL; direct impact 15; processes affected 6; modules affected 2 | Graph still reports `market_v2.py` route callers plus dashboard helper callers; current text guard shows route direct calls are `0`, so this is partly graph/text divergence, while dashboard helper calls remain real active compatibility consumers |
| `get_market_data_service_v2_dependency` | Target not found | GitNexus index does not yet expose this post-DI provider symbol; use text matrix until index refresh validates it |
| `install_market_data_service_v2` | Target not found | GitNexus index does not yet expose this post-DI installer symbol; use text matrix until index refresh validates it |
| `MarketDataServiceV2` | LOW; direct impact 0 | Class-level graph impact is not enough to justify deleting module-level compatibility functions |

## Decision

`get_market_data_service_v2()` remains **active dashboard-helper compatibility
surface**.

No `MarketDataServiceV2` compatibility getter cleanup implementation is
authorized by this packet.

Reasons:

- `market_v2.py` has `0` direct `get_market_data_service_v2()` calls, so there
  is no route-local cleanup left.
- `market_v2.py` intentionally uses `get_market_data_service_v2_dependency`;
  that provider is the canonical DI seam, not a legacy getter.
- `dashboard_data_source.py` still has two active non-route helper calls.
- Tests still validate the compatibility getter, installer, provider, and
  app-state fallback behavior.
- `install_market_data_service_v2(app, service=None)` currently uses
  `get_market_data_service_v2()` as its default fallback.
- GitNexus still reports `get_market_data_service_v2` as CRITICAL; this must not
  be treated as deletion proof.

Selected next lane:

**G2.31 `MarketDataServiceV2` dashboard helper provider migration authorization
packet.**

This is a future authorization packet, not an implementation step in this PR.
It should decide whether the two `dashboard_data_source.py` helper calls can be
migrated to a provider/app-state seam without changing route behavior,
OpenAPI schema, frontend contracts, or dashboard cache semantics.

## Future Scope If Dashboard Helper Migration Is Requested

Any future dashboard helper provider migration requires a separate
implementation authorization after human review. Its candidate write scope must
be explicit and should not include `market_v2.py` unless a future approved plan
changes the provider strategy.

Minimum future evidence before source edits:

1. Fresh text matrix showing direct getter calls, provider references, installer
   references, package exports, dashboard helper references, and tests.
2. GitNexus index refresh or an explicit graph-staleness note.
3. A decision on whether the compatibility getter is public API,
   dashboard-helper fallback, test-only fallback, package-internal fallback, or
   retirement candidate.
4. Focused tests covering:
   - `web/backend/tests/test_market_data_service_v2_lifecycle_di.py`
   - `web/backend/tests/services/test_market_data_service_v2_runtime_fallback.py`
   - dashboard data-source behavior for `_get_market_overview_data`
   - dashboard prewarm behavior for `prewarm_dashboard_market_overview_cache`
5. Rollback plan preserving `market_v2.py` route DI provider behavior and
   dashboard cache/prewarm behavior.

## Explicit Non-Goals

- No backend source edits
- No test edits
- No route/OpenAPI/docs/API/generated client edits
- No dashboard helper migration
- No compatibility getter deletion, rename, or privatization
- No issue label movement
- No OpenSpec proposal creation or archive
- No PM2/runtime verification

## Next Gate

Human review of this G2.30 matrix.

If accepted, keep `get_market_data_service_v2()` as active dashboard-helper
compatibility surface and prepare a separate G2.31 dashboard helper provider
migration authorization packet before any source edits.

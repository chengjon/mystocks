# Backend Stock Search Compatibility Getter Consumer Matrix - 2026-05-23

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: consumer-matrix-prepared-for-review
- Workline: G2.23 stock-search compatibility getter cleanup authorization /
  consumer matrix
- Base HEAD: `d186ce78ee0a`
- Parent issue: `#92`
- Service lifecycle issue: `#79`
- Execution mode: governance/evidence only
- Recorded at: `2026-05-23T11:40:44+08:00`

Boundary note: this packet classifies current stock-search service compatibility
getter consumers only. It does not authorize backend source edits, test edits,
route edits, OpenAPI changes, OpenSpec changes, issue label movement,
`ready-for-agent` movement, PM2/runtime work, or a compatibility getter deletion.

## Governance Boundary

This packet executes the G2.23 decision lane selected by G2.22. It is a
consumer matrix and authorization decision, not an implementation branch. It
does not create a source edit scope by itself.

The packet answers one narrow question: whether `get_stock_search_service()` can
be cleaned up after the route-surface DI migration.

## Input State

PR `#162` was merged at
`d186ce78ee0ad4017b36e3788a54533ce3a972df`. That merge recorded:

- 152 service Python files scanned.
- 42 broad heuristic service getter/singleton/provider hit files.
- 17 narrowed service lifecycle candidate files.
- No direct next route-surface implementation candidate.
- This G2.23 consumer-matrix lane before any stock-search compatibility getter
  source edit.

## Consumer Matrix Summary

The scan looked for:

- `get_stock_search_service`
- `get_stock_search_service_dependency`
- `install_stock_search_service`
- `STOCK_SEARCH_SERVICE_STATE_KEY`
- `StockSearchService`

Scope:

| Area | Files with matches | Interpretation |
|---|---:|---|
| Route files | 2 | Canonical dependency-provider references only |
| Service package files | 2 | Definition and package re-export surface |
| Test files | 5 | Compatibility, split/regression, and lifecycle DI assertions |
| Governance docs | 17 | Historical/planning evidence only; not runtime consumers |

Runtime and test token totals, excluding governance docs:

| Token | Count | Meaning |
|---|---:|---|
| `get_stock_search_service` | 10 | Definition/re-export plus test compatibility references |
| `get_stock_search_service_dependency` | 12 | Route provider, package export, provider definition, and lifecycle test |
| `install_stock_search_service` | 5 | Provider fallback, package export, and lifecycle test |
| `STOCK_SEARCH_SERVICE_STATE_KEY` | 7 | App-state key used by provider/export/tests |
| `StockSearchService` | 28 | Route type annotations, service class, and tests |

## Route Consumers

| File | Route handlers | Direct getter calls | Dependency provider refs | Decision |
|---|---|---:|---:|---|
| `web/backend/app/api/stock_search/stock_search_result.py` | `search_stocks`, `get_stock_quote`, `get_stock_news`, `get_market_news`, `clear_search_cache` | 0 | 6 | Keep provider refs; route-surface DI is complete |
| `web/backend/app/api/market/market_data_request.py` | `get_kline_data` | 0 | 2 | Keep provider refs; this is the approved fallback route consumer |

Route conclusion: there are no direct route-local calls to
`get_stock_search_service()`. The route surface now depends on
`get_stock_search_service_dependency`, which is the canonical DI provider for
this lane. The dependency provider is not a cleanup target.

## Service Package Surface

| File | Current role | Decision |
|---|---|---|
| `web/backend/app/services/stock_search_service/stock_search_service.py` | Defines `StockSearchService`, module-level compatibility getter, app-state installer, app-state dependency provider, and state key | Keep all current symbols as active compatibility/provider surface |
| `web/backend/app/services/stock_search_service/__init__.py` | Re-exports `StockSearchService`, `get_stock_search_service`, `get_stock_search_service_dependency`, `install_stock_search_service`, and `STOCK_SEARCH_SERVICE_STATE_KEY` | Keep package-level exports; tests and route imports rely on the package API |

The module-level `get_stock_search_service()` is still used as the default
fallback by `install_stock_search_service(app, service=None)`. Removing it would
change the current app-state fallback behavior and would require a separate
implementation proposal with route/test updates.

## Test Consumers

| File | Current role | Direct getter calls | Decision |
|---|---|---:|---|
| `web/backend/tests/test_runtime_regressions_p0.py` | Regression guard for compatibility getter singleton initialization and `StockSearchService` constructor behavior | 3 | Keep; it proves the compatibility getter remains valid |
| `web/backend/tests/test_stock_search_service_lifecycle_di.py` | App-state provider/installer lifecycle test | 0 direct calls; monkeypatches `get_stock_search_service` and calls provider/installer | Keep; it proves fallback and explicit service injection |
| `web/backend/tests/test_large_file_split_regressions.py` | Split-package public export regression | 0 direct calls; asserts callable package export | Keep unless package API is explicitly retired later |
| `web/backend/tests/test_stock_search_service_logging.py` | Logging and split-helper regression | 0 direct calls; asserts callable package export and instantiates service | Keep unless package API is explicitly retired later |
| `tests/001-fix-5-critical/plan.md` | Historical test plan mention only | 0 | Historical reference; not a runtime consumer |

## GitNexus Evidence

| Target | Result | Interpretation |
|---|---|---|
| `get_stock_search_service` | CRITICAL; direct impact 6; processes affected 11; route callers reported at confidence `0.5` | Graph still reports pre-DI route callers; current text guard shows route direct calls are `0`, so this is graph/text divergence and not deletion proof |
| `get_stock_search_service_dependency` | Target not found | GitNexus index does not yet expose this post-DI provider symbol; use text matrix until index refresh validates it |
| `install_stock_search_service` | Target not found | GitNexus index does not yet expose this post-DI installer symbol; use text matrix until index refresh validates it |
| `StockSearchService` | LOW; direct impact 0 | Class-level graph impact is not enough to justify deleting module-level compatibility functions |

## Decision

`get_stock_search_service()` remains **active public compatibility surface**.

No stock-search compatibility getter cleanup implementation is authorized by
this packet.

Reasons:

- Route files have `0` direct `get_stock_search_service()` calls, so there is no
  route-local cleanup left.
- Route files intentionally use `get_stock_search_service_dependency`; that
  provider is the canonical DI seam, not a legacy getter.
- Tests still validate the compatibility getter, package export, installer, and
  fallback behavior.
- `install_stock_search_service(app, service=None)` currently uses
  `get_stock_search_service()` as its default fallback.
- GitNexus still reports stale/heuristic route callers for the compatibility
  getter at confidence `0.5`; this must be reconciled before any deletion
  proposal.

## Future Scope If A Later Cleanup Is Requested

Any future stock-search compatibility cleanup would require a separate
implementation authorization after human review. Its candidate write scope would
need to be explicit and should not include route files unless a future approved
plan changes the provider strategy.

Minimum future evidence before source edits:

1. Fresh text matrix showing direct getter calls, provider references, installer
   references, package exports, and tests.
2. GitNexus index refresh or an explicit graph-staleness note.
3. A decision on whether the compatibility getter is public API, test-only
   fallback, package-internal fallback, or retirement candidate.
4. Focused tests covering:
   - `web/backend/tests/test_runtime_regressions_p0.py`
   - `web/backend/tests/test_stock_search_service_lifecycle_di.py`
   - `web/backend/tests/test_large_file_split_regressions.py`
   - `web/backend/tests/test_stock_search_service_logging.py`
5. Rollback plan preserving route DI provider behavior.

## Explicit Non-Goals

- No backend source edits
- No test edits
- No route/OpenAPI/docs/API/generated client edits
- No compatibility getter deletion, rename, or privatization
- No issue label movement
- No OpenSpec proposal creation or archive
- No PM2/runtime verification

## Next Gate

Human review of this G2.23 matrix. If accepted, keep the stock-search
compatibility getter as active compatibility surface and do not open a
stock-search cleanup implementation. The next service lifecycle DI step should
be a separate governance lane, likely a broad market/data/strategy seam design
packet, before any further service DI source edits.

# Change: Migrate `FundFlowMixin` (AkshareMarketDataAdapter) to OpenStock

> **Parent proposal**: `externalize-data-source-provider-to-openstock` (B4.014)
> **Scope**: `src/adapters/akshare/market_adapter/fund_flow.py` — `FundFlowMixin` class only
> **Predecessor**: Phase 1.1 batch 2 (commits `a40f38a0d` / `3c90212fb` / `d6209dc0a`) — endpoint-layer switch proven feasible

## Why

B4.014 Phase 1.1 batch 2 switched two endpoints (`hsgt-summary`, `north-stock/{symbol}`) at the **endpoint layer** by bypassing the adapter and calling `OpenStockClient` directly from `web/backend/app/api/akshare_market/fund_flow.py`. This was the correct call for a small-batch proof, but it leaves three structural problems that block B4.014 from completing:

1. **Akshare is still a runtime dependency.** `src/adapters/akshare/market_adapter/fund_flow.py` still does `import akshare as ak` and the seven remaining `FundFlowMixin` methods still call `ak.stock_hsgt_*`. AkShare version drift keeps breaking production (see P0 incident: `stock_hsgt_north_acc_flow_in_em` was removed in akshare 1.18.60). Until the import is gone, the dependency cannot be retired.
2. **The adapter abstraction is hollow.** With endpoint-layer bypass as the established pattern, every future endpoint switch duplicates `_build_openstock_client()` + `_translate_*_row()` + error-mapping boilerplate in the route file. `AkshareMarketDataAdapter` loses its purpose as the single data-access boundary.
3. **Six `FundFlowMixin` methods still hit akshare directly** even after Phase 1.1: `get_stock_hsgt_fund_flow_summary_em` (now superseded by Phase 1.1's endpoint-layer switch but the Mixin copy still imports akshare), `get_stock_hsgt_fund_flow_detail_em`, `get_stock_hsgt_north_net_flow_in_em`, `get_stock_hsgt_south_net_flow_in_em`, `get_stock_hsgt_north_acc_flow_in_em`, `get_stock_hsgt_south_acc_flow_in_em`, `get_stock_hsgt_hold_stock_em`, `get_stock_fund_flow_big_deal`. Eight methods + `get_stock_cyq_em` (chip distribution — out of scope, see Non-Goals).

This proposal moves the OpenStock switch from the endpoint layer down into the Mixin itself, so that **all fund-flow acquisition flows through `OpenStockClient`** and `akshare` import can be removed from this file.

## What Changes

- **MODIFIED** `src/adapters/akshare/market_adapter/fund_flow.py` — replace `import akshare as ak` and all `ak.stock_hsgt_*` / `ak.stock_fund_flow_big_deal` calls with `OpenStockClient` calls against the corresponding OpenStock categories.
- **MODIFIED** `AkshareMarketAdapter.__init__` (or constructor chain in `adapter.py`) — accept and store an `OpenStockClient` instance (constructor injection). Adapter methods that still genuinely need akshare (e.g., `cyq_em` chip distribution, other Mixins) retain akshare access for now.
- **REFACTORED** `web/backend/app/api/akshare_market/fund_flow.py` — remove the endpoint-layer `_build_openstock_client()` / `_translate_northbound_flow_row()` / `_translate_northbound_holding_row()` helpers (commit `a40f38a0d`) and route the two switched endpoints back through the adapter. The Mixin now does the translation.
- **ADDED** per-method translation units inside `FundFlowMixin` (mirroring `_translate_northbound_flow_row` / `_translate_northbound_holding_row` from Phase 1.1) so the existing endpoint-layer translations become Mixin methods.
- **REMOVED** `import akshare as ak` from `fund_flow.py` once all 8 methods are switched (this file only; other Mixins unchanged).
- **BREAKING (internal)** — `FundFlowMixin` methods change signature from `(self, start_date, end_date) -> pd.DataFrame` to `(self, ...) -> OpenStockFetchResult` (or wrap-into-DataFrame shim). The route handlers in `fund_flow.py` are the only callers; impact is internal and fully testable.

## Mapping: Mixin method → OpenStock category

| Mixin method | OpenStock category | Status |
|---|---|---|
| `get_stock_hsgt_fund_flow_summary_em` | `NORTHBOUND_FLOW` | ✅ Available (Phase 1.1 endpoint-layer proven) |
| `get_stock_hsgt_north_acc_flow_in_em` (per-symbol) | `NORTHBOUND_HOLDING` | ✅ Available (Phase 1.1 endpoint-layer proven) |
| `get_stock_hsgt_fund_flow_detail_em` | `NORTHBOUND_FLOW_DETAIL` | ⏳ OpenStock backlog |
| `get_stock_hsgt_north_net_flow_in_em` | `NORTHBOUND_DAILY_HISTORY` | ⏳ OpenStock backlog |
| `get_stock_hsgt_south_net_flow_in_em` | `SOUTHBOUND_DAILY_HISTORY` | ⏳ OpenStock backlog |
| `get_stock_hsgt_south_acc_flow_in_em` (per-symbol) | `SOUTHBOUND_HOLDING` | ⏳ OpenStock backlog |
| `get_stock_hsgt_hold_stock_em` | `HSGT_INDIVIDUAL_HOLDING` | ⏳ OpenStock backlog |
| `get_stock_fund_flow_big_deal` | `MARKET_BIG_DEAL_RANK` | ⏳ OpenStock backlog |

⏳ categories must be defined in `/opt/claude/openstock` before this proposal can complete the corresponding method switch. They are tracked as `## 4. OpenStock Contract-Gap Follow-up` in the parent proposal's `tasks.md`.

## Impact

- **Affected specs**: `data-source-runtime-service`, `data-sources` (delta under `specs/data-source-runtime-service/spec.md`)
- **Affected code**:
  - `src/adapters/akshare/market_adapter/fund_flow.py` (primary, ~400 LOC)
  - `src/adapters/akshare/market_adapter/adapter.py` (constructor change)
  - `web/backend/app/api/akshare_market/fund_flow.py` (revert endpoint-layer switch to adapter call)
  - `tests/api/test_fund_flow_openstock.py` (extend to cover all 8 methods, not just 2)
  - `tests/adapters/test_fund_flow_mixin.py` (new — Mixin-level unit tests with stubbed `OpenStockClient`)
  - `web/backend/.env` / `.env.example` (no change — `OPENSTOCK_BASE_URL` already configured in Phase 1.1)
- **Affected routes** (all under `/api/akshare/market/fund-flow/*`): `hsgt-summary`, `hsgt-detail`, `north-daily`, `south-daily`, `north-stock/{symbol}`, `south-stock/{symbol}`, `hsgt-holdings/{symbol}`, `big-deal`
- **Out of scope**:
  - Other Mixins (`KlineMixin`, `QuoteMixin`, `MarketOverviewMixin`, etc.) — separate proposals per Mixin
  - `get_stock_cyq_em` (chip-distribution pseudo-fund-flow) — belongs to a different OpenStock category family; deferred
  - Frontend changes — frontend contract (Chinese wide-table) is preserved as-is, zero frontend change required
  - `/opt/claude/openstock` modifications — category gaps are tracked in the parent proposal
- **Non-Goals**:
  - Do not retire `/api/akshare/market/**` route prefix (compatibility preserved per parent proposal)
  - Do not introduce feature flags for akshare fallback — once Mixin is switched, akshare is removed from this file
  - Do not migrate `cyq_em` or other Mixins in this proposal
- **Risks**:
  - 6 of 8 OpenStock categories are still backlog — implementation ships in waves (2 methods first, then batches as OpenStock adds categories). Each wave requires its own e2e + browser verification per Phase 1.1 playbook.
  - Constructor signature change on `AkshareMarketAdapter` may break callers in tests or scripts — needs grep audit before merge.
  - DataFrame-vs-`OpenStockFetchResult` return type shift: if any caller still expects DataFrame, will surface as runtime error. Mitigated by adapting the result to a DataFrame-shaped object at the adapter boundary (or migrating callers).

## Implementation Phasing

Per the parent proposal's Playbook, this work executes in three waves:

- **Wave 1 (this proposal, ready now)**: 2 methods (`get_stock_hsgt_fund_flow_summary_em`, `get_stock_hsgt_north_acc_flow_in_em`). Both endpoints already switched at endpoint layer in Phase 1.1 — this wave lifts the switch into the Mixin and removes the endpoint-layer bypass.
- **Wave 2**: 4 methods (`north-net-flow`, `south-net-flow`, `south-acc-flow`, `fund_flow_detail`). Blocked on OpenStock categories `NORTHBOUND_DAILY_HISTORY`, `SOUTHBOUND_DAILY_HISTORY`, `SOUTHBOUND_HOLDING`, `NORTHBOUND_FLOW_DETAIL`.
- **Wave 3**: 2 methods (`hsgt_hold_stock`, `big_deal`). Blocked on `HSGT_INDIVIDUAL_HOLDING`, `MARKET_BIG_DEAL_RANK`.

Each wave is a separate `tasks.md` checkbox group; the proposal ships only after Wave 3.

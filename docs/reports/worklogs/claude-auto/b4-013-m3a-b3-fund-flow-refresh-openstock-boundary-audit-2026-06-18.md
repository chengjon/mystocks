# B4.013-M3a-B3 FUND_FLOW refresh OpenStock boundary audit

Date: 2026-06-18
Mode: no-source boundary audit
Node: `b4-013-m3a-b3-fund-flow-refresh-openstock-audit`
Repository: `mystocks_spec`
OpenStock evidence repository: `/opt/claude/openstock`

## Scope

This audit covers the `market_v2` FUND_FLOW refresh boundary before any MyStocks source change.

Allowed in this phase:

- Read current MyStocks route, service, model, and OpenStock consumer contract.
- Read OpenStock provider-contract evidence for `FUND_FLOW`.
- Record the migration boundary and next implementation split.
- Keep all findings in governance/worklog artifacts.

Explicitly not allowed in this phase:

- No source, runtime, API, route, store, frontend, OpenSpec, or test edits.
- No provider/data-source implementation in MyStocks.
- No OpenStock source edit from this MyStocks workstream.
- No staging of external dirty files.

## Boundary Check

Current MyStocks branch/head:

- Branch: `wip/root-dirty-20260403`
- Head at audit start: `f90dee916 B4.013: align mainline methodology and queue priority`

Current OpenStock evidence head:

- Head observed during audit: `ca9ba1c feat: add zzshare dragon tiger trader category`

Working-tree isolation:

- Target MyStocks service/test files were clean at audit start.
- `web/backend/app/api/market_v2.py` is externally dirty and was treated as read-only evidence only.
- Existing unrelated dirty/untracked worklogs and other external files remain out of scope.

GitNexus impact evidence:

- Target symbol: `MarketDataServiceV2.fetch_and_save_fund_flow`
- GitNexus UID: `Method:web/backend/app/services/market_data_service_v2.py:MarketDataServiceV2.fetch_and_save_fund_flow#2`
- Risk: `LOW`
- Direct callers: `refresh_fund_flow`, `refresh_all_market_data`
- Affected process: `refresh_all_market_data`
- Affected modules: `Api`

## MyStocks Current Truth

Active route surface in `web/backend/app/api/market_v2.py`:

- `GET /fund-flow`
  - Calls `service.query_fund_flow(symbol, timeframe, start_date, end_date)`.
  - Read path remains database-backed and is not a provider call boundary.
- `POST /fund-flow/refresh`
  - Calls `service.fetch_and_save_fund_flow(symbol, timeframe)`.
  - This is the target acquisition/persistence boundary.
- `POST /refresh-all`
  - Calls `service.fetch_and_save_fund_flow(None, "今日")`.
  - This is a legacy all-market refresh behavior and is not compatible with the current OpenStock `FUND_FLOW` contract.

Current service behavior in `web/backend/app/services/market_data_service_v2.py`:

- `fetch_and_save_fund_flow(symbol: Optional[str] = None, timeframe: str = "今日")`
- Current provider call: `self.em_adapter.get_stock_fund_flow(symbol, timeframe)`
- Supported legacy timeframe map:
  - `"今日"` -> `"1"`
  - `"3日"` -> `"3"`
  - `"5日"` -> `"5"`
  - `"10日"` -> `"10"`
- Current persistence uses local current date as `trade_date`, not provider `trade_date`.
- Persisted `FundFlow` fields:
  - `symbol`
  - `trade_date`
  - `timeframe`
  - `main_net_inflow`
  - `main_net_inflow_rate`
  - `super_large_net_inflow`
  - `large_net_inflow`
  - `medium_net_inflow`
  - `small_net_inflow`
- Duplicate protection is based on `(symbol, today, timeframe)`.

Current read path:

- `query_fund_flow(symbol, timeframe="1", start_date=None, end_date=None)` reads `FundFlow` records from MyStocks database.
- This path can remain stable if refresh persistence preserves the model contract.

## OpenStock FUND_FLOW Contract Truth

OpenStock provider category evidence:

- Public category: `FUND_FLOW`
- Provider adapter: AkShare
- Provider endpoint: `akshare.stock_individual_fund_flow(stock, market)`
- OpenStock adapter file: `/opt/claude/openstock/openstock/adapters/akshare.py`
- OpenStock tests: `/opt/claude/openstock/tests/test_akshare_runtime_pilot.py`, `/opt/claude/openstock/tests/test_runtime_contract.py`

OpenStock input semantics:

- `symbol` is required.
- `market` is optional when it can be inferred from symbol.
- Prefixed symbols such as `sz.000001` are normalized to stock `000001` and inferred market `sz`.
- Missing `symbol` raises `ValueError("symbol is required")`.
- `FUND_FLOW` has no fallback candidate in the observed OpenStock adapter.

OpenStock output semantics:

- Normalized records include:
  - `symbol`
  - `trade_date`
  - `close`
  - `pct_chg`
  - `main_net_inflow`
  - `main_net_inflow_ratio`
  - `super_large_net_inflow`
  - `super_large_net_inflow_ratio`
  - `large_net_inflow`
  - `large_net_inflow_ratio`
  - `medium_net_inflow`
  - `medium_net_inflow_ratio`
  - `small_net_inflow`
  - `small_net_inflow_ratio`
  - `net_inflow`
  - `net_inflow_ratio`
- Empty provider result is a successful fetch with `data=[]`.
- Provider failures propagate through the OpenStock runtime contract.

## Compatibility Decision

The current OpenStock `FUND_FLOW` category is compatible with a narrow MyStocks refresh slice:

- `symbol` is provided.
- `timeframe` represents daily/today semantics, effectively `"今日"` or stored timeframe `"1"`.
- MyStocks persists provider `trade_date` and maps normalized OpenStock numeric fields into the existing `FundFlow` model.

The current OpenStock `FUND_FLOW` category is not compatible with these legacy MyStocks semantics:

- `symbol=None` all-market refresh through `refresh_all_market_data`.
- Multi-day aggregate timeframes `"3日"`, `"5日"`, and `"10日"`.
- Legacy EastMoney-style raw columns such as timeframe-prefixed main/super-large/large/medium/small flow values.

Therefore B3 must not be implemented as a blanket provider replacement. It must be split into a safe source-authorized vertical slice and a separate contract/decision slice.

## Proposed Next Split

### B4.013-M3a-B3a: source-authorized safe migration slice

Purpose:

- Migrate only symbol-scoped, daily/today FUND_FLOW refresh to the MyStocks OpenStock backend consumer.

Proposed allowed files:

- `web/backend/app/services/market_data_service_v2.py`
- `web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py`

Required implementation behavior:

- When `symbol` is provided and `timeframe` is `"今日"` or equivalent daily storage timeframe, call OpenStock category `FUND_FLOW`.
- Do not call `self.em_adapter.get_stock_fund_flow` for that supported slice.
- Persist OpenStock `trade_date`, not local current date, for returned records.
- Map fields:
  - `main_net_inflow` -> `FundFlow.main_net_inflow`
  - `main_net_inflow_ratio` -> `FundFlow.main_net_inflow_rate`
  - `super_large_net_inflow` -> `FundFlow.super_large_net_inflow`
  - `large_net_inflow` -> `FundFlow.large_net_inflow`
  - `medium_net_inflow` -> `FundFlow.medium_net_inflow`
  - `small_net_inflow` -> `FundFlow.small_net_inflow`
- Store timeframe as `"1"` for this daily/today slice.
- Preserve MyStocks public routes and response shape.
- Preserve frontend-to-MyStocks architecture; no frontend-to-OpenStock call.

Required tests:

- Add/extend service-level tests in `test_market_data_service_v2_openstock_refresh.py`.
- Assert `FUND_FLOW` consumer category and params.
- Assert local provider adapter is not called for the supported slice.
- Assert persistence field mapping and duplicate key behavior use OpenStock `trade_date`.
- Assert empty OpenStock payload maps to a controlled MyStocks no-data response.

### B4.013-M3a-B3b: contract decision slice

Purpose:

- Decide how to handle legacy no-symbol all-market refresh and multi-day aggregate timeframes.

Decision options:

- Extend OpenStock with a separate category/params contract for all-market or ranked FUND_FLOW acquisition.
- Keep these legacy semantics temporarily on the existing MyStocks provider path until OpenStock defines the provider contract.
- Retire or narrow the public behavior only through an explicit compatibility decision.

Non-goals:

- Do not synthesize 3/5/10-day aggregates inside MyStocks from daily OpenStock rows without a separate product/contract decision.
- Do not add provider fallback, provider SDK calls, or new data-source adapters in MyStocks.

## Risk Assessment

Impact:

- Runtime impact is limited if B3a only changes `fetch_and_save_fund_flow` for symbol-scoped daily refresh.
- `refresh_fund_flow` and `refresh_all_market_data` are the known direct callers.
- `refresh_all_market_data` currently passes `symbol=None`; this must remain guarded from accidental OpenStock `FUND_FLOW` calls until B3b is decided.

Risk level:

- B3 audit: low, docs/governance only.
- B3a implementation: medium-low if strictly limited to symbol/today.
- B3b decision: medium because public compatibility and OpenStock provider contract semantics are involved.

Primary hazard:

- Treating OpenStock `FUND_FLOW` as a full replacement for legacy EastMoney fund-flow refresh would break `symbol=None` refresh and multi-day aggregate timeframes.

## Gates For This No-Source Package

Required before commit:

- `git diff --check`
- `git diff --cached --check`
- GitNexus `verify-staged`
- GitNexus `detect-changes --scope staged`
- OPENDOG verification freshness
- Exact staging limited to governance/worklog files for this audit

Source/test gates are deferred until B3a source authorization.

## Current Conclusion

B4.013-M3a-B3 is evidence-prepared as a no-source boundary audit.

The next executable implementation should be `B4.013-M3a-B3a FUND_FLOW symbol/today service-only migration`, and it requires explicit source authorization for the service and directly bound service tests only. The all-market and multi-day aggregate semantics must remain out of B3a and be handled under a separate `B3b` contract decision.

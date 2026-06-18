# B4.013-M3a-B3b FUND_FLOW all-market and multi-day contract decision

Date: 2026-06-18
Mode: no-source contract decision audit
Node: `b4-013-m3a-b3b-fund-flow-all-market-multi-day-decision`
Repository: `mystocks_spec`
OpenStock evidence repository: `/opt/claude/openstock`

## Scope

This package decides how to handle the FUND_FLOW legacy compatibility surface that B3a intentionally did not migrate:

- `symbol=None` all-market refresh.
- `timeframe` values `"3日"`, `"5日"`, and `"10日"`.
- Existing route compatibility for `/fund-flow/refresh` and `/refresh-all`.

Allowed in this package:

- Read MyStocks route/service/adapter/model truth.
- Read OpenStock local contract evidence.
- Produce a decision matrix and next queue recommendation.
- Record evidence in docs/governance only.

Explicitly not allowed:

- No source/runtime/test/API/route edits.
- No OpenStock repository edits from this MyStocks line.
- No provider fallback, provider SDK calls, or adapter expansion in MyStocks.
- No direct frontend-to-OpenStock contract.
- No staging of external dirty files.

## Current Heads And Boundary State

MyStocks:

- Branch: `wip/root-dirty-20260403`
- Head at audit start: `96ff8a2df B4.013-M3a-B3a: close FUND_FLOW symbol refresh migration`
- Staged state: empty.
- Known external dirty file still isolated: `web/backend/app/api/market_v2.py`.

OpenStock:

- Head observed: `512143c feat: add eltdx market depth category`
- Working tree status: clean.

## MyStocks Route Truth

`web/backend/app/api/market_v2.py` exposes:

- `GET /fund-flow`
  - Requires `symbol`.
  - Reads persisted `FundFlow` records through `query_fund_flow(symbol, timeframe, start_date, end_date)`.
  - This is a MyStocks read-model query and is not a provider acquisition boundary.
- `POST /fund-flow/refresh`
  - Accepts `symbol: Optional[str] = None`.
  - Accepts `timeframe: "今日" / "3日" / "5日" / "10日"`.
  - Documents `symbol=None` as all-market refresh.
- `POST /refresh-all`
  - Calls `service.fetch_and_save_fund_flow(None, "今日")`.

After B3a, `web/backend/app/services/market_data_service_v2.py` behaves as follows:

- `symbol` provided and `timeframe in {"今日", "1"}`:
  - Uses OpenStock consumer category `FUND_FLOW`.
- Any other slice:
  - Still uses the legacy local EastMoney adapter path:
    - `symbol=None`
    - `"3日"`
    - `"5日"`
    - `"10日"`

The existing storage model has only the persisted fields needed by MyStocks:

- `symbol`
- `trade_date`
- `timeframe`
- `main_net_inflow`
- `main_net_inflow_rate`
- `super_large_net_inflow`
- `large_net_inflow`
- `medium_net_inflow`
- `small_net_inflow`

## Legacy Provider Semantics

`web/backend/app/adapters/eastmoney_adapter.py::get_stock_fund_flow` currently provides the legacy behavior:

- `symbol` is optional.
- If `symbol` is omitted, the method returns all-market stock fund-flow ranking rows.
- `timeframe` accepts:
  - `"今日"`
  - `"3日"`
  - `"5日"`
  - `"10日"`
- If `symbol` is provided, the method filters the all-market result by stock code.

This is ranking-style market-wide acquisition, not the same as OpenStock's current single-stock historical FUND_FLOW category.

## OpenStock Contract Truth

OpenStock current `FUND_FLOW` implementation:

- Category: `FUND_FLOW`
- Provider path: AkShare `stock_individual_fund_flow(stock, market)`
- Input: `symbol` is required.
- Missing symbol raises `ValueError("symbol is required")`.
- No fallback candidates are registered for `FUND_FLOW`.
- Output shape is individual-stock historical fund-flow records.
- Current docs explicitly note that this path does not fabricate `name`, `rank`, or `provider_timestamp`.

OpenStock current `SECTOR_FUND_FLOW` implementation:

- Category: `SECTOR_FUND_FLOW`
- Provider path: AkShare `stock_sector_fund_flow_rank(indicator, sector_type)`
- Supports sector dimensions: `industry`, `concept`, `region`.
- Supports indicators/timeframes such as `今日`, `5日`, and `10日`.
- Output shape is sector ranking records, not stock-level all-market fund-flow rows.

Therefore:

- Current OpenStock `FUND_FLOW` cannot represent MyStocks `symbol=None` all-market stock ranking.
- Current OpenStock `FUND_FLOW` cannot represent EastMoney-style `3日` / `5日` / `10日` stock ranking rows.
- Current OpenStock `SECTOR_FUND_FLOW` cannot be used as a stock-level all-market substitute.

## Compatibility Matrix

| MyStocks route slice | Current owner | OpenStock current coverage | Decision |
| --- | --- | --- | --- |
| `POST /fund-flow/refresh?symbol=000001&timeframe=今日` | MyStocks consumer via OpenStock | Covered by `FUND_FLOW` | Done in B3a |
| `POST /fund-flow/refresh?symbol=000001&timeframe=1` | MyStocks consumer via OpenStock | Covered by `FUND_FLOW` | Done in B3a |
| `POST /fund-flow/refresh?symbol=000001&timeframe=3日/5日/10日` | Legacy MyStocks provider path | Not covered | Do not migrate under current contract |
| `POST /fund-flow/refresh` with `symbol=None` | Legacy MyStocks provider path | Not covered | Do not migrate under current contract |
| `POST /refresh-all` fund-flow subtask | Legacy MyStocks provider path | Not covered | Keep temporarily; requires OpenStock contract before migration |
| `GET /fund-flow` read query | MyStocks persisted read model | Not a provider acquisition boundary | Keep in MyStocks |

## Options Considered

### Option A: Extend OpenStock with a dedicated stock ranking category

Potential category name:

- `STOCK_FUND_FLOW_RANKING`
- or `MARKET_FUND_FLOW_RANKING`

Contract shape:

- Provider runtime owner: OpenStock.
- Params:
  - `timeframe` or `indicator`: `"今日"`, `"3日"`, `"5日"`, `"10日"` if provider supports them.
  - Optional `symbol` filter as consumer-side compatibility convenience.
  - Optional `limit`, `market`, or exchange filters only if provider support is confirmed.
- Output should include stock-level fields compatible with MyStocks persistence:
  - `symbol`
  - `name` if provider returns it
  - `rank` if provider returns it
  - `trade_date` or documented provider-date semantics
  - `timeframe`
  - `main_net_inflow`
  - `main_net_inflow_ratio`
  - `super_large_net_inflow`
  - `large_net_inflow`
  - `medium_net_inflow`
  - `small_net_inflow`
  - corresponding ratio fields when available

Assessment:

- This is the preferred long-term direction if all-market/multi-day fund-flow refresh remains a supported public compatibility feature.
- It belongs in OpenStock, not in MyStocks.
- It needs OpenStock-side provider mapping and tests before MyStocks can consume it.

### Option B: Overload existing OpenStock `FUND_FLOW`

Example:

- `FUND_FLOW` with `symbol=None` returns ranking rows.
- `FUND_FLOW` with `symbol` returns individual-stock historical rows.

Assessment:

- Not recommended.
- The current `FUND_FLOW` contract is single-stock historical acquisition and requires `symbol`.
- Overloading it would mix incompatible schemas and failure semantics under one category.
- It would make MyStocks response adaptation fragile.

### Option C: Keep the current MyStocks legacy provider path temporarily

Assessment:

- Acceptable only as a short-term compatibility hold.
- It must not be expanded, refactored into a new provider layer, or treated as the target architecture.
- It prevents route behavior regression while OpenStock lacks a dedicated contract.
- It must remain visible as technical debt under the OpenStock externalization line.

### Option D: Retire `symbol=None` and multi-day refresh from MyStocks

Assessment:

- Not safe as an implicit cleanup.
- It changes public route behavior.
- It needs a separate compatibility/deprecation decision and likely OpenSpec proposal.
- It may break existing `refresh-all` behavior and any frontend/admin workflows relying on all-market refresh.

## Decision

B3b decision:

1. Do not migrate `symbol=None`, `"3日"`, `"5日"`, or `"10日"` FUND_FLOW refresh to OpenStock under the current `FUND_FLOW` contract.
2. Do not add provider fallback, provider SDK calls, or new local provider adapter behavior in MyStocks.
3. Keep the existing MyStocks legacy path temporarily only to preserve compatibility.
4. Treat stock-level all-market and multi-day fund-flow ranking as a missing OpenStock provider contract.
5. If the feature remains required, the next provider-side work must be an OpenStock category contract such as `STOCK_FUND_FLOW_RANKING` or `MARKET_FUND_FLOW_RANKING`.
6. MyStocks can only migrate these legacy slices after that OpenStock contract exists and is provider-tested.

## Impact And Risk

Impact:

- No runtime change in this package.
- No route behavior change.
- No persistence schema change.
- No OpenStock repo change.

Risk if ignored:

- Accidentally forcing `symbol=None` into current OpenStock `FUND_FLOW` would fail because OpenStock requires `symbol`.
- Mapping all-market ranking rows into the single-stock historical category would create schema ambiguity.
- Synthesizing multi-day values in MyStocks would violate the provider boundary and reintroduce provider responsibility into the application repository.

Risk of the selected decision:

- MyStocks retains a temporary legacy provider path for these slices.
- This is an architectural debt, but it is explicit, isolated, and not expanded.

## Next Queue Recommendation

Immediate next MyStocks work:

1. Continue to `B4.013-M3a-B4 SECTOR_FUND_FLOW readiness and refresh migration` as a separate no-source/readiness pass first.
2. Only proceed to B4 source implementation if OpenStock `SECTOR_FUND_FLOW` contract is confirmed sufficient for MyStocks route compatibility.
3. Keep B3b unsupported slices out of B4.

Parallel or later OpenStock-side work:

1. Define an OpenStock stock-level fund-flow ranking category if all-market/multi-day refresh remains required.
2. Implement provider mapping and tests in OpenStock.
3. Return to MyStocks with a new source-authorized consumer migration package after OpenStock contract evidence exists.

Do not create a MyStocks source implementation package for B3b now.

## Verification Scope For This Package

Because this is no-source:

- Required gates are governance/documentation only.
- No Python unit tests are required.
- No runtime source checks are required.

Required before commit:

- `git diff --check`
- `git diff --cached --check`
- FUNCTION_TREE validate
- GitNexus staged verify/detect
- OPENDOG fresh verification
- Exact staging limited to B3b worklog and governance metadata

## Final State

B4.013-M3a-B3b is ready as a no-source decision package.

It does not authorize source edits. It blocks direct migration of all-market and multi-day FUND_FLOW refresh until OpenStock has a dedicated provider contract or MyStocks receives a separate explicit deprecation decision.

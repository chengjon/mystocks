# B4.013-M3a-B4 SECTOR_FUND_FLOW readiness audit

Date: 2026-06-18
Mode: no-source readiness audit
Node: `b4-013-m3a-b4-sector-fund-flow-readiness-audit`
Repository: `mystocks_spec`
OpenStock evidence repository: `/opt/claude/openstock`

## Scope

This package audits whether MyStocks can migrate its sector fund-flow refresh path to OpenStock without reintroducing provider ownership into MyStocks.

Allowed in this package:

- Read MyStocks route, service, model, and focused refresh-test truth.
- Read OpenStock local contract and AkShare adapter evidence.
- Produce a readiness matrix and next implementation recommendation.
- Record governance evidence only.

Explicitly not allowed:

- No source, runtime, route, schema, model, or test edits.
- No OpenStock repository edits from this MyStocks line.
- No provider fallback, provider SDK calls, or provider adapter expansion in MyStocks.
- No frontend-to-OpenStock direct contract.
- No staging of external dirty files.

## Current Heads And Boundary State

MyStocks:

- Branch: `wip/root-dirty-20260403`.
- Head at audit start: `8946e165c B4.013-M3a-B3b: decide FUND_FLOW legacy contract boundary`.
- Staged state at audit start: empty.
- Known external dirty file still isolated: `web/backend/app/api/market_v2.py`.
- Worktree contains many unrelated dirty/untracked files; this audit must stage only B4 governance/worklog files.

OpenStock:

- Evidence read from local repository `/opt/claude/openstock`.
- MyStocks line remains consumer-only; any missing OpenStock provider capability must be handled in OpenStock, not reimplemented in MyStocks.

## MyStocks Route Truth

`web/backend/app/api/market_v2.py` exposes the active compatibility surface:

- `GET /sector/fund-flow`
  - Query params:
    - `sector_type`, default `行业`, documented values `行业/概念/地域`.
    - `timeframe`, default `今日`, documented values `今日/3日/5日/10日`.
    - `limit`, default `100`, range `1..500`.
  - Calls `service.query_sector_fund_flow(sector_type, timeframe, limit)`.
  - This is a MyStocks read-model query, not provider acquisition.
- `POST /sector/fund-flow/refresh`
  - Query params:
    - `sector_type`, default `行业`, documented values `行业/概念/地域`.
    - `timeframe`, default `今日`, documented values `今日/3日/5日/10日`.
  - Calls `service.fetch_and_save_sector_fund_flow(sector_type, timeframe)`.
  - Current route docstring still says it refreshes from EastMoney.

The route file is externally dirty and was treated as read-only evidence only.

## MyStocks Service Truth

`web/backend/app/services/market_data_service_v2.py` currently has the OpenStock consumer helper already used by earlier B4.013 slices:

- `_fetch_openstock_records(data_category, params=...)`.
- Existing migrated refresh slices:
  - `ETF_SPOT`.
  - `BLOCK_TRADE`.
  - `DRAGON_TIGER`.
  - `FUND_FLOW` only for `symbol + 今日/1`.

Current sector fund-flow behavior:

- `_build_sector_fund_flow_runtime_rows(sector_type, timeframe, limit)`
  - Still calls `self.em_adapter.get_sector_fund_flow(sector_type, timeframe)`.
  - Produces runtime fallback rows for query fallback.
- `fetch_and_save_sector_fund_flow(sector_type="行业", timeframe="今日")`
  - Still calls `self.em_adapter.get_sector_fund_flow(sector_type, timeframe)`.
  - Persists `SectorFundFlow` rows into MyStocks storage.
  - De-duplicates by `sector_code`, `trade_date`, and `timeframe`.
- `query_sector_fund_flow(sector_type="行业", timeframe="今日", limit=100)`
  - Reads latest persisted `SectorFundFlow` rows.
  - Falls back to runtime provider rows when runtime fallback is enabled and no persisted latest date exists.

This means B4 implementation, if authorized, should target refresh acquisition first. Query behavior can stay MyStocks read-model based.

## MyStocks Model Truth

`web/backend/app/models/market_data.py::SectorFundFlow` persists:

- `sector_code`, non-null.
- `sector_name`, non-null.
- `sector_type`, non-null, stored in compatibility values such as `行业/概念/地域`.
- `trade_date`, primary-key date.
- `timeframe`, non-null, documented as `今日/3日/5日/10日`.
- `latest_price`.
- `change_percent`.
- `main_net_inflow` and `main_net_inflow_rate`.
- `super_large_net_inflow` and ratio.
- `large_net_inflow` and ratio.
- `medium_net_inflow` and ratio.
- `small_net_inflow` and ratio.
- `leading_stock` and `leading_stock_change_percent`.

Important compatibility pressure:

- The persisted model currently requires `sector_code`.
- The service currently uses `trade_date = date.today()` at save time.
- OpenStock current `SECTOR_FUND_FLOW` does not fabricate `sector_code` or `trade_date`.

Therefore, a safe MyStocks implementation can derive `trade_date` locally exactly as the legacy save path does, but `sector_code` requires an explicit compatibility policy.

## OpenStock Contract Truth

OpenStock `docs/contracts/MYSTOCKS_MARKET_DATA_CATEGORY_GAPS.md` states:

- `SECTOR_FUND_FLOW` is implemented by AkShare.
- Provider path: `stock_sector_fund_flow_rank(indicator, sector_type)`.
- OpenStock sector types:
  - `industry`
  - `concept`
  - `region`
- Provider sector-type mapping:
  - `industry` -> `行业资金流`
  - `concept` -> `概念资金流`
  - `region` -> `地域资金流`
- Supported `indicator` values:
  - `今日`
  - `5日`
  - `10日`
- `timeframe` is accepted as an alias for `indicator`.
- Current normalized fields include:
  - `sector_name`
  - `sector_type`
  - `rank`
  - `change_pct`
  - `main_net_inflow`, `main_net_inflow_ratio`
  - `super_large_net_inflow`, `super_large_net_inflow_ratio`
  - `large_net_inflow`, `large_net_inflow_ratio`
  - `medium_net_inflow`, `medium_net_inflow_ratio`
  - `small_net_inflow`, `small_net_inflow_ratio`
  - `net_inflow`, `net_inflow_ratio`
  - `leading_name`
  - `leading_symbol`

OpenStock `openstock/adapters/akshare.py` confirms:

- `SECTOR_FUND_FLOW` is in `supported_categories`.
- `fallback_candidates_for_category(SECTOR_FUND_FLOW)` returns no fallback candidates.
- `_fetch_sector_fund_flow` calls `stock_sector_fund_flow_rank(indicator=..., sector_type=...)`.
- `_sector_fund_flow_type` rejects values outside `industry/concept/region`.
- `_sector_fund_flow_indicator` rejects values outside `今日/5日/10日`.
- `_normalize_sector_fund_flow_record` validates required AkShare ranking fields and returns normalized records.

OpenStock tests confirm:

- A runtime pilot test fetches `SECTOR_FUND_FLOW` with `{"sector_type": "industry", "indicator": "今日"}`.
- The expected provider call is `{"indicator": "今日", "sector_type": "行业资金流"}`.

## Readiness Matrix

| MyStocks compatibility slice | OpenStock readiness | Decision |
| --- | --- | --- |
| `sector_type=行业`, `timeframe=今日` | Ready after MyStocks maps `行业 -> industry`; OpenStock accepts `今日`. | Safe implementation candidate. |
| `sector_type=概念`, `timeframe=今日` | Ready after MyStocks maps `概念 -> concept`; OpenStock accepts `今日`. | Safe implementation candidate. |
| `sector_type=地域`, `timeframe=今日` | Ready after MyStocks maps `地域 -> region`; OpenStock accepts `今日`. | Safe implementation candidate. |
| `sector_type=行业/概念/地域`, `timeframe=5日` | Ready after sector-type mapping; OpenStock accepts `5日`. | Safe implementation candidate. |
| `sector_type=行业/概念/地域`, `timeframe=10日` | Ready after sector-type mapping; OpenStock accepts `10日`. | Safe implementation candidate. |
| `sector_type=行业/概念/地域`, `timeframe=3日` | Not supported by current OpenStock contract. | Keep legacy path unless OpenStock adds provider contract. |
| MyStocks `sector_code` persistence | OpenStock does not provide `sector_code`. | Requires explicit compatibility policy before source edit. |
| MyStocks `trade_date` persistence | OpenStock does not provide `trade_date`, but legacy save already uses local `date.today()`. | Safe to preserve local save-date behavior. |
| MyStocks `leading_stock` | OpenStock has `leading_name` and `leading_symbol`. | Map `leading_name` to `leading_stock`; optionally leave change percent empty/None. |
| MyStocks `latest_price` | OpenStock ranking output does not expose index price. | Preserve default/empty behavior or keep legacy if price is required. |

## Recommended B4a Implementation Slice

If source authorization is granted, implement only this limited slice:

- File scope:
  - `web/backend/app/services/market_data_service_v2.py`.
  - Direct focused tests in `web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py`.
- Behavior:
  - Add a local MyStocks compatibility mapper for `sector_type`:
    - `行业 -> industry`
    - `概念 -> concept`
    - `地域 -> region`
  - Route only `timeframe in {"今日", "5日", "10日"}` through OpenStock category `SECTOR_FUND_FLOW`.
  - Pass OpenStock params:
    - `sector_type`: mapped English value.
    - `indicator` or `timeframe`: original supported timeframe.
  - Preserve MyStocks persisted compatibility values:
    - `sector_type`: original Chinese route value.
    - `timeframe`: original Chinese route value.
    - `trade_date`: local `date.today()` as current legacy behavior.
  - Map normalized numeric fields from OpenStock to `SectorFundFlow`.
  - Map `sector_name`.
  - Map `leading_name` to `leading_stock`.
  - For missing `sector_code`, use a deterministic compatibility value only if approved. Safer options:
    - Preferred: use `leading_symbol` only for leading stock and require an OpenStock-side future `sector_code` enhancement before full persistence migration.
    - Limited compatibility option: use `sector_name` as a temporary deterministic key when `sector_code` is absent, but only if explicitly accepted as a storage compatibility shim.
  - Keep `timeframe="3日"` on legacy EastMoney path with no OpenStock call.
- Non-goals:
  - Do not modify route, API path, frontend, schemas, OpenStock repo, or provider adapters.
  - Do not add MyStocks provider fallback or direct provider SDK calls.
  - Do not change query/read-model semantics.

## Risk Assessment

Impact:

- Medium for `fetch_and_save_sector_fund_flow` because it changes acquisition source for an active refresh endpoint.
- Low for read route if implementation keeps `query_sector_fund_flow` unchanged.
- Medium compatibility risk around `sector_code` because MyStocks persistence currently requires it and OpenStock current category intentionally does not fabricate it.
- Low provider-boundary risk if MyStocks only calls `_fetch_openstock_records("SECTOR_FUND_FLOW", ...)` and does not add any local provider code.

Primary blockers before source authorization:

- Decide the `sector_code` compatibility policy for OpenStock rows.
- Decide whether `latest_price` absence is acceptable for migrated rows or should keep the slice on legacy until OpenStock exposes it.
- Confirm that `3日` remains legacy compatibility and is not silently removed.

## Test Scope For B4a

Focused TDD candidates:

- Red/green test: `fetch_and_save_sector_fund_flow("行业", "今日")` consumes OpenStock `SECTOR_FUND_FLOW` and does not call EastMoney.
- Contract test for params:
  - `{"sector_type": "industry", "indicator": "今日"}` or equivalent accepted alias.
- Mapping tests:
  - Chinese `行业/概念/地域` route values map to `industry/concept/region`.
  - OpenStock `change_pct` maps to MyStocks `change_percent`.
  - OpenStock `*_ratio` fields map to MyStocks `*_rate` fields.
  - OpenStock `leading_name` maps to `leading_stock`.
- Guard test:
  - `timeframe="3日"` still calls legacy path and does not call OpenStock.
- Regression test:
  - Existing ETF, block trade, dragon tiger, and FUND_FLOW OpenStock refresh tests stay green.

Suggested focused gate after implementation:

```bash
python -m py_compile web/backend/app/services/market_data_service_v2.py web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py
python -m ruff check web/backend/app/services/market_data_service_v2.py web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py
python -m pytest web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py web/backend/tests/services/test_market_data_service_v2_runtime_fallback.py tests/backend/test_openstock_client.py -q --no-cov
```

## Decision

`SECTOR_FUND_FLOW` is ready for a limited MyStocks consumer migration, but not ready for a blind full replacement of the legacy sector fund-flow refresh path.

Prepared next node recommendation:

- `B4.013-M3a-B4a SECTOR_FUND_FLOW supported timeframe refresh migration`.
- Source edits should be authorized only after the `sector_code` compatibility policy is explicitly approved.
- Keep `3日` as legacy compatibility until OpenStock defines and tests a matching provider contract.

## No-Source Gate Notes

- This package made no source, runtime, route, schema, model, test, or OpenStock repository edits.
- OPENDOG verification evidence is fresh and contains no failing recorded runs.
- OPENDOG guidance still flags stale snapshot evidence and a very dirty worktree, so this package must remain tightly staged to governance/worklog files only.

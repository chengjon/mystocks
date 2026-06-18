# B4.013-M3a-B4a SECTOR_FUND_FLOW implementation authorization draft

Date: 2026-06-18
Mode: authorization draft, no source edits
Parent decision node: `b4-013-m3a-b4-sector-fund-flow-readiness-audit`
Repository: `mystocks_spec`

## Purpose

This draft converts the B4 readiness audit into a precise source authorization request for a limited MyStocks consumer migration of `SECTOR_FUND_FLOW`.

The architectural boundary remains unchanged:

- OpenStock owns provider and data-source runtime.
- MyStocks only consumes OpenStock through backend consumer integration.
- MyStocks must not add provider fallback, provider SDK calls, provider adapters, or direct frontend-to-OpenStock calls.

## Requested Source Scope

Allowed paths only:

- `web/backend/app/services/market_data_service_v2.py`
- `web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py`

Forbidden paths:

- `web/backend/app/api/market_v2.py`
- `web/backend/app/models/market_data.py`
- `/opt/claude/openstock/**`
- `web/frontend/**`
- `ST-HOLD/**`
- `marketKlineData`
- Any external dirty or untracked file.

## Requested Behavior

If approved, B4a may implement only this limited slice:

- Route `fetch_and_save_sector_fund_flow` through OpenStock only for:
  - `sector_type` values `行业`, `概念`, `地域`.
  - `timeframe` values `今日`, `5日`, `10日`.
- Map MyStocks compatibility values to OpenStock params:
  - `行业 -> industry`
  - `概念 -> concept`
  - `地域 -> region`
  - pass `indicator` as the original supported timeframe.
- Preserve MyStocks persisted compatibility values:
  - stored `sector_type` remains the original Chinese value.
  - stored `timeframe` remains the original Chinese value.
  - stored `trade_date` remains local `date.today()`, matching current legacy save behavior.
- Preserve `timeframe="3日"` legacy behavior:
  - do not call OpenStock.
  - continue to call the existing legacy path.
- Map OpenStock fields into `SectorFundFlow`:
  - `sector_name -> sector_name`
  - `change_pct -> change_percent`
  - `main_net_inflow -> main_net_inflow`
  - `main_net_inflow_ratio -> main_net_inflow_rate`
  - `super_large_net_inflow_ratio -> super_large_net_inflow_rate`
  - `large_net_inflow_ratio -> large_net_inflow_rate`
  - `medium_net_inflow_ratio -> medium_net_inflow_rate`
  - `small_net_inflow_ratio -> small_net_inflow_rate`
  - `leading_name -> leading_stock`

## Sector Code Compatibility Policy

OpenStock current `SECTOR_FUND_FLOW` intentionally does not fabricate `sector_code`.

Recommended authorization decision:

- Permit a MyStocks-only persistence compatibility shim:
  - if OpenStock record contains `sector_code`, use it.
  - otherwise use deterministic `sector_name` as the storage key.
- Treat this as a MyStocks read-model compatibility decision, not an OpenStock provider contract.
- Do not update OpenStock docs or provider output to claim `sector_code` exists.
- Do not change the database model in B4a.

Reasoning:

- MyStocks current `SectorFundFlow.sector_code` is non-null and participates in de-duplication.
- OpenStock current provider path is ranking data and does not provide a stable sector code.
- Using `sector_name` as a deterministic fallback preserves existing MyStocks persistence constraints without moving provider responsibilities back into MyStocks.

## Non-Goals

- No route/API path changes.
- No model/schema/database migration changes.
- No query/read-model behavior changes.
- No OpenStock repository edits.
- No provider SDK calls in MyStocks.
- No new provider fallback path.
- No behavior change for unsupported `3日`.
- No frontend or E2E test edits.

## Required Tests

Focused TDD expectations:

- Supported slice:
  - `fetch_and_save_sector_fund_flow("行业", "今日")` consumes OpenStock `SECTOR_FUND_FLOW` and does not call EastMoney.
  - OpenStock params use `sector_type="industry"` and `indicator="今日"`.
  - persisted row keeps `sector_type="行业"` and `timeframe="今日"`.
  - persisted row uses deterministic `sector_code` fallback when OpenStock omits `sector_code`.
- Mapping:
  - `change_pct` maps to `change_percent`.
  - OpenStock ratio fields map to MyStocks rate fields.
  - `leading_name` maps to `leading_stock`.
- Unsupported slice:
  - `fetch_and_save_sector_fund_flow("行业", "3日")` does not call OpenStock.
  - legacy EastMoney path remains active.
- Regression:
  - Existing ETF, block trade, dragon tiger, and FUND_FLOW refresh tests remain green.

## Commit Gates

Run before implementation commit:

```bash
python -m py_compile web/backend/app/services/market_data_service_v2.py web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py
python -m ruff check web/backend/app/services/market_data_service_v2.py web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py
python -m pytest web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py web/backend/tests/services/test_market_data_service_v2_runtime_fallback.py tests/backend/test_openstock_client.py -q --no-cov
node .gitnexus/run.cjs verify-staged --repo mystocks
node .gitnexus/run.cjs detect-changes --scope staged --repo mystocks
```

## Authorization Status

Current status:

- Node has authorization draft prepared.
- Source edits are not yet authorized.
- Required next step: explicit user approval for B4a source implementation and the sector-code compatibility policy above.

# B4.013-M3a-B3a FUND_FLOW symbol today OpenStock migration closeout

Date: 2026-06-18
Node: `b4-013-m3a-b3a-fund-flow-symbol-today-openstock`
Mode: source-authorized implementation
Repository: `mystocks_spec`

## Scope

This package implements only the safe FUND_FLOW migration slice identified by the B3 boundary audit.

Allowed files:

- `web/backend/app/services/market_data_service_v2.py`
- `web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py`
- `docs/reports/worklogs/claude-auto/b4-013-m3a-b3a-fund-flow-symbol-today-openstock-closeout-2026-06-18.md`

Explicit non-goals:

- No route or API path changes.
- No OpenStock repository changes.
- No provider/data-source logic added to MyStocks.
- No frontend, store, OpenSpec, ST-HOLD, marketKlineData, BaseLayout, or external dirty file changes.
- No implementation of `symbol=None` all-market refresh.
- No implementation of `3日` / `5日` / `10日` aggregate semantics.

## Implemented Behavior

`MarketDataServiceV2.fetch_and_save_fund_flow` now routes only this supported slice through the MyStocks OpenStock backend consumer:

- `symbol` is provided.
- `timeframe` is `"今日"` or `"1"`.
- OpenStock category: `FUND_FLOW`.
- OpenStock params: `{"symbol": symbol}`.

Legacy behavior remains in place for unsupported slices:

- `symbol=None` all-market refresh still follows the existing local provider path.
- Multi-day timeframe refreshes still follow the existing local provider path pending B3b contract decision.

## Field Mapping

OpenStock normalized FUND_FLOW records are persisted into the existing `FundFlow` model as follows:

| OpenStock field | MyStocks field |
| --- | --- |
| `symbol` | `FundFlow.symbol` |
| `trade_date` | `FundFlow.trade_date` |
| fixed daily slice | `FundFlow.timeframe = "1"` |
| `main_net_inflow` | `FundFlow.main_net_inflow` |
| `main_net_inflow_ratio` | `FundFlow.main_net_inflow_rate` |
| `super_large_net_inflow` | `FundFlow.super_large_net_inflow` |
| `large_net_inflow` | `FundFlow.large_net_inflow` |
| `medium_net_inflow` | `FundFlow.medium_net_inflow` |
| `small_net_inflow` | `FundFlow.small_net_inflow` |

Duplicate detection now uses the persisted OpenStock `trade_date` for this OpenStock slice:

- `FundFlow.symbol == fund_flow.symbol`
- `FundFlow.trade_date == fund_flow.trade_date`
- `FundFlow.timeframe == "1"`

## TDD Evidence

Red test:

```bash
python -m pytest web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py::test_fetch_and_save_fund_flow_symbol_today_consumes_openstock_without_local_provider -q --no-cov
```

Expected failure observed before implementation:

- Existing code called `EastMoney fund flow provider should not be called`.
- Result was `{"success": False, "message": "EastMoney fund flow provider should not be called"}`.

Green test:

```bash
python -m pytest web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py::test_fetch_and_save_fund_flow_symbol_today_consumes_openstock_without_local_provider -q --no-cov
```

Observed result:

- `1 passed`

## Verification

Syntax:

```bash
python -m py_compile web/backend/app/services/market_data_service_v2.py web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py
```

Result:

- Passed.

Lint:

```bash
python -m ruff check web/backend/app/services/market_data_service_v2.py web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py
```

Result:

- `All checks passed!`

Focused OpenStock refresh tests:

```bash
python -m pytest web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py -q --no-cov
```

Result:

- `4 passed`

Focused OpenStock consumer regression:

```bash
python -m pytest web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py web/backend/tests/services/test_market_data_service_v2_runtime_fallback.py tests/backend/test_openstock_client.py -q --no-cov
```

Result:

- `16 passed`

Staged diff check:

```bash
git diff --cached --check
```

Result:

- Passed.

FUNCTION_TREE validation:

```bash
node /root/.codex/skills/myskills/skills/function-tree/scripts/ft-governance.cjs validate --root /opt/claude/mystocks_spec
```

Result:

- `governance validation passed`

GitNexus staged gates:

```bash
node .gitnexus/run.cjs verify-staged --repo mystocks
node .gitnexus/run.cjs detect-changes --scope staged --repo mystocks
```

Result:

- Changes: 8 files, 12 symbols.
- Affected processes: 1.
- Risk level: medium.
- Affected execution flow: `Refresh_all_market_data -> _run_async`.
- The medium risk is expected because `fetch_and_save_fund_flow` is a direct refresh boundary used by active market refresh routes.

OPENDOG verification:

```bash
env OPENDOG_HOME=/root/.opendog /opt/claude/opendog/target/release/opendog verification --id mystocks --json
```

Result:

- status: `available`
- freshness: `fresh`
- failing runs: `0`
- cleanup blockers: `0`
- missing kinds: `[]`

Exact staged files:

- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/cards/b4-013-m3a-b3a-fund-flow-symbol-today-openstock.yaml`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `.governance/programs/artdeco-web-design-governance/tree.md`
- `docs/reports/worklogs/claude-auto/b4-013-m3a-b3a-fund-flow-symbol-today-openstock-closeout-2026-06-18.md`
- `web/backend/app/services/market_data_service_v2.py`
- `web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py`

## Risk Notes

Impact remains constrained to the service acquisition/persistence boundary.

Known direct callers from the B3 audit:

- `refresh_fund_flow`
- `refresh_all_market_data`

The `refresh_all_market_data` caller still passes `symbol=None`; this package intentionally does not migrate that path to OpenStock because current OpenStock `FUND_FLOW` requires `symbol`.

## Closeout Decision

B4.013-M3a-B3a is implementation-complete for the symbol-scoped daily FUND_FLOW refresh slice.

Next work should be `B4.013-M3a-B3b FUND_FLOW all-market and multi-day contract decision`, starting no-source. That package must decide whether to extend OpenStock contracts or retain/retire the MyStocks legacy all-market and multi-day refresh behavior.

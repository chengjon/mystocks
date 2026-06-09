# B4.009-M2d-C asNumber numeric-string no-source decision audit

Date: 2026-06-09
Scope: no-source audit only
Current HEAD: `ee2dfc637ec5d7c652ddfb120840e46b0ad448cc`

## Scope

Audited only the numeric conversion helpers named `asNumber` in:

- `web/frontend/src/utils/strategy-adapters.ts`
- `web/frontend/src/utils/trade-adapters.ts`

No source code, tests, routes, stores, views, API paths, ST-HOLD/B4.006 files, `atrading.ts`, or `marketKlineData` were modified.

## Current workspace boundary

Scoped status showed the M2d-C target files clean before the audit.

Known external dirty items remain outside this audit:

- `web/frontend/src/layouts/archive/BaseLayout.vue`
- `web/frontend/src/views/artdeco-pages/market-tabs/__node_tests__/marketKlineData.test.ts`
- `docs/reports/worklogs/claude-auto/b4-009-m2d-sa4-strategy-trade-adapter-boundary-no-source-audit-2026-06-09.md`

GitNexus CLI status before audit:

- indexed commit: `ee2dfc637ec5d7c652ddfb120840e46b0ad448cc`
- current commit: `ee2dfc637ec5d7c652ddfb120840e46b0ad448cc`
- upToDate: `true`
- stagedFiles: `0`

## Current implementation

Both helpers currently accept only finite JavaScript numbers:

```ts
const asNumber = (value: unknown, fallback = 0): number =>
  typeof value === 'number' && Number.isFinite(value) ? value : fallback
```

Consequence: numeric strings such as `"12.3"`, `"0"`, and `"-0.08"` fall back to `0`.

Strict candidate behavior considered for a future source-authorized patch:

- accept finite numbers unchanged
- accept non-empty finite numeric strings after `trim()`
- reject empty strings
- reject formatted strings such as `"12%"`, `"1,234"`, `"Infinity"`
- keep fallback behavior for nullish, object, boolean, NaN, and Infinity values

## Call-site inventory

### Strategy adapter

`strategy-adapters.ts` has 32 `asNumber` call sites across:

- strategy list VM metrics: `totalReturn`, `sharpeRatio`, `maxDrawdown`, `winRate`
- backtest result VM fields: capital, returns, drawdown, trade count, equity curve, PnL metrics
- adapted strategy performance: snake_case/camelCase performance metrics

Direct GitNexus callers for `Function:web/frontend/src/utils/strategy-adapters.ts:asNumber`:

- `StrategyAdapter.toStrategyListVM`
- `StrategyAdapter.toBacktestResultVM`
- `StrategyAdapter.adaptStrategy`

Second-depth impacted surfaces include:

- `web/frontend/src/api/strategy.ts`
- `web/frontend/src/composables/useStrategy.ts`
- `web/frontend/src/composables/useStrategy.shared.ts`
- `web/frontend/tests/unit/strategy-adapter-utils.spec.ts`

### Trade adapter

`trade-adapters.ts` has 26 `asNumber` call sites across:

- account overview: assets, PnL, asset allocation
- order VM: quantity, price, amount, fills
- position VM: quantity, price, cost basis, PnL, margin
- trade VM/history: quantity, price, amount, commission

Direct GitNexus callers for `Function:web/frontend/src/utils/trade-adapters.ts:asNumber`:

- `TradeAdapter.toAccountOverviewVM`
- `TradeAdapter.toOrderVM`
- `TradeAdapter.toPositionVM`
- `TradeAdapter.toTradeVM`

Second-depth impacted surfaces include:

- `web/frontend/src/api/trade.ts`
- `web/frontend/tests/unit/trade-adapter-utils.spec.ts`

## GitNexus impact

`strategy-adapters.ts` `asNumber`:

- risk: `CRITICAL`
- impactedCount: 12
- direct: 3
- modules_affected: 5
- affected_processes: 0

`trade-adapters.ts` `asNumber`:

- risk: `HIGH`
- impactedCount: 10
- direct: 4
- modules_affected: 4
- affected_processes: 0

Note: GitNexus MCP impact responses emitted a stale hint, while GitNexus CLI status reported the index as up to date at the same HEAD. Any future source patch must still run both CLI staged verification and MCP `detect_changes` before commit.

## Contract and test observations

Generated frontend type lookup did not find exported `StrategyListResponse`, `OrderResponse`, or `TradeHistoryResponse` in `generated-types.ts`, despite adapter imports compiling today. The active API service layer uses local normalization and adapter calls in:

- `web/frontend/src/api/strategy.ts`
- `web/frontend/src/api/trade.ts`

Backend schema evidence shows strategy/backtest numeric fields as numeric Python/Pydantic fields, for example:

- `initial_capital: float`
- `total_return: float`
- `max_drawdown: float`
- `sharpe_ratio: float`
- `win_rate: float`
- trade/price/amount fields represented as numeric/Decimal values

Existing bound tests cover:

- strategy status mapping
- strategy snake_case payload adaptation with numeric values
- empty strategy payload defaults
- empty trade account payload defaults
- invalid trade collection boundaries
- ts-nocheck absence in both adapter files

Existing bound tests do not yet cover numeric-string acceptance or rejection behavior.

## Risk analysis

Changing `asNumber` is behavior-changing, not metadata cleanup.

Expected positive effect:

- API numeric strings stop collapsing to zero in strategy/trade view models.
- Strategy performance, backtest metrics, order quantities, prices, PnL, and commissions become more tolerant of serialization drift.

Main risks:

- High/critical helper blast radius across API/composable/test surfaces.
- Loose parsing could accidentally accept formatted display strings.
- `Number('') === 0` would be unsafe if not guarded.
- Percent strings and localized strings need separate semantics and must not be silently interpreted in this patch.

Risk control requirement:

- Use strict finite numeric-string parsing only.
- Do not parse percent, currency, thousands separators, booleans, arrays, or objects.
- Add positive and negative contract tests before implementation.
- Keep changes local to the two adapter files and their directly bound tests.

## Decision

Do not authorize an immediate broad numeric parser change without explicit source authorization.

Recommended next step: request source authorization for a split implementation, because strategy is CRITICAL and trade is HIGH.

### Recommended source plan

Option A, safest:

1. `B4.009-M2d-C1 trade asNumber numeric-string standardization`
   - files: `trade-adapters.ts`, `trade-adapter-utils.spec.ts`
   - risk: HIGH
   - add positive/negative numeric-string tests for account/order/position/trade history

2. `B4.009-M2d-C2 strategy asNumber numeric-string standardization`
   - files: `strategy-adapters.ts`, `strategy-adapter-utils.spec.ts`
   - risk: CRITICAL
   - add positive/negative numeric-string tests for list/backtest/adaptStrategy metrics

Option B, acceptable only with explicit approval:

- one combined M2d-C source patch touching both helpers and both bound tests
- must explicitly acknowledge `strategy asNumber` CRITICAL and `trade asNumber` HIGH
- must run full front-end gates before commit

## Proposed authorization boundaries

Allowed files for a future source patch:

- `web/frontend/src/utils/strategy-adapters.ts`
- `web/frontend/src/utils/trade-adapters.ts`
- `web/frontend/tests/unit/strategy-adapter-utils.spec.ts`
- `web/frontend/tests/unit/trade-adapter-utils.spec.ts`
- existing adapter type-cleanup tests only if they require direct adjustment

Forbidden:

- `web/frontend/src/utils/atrading.ts`
- ST-HOLD / B4.006 files
- `marketKlineData`
- routes, views, stores, API paths
- strategy/trade execution logic
- generated types or OpenAPI contract files
- external dirty files

Required gates for a future source patch:

- GitNexus impact before edit, with HIGH/CRITICAL acknowledged
- focused adapter unit tests
- adapter type-cleanup tests
- `npm run type-check`
- `npm run test:unit:stable`
- PM2 business smoke E2E 55/55
- OPENDOG verification fresh, no new blockers
- exact staging only
- GitNexus `verify-staged`
- GitNexus MCP `detect_changes`
- post-commit GitNexus analyze/status

## Audit conclusion

`asNumber` numeric-string convergence is justified as adapter boundary hardening, but it is not a low-risk cleanup. It should proceed only after explicit source authorization, preferably split into trade and strategy sub-batches. The implementation should be strict, contract-tested, and explicitly avoid formatted string parsing.

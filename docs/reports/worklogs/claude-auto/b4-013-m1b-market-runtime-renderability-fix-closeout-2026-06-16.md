# B4.013-M1-B Market Runtime Renderability Fix Closeout

Date: 2026-06-16
Branch: `wip/root-dirty-20260403`
Implementation node: `b4-013-m1b-market-runtime-renderability-audit`
Implementation package: `B4.013-M1-B-FIX market technical K-line period contract alignment`

## Scope

Authorized source/test files changed:

- `web/frontend/src/views/market/marketKlineData.ts`
- `web/frontend/src/views/market/__node_tests__/marketKlineData.test.ts`

Governance/closeout files changed:

- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `docs/reports/worklogs/claude-auto/b4-013-m1b-market-runtime-renderability-fix-closeout-2026-06-16.md`

Explicitly not changed:

- Backend route validation
- `Technical.vue` layout or chart behavior
- `/market/lhb` prop-warning cleanup
- `pageConfig.ts` endpoint drift
- B4.012 residual dirty work
- ST-HOLD, OpenSpec, marketKlineData deletion/retirement, or external dirty files

## Implementation

`buildMarketKlineParams` now normalizes frontend selector periods to the backend K-line contract:

- `1d -> daily`
- `1w -> weekly`
- `1m -> monthly`

Backend-native period values remain pass-through, including `daily`, `weekly`, and `monthly`.

This keeps current route callers stable while making `/market/technical` emit a request accepted by `GET /api/v1/market/kline`.

## TDD Evidence

Red test run before implementation:

- Command: `cd web/frontend && npx tsx src/views/market/__node_tests__/marketKlineData.test.ts`
- Result: expected failure, 3 failed assertions
- Failure reason: helper still returned `period: "1d"` and `period: "1w"` while tests expected backend-compatible `daily` and `weekly`

Green focused test after implementation:

- Command: `cd web/frontend && npx tsx src/views/market/__node_tests__/marketKlineData.test.ts`
- Result: 6 tests passed, 0 failed

## Verification

Type check:

- Command: `cd web/frontend && npm run type-check`
- Result: exit 0, `vue-tsc --noEmit` passed

PM2-backed browser smoke:

- Services:
  - `mystocks-backend`: PM2 `online`, port `8020`
  - `mystocks-frontend`: PM2 `online`
- Direct backend probe:
  - `/api/v1/market/kline?stock_code=000001&period=daily&limit=100&refresh_seq=201` -> 200
  - `/api/v1/market/kline?stock_code=000001&period=1d&limit=100&refresh_seq=202` -> 422, confirming backend contract remains unchanged
- Browser route:
  - `/market/technical`
  - title: `K线分析 - MyStocks`
  - K-line API observed: `/api/v1/market/kline?stock_code=000001&period=daily&limit=100&refresh_seq=1` -> 200
  - page rendered `K线分析工作台`
  - `K线数据加载失败` / `K线异常` absent
  - route points count populated

Known non-blocking warnings still observed:

- `ArtDecoIcon: Icon "Monitor" not found, fallback to "Alert"`
- `ArtDecoIcon: Icon "BarChart2" not found, fallback to "Alert"`

These warnings predate this fix and are outside the authorized package.

## Compatibility

The fix preserves caller compatibility:

- Existing callers still pass selector values such as `1d`.
- The helper translates selector values at the API-boundary param builder.
- Backend validation remains unchanged.
- Unknown period values are still passed through, preserving prior behavior for non-standard callers.

## Decision

`/market/technical` no longer reproduces the B4.013-M1-B K-line data-flow blocker under PM2-backed runtime verification.

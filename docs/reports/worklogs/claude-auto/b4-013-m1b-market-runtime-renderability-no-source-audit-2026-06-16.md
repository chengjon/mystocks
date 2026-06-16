# B4.013-M1-B Market Runtime Renderability No-Source Audit

Date: 2026-06-16
Branch: `wip/root-dirty-20260403`
Head at audit start: `5b86c6c82 B4.013-GOV: adopt runtime mainline alignment`
Governance node: `b4-013-m1b-market-runtime-renderability-audit`
Mode: no-source audit
Source edits authorized: false

## Scope

This audit covers the B4.013 runtime-first mainline slice for the market domain:

- Frontend route truth for `/market`, `/market/realtime`, `/market/technical`, `/market/lhb`
- Frontend view/component entrypoints used by those routes
- Market data helper contract around K-line params
- API client target for K-line requests
- Backend runtime contract for `/api/v1/market/kline`
- PM2-backed browser renderability for market routes

Explicitly excluded:

- No source/runtime/test/config edits
- No B4.012 residual dirty cleanup
- No OpenSpec, ST-HOLD, marketKlineData deletion/retirement, or external dirty-file handling
- No pageConfig cleanup unless later source-authorized

## Static Findings

### Route Truth

`web/frontend/src/router/index.ts` defines:

- `/market` redirects to `/market/realtime`
- `/market/realtime` -> `@/views/market/Realtime.vue`, route meta API `/api/v1/market/quotes`
- `/market/technical` -> `@/views/market/Technical.vue`, route meta API `/api/v1/market/kline`
- `/market/lhb` -> `@/views/market/LHB.vue`, route meta API `/api/v2/market/lhb`

### K-Line Frontend Request Contract

`web/frontend/src/views/market/Technical.vue` calls:

- `dataApi.getKline(buildMarketKlineParams(currentSymbol.value, '1d', currentRequest))`

`web/frontend/src/views/market/marketKlineData.ts` currently builds params with:

- `stock_code`
- `period`, defaulting to `"1d"`
- `limit: 100`
- optional `refresh_seq`

The existing node test `web/frontend/src/views/market/__node_tests__/marketKlineData.test.ts` also asserts `"1d"` and `"1w"` selector-style period values.

### K-Line Backend Runtime Contract

`web/backend/app/api/market/market_data_request.py` defines:

- `GET /api/v1/market/kline`
- `period` default: `"daily"`
- accepted pattern: `daily|weekly|monthly`
- rejected values include frontend selector-style `"1d"`

The backend route passes the validated `period` through to `get_stock_search_service().get_a_stock_kline(...)`.

### Config Drift

`web/frontend/src/config/pageConfig.ts` is not the live route runtime source for this finding, but it still has market endpoint drift:

- `market-realtime`: `/api/market/realtime` while route/runtime uses `/api/v1/market/quotes`
- `market-technical`: `/api/technical/indicators` while route/runtime uses `/api/v1/market/kline`
- `market-lhb`: `/api/v1/market/lhb` while route/runtime uses `/api/v2/market/lhb`

Disposition: P2 config truth cleanup candidate, not part of this P0/P1 runtime fix.

## Runtime Evidence

Environment:

- `mystocks-backend`: PM2 `online`, port `8020`
- `mystocks-frontend`: PM2 `online`, frontend served at `http://127.0.0.1:3020`

Direct backend probes:

| Probe | Status | Result |
| --- | ---: | --- |
| `/api/v1/market/kline?stock_code=000001&period=1d&limit=100&refresh_seq=91` | 422 | `{"code":1001,"message":"输入参数验证失败"}` |
| `/api/v1/market/kline?stock_code=000001&period=daily&limit=100&refresh_seq=92` | 200 | fallback K-line payload with `period:"daily"` |
| `/api/v1/market/quotes?symbols=000001,600519` | 200 | realtime quote payload |
| `/api/v2/market/lhb?limit=5` | 200 | LHB payload |

Browser route probes after login with seeded local account:

| Route | Observed URL | Title | Text length | Runtime status |
| --- | --- | --- | ---: | --- |
| `/market` | `/market/realtime` | `实时行情 - MyStocks` | 1516 | renders realtime page, quotes API 200 |
| `/market/realtime` | `/market/realtime` | `实时行情 - MyStocks` | 1515 | renders realtime page, quotes API 200 |
| `/market/technical` | `/market/technical` | `K线分析 - MyStocks` | 1255 | renders page shell but shows K-line error; K-line API 422 |
| `/market/lhb` | `/market/lhb` | `龙虎榜 - MyStocks` | 4441 | renders LHB page, LHB API 200 |

Console warnings observed:

- `ArtDecoIcon: Icon "Monitor" not found, fallback to "Alert"` on market pages
- `/market/lhb` emits missing required prop warnings for `lhbData`, `lhbDate`, and `activeFilter`

Disposition:

- Icon fallback and LHB prop warnings are visible technical debt but do not currently block market route renderability.
- `/market/technical` data-flow failure is the only market-domain runtime blocker found in this audit.

## Decision

M0's original `/market` fallback concern is not reproducible in the current runtime: `/market` redirects into `/market/realtime` and renders real quote-backed content.

The current B4.013 market-domain blocker is narrower:

- `/market/technical` is reachable and visible.
- Its data flow fails because frontend selector-period `"1d"` is sent directly to a backend endpoint that only accepts `daily|weekly|monthly`.
- The same backend endpoint succeeds with `period=daily`.

This should be handled as a small B4.013-M1-B implementation package, not as broad market cleanup.

## Recommended Minimal Source Package

Recommended authorization name:

`B4.013-M1-B-FIX market technical K-line period contract alignment`

Recommended allowed paths:

- `web/frontend/src/views/market/marketKlineData.ts`
- `web/frontend/src/views/market/__node_tests__/marketKlineData.test.ts`
- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `.governance/programs/artdeco-web-design-governance/tree.md`
- `.governance/programs/artdeco-web-design-governance/cards/b4-013-m1b-market-runtime-renderability-audit.yaml`
- `docs/reports/worklogs/claude-auto/b4-013-m1b-market-runtime-renderability-fix-closeout-2026-06-16.md`

Recommended implementation:

- Keep UI/helper callers stable.
- Normalize selector-style frontend periods inside `buildMarketKlineParams`:
  - `1d -> daily`
  - `1w -> weekly`
  - `1m -> monthly`
- Preserve explicit backend-native periods (`daily`, `weekly`, `monthly`) unchanged.
- Update the focused node tests to assert backend-compatible emitted params.

Recommended focused gates:

- `node .gitnexus/run.cjs verify-staged --repo mystocks --cwd /opt/claude/mystocks_spec --json`
- `node .gitnexus/run.cjs detect-changes --scope staged --repo mystocks --cwd /opt/claude/mystocks_spec`
- `cd web/frontend && npm run type-check`
- Focused market K-line node/unit test for `marketKlineData`
- PM2-backed browser smoke for `/market/technical` verifying K-line API 200 and no K-line error banner
- OPENDOG verification with no new blockers

## Non-Goals For Next Package

- Do not modify backend route validation unless frontend-only normalization proves insufficient.
- Do not change `Technical.vue` layout or chart behavior.
- Do not touch `/market/lhb` prop warnings in the K-line period package.
- Do not clean pageConfig endpoint drift in the K-line period package.
- Do not touch B4.012 residual dirty work, ST-HOLD, OpenSpec, source/runtime domains outside the allowed paths, or any external dirty files.

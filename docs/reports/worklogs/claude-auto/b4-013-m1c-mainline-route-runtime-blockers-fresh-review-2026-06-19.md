# B4.013-M1C Mainline Route Runtime Blockers Fresh Review

Date: 2026-06-19
Node: `b4-013-m1c-mainline-route-runtime-blockers-audit`
Mode: no-source fresh review
Source edits authorized: false

## Purpose

This review rechecks whether the old M1C route-runtime blocker node still needs a source authorization package after the B4.013 parent runtime-mainline cycle closed.

The review stays no-source:

- no router edits
- no frontend source edits
- no backend source edits
- no test edits
- no OpenStock edits
- no ST-HOLD / marketKlineData / external dirty file changes

## Prior Evidence

Existing M1C evidence from 2026-06-16 recorded:

- primary navigation default routes rendered after verification-ladder reruns;
- no confirmed P0 blank route remained;
- dashboard aggregate data/provenance was the next mainline candidate.

That dashboard follow-up was later handled by `b4-013-m1d-dashboard-aggregate-runtime-data-provenance-audit`, which is now closed.

## Fresh State

FUNCTION_TREE state before this review:

- `b4-013-runtime-mainline-bring-up`: closed.
- `b4-013-m1c-mainline-route-runtime-blockers-audit`: decision-prepared, next gate `prepare authorization`.
- `b4-013-m1d-dashboard-aggregate-runtime-data-provenance-audit`: closed.
- `b4-013-m1e-backend-api-residual-slow-endpoint-attribution-audit`: blocked, preserved as a separate future-cycle input.

Route inventory snapshot:

- `web/frontend/src/router/index.ts` exists.
- Route path count: 55.
- Redirect count: 8.
- Route name count: 42.
- Primary redirects remain:
  - `/market/realtime`
  - `/data/industry`
  - `/watchlist/manage`
  - `/strategy/repo`
  - `/ai/sentiment`
  - `/trade/terminal`
  - `/risk/overview`
  - `/system/config`

PM2 runtime state:

- `mystocks-backend`: online on port `8020`.
- `mystocks-frontend`: online on port `3020`.

## Business Smoke Evidence

Initial command:

```text
npm run test:e2e:business-smoke
```

Result:

- Did not enter test execution because Playwright tried to start its own web server on `3020`.
- Error: `http://localhost:3020 is already used`.
- This is an execution-mode mismatch under PM2, not a route/runtime failure.

PM2-compatible rerun:

```text
PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://localhost:3020 npm run test:e2e:business-smoke
```

Result:

- Chromium business smoke executed against the PM2-managed frontend.
- `55 passed (2.9m)`.
- Failure line count: `0`.
- Residual Playwright processes after completion: `0`.

The executed suite covered:

- auth login
- critical menu navigation
- market data
- risk overview
- risk PnL
- trade terminal
- strategy management chain
- strategy backtest
- K-line chart

## Decision

No fresh P0 route-runtime blocker is confirmed.

The old M1C node should not proceed to source authorization. Its original pending route/runtime concern has been absorbed by later B4.013 work:

- dashboard aggregate runtime/provenance was handled under M1D;
- OpenStock-backed market data runtime paths were handled under later M3a slices;
- PM2 business smoke now verifies the main route/business chain as reachable.

## Next Queue

Do not use M1C as a source-edit package.

Next P0 work should start as a fresh no-source cycle against a still-live runtime concern, likely:

1. residual backend API slow endpoint attribution if it can be unblocked without violating the OpenStock provider boundary;
2. any newly observed visible PM2 route/API/data-flow regression;
3. OpenStock provider-contract gaps only after OpenStock exposes tested provider-backed contracts.

MyStocks remains consumer-only for OpenStock data. Unsupported provider gaps must not be synthesized inside MyStocks.

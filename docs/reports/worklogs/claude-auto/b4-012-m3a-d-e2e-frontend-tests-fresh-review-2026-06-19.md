# B4.012-M3a-D E2E / Frontend Tests Fresh Review

Date: 2026-06-19
Repository: `/opt/claude/mystocks_spec`
Baseline HEAD: `aae6b6bed47abdbb63ad4277f5487cf802f87437`
Mode: no-source family reactivation review

## Scope

This review refreshes the B4.012-M3a-D E2E/frontend tests parent after B4.013 closeout and B4.012-M3a parent reactivation.

The immediate target is only:

- `b4-012-m3a-d-e2e-frontend-tests-split`

This package does not authorize test edits, source edits, runtime edits, OpenSpec edits, OpenStock edits, deletion, untracked preservation, E2E assertion changes, or broad frontend test acceptance.

## Current Gate Truth

- `b4-012-m3a-tests-residual-domain-audit` is `decision-prepared`.
- `b4-012-m3a-d-e2e-frontend-tests-split` is still `blocked` only because it was paused by the B4.013 runtime-first reset.
- `b4-012-m3a-d1-e2e-browser-smoke-authorization` remains `blocked` and downstream. It is not restored by this package.
- PM2 runtime context is available for future browser-smoke work:
  - `mystocks-backend`: online, service URL `http://localhost:8020`
  - `mystocks-frontend`: online, service URL `http://localhost:3020`

PM2 availability is recorded only as runtime context. This review does not claim E2E acceptance or browser-smoke pass status.

## Fresh Dirty Surface

Current E2E/frontend-test dirty surface remains mixed and must not be accepted as one batch:

| Group | Count | Notes |
| --- | ---: | --- |
| Total matching status entries | 28 | Includes tracked E2E files, frontend unit/view tests, and untracked frontend test directories. |
| Tracked | 10 | Tracked dirty tests require explicit family authorization before staging. |
| Untracked | 18 | Untracked frontend test paths remain provenance-only until separately authorized. |
| `tests/e2e/**` | 6 | Browser/business smoke risk surface; high signal and must not mix with frontend unit/view test provenance. |
| `web/frontend/tests/**` | 3 | Includes unit/config test dirtiness; not automatically accepted by D parent reactivation. |
| `web/frontend/src/views/**` tests | 19 | Mostly untracked source-tree test candidates; provenance and ownership must be decided before preservation. |
| `web/frontend/src/components/**` tests | 0 | No current component-test status entries in this filtered surface. |
| Playwright-style `.spec.ts` entries | 13 | Includes tracked and untracked frontend/browser specs; selectors/assertions require focused authorization. |

Tracked E2E/frontend-test paths observed:

- `tests/e2e/specs/auth-optimized.spec.ts`
- `tests/e2e/specs/dashboard.spec.ts`
- `tests/e2e/test_fund_flow.py`
- `tests/e2e/test_login.py`
- `tests/e2e/test_risk.py`
- `tests/e2e/test_web_e2e.py`
- `web/frontend/src/views/artdeco-pages/market-data-tabs/__node_tests__/fundFlowPageData.test.ts`
- `web/frontend/src/views/artdeco-pages/market-tabs/__node_tests__/marketKlineData.test.ts`
- `web/frontend/src/views/stocks/__node_tests__/stockScreenerData.test.ts`
- `web/frontend/tests/unit/config/trading-style-normalization.spec.ts`

Representative untracked frontend test candidates include:

- `web/frontend/src/views/announcement/__tests__/AnnouncementMonitor.spec.ts`
- `web/frontend/src/views/artdeco-pages/market-data-tabs/__tests__/ArtDecoMarketAnalysis.spec.ts`
- `web/frontend/src/views/artdeco-pages/market-data-tabs/__tests__/ArtDecoMarketOverview.spec.ts`
- `web/frontend/src/views/artdeco-pages/market-data-tabs/__tests__/ArtDecoRealtimeMonitor.spec.ts`
- `web/frontend/src/views/data/__tests__/FundFlow.spec.ts`
- `web/frontend/src/views/market/__tests__/LHB.spec.ts`
- `web/frontend/src/views/watchlist/__tests__/Screener.spec.ts`
- `web/frontend/src/views/watchlist/__tests__/Signals.spec.ts`
- `web/frontend/tests/unit/views/data-concept-refresh-fallback.spec.ts`
- `web/frontend/tests/unit/views/data-industry-refresh-fallback.spec.ts`

## Boundary Decisions

The D family parent can return from `blocked` to `decision-prepared` because:

- B4.013 no longer blocks residual cleanup.
- The tests residual domain parent is now current.
- This package only restores the family-level decision point.

This reactivation does not accept remaining dirty test behavior. It does not reopen or authorize D1 browser-smoke implementation. D1 must be refreshed as a separate authorization package before any E2E/browser-smoke test edits, selector changes, assertion changes, or runtime acceptance claims.

## Risk Notes

- The six `tests/e2e/**` files are business-smoke sensitive and can hide or expose mainline route/runtime regressions.
- Frontend source-tree tests under `web/frontend/src/views/**/__tests__` are currently provenance candidates, not accepted repository truth.
- `web/frontend/src/views/artdeco-pages/market-tabs/__node_tests__/marketKlineData.test.ts` remains isolated under the existing `marketKlineData` boundary.
- `web/frontend/tests/unit/config/trading-style-normalization.spec.ts` remains isolated and must not be staged by this parent package.
- Any frontend source/runtime behavior drift discovered while preparing D1 requires a separate source-authorized package; this no-source package does not grant that authority.

## Recommended Next Queue

1. Prepare a separate `B4.012-M3a-D1 E2E browser smoke authorization refresh` package if the tracked business-smoke files still need implementation cleanup.
2. Keep untracked frontend view/unit tests routed to `B4.012-M3a-U untracked tests provenance review` before any preserve/delete/ignore decision.
3. Keep `marketKlineData`, `trading-style-normalization.spec.ts`, frontend source dirty files, and external dirty files out of staging unless independently authorized.

## Verification Plan

Before commit:

- `git diff --cached --check`
- FUNCTION_TREE validate
- GitNexus staged verification and staged change detection
- OPENDOG verification

After commit:

- GitNexus analyze
- staged index empty
- `b4-012-m3a-d-e2e-frontend-tests-split` is `decision-prepared`
- `b4-012-m3a-d1-e2e-browser-smoke-authorization` remains `blocked`

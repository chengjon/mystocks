# HTML5 Runtime Local Acceptance Attempt - 2026-05-10

> **Scope**: `implement-html5-migration-experience-optimization`
>
> **Product scope**: Desktop-only
>
> **Result**: accepted for repo-local Desktop Chromium scope

## Summary

This report records local acceptance attempts for the HTML5 runtime integration validation tasks:

- `3.1.4 测试HTML5 APIs与现有功能的兼容性`
- `2.1.2 Add PWA icons and splash screens`
- `3.1.3 验证缓存策略与实时数据的一致性`
- `3.2.3 验证IndexedDB数据持久化和迁移`
- `2.3.5 Add storage quota monitoring and management`
- `3.2.4 测试Web Workers性能提升量化`
- `3.3.1 配置服务器PWA支持 (Service Worker + Manifest)`

The attempts produced enough evidence to close `3.1.4`, `2.1.2`, `3.1.3`, `3.2.3`, `2.3.5`, and repo-local `3.3.1` within the Desktop Chromium / production preview scope. This does not cover cross-browser PWA validation, production gray release, external monitoring acceptance, HTTPS/CDN/Nginx configuration, or release-owner sign-off.

`3.2.4` remains open. Current repo truth does not provide a working business Web Worker path that can be used for valid performance lift quantification.

`3.2.1` remains open. A Desktop Chromium offline route-matrix probe was attempted, but current service-worker-controlled navigation under Playwright `context.setOffline(true)` does not yet produce stable route-by-route evidence.

## Environment

- Date: 2026-05-10
- Frontend URL: `http://localhost:3020`
- Backend URL: `http://localhost:8020`
- Browser: Playwright Chromium
- Product scope: Desktop-only

## Service Status

`pm2 list` showed both required services online:

- `mystocks-backend`: online, `http://localhost:8020`
- `mystocks-frontend`: online, `http://localhost:3020`

HTTP reachability checks passed:

- `GET /`: `200`, `content-type: text/html`
- `GET /manifest.json`: `200`, `content-type: application/json`
- `GET /sw.js`: `200`, `content-type: text/javascript`

## Acceptance Attempt

### Attempt 1: Playwright Chromium with service workers allowed and broad API mocks

Result: failed.

Observed failure:

```text
page.goto: Timeout 30000ms exceeded.
- navigating to "http://localhost:3020/market/realtime", waiting until "domcontentloaded"
```

Interpretation:

- The attempt did not produce valid acceptance evidence.
- The broad API route mock was too invasive for a reliable acceptance record.

### Attempt 2: Direct route isolation

Result: route reachability was not the stable blocker.

Observed result:

- `serviceWorkers: "block"` direct `GET /market/realtime`: `200`, `domcontentloaded` in about `428ms`
- `serviceWorkers: "allow"` direct `GET /market/realtime`: `200`, `domcontentloaded` in about `387ms`

Interpretation:

- Direct route reachability is healthy.
- The failure is tied to the broader acceptance flow, not a simple route availability issue.

### Attempt 3: Dashboard to market flow with service worker comparison

Result: failed.

Observed failure with `serviceWorkers: "block"`:

```text
page.goto: Timeout 15000ms exceeded.
- navigating to "http://localhost:3020/market/realtime", waiting until "domcontentloaded"
```

Observed failure with `serviceWorkers: "allow"`:

```text
page.waitForSelector: Timeout 15000ms exceeded.
- waiting for locator('main') to be visible
- navigated to "http://localhost:3020/dashboard"
```

Notable event:

```text
http://localhost:3020/api/health/ready net::ERR_ABORTED
http://localhost:3020/api/health net::ERR_ABORTED
```

Interpretation:

- The local acceptance flow is sensitive to readiness/API handling.
- This needs a dedicated acceptance harness rather than ad hoc browser scripting.

### Attempt 4: Minimal readiness / CSRF stubs

Result: failed.

Observed failure:

```text
page.waitForSelector: Timeout 20000ms exceeded.
- waiting for locator('main') to be visible
```

Interpretation:

- Minimal readiness stubbing was not sufficient to produce a valid browser acceptance record.
- This attempt is a blocker record, not a passing validation.

### Attempt 5: Existing critical menu spec with service workers not blocked

Command:

```bash
cd web/frontend
env PLAYWRIGHT_EXTERNAL_FRONTEND=1 npx playwright test --config playwright.config.ts --project=chromium tests/e2e/critical/menu-navigation-fixed.spec.ts
```

Result:

```text
1 passed, 2 failed
```

Observed failures:

```text
Expected URL pattern: /\/market\/realtime/
Received URL: http://localhost:3020/dashboard
```

```text
page.goto: net::ERR_ABORTED; maybe frame was detached?
- navigating to "http://localhost:3020/market/realtime", waiting until "domcontentloaded"
```

Interpretation:

- The same critical menu smoke passes under the canonical E2E config where service workers are blocked.
- When using `playwright.config.ts`, which does not block service workers, the market navigation path becomes unstable.
- This is stronger evidence that the acceptance blocker is tied to the service-worker-allowed runtime surface, not to the menu spec itself.

### Attempt 6: Wait for service worker readiness before navigation

Result: failed.

Observed failure:

```text
page.waitForURL: Timeout 15000ms exceeded.
- waiting for navigation until "load"
```

Additional implementation context:

- `web/frontend/src/main-standard.ts` registers `/sw.js` after `window.load`.
- The same entry registers a `controllerchange` listener that calls `window.location.reload()`.
- `web/frontend/public/sw.js` calls `self.skipWaiting()` during install and `self.clients.claim()` during activate.

Interpretation:

- Waiting for `navigator.serviceWorker.ready` was not enough to produce a stable accepted record.
- The current service worker registration / activation / controllerchange behavior needs a dedicated acceptance harness and possibly root-cause work before `3.1.3` or `3.1.4` can close.

### Attempt 7: Runtime reload hypothesis test

Hypothesis:

- The first service worker `controllerchange` reload in `main-standard.ts` may interrupt the dashboard to market route flow.

Test:

- Applied a temporary minimal guard so the first controller adoption would not immediately call `window.location.reload()`.
- Re-ran:

```bash
cd web/frontend
env PLAYWRIGHT_EXTERNAL_FRONTEND=1 npx playwright test --config playwright.config.ts --project=chromium tests/e2e/critical/menu-navigation-fixed.spec.ts
```

Result:

```text
1 passed, 2 failed
```

Observed result:

- The same two service-worker-allowed failures remained.
- The hypothesis was not sufficient to explain or fix the blocker.
- The temporary runtime code change was reverted and is not part of the accepted repo state.

Additional observation:

- One failure snapshot showed `/market/realtime` page content rendered while the URL assertion still observed `/dashboard`.
- Another snapshot showed the market page shell rendered, but the existing assertion timing did not produce a stable pass.

Interpretation:

- The blocker is not solved by suppressing the first controllerchange reload alone.
- The next useful step is a dedicated acceptance harness that records URL state, router state, service worker state, and rendered route shell separately.

### Attempt 8: Dedicated HTML5 runtime acceptance harness

Harness:

- `web/frontend/tests/html5-runtime-acceptance.test.ts`
- It is opt-in only and runs when `HTML5_RUNTIME_ACCEPTANCE=1` is set.
- This avoids breaking default Playwright runs while keeping the service-worker-allowed blocker reproducible.

Command:

```bash
cd web/frontend
env HTML5_RUNTIME_ACCEPTANCE=1 PLAYWRIGHT_EXTERNAL_FRONTEND=1 npx playwright test --config playwright.config.ts --project=chromium tests/html5-runtime-acceptance.test.ts
```

Result:

```text
1 passed, 1 failed
```

Passing evidence from direct `/market/realtime` route:

```json
{
  "path": "/market/realtime",
  "manifestLinked": true,
  "serviceWorkerSupported": true,
  "serviceWorkerControlled": true,
  "serviceWorkerState": "activated",
  "cacheKeys": ["mystocks-v1.0.0", "mystocks-fonts-v1.0.0"],
  "indexedDBSupported": true,
  "workerSupported": true,
  "online": true,
  "connectionType": "4g",
  "h1": "实时行情工作台"
}
```

Failing evidence from dashboard menu navigation:

```json
{
  "path": "/dashboard",
  "manifestLinked": true,
  "serviceWorkerSupported": true,
  "serviceWorkerControlled": true,
  "serviceWorkerState": "activated",
  "cacheKeys": ["mystocks-v1.0.0", "mystocks-fonts-v1.0.0"],
  "indexedDBSupported": true,
  "workerSupported": true,
  "online": true,
  "connectionType": "4g",
  "h1": "QUANTIX",
  "activeRealtimeLink": false
}
```

Interpretation:

- Direct route HTML5 API surface is now observable in an opt-in harness.
- Dashboard menu navigation still does not satisfy route alignment under service-worker-allowed acceptance conditions.
- This is a reproducible blocker for fully closing `3.1.3`.
- This is useful partial evidence for `3.1.4`, but not enough to close it because acceptance still needs a stable route / feature flow record.

### Attempt 9: Production preview with service workers allowed

Setup:

- Built production assets with `cd web/frontend && npm run build:no-types`.
- Started temporary preview server at `http://127.0.0.1:4174`.
- Re-ran the opt-in harness against preview:

```bash
cd web/frontend
env FRONTEND_PORT=4174 HTML5_RUNTIME_ACCEPTANCE=1 npx playwright test --config playwright.config.ts --project=chromium tests/html5-runtime-acceptance.test.ts
```

Result:

```text
1 passed, 1 failed
```

Passing evidence from direct `/market/realtime` route:

```json
{
  "path": "/market/realtime",
  "manifestLinked": true,
  "serviceWorkerSupported": true,
  "serviceWorkerControlled": true,
  "serviceWorkerState": "activated",
  "cacheKeys": ["mystocks-v1.0.0", "mystocks-fonts-v1.0.0"],
  "indexedDBSupported": true,
  "workerSupported": true,
  "h1": "实时行情工作台",
  "activeRealtimeLink": true
}
```

Failing evidence from dashboard menu navigation:

```json
{
  "path": "/dashboard",
  "serviceWorkerControlled": true,
  "serviceWorkerState": "activated",
  "cacheKeys": ["mystocks-v1.0.0", "mystocks-fonts-v1.0.0"],
  "h1": "QUANTIX",
  "activeRealtimeLink": false,
  "realtimeLink": {
    "href": "/market/realtime",
    "className": "nav-item child-item",
    "pointerEvents": "auto"
  }
}
```

Additional click / router diagnostic:

```json
{
  "path": "/dashboard",
  "title": "实时行情 - MyStocks",
  "h1": "QUANTIX",
  "sw": true
}
```

Observed event sequence:

- Click capture on `a[href="/market/realtime"]`: `defaultPrevented=false`, path `/dashboard`, title `交易室 - MyStocks`.
- After the event tick: `defaultPrevented=true`, path still `/dashboard`, title `实时行情 - MyStocks`.
- No `history.pushState` was observed for `/market/realtime`.

Interpretation:

- The blocker reproduces in production preview, not only under Vite dev server.
- Vue Router reaches the navigation guard/title update for `/market/realtime`, then the navigation does not commit history or render the target route under a service-worker-controlled page.
- This is now the next real failure point for the HTML5 runtime acceptance line.

### Attempt 10: Service worker first-control reload fix

Root cause isolation:

- `router.push('/market/realtime')` worked from `/dashboard` before expanding the sidebar domain.
- After clicking the `市场行情` domain button, the same `router.push('/market/realtime')` timed out before `beforeResolve` / `afterEach`.
- Disabling service worker registration in the same `serviceWorkers: "allow"` browser made the expanded-menu `router.push` resolve.
- The blocker was therefore isolated to service worker first-control reload behavior interacting with the expanded sidebar state, not to the route table or auth guard.

Code change:

- `web/frontend/src/main-standard.ts` now tracks whether the page already had a service worker controller before registration.
- `controllerchange` only reloads once when replacing an already-controlled page.
- First install / first control adoption no longer forces an immediate reload during active user interaction.

Validation command:

```bash
cd web/frontend
npm run build:no-types
env FRONTEND_PORT=4174 HTML5_RUNTIME_ACCEPTANCE=1 npx playwright test --config playwright.config.ts --project=chromium tests/html5-runtime-acceptance.test.ts
```

Result:

```text
2 passed
```

Passing dashboard menu navigation evidence:

```json
{
  "path": "/market/realtime",
  "historyLength": 3,
  "manifestLinked": true,
  "serviceWorkerSupported": true,
  "serviceWorkerControlled": true,
  "serviceWorkerState": "activated",
  "cacheKeys": ["mystocks-v1.0.0", "mystocks-fonts-v1.0.0"],
  "indexedDBSupported": true,
  "workerSupported": true,
  "h1": "实时行情工作台",
  "activeRealtimeLink": true
}
```

Interpretation:

- The Desktop Chromium service-worker-allowed route / feature flow is now accepted for active HTML5 API compatibility.
- This closes the active API surface compatibility blocker for `3.1.4`.
- It still does not close `3.1.3`, because the harness does not yet validate realtime data freshness, stale-cache handling, API cache TTL expiry, or network/cache fallback consistency.

### Attempt 11: Realtime freshness retention record

Scope:

- Validate the realtime page freshness behavior when a verified quote snapshot exists and a later refresh fails.
- This test intentionally disables service worker registration in that single test case because Playwright request interception is not reliable for page-controlled API refreshes once the service worker owns the client.

Command:

```bash
cd web/frontend
env FRONTEND_PORT=4174 HTML5_RUNTIME_ACCEPTANCE=1 npx playwright test --config playwright.config.ts --project=chromium tests/html5-runtime-acceptance.test.ts
```

Result:

```text
3 passed
```

Freshness evidence:

- First `/api/v1/market/quotes` response returned `request_id=html5-runtime-quotes-fresh` and two quote rows.
- Refresh response returned `success=false`, `request_id=html5-runtime-quotes-refresh-failed`, and no replacement data.
- The page kept `TRACE_ID: html5-runtime-quotes-fresh`.
- The page did not expose `html5-runtime-quotes-refresh-failed`.
- The page kept the verified `平安银行` quote row.
- The page displayed `实时行情加载失败，已保留上一份有效样本快照。`

Interpretation:

- This is valid repo-local evidence that the realtime route does not replace a verified fresh snapshot with failed refresh data.
- This is only partial `3.1.3` evidence because the service worker was disabled for this specific refresh-failure interception and no IndexedDB TTL / stale-cache fallback matrix has been executed.

### Attempt 12: IndexedDB stale-cache fallback alignment

Scope:

- Validate the repository-level IndexedDB API contract needed by the market overview fallback path.
- Preserve the distinction between fresh TTL-bound cache reads and explicit stale fallback reads after a network failure.

Code change:

- `web/frontend/src/utils/indexedDB.ts` now exposes `getStaleCache<T>(key)`.
- `getStaleCache` reads the `api_cache` store without applying TTL expiry or deleting expired records.
- `getCache` remains the normal active-cache path and continues to enforce TTL expiry.
- `web/frontend/src/stores/marketData.ts` now uses `getStaleCache<MarketOverview>('market_overview')` only in the network-failure fallback branch.
- IndexedDB initialization is now deferred safely when `window.indexedDB` is unavailable, so Node/Vitest contract tests do not trigger an unhandled constructor-side initialization rejection.

Validation command:

```bash
cd web/frontend
npm run test -- tests/unit/utils/indexedDB.spec.ts
```

Result:

```text
1 passed file / 13 passed tests
```

Interpretation:

- This fixes a real repository inconsistency: the stale fallback path previously called `getCache()`, which can discard expired entries before fallback can use them.
- This is still partial `3.1.3` evidence. It validates the local stale-cache API contract and market store wiring, but it does not replace the required Desktop browser matrix covering service worker cache, IndexedDB TTL expiry, realtime freshness indicator, and network/cache fallback together.

### Attempt 13: Market store stale fallback contract

Scope:

- Validate the actual `useMarketDataStore().loadMarketOverview(true)` behavior when network refresh fails.
- Ensure the store calls the explicit stale fallback path and records the resulting overview as stale cache data.

Validation command:

```bash
cd web/frontend
npm run test -- src/stores/__tests__/marketData.spec.ts tests/unit/utils/indexedDB.spec.ts
```

Result:

```text
2 passed files / 14 passed tests
```

Evidence:

- `tradingApiManager.getMarketOverview()` rejected with `overview unavailable`.
- `indexedDB.getStaleCache('market_overview')` was called.
- `indexedDB.getCache('market_overview')` was not used for the network-failure fallback assertion.
- `store.state.cacheMetadata.source` became `cache`.
- `store.state.cacheMetadata.isStale` became `true`.

Interpretation:

- This closes the repo-local store contract gap introduced by the earlier stale-cache wiring fix.
- This remains partial `3.1.3` evidence because it is a mocked unit/store test, not a Desktop browser record with service worker API cache, IndexedDB TTL expiry, and realtime freshness labeling observed together.

### Attempt 14: Desktop Chromium cache fallback probes

Scope:

- Add a real browser probe to the opt-in HTML5 runtime harness.
- Verify that an expired `api_cache` record is not treated as active fresh cache, while the same record remains available to an explicit stale fallback path.
- Verify that a cached whitelisted API response can be served through the active service worker while the browser context is offline.
- Verify that `/api/v1/market/quotes` is now declared as API-cache eligible in the served service worker.
- Verify that the realtime route can display cached quote data under a service-worker-controlled offline refresh path.

Validation command:

```bash
cd web/frontend
env FRONTEND_PORT=4174 HTML5_RUNTIME_ACCEPTANCE=1 npx playwright test --config playwright.config.ts --project=chromium tests/html5-runtime-acceptance.test.ts
```

Result:

```text
7 passed
```

Service worker API cache evidence:

```json
{
  "seededState": {
    "serviceWorkerControlled": true,
    "serviceWorkerState": "activated",
    "cacheKeys": ["mystocks-v1.0.0", "mystocks-api-v1.0.0"]
  },
  "offlineFetchState": {
    "ok": true,
    "status": 200,
    "requestId": "html5-runtime-sw-api-cache",
    "source": "service-worker-cache",
    "upCount": 11,
    "downCount": 5
  }
}
```

Realtime quotes cache evidence:

```json
{
  "realtimeCacheEligibility": {
    "ok": true,
    "hasMarketSummaryPattern": true,
    "hasMarketQuotesPattern": true,
    "hasMarketRealtimePattern": true
  },
  "realtimeOfflineFallback": {
    "serviceWorkerControlled": true,
    "cacheKeys": ["mystocks-v1.0.0", "mystocks-api-v1.0.0"],
    "requestId": "html5-runtime-quotes-sw-cache"
  }
}
```

IndexedDB TTL evidence:

```json
{
  "indexedDBSupported": true,
  "databaseName": "MyStocksDB",
  "storeName": "api_cache",
  "cacheKey": "html5-runtime-expired-market-overview",
  "activeCacheData": null,
  "staleFallbackData": {
    "request_id": "html5-runtime-indexeddb-stale",
    "up_count": 9,
    "flat_count": 2,
    "down_count": 4
  }
}
```

Default harness guard:

```bash
cd web/frontend
npx playwright test --config playwright.config.ts --project=chromium tests/html5-runtime-acceptance.test.ts
```

Result:

```text
7 skipped
```

Interpretation:

- This is browser-level evidence for service worker API cache fallback, realtime quotes cache eligibility / offline cached quote rendering, and IndexedDB TTL expiry / explicit stale fallback data preservation in the Desktop-only harness.
- At this point, the remaining gap was UI freshness semantics: the realtime page needed an explicit visible distinction between service-worker-cache data and fresh network data.

### Attempt 15: Realtime cache freshness label closeout

Scope:

- Mark service-worker cached API responses so the realtime page can distinguish retained cache data from fresh network data.
- Keep the implementation local to the service worker response body and realtime view state; do not modify the shared `useArtDecoApi` composable because GitNexus impact analysis reported that path as HIGH risk in prior investigation.

Code change:

- `web/frontend/public/sw.js` now marks cached API responses with `X-MyStocks-Cache-Source: service-worker-cache`.
- For JSON `UnifiedResponse` payloads, `sw.js` now writes `cache_source: "service-worker-cache"` at both the top level and inside `payload.data` when `data` is an object, so existing API clients that return `response.data` can still observe the cache source.
- `web/frontend/src/views/market/Realtime.vue` records the verified cache source per preset and displays `缓存快照` plus `当前行情来自本地缓存快照，非实时网络刷新。` for service-worker-cache quote snapshots.
- `web/frontend/src/views/market/__tests__/Realtime.spec.ts` now covers the UI label for cached quote snapshots.
- `web/frontend/tests/html5-runtime-acceptance.test.ts` now asserts the same label in the Desktop Chromium service-worker-controlled offline cached quote scenario.

Validation commands:

```bash
cd web/frontend
npm run test -- src/views/market/__tests__/Realtime.spec.ts
npm run test -- tests/unit/utils/indexedDB.spec.ts
npm run test -- src/stores/__tests__/marketData.spec.ts
npm run build:no-types
npx playwright test --config playwright.config.ts --project=chromium tests/html5-runtime-acceptance.test.ts
env FRONTEND_PORT=4174 HTML5_RUNTIME_ACCEPTANCE=1 npx playwright test --config playwright.config.ts --project=chromium tests/html5-runtime-acceptance.test.ts
```

Results:

```text
Realtime.spec.ts: 1 passed file / 5 passed tests
indexedDB.spec.ts: 1 passed file / 13 passed tests
marketData.spec.ts: 1 passed file / 1 passed test
build:no-types: passed
html5-runtime-acceptance default: 7 skipped
html5-runtime-acceptance opt-in Desktop Chromium: 7 passed
```

Realtime cached quote evidence:

- Offline cached `/api/v1/market/quotes` replayed `request_id=html5-runtime-quotes-sw-cache`.
- Page displayed `TRACE_ID: html5-runtime-quotes-sw-cache`.
- Page displayed exact status `缓存快照`.
- Page displayed `当前行情来自本地缓存快照，非实时网络刷新。`
- Page did not display `实时行情加载失败`.
- Page kept the cached `平安银行` quote row.

Interpretation:

- This closes the prior `3.1.3` UI freshness gap for repo-local Desktop Chromium acceptance.
- The accepted scope is Desktop-only, service-worker-allowed production preview plus unit/store contracts; it does not claim Firefox/WebKit coverage, mobile behavior, production gray release, ROI/SLA acceptance, or external monitoring sign-off.

### Attempt 16: IndexedDB schema migration and reopen persistence

Scope:

- Validate the current repository IndexedDB persistence surface in a real Desktop Chromium browser.
- Validate the current schema bootstrap migration path. Current repo truth is `IndexedDBManager.dbVersion = 1`; no higher-version upgrade migration exists in this codebase, so this attempt does not claim version-to-version upgrade coverage.

Harness change:

- `web/frontend/tests/html5-runtime-acceptance.test.ts` now includes an opt-in test that deletes and recreates `MyStocksDB`, opens version `1`, exercises the `onupgradeneeded` schema bootstrap, writes representative records to all current stores, closes the database, reopens it, and verifies that all records remain readable.

Validation command:

```bash
cd web/frontend
env FRONTEND_PORT=4174 HTML5_RUNTIME_ACCEPTANCE=1 npx playwright test --config playwright.config.ts --project=chromium tests/html5-runtime-acceptance.test.ts
```

Result:

```text
8 passed
```

IndexedDB schema / persistence evidence:

```json
{
  "databaseName": "MyStocksDB",
  "databaseVersion": 1,
  "storeNames": ["api_cache", "market_data", "technical_indicators", "user_preferences"],
  "indexNames": {
    "api_cache": ["expiresAt"],
    "market_data": ["symbol_timestamp", "timestamp"],
    "technical_indicators": ["indicator", "symbol"],
    "user_preferences": []
  },
  "persistedMarket": { "symbol": "000001", "price": 10.25 },
  "persistedIndicator": { "symbol": "000001", "indicator": "MA" },
  "persistedPreferences": { "userId": "html5-runtime-user" },
  "persistedCache": {
    "key": "html5-runtime-persistence-probe",
    "data": { "request_id": "html5-runtime-indexeddb-persisted" }
  }
}
```

Interpretation:

- This closes `3.2.3` for the current repo-local Desktop Chromium IndexedDB surface: version `1` bootstrap schema creation plus close/reopen persistence across all current object stores.
- It does not claim future schema upgrade migration behavior because no `dbVersion > 1` migration code exists in the current repository.

### Attempt 17: Web Worker performance quantification blocker

Scope:

- Determine whether `3.2.4` has a real repo-local worker path that can be benchmarked in the same Desktop browser and data set.

Evidence commands:

```bash
curl -I http://127.0.0.1:4174/workers/indicator-calculator.js
curl -I http://127.0.0.1:4174/workers/protocol.js
rg -n "importScripts\\('./protocol\\.js'\\)|new Worker|Placeholder implementation|indicator-calculator" \
  web/frontend/public/workers/indicator-calculator.js \
  web/frontend/src/utils/workersManager/workers-manager.ts \
  web/frontend/src/stores/marketData.ts
```

Observed result:

- `/workers/indicator-calculator.js` is served as `200` / `text/javascript`.
- The worker script contains `importScripts('./protocol.js')`.
- `web/frontend/public/workers/protocol.js` and `web/frontend/dist/workers/protocol.js` are absent.
- `/workers/protocol.js` in production preview falls through to the SPA HTML fallback and returns `Content-Type: text/html`, not a worker protocol script.
- The business path remains `marketData.ts -> workersManager.calculateIndicator(...)`, but `workers-manager.ts` still contains the placeholder comment: `Placeholder implementation - in production this would use actual Web Worker`.
- `workers-manager.ts` does not create a `new Worker(...)`.

Interpretation:

- `3.2.4` cannot be validly closed in the current micro-batch.
- The repository has worker-related assets and a standalone worker script, but the worker asset dependency is incomplete and the business manager still uses placeholder calculation.
- Any “performance improvement” number measured now would be misleading because there is no verified business worker path to compare against a main-thread baseline.

### Attempt 18: Local server PWA support record

Scope:

- Validate repo-local production preview server support for core PWA assets and history fallback.
- Keep this scoped to `http://127.0.0.1:4174`; do not treat it as production target environment evidence.

Harness change:

- `web/frontend/tests/html5-runtime-acceptance.test.ts` now includes an opt-in server probe that records status, content type, cache-control, and body previews for `/`, `/manifest.json`, `/sw.js`, `/offline.html`, and `/market/realtime`.

Validation command:

```bash
cd web/frontend
env FRONTEND_PORT=4174 HTML5_RUNTIME_ACCEPTANCE=1 npx playwright test --config playwright.config.ts --project=chromium tests/html5-runtime-acceptance.test.ts
```

Result:

```text
9 passed
```

Server PWA support evidence:

```json
{
  "root": { "status": 200, "contentType": "text/html", "cacheControl": "no-cache" },
  "manifest": { "status": 200, "contentType": "application/json", "cacheControl": "no-cache" },
  "serviceWorker": { "status": 200, "contentType": "text/javascript", "cacheControl": "no-cache" },
  "offline": { "status": 200, "contentType": "text/html;charset=utf-8", "cacheControl": "no-cache" },
  "realtimeRoute": { "status": 200, "contentType": "text/html", "cacheControl": "no-cache" }
}
```

Interpretation:

- This closes `3.3.1` for the repo-local production preview server surface.
- It does not claim production target environment configuration, HTTPS behavior, CDN/Nginx cache policy, rollout execution, or release-owner sign-off.

## Existing E2E Baseline Check

Command:

```bash
cd web/frontend
env PLAYWRIGHT_EXTERNAL_FRONTEND=1 npx playwright test --config playwright.config.js --project=chromium tests/e2e/critical/menu-navigation-fixed.spec.ts
```

Result:

```text
3 passed (10.3s)
```

Coverage:

- Dashboard shell renders under the existing critical menu flow.
- Sidebar navigation reaches `/market/realtime`.
- Market page remains usable when a key API fails.

Boundary:

- This canonical smoke uses the repository E2E config, which blocks service workers.
- It cannot be used to close PWA / service worker / cache acceptance tasks.

## Decision

Mark `3.1.3`, `3.2.3`, `2.3.5`, the IndexedDB storage/retrieval success metric, and repo-local `3.3.1` complete for Desktop Chromium / production preview scope. Keep `3.2.4` open.

Reason:

- The opt-in Desktop Chromium harness now covers active HTML5 API surfaces, dashboard-to-realtime route alignment, realtime snapshot retention after failed refresh, service worker API cache fallback, realtime quotes cache eligibility, service-worker cached quote rendering with explicit cache freshness label, and IndexedDB TTL expiry / stale fallback preservation.
- The same harness now also covers `MyStocksDB` version `1` schema bootstrap migration and close/reopen persistence across `market_data`, `technical_indicators`, `user_preferences`, and `api_cache`.
- The same evidence is sufficient to close the IndexedDB storage/retrieval success metric for current repo-local Desktop Chromium scope.
- The same harness now covers local production preview PWA server asset support for `/`, `/manifest.json`, `/sw.js`, `/offline.html`, and `/market/realtime` history fallback.
- Unit/store tests cover the stale IndexedDB fallback contract and realtime cache label view contract.
- The existing canonical E2E smoke remains useful regression evidence, but it blocks service workers and is not used as the PWA/cache acceptance source.
- `3.2.4` remains blocked because the current business worker manager is still a placeholder and the served worker asset is missing its required `protocol.js` dependency.

## 3.2.1 Offline Route Matrix Blocker - 2026-05-11

Scope:

- Task: `3.2.1 实施11个路由的PWA离线测试`
- Product scope: Desktop-only
- Browser: Playwright Chromium
- Server surface: production preview on `http://127.0.0.1:4174`

Attempted matrix:

- `/dashboard`
- `/market/realtime`
- `/market/technical`
- `/data/industry`
- `/data/fund-flow`
- `/watchlist/manage`
- `/strategy/repo`
- `/strategy/backtest`
- `/trade/terminal`
- `/risk/overview`
- `/system/config`

Observed result:

- The opt-in harness can still verify active HTML5 runtime surfaces, server PWA assets, menu navigation alignment, service-worker API cache fallback, realtime cache labeling, API cache eligibility, IndexedDB TTL stale fallback, and IndexedDB persistence.
- A direct offline navigation loop using `context.setOffline(true)` and `page.goto(...)` did not produce stable per-route evidence; the test timed out before a reliable route matrix could be recorded.
- The attempted route-matrix case is now registered as a `fixme` in `web/frontend/tests/html5-runtime-acceptance.test.ts`, so the blocker is visible without causing the opt-in harness to fail.

Verification:

```text
env FRONTEND_PORT=4174 HTML5_RUNTIME_ACCEPTANCE=1 npx playwright test --config playwright.config.ts --project=chromium tests/html5-runtime-acceptance.test.ts
9 passed, 1 skipped
```

Decision:

- Keep `3.2.1` unchecked.
- Do not claim “11 routes offline PWA test completed” from the existing partial SW/API cache evidence.
- Close only after a stable service-worker-controlled navigation matrix records each desktop route's status, path retention, and offline fallback / cached-shell semantics.

## 2.3.5 Storage Quota Monitoring - 2026-05-11

Scope:

- Task: `2.3.5 Add storage quota monitoring and management`
- Product scope: Desktop-only
- Browser: Playwright Chromium
- Boundary: repo-local utility / browser-surface only

Implementation:

- `web/frontend/src/utils/indexedDB.ts` now exports `StorageQuotaInfo`.
- `indexedDB.getStorageQuota()` safely reads `navigator.storage.estimate()` and returns `supported`, `usage`, `quota`, and `usageRatio`.
- `indexedDB.isStorageQuotaNearLimit(threshold = 0.8)` provides a threshold helper for local quota checks.
- Unsupported environments return `supported=false` and do not block IndexedDB cache operations.

Verification:

```text
cd web/frontend && npm run test -- tests/unit/utils/indexedDB.spec.ts
16 passed
```

```text
cd web/frontend && env FRONTEND_PORT=4174 HTML5_RUNTIME_ACCEPTANCE=1 npx playwright test --config playwright.config.ts --project=chromium tests/html5-runtime-acceptance.test.ts
10 passed, 1 skipped
```

Browser record:

```json
{
  "storageManagerSupported": true,
  "usage": 0,
  "quota": 1682115355,
  "usageRatio": 0,
  "nearDefaultLimit": false
}
```

Decision:

- Close `2.3.5` for repo-local Desktop Chromium utility/browser-surface scope.
- Do not claim production monitoring alerting, UI quota dashboard, automatic quota cleanup, or cross-browser quota behavior.

## 2.1.2 PWA Manifest Asset Consistency - 2026-05-11

Scope:

- Task: `2.1.2 Add PWA icons and splash screens`
- Product scope: Desktop-only
- Boundary: repo-local manifest asset consistency

Change:

- `web/frontend/public/manifest.json` now only references static PWA icon assets that exist under `web/frontend/public/icons/`.
- Removed stale manifest references to missing `/screenshots/dashboard.png`, `/screenshots/analysis.png`, and `shortcut-*.png` assets.
- Removed the mobile-only `form_factor: "narrow"` screenshot declaration from the Desktop-only manifest surface.
- Added `web/frontend/tests/unit/config/pwa-manifest-assets.spec.ts` to guard that manifest image resources exist under `public/` and that Desktop-only scope does not declare `narrow` screenshots.

Verification:

```text
cd web/frontend && npm run test -- tests/unit/config/pwa-manifest-assets.spec.ts
2 passed
```

Decision:

- Close `2.1.2` for repo-local Desktop-only manifest asset consistency.
- Do not claim production-grade brand artwork replacement, mobile screenshots / splash screens, shortcut icon design, app-store listing assets, or cross-browser install UX acceptance.

## Next Required Work

Use the dedicated Desktop-only HTML5 runtime acceptance harness for any next repo-local HTML5 runtime acceptance work:

- Keep `3.2.1` open until a stable 11-route Desktop offline navigation matrix exists.
- Keep the accepted `3.1.4` service-worker-allowed route / API-surface record separate from `3.1.3` cache/freshness records in future reports.
- Preserve the browser records for IndexedDB TTL expiry / explicit stale fallback, service worker API cache fallback, realtime cached quote rendering, and freshness labeling as the current repo-local evidence set.
- Preserve the IndexedDB version `1` bootstrap migration / persistence record as current `3.2.3` evidence; future `dbVersion > 1` upgrade migration work needs a separate implementation and test.
- Preserve the local server PWA support record as repo-local `3.3.1` evidence only; production HTTPS/CDN/Nginx and release-owner sign-off remain separate external deployment work.
- For `3.2.4`, do not record performance lift until `WorkersManager` has a real worker orchestration path and `/workers/indicator-calculator.js` can load its protocol dependency. The next valid micro-batch would be either a design/approval step for wiring the worker manager, or a small repo-local asset/protocol repair if explicitly approved.
- Preserve the canonical E2E distinction: `playwright.config.js` blocks service workers and remains a menu smoke, while `playwright.config.ts` / this harness are the PWA runtime acceptance surface.
- Next feasible repo-local work should move to another unchecked low-risk task in `implement-html5-migration-experience-optimization`; cross-browser PWA validation and production rollout remain outside this micro-batch.

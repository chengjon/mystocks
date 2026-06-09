# HTML5 Migration Cache Warming and Analytics Audit

Date: 2026-05-12
Change: `implement-html5-migration-experience-optimization`
Task focus: `2.6.4` and `2.6.5`
Scope: Desktop-only, repo-local audit only

## Decision

`2.6.4` and `2.6.5` remain open.

This batch records the current advanced caching surface. The repo has static precache, network-first API runtime cache, IndexedDB TTL cache, local cache stats helpers, and service-worker cache stats helpers. It does not yet implement hot-market-data cache warming or an active cache analytics/monitoring dashboard.

## Evidence Checked

Commands:

```bash
sed -n '1,220p' web/frontend/public/sw.js
sed -n '1,220p' web/frontend/src/utils/indexedDB.ts
sed -n '1,220p' web/frontend/src/utils/cache/part-1.ts
sed -n '1,220p' web/frontend/src/utils/cache/part-1.analytics.ts
sed -n '1,220p' web/frontend/src/utils/cache/part-2.ts
sed -n '380,430p' web/frontend/src/stores/marketData.ts
rg -n "warm|prewarm|cache warming|hot data|热门|CacheAnalytics|getStats|hitRate|cacheHitRate" web/frontend/src web/frontend/public web/frontend/tests
```

Observed repo facts:

- `web/frontend/public/sw.js` precaches only the root app shell, manifest, and core icons in `STATIC_CACHE_URLS`.
- `web/frontend/public/sw.js` uses runtime network-first caching for matching API requests, then falls back to cached responses when offline.
- `web/frontend/src/utils/indexedDB.ts` provides TTL-style API cache functionality.
- `web/frontend/src/stores/marketData.ts` uses cache status and IndexedDB stores, but its warmup-period logic is for indicator history length, not hot-market-data prewarming.
- `web/frontend/src/utils/cache/part-1.ts`, `part-1.analytics.ts`, and `part-2.ts` expose local stats/analytics helper surfaces.
- `CacheManager.getStats()` exists in `public/sw.js`, but this audit did not find an active UI, message handler, or dashboard that consumes it as a monitoring truth.

## Gap Summary

The repo has caching infrastructure, but not hot-data cache warming. Runtime caching after a successful request is not the same as proactively warming hot stocks, quotes, or market overview data.

The repo also has cache stats helpers, but not a canonical cache analytics and monitoring surface. Helper functions and local counters do not establish an operational monitoring loop, dashboard, alerting threshold, or acceptance report.

## Task Disposition

Keep `2.6.4` and `2.6.5` unchecked until later approved batches implement and verify those capabilities.

Minimum future evidence for `2.6.4` should include:

- A declared hot-data source list or ranking policy.
- A proactive warm path for representative market/quote APIs.
- Verification that warmed entries are present before user navigation requires them.

Minimum future evidence for `2.6.5` should include:

- A canonical cache analytics source of truth.
- Active UI, report, or telemetry consumption of hit/miss/capacity/staleness data.
- Acceptance evidence for representative cache families.

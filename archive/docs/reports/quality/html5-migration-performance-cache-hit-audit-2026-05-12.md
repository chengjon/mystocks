# HTML5 Migration Performance Cache Hit Audit

Date: 2026-05-12
Change: `implement-html5-migration-experience-optimization`
Task focus: `2.9.2 Add cache hit rate analytics`
Scope: Desktop-only, repo-local audit only

## Decision

`2.9.2` remains open.

This batch records the current cache analytics surface. The repo contains local cache-stat helpers and sample values, but it does not yet expose a canonical active cache-hit analytics route, dashboard, or verified acceptance report.

## Evidence Checked

Commands:

```bash
sed -n '1,220p' web/frontend/src/composables/useArtDecoSettings.ts
sed -n '1,220p' web/frontend/src/views/artdeco-pages/settings/SystemInfoSettings.vue
sed -n '1,220p' web/frontend/src/utils/cache/part-1.ts
sed -n '1,220p' web/frontend/src/utils/cache/part-2.ts
sed -n '1,220p' web/frontend/src/composables/useMarket.ts
sed -n '1,220p' web/frontend/src/stores/marketData.ts
```

Observed repo facts:

- `web/frontend/src/composables/useArtDecoSettings.ts` and `web/frontend/src/views/artdeco-pages/settings/SystemInfoSettings.vue` expose `cacheHitRate` as static or example-facing data.
- `web/frontend/src/utils/cache/part-1.ts` and `part-2.ts` expose local LRU cache stats and `hitRate` / `getStats()` helpers.
- `web/frontend/src/composables/useMarket.ts` exposes `getCacheStats()`.
- `web/frontend/src/stores/marketData.ts` can return `indexedDB.getStats()` for object-store counts and local store state.

## Gap Summary

The repo has local cache statistics helpers, but they are not yet wired into a canonical dashboard or acceptance artifact as cache-hit analytics.

The available signals are still mostly local or illustrative. They do not establish a route-level cache-hit ratio, trend, threshold, or operational acceptance loop.

There is no evidence that any active system page currently owns cache-hit analytics as a first-class truth surface.

## Task Disposition

Keep `2.9.2` unchecked until a later approved batch defines and verifies a canonical cache-hit analytics surface.

Minimum future evidence should include:

- An active route or dashboard entry for cache-hit analytics.
- A clear cache-hit / miss ratio source of truth.
- Acceptance evidence for at least one representative route or store family.
- A decision on whether indexedDB object-store counts are sufficient or only supplementary.

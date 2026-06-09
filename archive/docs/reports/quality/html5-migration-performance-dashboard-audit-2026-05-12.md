# HTML5 Migration Performance Dashboard Audit

Date: 2026-05-12
Change: `implement-html5-migration-experience-optimization`
Task focus: `2.9.5 Create performance dashboard`
Scope: Desktop-only, repo-local audit only

## Decision

`2.9.5` remains open.

This batch records the current performance-dashboard surface. The repo has a legacy performance page and an active floating monitor, but it does not yet expose a canonical dashboard route for Web Vitals, cache hit rate, PWA usage metrics, or RUM.

## Evidence Checked

Commands:

```bash
sed -n '1,240p' web/frontend/src/router/index.ts
sed -n '1,240p' web/frontend/src/layouts/MenuConfig.ts
sed -n '1,240p' web/frontend/src/views/system/PerformanceMonitor.vue
sed -n '1,200p' web/frontend/src/views/system/__tests__/PerformanceMonitor.spec.ts
sed -n '1,200p' web/frontend/src/views/system/Settings.vue
```

Observed repo facts:

- `web/frontend/src/router/index.ts` exposes `system` routes for `/system/config`, `/system/health`, `/system/api`, `/system/resources`, and `/system/data`, but not a canonical `/system/performance` route.
- `web/frontend/src/layouts/MenuConfig.ts` also lacks a performance-dashboard menu entry.
- `web/frontend/src/views/system/PerformanceMonitor.vue` is explicitly marked as `legacy-static-shell`.
- `web/frontend/src/views/system/__tests__/PerformanceMonitor.spec.ts` guards that the legacy page does not reintroduce canonical Web Vitals or budget truth.
- `web/frontend/src/views/system/Settings.vue` contains only a monitor-style surface and does not function as a performance dashboard.

## Gap Summary

The repo does not currently have a canonical performance dashboard route owned by the active desktop navigation model.

The legacy performance page is intentionally de-canonicalized, and the active overlay is too small to serve as the performance dashboard requested by this task.

## Task Disposition

Keep `2.9.5` unchecked until a later approved batch defines the canonical performance dashboard route and its accepted metrics.

Minimum future evidence should include:

- A canonical active dashboard route or menu entry.
- A clear metric set owned by that dashboard.
- A verified relationship to Web Vitals, cache hit analytics, PWA usage metrics, or RUM.

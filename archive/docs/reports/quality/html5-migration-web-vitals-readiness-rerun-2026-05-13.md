# HTML5 Migration Web Vitals Readiness Rerun

Date: 2026-05-13

Change: `implement-html5-migration-experience-optimization`

Scope: Current repo-local readiness check for task `2.9.1`; this is not Web Vitals tracking closure.

## Check

The rerun inspected the current active performance-monitoring path and package dependencies:

- `web/frontend/package.json`
- `web/frontend/src/composables/usePerformanceMonitor.ts`
- `web/frontend/src/components/common/PerformanceMonitor.vue`
- `web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue`
- `web/frontend/src/views/system/PerformanceMonitor.vue`
- `web/frontend/src/router/index.ts`
- `web/frontend/src/layouts/MenuConfig.ts`

## Result

Current Web Vitals readiness: `false`.

Observed facts:

- `web-vitals` is not present in frontend dependencies.
- Active `usePerformanceMonitor.ts` exposes FPS and memory surfaces.
- Active `usePerformanceMonitor.ts` does not mention LCP / `largest-contentful-paint`.
- Active `usePerformanceMonitor.ts` does not mention FID / `first-input`.
- Active `usePerformanceMonitor.ts` does not mention CLS / `layout-shift`.
- Active `components/common/PerformanceMonitor.vue` renders FPS / memory style metrics, not Web Vitals.
- `ArtDecoLayoutEnhanced.vue` mounts the common performance monitor.
- `views/system/PerformanceMonitor.vue` remains a legacy/static shell.
- Router and `MenuConfig.ts` do not expose a canonical `/system/performance` dashboard route.

## Disposition

`2.9.1` remains open.

The current active performance overlay can be described as FPS / memory monitoring only. It cannot be used as evidence for LCP / FID / CLS Web Vitals tracking.

Future closure requires:

- a defined Web Vitals collection path;
- LCP / FID or replacement INP / CLS metric capture, with browser support notes;
- a sink or dashboard for those metrics;
- route-level verification showing the metrics are actually collected in the active app path.


# HTML5 Migration Performance Web Vitals Audit

Date: 2026-05-12
Change: `implement-html5-migration-experience-optimization`
Task focus: `2.9.1 Implement Web Vitals tracking`
Scope: Desktop-only, repo-local audit only

## Decision

`2.9.1` remains open.

This batch records the current Web Vitals surface. The repo has a legacy page that mentions LCP/FID/CLS in static form and a live desktop overlay that tracks FPS and JS heap. It does not yet provide a canonical active Web Vitals dashboard or a live route-level Web Vitals telemetry path.

## Evidence Checked

Commands:

```bash
sed -n '1,220p' web/frontend/src/components/common/PerformanceMonitor.vue
sed -n '1,260p' web/frontend/src/composables/usePerformanceMonitor.ts
sed -n '1,240p' web/frontend/src/views/system/PerformanceMonitor.vue
rg -n "largest-contentful-paint|first-input|layout-shift|FCP|LCP|CLS|FID|INP|PerformanceObserver|web vitals|web-vitals" web/frontend/src web/frontend/tests web/frontend/package.json
```

Observed repo facts:

- `web/frontend/src/components/common/PerformanceMonitor.vue` currently renders only `FPS` and `MEM`.
- `web/frontend/src/composables/usePerformanceMonitor.ts` currently defines `PerformanceMetrics` with `fps` and `memory` only; it computes FPS with `requestAnimationFrame` and reads Chrome-only `performance.memory`.
- `web/frontend/src/views/system/PerformanceMonitor.vue` is a `legacy-static-shell` and explicitly says it does not show shell-level LCP, FID, CLS, FCP, bundle budget, or local trend charts.
- The active layout chain remains `ArtDecoLayoutEnhanced.vue -> components/common/PerformanceMonitor.vue -> usePerformanceMonitor.ts`.

## Gap Summary

The repo does not have a canonical active Web Vitals dashboard. The active performance overlay is limited to FPS and memory, while the legacy page is explicitly non-canonical.

There is no verified route-level telemetry sink for LCP, FID, CLS, or INP. The repo-local evidence only shows isolated comments or legacy references, not a production-style measurement pipeline.

There is no active dashboard route or menu entry that canonicalizes Web Vitals as a first-class performance surface.

## Task Disposition

Keep `2.9.1` unchecked until a later approved batch defines a canonical Web Vitals dashboard and verifies the live data path.

Minimum future evidence should include:

- A canonical active route for Web Vitals.
- A route-level telemetry path for at least LCP / CLS / INP or an approved legacy equivalent.
- A decision on whether FPS / JS heap are merely supplementary or sufficient for this task.
- Verification that the active shell, not the legacy static shell, owns the accepted truth.

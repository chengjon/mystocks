# HTML5 Migration Performance RUM Audit

Date: 2026-05-12
Change: `implement-html5-migration-experience-optimization`
Task focus: `2.9.4 Add Real User Monitoring`
Scope: Desktop-only, repo-local audit only

## Decision

`2.9.4` remains open.

This batch records the current RUM surface. The repo contains local performance observers and console-style diagnostic helpers, but it does not yet integrate a real user monitoring SDK or route-level telemetry sink.

## Evidence Checked

Commands:

```bash
sed -n '1,240p' web/frontend/package.json
sed -n '1,240p' web/frontend/src/utils/performance/part-1.ts
sed -n '1,240p' web/frontend/src/utils/performance/part-2.ts
rg -n "sendBeacon|OpenTelemetry|Sentry|Datadog|New Relic|RUM|real user monitoring|web-vitals|analytics" web/frontend/src web/frontend/tests web/frontend/package.json
```

Observed repo facts:

- `web/frontend/package.json` does not include a RUM SDK dependency such as Sentry, Datadog, New Relic, OpenTelemetry, or `web-vitals`.
- `web/frontend/src/utils/performance/part-1.ts` uses `PerformanceObserver` for local console visibility of navigation/resource/longtask signals.
- `web/frontend/src/utils/performance/part-2.ts` still has placeholder-style functions and returns an empty object from `getAllMetrics()`.
- `initPerformanceMonitoring()` currently logs in DEV rather than posting telemetry to a backend or analytics sink.

## Gap Summary

The current repo can observe performance locally, but it does not yet monitor real users in a canonical, routable, or back-end-backed way.

There is no sampling policy, no route-level telemetry store, no sendBeacon path, and no externally plumbed SDK in the current repo-local surface.

## Task Disposition

Keep `2.9.4` unchecked until a later approved batch defines and verifies a real user monitoring integration.

Minimum future evidence should include:

- A chosen RUM backend or SDK.
- A route-level telemetry sink or export path.
- A sampling and privacy policy for Desktop-only usage.
- A verified page/route that consumes the collected RUM data.

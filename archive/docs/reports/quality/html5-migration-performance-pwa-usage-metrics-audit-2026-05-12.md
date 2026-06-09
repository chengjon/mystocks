# HTML5 Migration Performance PWA Usage Metrics Audit

Date: 2026-05-12
Change: `implement-html5-migration-experience-optimization`
Task focus: `2.9.3 Implement PWA usage metrics`
Scope: Desktop-only, repo-local audit only

## Decision

`2.9.3` remains open.

This batch records the current PWA usage-metrics surface. The repo has manifest and service-worker plumbing, but it does not yet collect install-rate or usage-duration telemetry.

## Evidence Checked

Commands:

```bash
sed -n '1,220p' web/frontend/public/manifest.json
sed -n '1,220p' web/frontend/src/main-standard.ts
rg -n "beforeinstallprompt|appinstalled|display-mode|standalone|install rate|usage time|usage duration|telemetry|analytics" web/frontend/src web/frontend/tests web/frontend/package.json
```

Observed repo facts:

- `web/frontend/public/manifest.json` declares `display: "standalone"` and `start_url: "/"`, plus core icons.
- `web/frontend/src/main-standard.ts` registers `/sw.js` after `load` and handles `updatefound` / `controllerchange`.
- The repo does not show active `beforeinstallprompt`, `appinstalled`, display-mode session tracking, or PWA install-success-rate reporting.
- Multiple Playwright specs still block service workers, so current smoke execution does not establish a stable install/usage telemetry baseline.

## Gap Summary

The repo has PWA plumbing, but not PWA usage metrics. Manifest and service-worker registration are necessary prerequisites, not telemetry.

There is no install-rate sink, no usage-duration sink, and no report that proves the ratio or duration metrics are being tracked on the Desktop-only product surface.

## Task Disposition

Keep `2.9.3` unchecked until a later approved batch defines a measurable PWA usage-metrics pipeline.

Minimum future evidence should include:

- `beforeinstallprompt` / `appinstalled` or an approved equivalent measurement path.
- A usage-duration or session-duration metric source of truth.
- A route or report that presents the metric for Desktop-only usage.

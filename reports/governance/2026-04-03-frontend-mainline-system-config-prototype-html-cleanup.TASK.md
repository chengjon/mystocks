# TASK

> Exported from Mongo control plane. Do not treat this file as the primary editable task source.

- Issue Identifier: `2026-04-03-frontend-mainline-system-config-prototype-html-cleanup-main`
- Issue Title: `Frontend Mainline System-Config Prototype HTML Cleanup`
- Objective: `Align the remaining ArtDeco System-Config prototype HTML hints to the confirmed current truth: read-only health endpoints, local-only page save semantics, and datasource writeback under System-Data.`
- Branch: `wip/root-dirty-20260403`
- Assigned Worker CLI: `main`
- Tracker State: `verified`

## Allowed Paths
- `web/frontend/public/artdeco/09-system-settings.html`
- `web/frontend/artdeco-design/09-system-settings.html`
- `reports/governance/2026-04-03-frontend-mainline-system-config-prototype-html-cleanup.TASK.md`
- `reports/governance/2026-04-03-frontend-mainline-system-config-prototype-html-cleanup.TASK-REPORT.md`

## Forbidden Paths
- (none)

## Acceptance Checks
- `git diff --check -- web/frontend/public/artdeco/09-system-settings.html web/frontend/artdeco-design/09-system-settings.html`
- `rg -n 'localStorage|System-Data|/health/detailed|/health' web/frontend/public/artdeco/09-system-settings.html web/frontend/artdeco-design/09-system-settings.html`

## OpenSpec
- (none)

## Related Plans
- web/frontend/public/artdeco/09-system-settings.html
- web/frontend/artdeco-design/09-system-settings.html

## Owner Decision
- Suggested Owner: `main`
- Final Owner: `main`
- Worker CLI: `main`
- Decision Basis:
  - The remaining stale contract hints sit in two ArtDeco prototype HTML files.
  - The active truth is already confirmed: health endpoints are read-only, local page save is local-only, and datasource writeback belongs to System-Data.

## Scope Paths
- web/frontend/public/artdeco/09-system-settings.html
- web/frontend/artdeco-design/09-system-settings.html

## Next Steps
- No further cleanup is needed unless more prototype-only stale hints are discovered.

## Compatibility Notes
- Mongo is the source of truth; this cleanup only aligns prototype HTML hints to the current System-Config truth.
- These prototype files are not the live Vue page, but stale API hints here can still mislead manual review or future copy-forward work.

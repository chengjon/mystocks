# Frontend View Governance A4 Phase4 And Wencai Wrapper Defer Decision

> **Scope**: `openspec/changes/update-frontend-view-governance`
> **Decision date**: 2026-05-12

## Decision

Select `A4-phase4-wencai-wrapper-defer`.

Do not execute archive moves for these top-level legacy wrappers in the current repo-local micro-batch:

- `web/frontend/src/views/Phase4Dashboard.vue`
- `web/frontend/src/views/Wencai.vue`

## Reason

Both files are no longer independent runtime truth, but both still have deliberate owner specs that preserve thin-wrapper behavior.

Current guard and history:

- `web/frontend/src/views/__tests__/Phase4Dashboard.spec.ts` imports `Phase4Dashboard.vue` directly and verifies it delegates to the canonical dashboard owner instead of restoring the old Phase 4 pseudo-live shell.
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/phase4-dashboard-legacy-canonical-wrapper-truth-audit.md` records the previous repair that collapsed `Phase4Dashboard.vue` into a thin wrapper over `ArtDecoDashboard.vue`.
- `web/frontend/src/views/__tests__/Wencai.spec.ts` imports `Wencai.vue` directly and verifies it keeps the live `WencaiPanel.vue` truth component without reintroducing the old pseudo overview or fake statistics shell.
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/wencai-legacy-live-panel-wrapper-truth-audit.md` records the previous repair that replaced the old Wencai shell with a thin wrapper over `WencaiPanel.vue`.
- `docs/reports/quality/myweb-audit/frontend-view-checklist-top-level-legacy-2026-05-10.md` classifies both as top-level legacy `candidate-review` entries and not archive-approved.
- `docs/reports/quality/myweb-audit/frontend-view-guard-map-2026-05-10.json` still records these files and their direct specs as guard/history references.

Archiving either wrapper safely requires a separate decision to retire or migrate the direct owner specs and confirm the canonical successor surfaces still cover the intended handoff.

## Boundary

This decision does not move files, edit runtime code, retire tests, or change wrapper behavior.

Current classifications:

- `Phase4Dashboard.vue`: `candidate-review/legacy-canonical-wrapper`, retain as dashboard-wrapper guard anchor.
- `Wencai.vue`: `candidate-review/legacy-live-panel-wrapper`, retain as Wencai-panel guard anchor.

This decision does not cover similarly named demo files under `web/frontend/src/views/demo/`; those remain governed by the demo-directory lifecycle.

This decision does not claim global frontend lint is clean.

## Next Valid Step

Prepare a separate approval package if the team wants to retire these wrappers. That package must decide:

- whether each wrapper proof is still needed
- whether the direct owner spec should be retired or migrated
- the canonical successor confirmation for dashboard and Wencai behavior
- the successor or explicit `no-successor-needed` rationale

Until then, no archive execution is approved for `Phase4Dashboard.vue` or `Wencai.vue`.

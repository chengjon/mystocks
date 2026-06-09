# Frontend View Governance A4 TestPage Static Shell Defer Decision

> **Scope**: `openspec/changes/update-frontend-view-governance`
> **Decision date**: 2026-05-12

## Decision

Select `A4-testpage-static-shell-defer`.

Do not execute an archive move for `web/frontend/src/views/TestPage.vue` in the current repo-local micro-batch.

## Reason

`TestPage.vue` is not active route truth, but it is still a deliberate legacy static-shell guard anchor.

Current guard and history:

- `web/frontend/src/views/__tests__/TestPage.spec.ts` imports `TestPage.vue` directly and verifies the `legacy-static-shell` behavior.
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/settings-test-static-shells-truth-audit.md` records that `TestPage.vue` was converted from local integration-test UI with console side effects into an honest static shell.
- `docs/reports/quality/myweb-audit/frontend-view-checklist-top-level-legacy-2026-05-10.md` classifies `TestPage.vue` as `candidate-review`, route status `dead`, and not archive-approved.
- `docs/reports/quality/myweb-audit/frontend-view-guard-map-2026-05-10.json` still records `TestPage.vue` and its direct spec as guard/history references.

Archiving this file safely requires a separate decision to retire or migrate its static-shell proof. That is outside the current micro-batch.

## Boundary

This decision does not move files, edit runtime code, retire tests, or change the static-shell copy.

`TestPage.vue` remains `candidate-review/legacy-static-shell` and `retain-as-static-shell-guard-anchor`.

This decision does not claim global frontend lint is clean.

## Next Valid Step

Prepare a separate approval package if the team wants to retire this static-shell guard. That package must decide:

- whether `TestPage.vue` still needs a static-shell proof
- whether `web/frontend/src/views/__tests__/TestPage.spec.ts` should be retired or migrated
- whether any historical docs should remain as history-only references
- the successor or explicit `no-successor-needed` rationale

Until then, no archive execution is approved for `TestPage.vue`.

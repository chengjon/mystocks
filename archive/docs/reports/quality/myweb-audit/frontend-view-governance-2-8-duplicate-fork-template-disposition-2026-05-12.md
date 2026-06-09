# Frontend View Governance 2.8 Duplicate Fork Template Disposition

> **Scope**: `openspec/changes/update-frontend-view-governance`
> **Decision date**: 2026-05-12

## Decision

Close task `2.8` for the currently entered governance scope by applying the duplicate/fork handling template to the known forked families that entered review:

- `Phase4Dashboard`
- `TechnicalAnalysis`

This disposition is read-only. It does not approve archive moves, code edits, test retirement, or guard retirement.

## Phase4Dashboard Disposition

Known fork evidence:

- `docs/reports/quality/myweb-audit/frontend-view-governance-history-2026-05-10.md` records `Phase4Dashboard` as a known historical duplicate/fork family.
- `docs/reports/quality/myweb-audit/frontend-view-governance-lessons-learned-2026-05-10.md` records that root and demo `usePhase4Dashboard` implementations were separate historical page implementations, not a reusable shared layer.
- `docs/reports/quality/myweb-audit/frontend-view-checklist-top-level-legacy-2026-05-10.md` classifies root `Phase4Dashboard.vue` as a thin compatibility wrapper over `ArtDecoDashboard.vue`, `compat-retained`, and not archive-approved.
- `docs/reports/quality/myweb-audit/frontend-view-governance-a4-phase4-wencai-wrapper-defer-decision-2026-05-12.md` keeps root `Phase4Dashboard.vue` as `candidate-review/legacy-canonical-wrapper`.

Current handling:

- Root `web/frontend/src/views/Phase4Dashboard.vue` remains retained as a guarded thin wrapper.
- Demo `web/frontend/src/views/demo/Phase4Dashboard.vue` remains under demo-directory lifecycle and is not resolved by the root wrapper decision.
- No mechanical merge is approved between root and demo variants.

## TechnicalAnalysis Disposition

Known fork evidence:

- `docs/reports/quality/myweb-audit/frontend-view-governance-history-2026-05-10.md` records `TechnicalAnalysis` as a known duplicate/fork family.
- `docs/reports/quality/myweb-audit/frontend-view-checklist-top-level-legacy-2026-05-10.md` classifies root `web/frontend/src/views/TechnicalAnalysis.vue` as top-level legacy `candidate-review`, dead route status, and not archive-approved.
- `docs/reports/quality/myweb-audit/frontend-view-governance-a4-top-level-static-shells-defer-decision-2026-05-12.md` keeps root `TechnicalAnalysis.vue` as `candidate-review/legacy-static-shell`.
- `docs/reports/quality/myweb-audit/frontend-view-checklist-technical-2026-05-10.md` separately classifies nested `web/frontend/src/views/technical/TechnicalAnalysis.vue` as an honest static shell, spec-guarded, `candidate-review`, and not archive-approved.

Current handling:

- Root `web/frontend/src/views/TechnicalAnalysis.vue` remains a retained top-level static-shell guard anchor.
- Nested `web/frontend/src/views/technical/TechnicalAnalysis.vue` remains governed by the technical-domain checklist, not by the top-level A4 static-shell batch.
- ArtDeco technical shells and advanced-analysis technical children are explicitly separate surfaces and require their own domain decisions.
- No mechanical merge is approved between root, nested technical, ArtDeco, or advanced-analysis variants.

## Boundary

This record only closes the template-application requirement for the known forked pages that entered this governance batch.

It does not:

- mark any `Phase4Dashboard` or `TechnicalAnalysis` file as archive-approved
- retire direct owner specs
- move demo files, technical-domain files, or style/composable support files
- claim global frontend lint is clean
- change FUNCTION_TREE or route truth

## Next Valid Step

Any future archive or consolidation package for these families must be a separate approved batch and must include:

- exact file list
- current route/menu owner status
- direct guard/test references
- successor or explicit `no-successor-needed` rationale
- coupled style/composable disposition where applicable
- verification plan for affected owner specs

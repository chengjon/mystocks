# Change: Add ArtDeco Impeccable Design Gate

## Why

The Web frontend already has multiple ArtDeco layers, canonical business routes, compatibility-era ArtDeco assets, and a refreshed `PRODUCT.md` / `DESIGN.md` context. The current risk is not a lack of visual ideas. The risk is improving pages directly before the implemented design, document truth, visual tokens, runtime states, and verification gates are audited together.

This change turns the 2026-05-28 ArtDeco Web design alignment plan into an OpenSpec-governed workflow. The workflow uses `impeccable` to audit the implemented Web ArtDeco design and produce design documents first. Source implementation begins only after the design documents and page shape brief are approved.

## What Changes

- Add a design-documentation gate for ArtDeco Web design improvement work.
- Require an `impeccable` sequence of `document -> critique -> shape -> approval` before `craft`.
- Make `market/Realtime.vue` the first pilot critique target unless an approved design document changes the pilot order.
- Require optimization findings to be prioritized by impact, risk, reuse value, and verification cost.
- Make pre-approval outputs documentation-only: design context findings, critique reports, shape briefs, review checklists, task plans, and verification plans.
- Explicitly block pre-approval Vue, TypeScript, SCSS, token, route, and component implementation changes.
- Preserve the post-approval implementation path: `craft -> audit -> polish -> extract`, bounded by the approved shape scope and existing frontend quality gates.

## Impact

- Affected spec: `artdeco-design-governance`
- Primary plan: `docs/reports/tasks/2026-05-28-artdeco-web-design-alignment-plan.md`
- Expected design artifacts:
  - refreshed `DESIGN.md` facts or design-context findings
  - ArtDeco documentation alignment findings
  - page review checklist
  - `market/Realtime.vue` critique report
  - `market/Realtime.vue` shape brief for approval
- No frontend runtime code is changed by this proposal itself.
- Post-approval implementation may later touch `web/frontend/src/views/**`, `web/frontend/src/components/**`, `web/frontend/src/composables/**`, and `web/frontend/src/styles/**`, but only inside an approved shape scope.

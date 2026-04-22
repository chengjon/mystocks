# Change: Align ArtDeco Stateful Primitives With DESIGN

## Why

Phase A+B completed runtime-truth and typography-truth closure for the active ArtDeco stack, but the highest-value runtime gap remains open:

- the `--ad-*` component state-machine token system is documented and tokenized, but not yet consistently adopted by shared primitives
- chip / badge / status semantics are still uneven across reusable components and page-local styling
- tooltip / overlay token contracts exist in `DESIGN.md` and `artdeco-tokens.scss`, but shared primitive adoption is still incomplete

Without a controlled follow-up batch, the project risks drifting back into ad-hoc state styles, page-local semantic styling, and partial design-contract adoption.

## What Changes

- adopt `--ad-*` state tokens on a narrow shared primitive surface
- align reusable chip / badge / status semantics with the current `DESIGN.md` contract
- adopt shared tooltip / overlay token contracts on shared primitives where applicable
- keep compatibility files as bridges only; do not create new runtime truth outside the active ArtDeco token chain

## Implementation Boundary

Primary implementation targets:

- `web/frontend/src/components/artdeco/base/ArtDecoButton.vue`
- `web/frontend/src/components/artdeco/base/ArtDecoInput.vue`
- `web/frontend/src/components/artdeco/base/ArtDecoCard.vue`
- `web/frontend/src/components/artdeco/base/ArtDecoBadge.vue` as the canonical shared owner for filter-chip and status-chip semantics
- `web/frontend/src/components/artdeco/business/ArtDecoStatus.vue` only where dot-status presentation must stay distinct from chip semantics

Supporting truth sources:

- `DESIGN.md`
- `web/frontend/src/styles/artdeco-tokens.scss`
- `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`
- `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md`
- `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`
- `docs/reports/artdeco-alignment/ARTDECO_PHASE_A_B_REVIEW_2026-04-19.md`

## Non-Goals

- responsive residue cleanup
- chart-theme or demo-theme normalization
- broad page-by-page visual restyling
- route or layout shell rewrites
- decorative corner-marker reintroduction
- Element Plus behavior replacement or logic rewrites

## Impact

- Affected specs: `artdeco-design-governance`
- Affected code: shared ArtDeco base primitives, selected shared status surfaces, ArtDeco design/tokens governance docs
- Risk: medium, but bounded by limiting implementation to shared primitives rather than page-wide conversion

## Success Criteria

- shared ArtDeco primitives use the `--ad-*` token system for visual state behavior where the contract now requires it
- shared chip / badge / status semantics align with the current `DESIGN.md` definitions
- tooltip / overlay shared styling uses the active token contract without introducing new parallel truth
- no new runtime truth is introduced into compatibility files
- the change remains scoped to reusable/shared surfaces and does not expand into broad page cleanup

## 1. Scope Lock

- [x] 1.1 Re-read `DESIGN.md`, `ARTDECO_FINTECH_UNIFIED_SPEC.md`, `ARTDECO_COMPONENT_GUIDE.md`, and `ARTDECO_PHASE_A_B_REVIEW_2026-04-19.md` before code changes
- [x] 1.2 Record the exact shared primitive targets for this change and confirm the batch excludes responsive cleanup, chart-theme cleanup, and route/layout rewrites
- [x] 1.3 Lock `ArtDecoBadge.vue` as the canonical shared owner for filter-chip and status-chip semantics, while keeping `ArtDecoStatus.vue` scoped to dot-status presentation

## 2. Shared Primitive State-Machine Adoption

- [x] 2.1 Align `ArtDecoButton.vue` visual states to the `--ad-*` state token system without changing underlying behavior contracts
- [x] 2.2 Align `ArtDecoInput.vue` visual states to the `--ad-*` state token system without changing underlying behavior contracts
- [x] 2.3 Align `ArtDecoCard.vue` visual states to the `--ad-*` state token system where the component currently expresses hover / elevated / focus-like visual states
- [x] 2.4 Remove or reduce ad-hoc hover/focus/error styling only where the tokenized state fully replaces it

## 3. Shared Semantic Surface Alignment

- [x] 3.1 Implement the approved filter-chip semantics on `ArtDecoBadge.vue`
- [x] 3.2 Implement the approved status-chip semantics on `ArtDecoBadge.vue`, including holding / pending / warning / profit / loss meanings where supported
- [x] 3.3 Align shared badge / status usage with `DESIGN.md`, keeping chip semantics on `ArtDecoBadge.vue` and avoiding page-local inline semantic restyling where the reusable primitive can own the contract
- [x] 3.4 Adopt tooltip / overlay token contracts on shared primitives where those surfaces are already part of the shared component API

## 4. Governance And Documentation Synchronization

- [x] 4.1 Update `ARTDECO_COMPONENTS_CATALOG.md` if primitive ownership or semantic responsibility becomes clearer after implementation
- [x] 4.2 Update `ARTDECO_COMPONENT_GUIDE.md` or related ArtDeco governance docs only if placement/ownership rules need clarification after the batch
- [x] 4.3 Keep compatibility files (`artdeco-main.css`, `artdeco-variables.css`, `artdeco-colors.css`) out of new truth creation

## 5. Verification

- [x] 5.1 Run frontend type verification with `npx vue-tsc --noEmit`
- [x] 5.2 Run targeted style/build verification for touched shared primitives
- [x] 5.3 Verify at least one consumer page for each changed primitive surface
- [x] 5.4 If the batch unexpectedly touches route, layout, or shared shell behavior, expand verification to PM2 + Playwright and report actual results

## 6. Exit Criteria

- [x] 6.1 Confirm the batch stayed within shared primitive scope
- [x] 6.2 Confirm no new parallel design truth was introduced
- [x] 6.3 Confirm the batch is ready for a separate follow-up change rather than continuing into responsive or chart-theme cleanup

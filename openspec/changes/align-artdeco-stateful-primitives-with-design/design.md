## Context

Phase A+B closed the runtime truth split around ArtDeco token authority, typography authority, and compatibility-path alignment. The next batch should not reopen those questions. It should consume the established truth chain and apply it to a narrow set of shared primitives.

The relevant current truths are:

- `DESIGN.md` defines the experience contract
- `artdeco-tokens.scss` defines the active token truth
- compatibility files remain bridges only
- `ARTDECO_FINTECH_UNIFIED_SPEC.md` and `ARTDECO_COMPONENT_GUIDE.md` define runtime and placement boundaries

## Goals

- adopt the `--ad-*` state-machine token model on shared primitives
- align canonical shared chip / badge / status semantics with `DESIGN.md`
- adopt tooltip / overlay token contracts where they belong on shared primitives
- keep the change small enough to verify without turning into another system-wide cleanup wave

## Non-Goals

- responsive residue cleanup
- chart-theme normalization
- route or layout rewrites
- converting every page to tokenized state behavior
- introducing a second ArtDeco design truth outside the current active chain

## Design Decisions

### Decision 1: Primitive-first adoption

State-machine adoption begins on shared primitives, not page-level blocks.

Reason:

- this yields the highest reuse per change
- it avoids page-wide churn
- it keeps verification small and attributable

### Decision 2: Token wiring only, no logic rewrite

The batch will change visual-state expression, not replace Element Plus or component behavior contracts.

Reason:

- `DESIGN.md` and the current project direction both prefer theme/token overrides over behavioral rewrites
- this minimizes regression risk

### Decision 3: `ArtDecoBadge.vue` owns chip semantics

Filter-chip and status-chip semantics will be centralized on `web/frontend/src/components/artdeco/base/ArtDecoBadge.vue`.

Reason:

- it is already the shared base-level capsule surface used across multiple ArtDeco contexts
- it matches the visual shape and semantic role of filter/status chips better than dot-status components
- it prevents the batch from spreading chip truth across multiple badge/status primitives

Boundary:

- `ArtDecoStatus.vue` remains the owner of dot-status presentation for operational states such as online/offline/loading
- this change does not collapse dot-status and chip-status into one component

### Decision 4: Compatibility files stay read-only in spirit

If a touched primitive depends on compatibility-era variables, the fix should flow back to canonical tokens or primitive-local usage, not by creating new truth in compatibility files.

Reason:

- Phase A+B already established those files as bridges only

### Decision 5: Overlay token adoption stays on existing shared surfaces

Tooltip / overlay token adoption is limited to shared primitives that already own overlay-like presentation.

Implemented surfaces in this batch:

- `web/frontend/src/components/artdeco/core/ArtDecoLoadingOverlay.vue`
- `web/frontend/src/components/artdeco/trading/ArtDecoTradeForm.vue`

Reason:

- these components already own shared backdrop / elevated-panel rendering
- this satisfies the token-contract goal without expanding into chart-local tooltip styling or page-specific floating UI
- it keeps the batch inside reusable/shared-surface scope

## Verification Strategy

Minimum verification:

- `npx vue-tsc --noEmit`
- targeted style/build sanity for touched primitives
- consumer-page inspection for each changed primitive family

Escalation rule:

- if the change spreads into route/layout/shared-shell behavior, verification must escalate to PM2 + Playwright instead of staying local

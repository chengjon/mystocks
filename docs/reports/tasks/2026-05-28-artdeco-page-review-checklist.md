# ArtDeco Web Page Review Checklist

Date: 2026-05-28

OpenSpec change: `add-artdeco-impeccable-design-gate`

Use this checklist with `$impeccable critique <target>` before any ArtDeco Web implementation task.

## 1. Scoring

Score each item:

- `0`: missing or actively contradicts current ArtDeco governance
- `1`: present but incomplete, local-only, or inconsistent
- `2`: present, coherent, and aligned with current Web ArtDeco docs

Classify findings:

- `P0`: blocks implementation because it conflicts with route truth, token truth, runtime safety, or approval gates
- `P1`: high-use page or task-critical workflow issue
- `P2`: reusable pattern or component extraction opportunity
- `P3`: historical, cosmetic, or low-risk documentation cleanup

## 2. Route and Ownership

- [ ] Target is an active routed page or an explicitly documented route exception.
- [ ] Route truth is verified against `web/frontend/src/router/index.ts`.
- [ ] Page ownership is classified as `views/<domain>`, `views/artdeco-pages`, embedded block, wrapper, or compatibility asset.
- [ ] The review does not assume `views/artdeco-pages/**` is universal route truth.
- [ ] Proposed extraction respects `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md`.

## 3. Page Grammar

- [ ] Page has one clear workbench structure: header band, control row, primary work area, secondary context, and runtime status.
- [ ] Header communicates page purpose and operational state without marketing-style hero composition.
- [ ] Control row groups filters, refresh, and primary actions in one predictable area.
- [ ] Primary work area gives data the largest and clearest surface.
- [ ] Secondary context supports decisions without competing with primary data.
- [ ] No nested page cards inside larger decorative cards unless the hierarchy is functionally necessary.

## 4. Data Density and Financial Semantics

- [ ] Dense tables use tabular numerals and aligned columns.
- [ ] Data panels preserve scannability at desktop target widths.
- [ ] A-share color semantics are preserved: red/up/positive, green/down/negative.
- [ ] Color is supported by labels, signs, icons, or text where state matters.
- [ ] Decorative ArtDeco gold does not compete with risk, freshness, execution, or price state.

## 5. Runtime States

- [ ] Initial loading state is explicit and does not collapse the page.
- [ ] Refreshing state is distinguishable from first load.
- [ ] Empty state explains what is missing and what to try next.
- [ ] Error state includes retry or recovery path.
- [ ] Cache state is visible when data is served from cache.
- [ ] Stale state is explicit when freshness is uncertain or outdated.
- [ ] Degraded or partial data state is explicit when only part of the workflow is trustworthy.
- [ ] Status copy is short, domain-specific, and useful under market pressure.

## 6. Token and Style Governance

- [ ] New or touched visual values use `artdeco-tokens.scss` and the approved token family.
- [ ] Raw hex, rgba, box-shadow, blur, and color-mix values are either existing untouched debt or documented exceptions.
- [ ] `--ad-*` and `--artdeco-*` usage is classified as canonical, alias-backed, or compatibility bridge before cleanup.
- [ ] Element Plus overrides remain bridge code, not a second design truth.
- [ ] Bloomberg terminal overrides stay limited to terminal surfaces.

## 7. Component Reuse

- [ ] Existing ArtDeco primitives are checked before creating new components.
- [ ] Candidate reusable patterns have at least two consumers or an approved extraction rationale.
- [ ] Domain-specific state is not hidden inside base or core components.
- [ ] Route-level state logic is kept in page or composable ownership with clear reuse boundary.

## 8. Accessibility and Interaction

- [ ] Focus states are visible against dark surfaces and do not rely only on glow.
- [ ] Controls have familiar affordances and predictable keyboard behavior.
- [ ] `aria-live`, `role=alert`, or `role=status` is used where runtime state changes need announcement.
- [ ] Motion conveys state only and respects reduced-motion expectations.
- [ ] Copy does not rely on English decorative labels for critical meaning.

## 9. Verification Planning

Before approval:

- [ ] Design-context report exists.
- [ ] Page critique exists.
- [ ] Shape brief exists and names implementation scope.
- [ ] No frontend source implementation changes are included.

After approval:

- [ ] Structural syntax errors are reported.
- [ ] Type-check result is compared to baseline.
- [ ] ArtDeco lint or targeted style gate is reported.
- [ ] PM2 service status is reported when build, type check, E2E, or service startup is involved.
- [ ] E2E or smoke report includes command, browser project, pass/fail/skip counts, and scope.

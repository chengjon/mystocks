# ArtDeco Runtime Truth Alignment Proposal

Date: 2026-04-19  
Scope: `DESIGN.md`, `web/frontend/src/styles/**`, `web/frontend/src/components/artdeco/**`, selected shared UI/data components  
Status: Draft for review only  
Change type: Documentation and implementation alignment proposal, no code changes in this document

---

## 1. Executive Summary

The current MyStocks ArtDeco system has already evolved from a generic ArtDeco mother-style into a project-specific `ArtDeco × Fintech × A-share` design system. That strategic direction is correct and should be preserved.

The main problem is not design direction drift. The main problem is runtime truth fragmentation:

- `DESIGN.md` defines the current project-level design contract.
- `web/frontend/src/styles/artdeco-tokens.scss` expresses the newer runtime token truth.
- older runtime files and component styles still preserve earlier ArtDeco assumptions and partially conflicting values.

This creates a layered drift:

1. design contract is newer than runtime implementation
2. token layer is newer than component consumption
3. old compatibility style files still appear authoritative

This proposal recommends aligning runtime truth in controlled batches without undoing intentional project-specific improvements.

---

## 2. What Should Be Preserved

The following project-specific decisions are assessed as correct and should remain the active direction:

- `Cinzel + Barlow + JetBrains Mono` as the active typography stack
- A-share convention as the global semantic truth: red = up/profit, green = down/loss
- financial semantic glow as an ArtDeco-compatible enhancement
- component state-machine tokenization for button/input/card/table/chip states
- compact and micro-density modes for data-dense trading and monitoring surfaces
- single-primary-action rule for trading/execution panels
- desktop-first product positioning
- decorative corner markers remaining globally disabled at runtime due to overlap/collision issues

These are not regressions from the mother-style guide. They are project-level optimizations that improve usability, trading safety, and scanability.

---

## 3. Confirmed Runtime Drift

### 3.1 Typography Truth Drift

Current design contract and active token direction:

- `DESIGN.md` uses `Cinzel + Barlow + JetBrains Mono`
- `artdeco-tokens.scss` documents the same stack as typography truth

Current runtime drift:

- `artdeco-global.scss` still imports `Marcellus + Josefin Sans`
- `artdeco-variables.css` still exposes `Marcellus` and `Josefin Sans` as active font tokens
- some older charts/views/components still reference the older stack or mixed aliases

Impact:

- inconsistent display/body rendering across screens
- unclear typography authority for future contributors
- unnecessary risk of partial visual regressions when touching shared styles

Assessment:

- this is legacy implementation drift, not a justified product exception

---

### 3.2 Legacy Style Truth Drift

Current design contract and token truth:

- `DESIGN.md` + `artdeco-tokens.scss` represent the newer baseline

Current runtime drift:

- `artdeco-variables.css` still contains older palette assumptions
- `index.scss` still contains generic global web-app defaults
- some legacy aliases and older spacing/body/reset assumptions remain in shared style entry points

Impact:

- multiple files look like design truth sources even when they are not
- maintainers cannot quickly tell which layer is canonical
- legacy styles may leak into newer pages unexpectedly

Assessment:

- this is a structural governance issue in the style layer

---

### 3.2.1 Confirmed Token-Level Conflict Table

The following explicit token/value conflicts have already been confirmed between `artdeco-variables.css` and `artdeco-tokens.scss` and should be treated as Phase A truth-conflict items:

| Token / Concern | `artdeco-variables.css` | `artdeco-tokens.scss` | Assessment |
|-----------------|-------------------------|------------------------|------------|
| `--artdeco-bg-elevated` | `#1E3D59` | `#1A1A1A` | Direct conflict; old midnight-blue elevated surface vs current warm-charcoal elevated surface |
| `--artdeco-fg-secondary` / muted text model | `#888888` secondary and `#666` muted | primary alias + `#A0A0A0` muted | Text hierarchy drift; old muted palette is darker and less aligned with current AA-oriented contract |
| `--artdeco-gold-hover` | `#F2E8C4` | `#F0E68C` | Direct hover/accent conflict; older pale-gold hover still survives in compatibility layer |
| `--artdeco-warning` | `#ff9800` | `#D4AF37` | Direct semantic/accent conflict; warning badges and callouts shift from orange to brand gold depending on import path |
| Typography truth | `Marcellus` / `Josefin Sans` | `Cinzel` / `Barlow` / `JetBrains Mono` | Major runtime truth split, affects headings/body typography across active pages |
| `--artdeco-font-display` | `'Marcellus', serif` | `var(--artdeco-font-heading)` -> `Cinzel` | High-impact runtime conflict because active consumers of `var(--artdeco-font-display)` span dozens of view/component/style files and resolve to different display faces depending on which layer wins |
| `--artdeco-bg-surface` vs `--artdeco-bg-card` | `--artdeco-bg-surface: #141414` | `--artdeco-bg-card: #141414` | Same current value, different names; not a visual conflict today but a naming split that can silently diverge in future edits |
| Radius / component softness model | `radius-md = 0px`, `radius-lg = 0px` | `radius-md = 8px`, `radius-lg = 12px` | Direct component-shape conflict; older strict-sharp baseline vs current sharp-first but selectively softened contract |

These conflicts are significant because they are not merely historical notes. They encode materially different runtime decisions and can lead maintainers to implement against the wrong baseline.

---

### 3.3 Component State Machine Adoption Gap

Current design contract and token truth:

- `DESIGN.md` defines the component state machine
- `artdeco-tokens.scss` defines `--ad-*` state tokens for buttons, inputs, cards, rows, chips, tooltips, and overlays

Current runtime drift:

- those tokens are largely defined but not yet widely consumed by components
- core components still hand-code hover/focus/error/disabled behavior directly in component styles
- state logic is not yet centralized in the way the new contract intends

Impact:

- state behavior remains uneven across components
- design system upgrades still require per-component restyling
- documentation progress is ahead of runtime reality

Assessment:

- this is the highest-value implementation gap after typography alignment

---

### 3.4 Desktop-Only Contract vs Historical Responsive Residue

Current design contract:

- project is desktop-first / desktop-only in the active ArtDeco contract

Current runtime drift:

- responsive residue is broader than an incidental leftover; current inventory indicates 50+ media-query branches across 8+ active style/component files
- base style files still preserve responsive assumptions from earlier project phases
- responsive logic still exists in both generic style entry points and ArtDeco-era component/page styles

Impact:

- unnecessary maintenance burden
- layout policy remains ambiguous
- testing scope stays broader than the product’s intended surface

Assessment:

- this drift is understandable historically but should be gradually reduced, but its size should not be understated during planning

---

### 3.5 Controlled Exception: Decorative Corner Markers

Mother-style expectation:

- stepped corners and corner embellishments are part of ArtDeco identity

Current project exception:

- decorative corner markers are globally disabled at runtime because earlier implementations overlapped with existing UI elements and harmed clarity

Impact:

- some mother-style visual signatures are intentionally suppressed

Assessment:

- this is a valid and approved project exception
- it should remain documented, not “fixed”

---

## 4. Root Cause Analysis

The drift appears to come from phased evolution rather than random inconsistency.

### 4.1 Likely evolution sequence

1. early generic ArtDeco implementation
2. later financial/quant adaptation
3. later CoinPulse-informed component-state and interaction upgrades
4. documentation and token truth upgraded faster than component/runtime cleanup

### 4.2 Why the current state is unstable

- style truth is distributed across too many partially authoritative files
- compatibility aliases helped avoid regressions but delayed truth convergence
- component-level authored styles still dominate over token-driven shared behavior
- historical responsive assumptions and early ArtDeco assets still exist in active paths

---

## 5. Proposed Alignment Strategy

### Phase A: Truth Consolidation

Goal:

- make canonical truth obvious before broader refactors

Actions:

- explicitly designate `DESIGN.md` as design contract truth
- explicitly designate `artdeco-tokens.scss` as active token truth
- classify `artdeco-variables.css` as either compatibility-only or deprecation candidate
- classify `index.scss` as generic legacy base or trim it to non-conflicting primitives only
- explicitly document the current token conflict set between `artdeco-variables.css` and `artdeco-tokens.scss`
- explicitly document `index.scss` as a current conflict source because its global `font-family` falls back to `Helvetica Neue` and related system fonts instead of the active ArtDeco typography stack
- add short header comments to affected files describing their current truth role

Expected benefit:

- lowers design ambiguity immediately without risky visual refactors

Risk:

- low

Recommended priority:

- highest

---

### Phase B: Typography Truth Alignment

Goal:

- eliminate the active font-stack split

Actions:

- align global runtime imports with `Cinzel + Barlow + JetBrains Mono`
- remove or isolate older `Marcellus/Josefin Sans` runtime truth from active entry points
- preserve compatibility aliases only where migration is incomplete and explicitly justified
- eliminate duplicate font loading in global runtime entry points; the current system should not load both the old and new ArtDeco stacks simultaneously
- explicitly resolve `index.scss` global font-family overrides so base html/body/app typography no longer fights the active ArtDeco token stack

Expected benefit:

- immediate improvement in visual consistency
- easier future theme maintenance
- stronger correlation between docs, tokens, and actual UI

Risk:

- medium
- typography changes can subtly affect spacing, truncation, and chart label fit

Recommended priority:

- highest

Validation focus:

- header/title rendering
- dense tables
- chart labels
- button/input text alignment
- duplicate webfont request removal and stable runtime font fallback behavior

---

### Phase C: State Machine Wiring

Goal:

- convert the new state machine from documentation/token definition into actual runtime behavior

Actions:

- wire `ArtDecoButton` to `--ad-btn-*`
- wire `ArtDecoInput` to `--ad-input-*`
- identify the canonical shared card shell and align it to `--ad-card-*`
- identify shared chip/status badge patterns and align them to `--ad-chip-*`
- align table row hover/selected states in shared table primitives to `--ad-row-*`
- define tooltip/overlay adoption targets in shared wrappers before touching page-local implementations

Expected benefit:

- consistent interaction states
- lower one-off styling cost
- easier future contract upgrades

Risk:

- medium to high if applied too broadly in one batch

Recommended priority:

- high, but after Phase A and B

Execution note:

- apply to shared primitives first, not to every page in parallel

---

### Phase D: Legacy Base Style Reduction

Goal:

- reduce runtime interference from generic or historical global styles

Actions:

- audit `index.scss` for conflicting font, scrollbar, and responsive rules
- retain only truly generic layout/reset helpers that do not override ArtDeco truth
- move any remaining ArtDeco-specific responsibilities fully into ArtDeco style entry points

Expected benefit:

- reduces visual unpredictability
- clarifies which global styles are framework base vs product theme

Risk:

- medium

Recommended priority:

- medium

---

### Phase E: Responsive Residue Cleanup

Goal:

- match runtime implementation more closely to desktop-first product reality

Actions:

- inventory active mobile/responsive branches
- record the actual responsive residue scope as a baseline number before removal so the cleanup plan is tied to measured reality rather than qualitative wording
- classify each as required, harmless legacy, or removable debt
- remove only low-risk residue that no longer serves active screens

Expected benefit:

- simpler layout policy
- lower maintenance and testing burden

Risk:

- medium

Recommended priority:

- medium to low

---

## 6. Proposed Execution Order

Recommended implementation order:

1. Phase A: truth consolidation
2. Phase B: typography truth alignment
3. Phase C1: `ArtDecoButton` state-machine adoption
4. Phase C2: `ArtDecoInput` state-machine adoption
5. Phase C3: shared card / table / chip primitives
6. Phase D: legacy base style reduction
7. Phase E: responsive residue cleanup

This order minimizes churn and reduces the chance of debugging multiple overlapping style migrations at once.

---

## 7. File-Level Recommendations

### 7.1 Files That Should Remain Canonical

- `DESIGN.md`
- `web/frontend/src/styles/artdeco-tokens.scss`
- `docs/guides/web/ARTDECO_MASTER_INDEX.md`

### 7.2 Files That Need Explicit Role Clarification

- `web/frontend/src/styles/artdeco-global.scss`
- `web/frontend/src/styles/artdeco-variables.css`
- `web/frontend/src/styles/index.scss`
- `web/frontend/src/styles/element-plus-artdeco.scss`

### 7.3 First Components Recommended for Alignment

- `web/frontend/src/components/artdeco/base/ArtDecoButton.vue`
- `web/frontend/src/components/artdeco/base/ArtDecoInput.vue`
- shared data/button/table/chip primitives under `web/frontend/src/components/data/`
- canonical ArtDeco card shell / compact card primitives

---

## 8. Non-Goals

The following are explicitly out of scope for the first alignment batch:

- re-enabling decorative corner markers
- replacing Element Plus component logic
- redesigning all legacy pages in one pass
- converting every chart tooltip implementation immediately
- introducing mobile-first design
- changing A-share semantic color truth

---

## 9. Review Questions

The following decisions should be explicitly reviewed before implementation begins:

1. Should `artdeco-variables.css` be marked compatibility-only or scheduled for retirement?
2. Should typography alignment happen in one batch or behind a temporary rollout flag?
3. Which component should be treated as the canonical shared card primitive?
4. For tooltip/overlay state tokens, should the first adoption target be Element Plus wrappers or custom ArtDeco overlays?
5. Do we want a formal “desktop-only implementation cleanup” task after the visual truth alignment is complete?

---

## 10. Suggested Approval Format

If this proposal is accepted, suggested implementation approval can be given in one of these forms:

- `Approve Phase A only`
- `Approve Phase A + B`
- `Approve through Button/Input state-machine alignment`
- `Approve full runtime alignment plan`

This allows implementation to proceed in safe, reviewable micro-batches rather than one large visual migration.

---

## 11. Recommendation

Recommended next step:

- approve `Phase A + Phase B` first

Reason:

- they provide the highest clarity-to-risk ratio
- they reduce style truth ambiguity before touching broader component behavior
- they prepare the codebase for safe state-machine adoption in later batches

After that, the next best micro-batch is:

- `ArtDecoButton` + `ArtDecoInput` state-machine adoption

This sequence is the most practical way to turn the current design contract into reliable runtime truth without destabilizing the active web frontend.

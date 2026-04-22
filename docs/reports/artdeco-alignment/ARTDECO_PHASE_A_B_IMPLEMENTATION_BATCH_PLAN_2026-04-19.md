# ArtDeco Phase A+B Implementation Batch Plan

Date: 2026-04-19  
Status: Draft for approval  
Source proposal: `docs/reports/artdeco-alignment/ARTDECO_RUNTIME_TRUTH_ALIGNMENT_PROPOSAL_2026-04-19.md`

---

## 1. Scope

This batch plan covers only:

- Phase A: truth consolidation
- Phase B: typography truth alignment

This batch explicitly does **not** include:

- state-machine wiring for components
- large-scale page restyling
- responsive residue removal
- re-enabling decorative corner markers

---

## 2. Objectives

The objective of this batch is to make runtime truth unambiguous before broader style refactors begin.

Expected outcomes:

- contributors can clearly identify which files are canonical
- the active ArtDeco font stack becomes consistent at runtime
- duplicate loading of old and new font stacks is removed
- generic global style overrides stop fighting the ArtDeco theme baseline

---

## 3. Target Files

### 3.1 Primary files to update

- `DESIGN.md`
- `web/frontend/src/styles/artdeco-tokens.scss`
- `web/frontend/src/styles/artdeco-global.scss`
- `web/frontend/src/styles/artdeco-main.css`
- `web/frontend/src/styles/artdeco-variables.css`
- `web/frontend/src/styles/index.scss`
- `docs/guides/web/ARTDECO_MASTER_INDEX.md`

### 3.2 Secondary files to inspect during verification

- `web/frontend/src/main-standard.ts`
- `web/frontend/src/styles/element-plus-artdeco.scss`
- selected shared ArtDeco/base components that directly depend on global font aliases

---

## 4. Batch Breakdown

## Batch A1: Truth Role Labeling

Goal:

- clarify file responsibility before changing values

Actions:

- add or update top-of-file comments in style truth files
- explicitly label:
  - `DESIGN.md` as design contract truth
  - `artdeco-tokens.scss` as active token truth
  - `artdeco-variables.css` as compatibility-only or pending deprecation
  - `index.scss` as generic base layer, not design-truth authority
- ensure documentation wording does not imply multiple active runtime truths

Success criteria:

- no active style file appears to be an undocumented parallel truth source

Risk:

- low

---

## Batch A2: Token Conflict Documentation

Goal:

- make known token conflicts explicit and reviewable

Actions:

- document the currently confirmed conflict set between:
  - `artdeco-main.css`
  - `artdeco-variables.css`
  - `artdeco-tokens.scss`
- include at minimum:
  - elevated background conflict
  - muted/secondary text conflict
  - gold-hover conflict
  - warning color conflict
  - typography truth conflict
  - `--artdeco-font-display` conflict
  - radius model conflict
  - `--artdeco-bg-surface` vs `--artdeco-bg-card` naming divergence

Success criteria:

- conflict set is visible in code comments or adjacent documentation
- future edits cannot accidentally treat `artdeco-variables.css` as equal truth

Risk:

- low

---

## Batch B1: Font Loading Alignment

Goal:

- ensure only the active ArtDeco font stack is loaded in the main runtime path

Actions:

- update `artdeco-global.scss` so active runtime font imports align with:
  - `Cinzel`
  - `Barlow`
  - `JetBrains Mono`
- remove simultaneous loading of:
  - `Marcellus`
  - `Josefin Sans`
  from the active global entry path unless explicitly justified as compatibility-only
- audit the `artdeco-main.css -> artdeco-variables.css` dependency chain and record whether it remains part of an active runtime path
- align the CSS variable `--artdeco-font-display` in `artdeco-variables.css` so active runtime consumers do not fall back to generic serif after font-loading cleanup
- inventory the current dependency scope of `var(--artdeco-font-display)` consumers and record that scope as a follow-up migration surface; current audit baseline is 87 known consumers across views, components, and shared SCSS files

Success criteria:

- main runtime path no longer loads both old and new ArtDeco font stacks
- visual font truth matches `DESIGN.md` and `artdeco-tokens.scss`
- active runtime consumers of `--artdeco-font-display` resolve to the approved display stack rather than `Marcellus` or generic serif fallback

Risk:

- medium

Validation focus:

- display headings
- body labels
- data tables
- chart labels
- active layout entry points that import `artdeco-main.css`

---

## Batch B2: Global Font Override Cleanup

Goal:

- stop generic base styles from overriding ArtDeco typography truth

Actions:

- audit `index.scss`
- remove or narrow the global `font-family` on `html, body, #app` if it still points to:
  - `Helvetica Neue`
  - generic Chinese/system sans stack
- audit the legacy light scrollbar styles in `index.scss` and either align them to the active ArtDeco dark theme or explicitly defer them out of this batch
- ensure the final global typography inheritance flows from ArtDeco token truth instead of legacy base CSS

Success criteria:

- `html/body/#app` no longer fight the active ArtDeco font stack
- the final computed base font stack matches the approved ArtDeco contract

Risk:

- medium

Validation focus:

- app shell
- router root
- shared forms
- shared table cells

---

## Batch B3: Compatibility File Role Decision

Goal:

- avoid leaving `artdeco-variables.css` in a misleading state

Decision options:

### Option 1: Compatibility-only

- keep the file
- add a clear compatibility-only header
- forbid new runtime truth additions there
- redirect any still-active compatibility typography token needed by runtime consumers to the approved display stack

### Option 2: Retirement candidate

- mark as pending deprecation
- leave only what is still needed by legacy consumers
- plan future removal after dependency audit

Recommended option:

- Option 1 for this batch

Reason:

- lowest migration risk
- supports phased cleanup without forcing immediate dependency removal
- avoids leaving `--artdeco-font-display` as an active conflicting token while known consumers still depend on it

Success criteria:

- reviewers can tell whether this file is canonical or compatibility-only in under 10 seconds
- compatibility tokens that still participate in active runtime paths do not contradict the approved ArtDeco truth

Risk:

- low

---

## 5. Implementation Order

Recommended execution order:

1. Batch A1
2. Batch A2
3. Batch B1
4. Batch B2
5. Batch B3

Reason:

- documentation and file-role clarification should happen before value changes
- font loading and global override cleanup should happen before any component-level migration

---

## 6. Verification Checklist

After implementation, verify:

- `DESIGN.md` and `artdeco-tokens.scss` still match
- `artdeco-global.scss` loads only the approved active font stack
- `index.scss` no longer overrides base typography with legacy system fonts
- `index.scss` no longer imposes legacy light-theme scrollbar treatment unless explicitly deferred and documented
- `artdeco-variables.css` has a clearly declared non-canonical role
- `artdeco-main.css` has a clearly declared role in the runtime graph
- no duplicate ArtDeco font stacks are loaded in the main runtime path
- importing `artdeco-variables.css` via `artdeco-main.css` does not silently override aligned tokens in the main standard runtime path
- heading/body/data text visually align with:
  - `Cinzel`
  - `Barlow`
  - `JetBrains Mono`

---

## 7. Suggested Testing Pass

Minimum post-change testing:

- run frontend build/type/lint checks relevant to style imports
- inspect:
  - app shell
  - dashboard
  - at least one table-heavy page
  - at least one chart-heavy page
  - at least one form-heavy page
- confirm no visible typography regression in:
  - headings
  - body labels
  - table cells
  - button text
  - input labels

If service startup or frontend verification is performed as part of implementation, final reporting should include:

- structural syntax errors
- type inference errors versus baseline
- PM2 service state
- actual executed E2E or smoke verification scope

---

## 8. Approval Options

Recommended approval wording:

- `Approve Batch A1-A2 only`
- `Approve Phase A only`
- `Approve Phase A + B`

Recommended choice:

- `Approve Phase A + B`

Reason:

- this is the highest clarity-to-risk batch
- it resolves the most important truth conflicts before touching component behavior

---

## 9. Next Batch After Approval

If this batch is completed successfully, the next recommended batch is:

- `ArtDecoButton` state-machine adoption
- `ArtDecoInput` state-machine adoption

Those should be handled as a separate reviewable phase, not appended to Phase A+B in the same implementation turn.

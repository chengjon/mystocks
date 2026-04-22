# ArtDeco Phase A+B Review

Date: 2026-04-19  
Status: Ready for review  
Scope: Phase A truth consolidation + Phase B typography truth alignment only

---

## 1. Executive Verdict

Phase A+B has been implemented within the approved boundary.

This batch now does the following:

- makes the active runtime token truth explicit
- aligns the main runtime font-loading path to `Cinzel + Barlow`
- stops `index.scss` from overriding the ArtDeco typography baseline with `Helvetica Neue`
- converts the `artdeco-main.css` dependency chain into a clearly documented compatibility path rather than an implicit parallel truth source
- closes the warning-color conflict in the compatibility chain so legacy ArtDeco entry points do not keep emitting an old orange warning token

This batch intentionally does **not** yet do the following:

- wire `--ad-*` state-machine tokens into component implementations
- clean responsive residue across 50+ media-query branches
- normalize old chart/demo/theme files that still carry legacy font assumptions
- re-enable decorative corner markers

---

## 2. Files Touched In This Batch

### Design contract and governance docs

- `DESIGN.md`
- `docs/reports/artdeco-alignment/ARTDECO_RUNTIME_TRUTH_ALIGNMENT_PROPOSAL_2026-04-19.md`
- `docs/reports/artdeco-alignment/ARTDECO_PHASE_A_B_IMPLEMENTATION_BATCH_PLAN_2026-04-19.md`
- `docs/guides/web/ARTDECO_MASTER_INDEX.md`

### Runtime style truth and compatibility files

- `web/frontend/src/styles/artdeco-tokens.scss`
- `web/frontend/src/styles/artdeco-global.scss`
- `web/frontend/src/styles/artdeco-main.css`
- `web/frontend/src/styles/artdeco-variables.css`
- `web/frontend/src/styles/artdeco-colors.css`
- `web/frontend/src/styles/index.scss`

---

## 3. What Was Completed

### A1. Truth-role labeling

The runtime style chain is now explicitly labeled:

- `DESIGN.md` acts as the design contract truth
- `artdeco-tokens.scss` is treated as the active token truth
- `artdeco-global.scss` is documented as the active global ArtDeco runtime entry
- `artdeco-main.css` is documented as a compatibility entry, not canonical truth
- `artdeco-variables.css` and `artdeco-colors.css` are documented as compatibility-only bridges
- `index.scss` is documented as a generic base layer, not a design-truth source

Result:

- future contributors are less likely to implement against the wrong file

### A2. Token conflict documentation

The explicit conflict set is now documented in the proposal, including the items requested during review:

- elevated background conflict
- muted/secondary text conflict
- gold-hover conflict
- warning color conflict
- typography truth conflict
- `--artdeco-font-display` conflict
- `--artdeco-bg-surface` vs `--artdeco-bg-card` naming divergence
- radius model conflict

Result:

- the true drift between compatibility tokens and canonical tokens is now auditable

### B1. Font-loading alignment

The active global ArtDeco font import was changed from:

- `Marcellus + Josefin Sans`

to:

- `Cinzel + Barlow`

The compatibility typography tokens in `artdeco-variables.css` were also redirected so runtime consumers of:

- `--artdeco-font-display`
- `--artdeco-font-sans`
- `--artdeco-font-mono`

resolve toward the approved stack instead of falling back to old fonts or generic serif/sans.

Result:

- the main runtime path no longer loads both old and new ArtDeco font stacks simultaneously
- active `--artdeco-font-display` consumers now resolve toward the approved display stack

### B2. Global base override cleanup

`index.scss` no longer pushes `Helvetica Neue` and a generic system stack onto `html, body, #app`.

It now inherits from ArtDeco token truth and also aligns the scrollbar with the dark ArtDeco baseline instead of the old light scrollbar.

Result:

- the generic base layer no longer fights the ArtDeco runtime contract at the root of the app

### B3. Compatibility-path alignment

The compatibility chain `artdeco-main.css -> artdeco-colors.css -> artdeco-variables.css` remains active for some layout paths, but it now behaves more like a bridge and less like a parallel truth source.

Specific alignment completed:

- `artdeco-main.css` explicitly marked compatibility-only
- `artdeco-variables.css` aligned on typography, warning, hover gold, elevated surface, muted text, radius
- `artdeco-colors.css` warning color aligned away from legacy orange and toward the approved gold warning contract
- `--artdeco-font-body` alias added in `artdeco-tokens.scss` for cleaner compatibility resolution

Result:

- the active compatibility path is less likely to silently override approved runtime truth with older token values

---

## 4. Key Review Findings

### Finding 1: `artdeco-main.css` is active, not archive-only

This was confirmed through its import in:

- `web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue`

Implication:

- `artdeco-variables.css` and `artdeco-colors.css` could not be ignored as “dead legacy”
- compatibility-path alignment was necessary in this batch

### Finding 2: `--artdeco-font-display` was a real runtime risk

The batch plan now records the current audit baseline:

- 87 known consumers of `var(--artdeco-font-display)`

Implication:

- simply removing old Google Fonts imports would have caused visual fallback regressions if the compatibility token had not been redirected

### Finding 3: warning-color drift existed in more than one layer

Confirmed conflict sources included:

- `artdeco-variables.css`
- `artdeco-colors.css`
- `artdeco-tokens.scss`

Implication:

- if only one compatibility file had been aligned, the legacy ArtDeco entry could still surface orange warning UI depending on import path

---

## 5. Validation Performed

Commands run:

```bash
cd web/frontend
npx sass --no-source-map src/styles/artdeco-global.scss /tmp/artdeco-global.css
npx sass --no-source-map src/styles/index.scss /tmp/index.css
```

Observed result:

- both compilations passed
- no structural Sass syntax errors were introduced
- only Sass `@import` deprecation warnings remain

Current batch validation status:

- structural syntax errors: `0`
- type inference errors: not checked in this batch
- PM2 services: not checked in this batch
- E2E: not run in this batch

Reason:

- this batch stayed inside style truth/documentation alignment and did not yet justify a broader runtime verification pass

---

## 6. What Remains Out Of Scope

The following drift remains, but was intentionally not pulled into Phase A+B:

- legacy font references in `theme-dark.scss`, `kline-chart.scss`, `kline-chart-responsive.scss`, `echarts-theme.ts`, and related chart/demo style files
- responsive residue across 50+ media-query branches in 8+ files
- actual component adoption of the new `--ad-*` state-machine tokens
- broader semantic-token normalization across older demo and experimental surfaces
- any visual attempt to re-enable decorative corner markers

These should be treated as later batches, not retroactively expanded into Phase A+B.

---

## 7. Residual Risks

### Low risk

- compatibility headers and documentation could still be ignored by future contributors if follow-up governance is not enforced

### Medium risk

- some older style/theme files outside this batch still embed old font families and may visually drift on isolated pages
- some compatibility aliases still depend on global token availability and should eventually be retired rather than carried forever

### Not yet addressed

- runtime adoption of `--ad-*` component state tokens
- systematic cleanup of responsive residue
- chart-specific typography normalization

---

## 8. Recommended Next Batch

The safest next approved batch is:

1. state-machine token adoption on a narrow surface
2. chip/tag implementation alignment on shared components
3. tooltip/overlay token adoption on shared primitives

Do **not** combine that with responsive cleanup in the same batch.

Responsive residue should remain a separate governance/cleanup track because its scope is much larger and less localized.

---

## 9. Review Decision Template

Recommended decision for this batch:

- approve Phase A+B as completed within scope
- record remaining legacy style files as follow-up scope, not current-batch failure
- move next to component-level token adoption in a new reviewed batch

---

## 10. OpenSpec Extraction

This review is now specific enough to be converted into a controlled OpenSpec change.

### Recommended change focus

The next approved change should be limited to:

1. shared primitive state-machine adoption
2. shared chip / badge / status semantic alignment
3. shared tooltip / overlay token adoption

This next change should explicitly exclude:

- responsive residue cleanup
- broad chart-theme normalization
- route or layout shell rewrites
- decorative corner-marker reintroduction
- wide-scope page-by-page restyling

### Recommended change-id

- `align-artdeco-stateful-primitives-with-design`

### Why this should be the next controlled change

Phase A+B already finished the runtime-truth and typography-truth closure needed before component-level adoption.

The highest-value remaining gap is now:

- runtime adoption of the `--ad-*` state-machine token system on shared primitives

This is controllable because it can be constrained to a narrow reusable surface rather than expanded into page-wide cleanup.

### Recommended implementation boundary

Primary target surfaces:

- `web/frontend/src/components/artdeco/base/ArtDecoButton.vue`
- `web/frontend/src/components/artdeco/base/ArtDecoInput.vue`
- `web/frontend/src/components/artdeco/base/ArtDecoCard.vue`
- `web/frontend/src/components/artdeco/base/ArtDecoBadge.vue` as the canonical shared owner for filter-chip and status-chip semantics
- `web/frontend/src/components/artdeco/business/ArtDecoStatus.vue` only for dot-style operational status presentation

Supporting truth files:

- `DESIGN.md`
- `web/frontend/src/styles/artdeco-tokens.scss`
- `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`
- `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md`
- `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`

### Recommended non-goals

- no new canonical truth outside `DESIGN.md` + `artdeco-tokens.scss`
- no reintroduction of Marcellus / Josefin runtime assumptions
- no migration of every page to the new tokens in one batch
- no deletion of legacy chart/theme style files in this change
- no changes that make `artdeco-pages/**` look like the default routed-page truth

### Recommended verification contract for the next change

Minimum verification should include:

- Sass / style import sanity for touched shared primitives
- `npx vue-tsc --noEmit` for the frontend
- targeted UI verification on at least one page using each changed primitive
- if route, layout, or shared shell behavior changes are introduced, escalate to PM2 + Playwright verification; otherwise keep verification scoped

### OpenSpec task extraction summary

The next change should therefore be expressed as four ordered task groups:

1. document the exact primitive surfaces and semantic ownership before mutation
2. wire `--ad-*` state tokens into shared primitives without changing Element Plus behavior
3. align shared chip / badge / status semantics with the current `DESIGN.md` contract
4. verify that the changed primitives do not reintroduce compatibility-layer truth drift

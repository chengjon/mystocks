# Dashboard MyWeb Audit Report (Merged Quick Mode)

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **Date**: 2026-05-11
> **Skill**: `myweb-audit` v2.1
> **Scope**: `/dashboard`
> **Execution mode**: Quick Mode / code-review-only
> **Canonical owner**: `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
> **Artifact mode**: inline report only, no manifest/findings/approval artifacts created

## Pre-Merge Verification

- Confirmed project-level skill source: `.claude/skills/myweb-audit/SKILL.md`, current major edition `v2.1`.
- Confirmed route truth from `web/frontend/src/router/index.ts`: `/dashboard` routes directly to `ArtDecoDashboard.vue`.
- Confirmed frontend structure exception: `docs/guides/frontend-structure.md` records `/dashboard` as intentionally backed by `views/artdeco-pages/ArtDecoDashboard.vue`.
- Confirmed route-family matrix row: `/dashboard` = `NUM R`, `PROV R`, `FRESH S`, `PART R`, `SEL R`, `EXEC -`, `ENR R`.
- Confirmed runtime process status with `pm2 list`: `mystocks-backend` and `mystocks-frontend` were both `online` during this review.
- Confirmed this file was untracked before merge: no existing committed report was overwritten.

## Audited Files

| File | Role |
| --- | --- |
| `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue` | routed dashboard owner |
| `web/frontend/src/views/artdeco-pages/components/DashboardMarketPanorama.vue` | market panorama child surface |
| `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts` | route-local state and computed shell truth |
| `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.fetchers.ts` | route-local fetch and action logic |
| `web/frontend/src/views/artdeco-pages/styles/ArtDecoDashboard.scss` | route-local dashboard styles |
| `web/frontend/src/components/artdeco/base/ArtDecoCard.vue` | shared card primitive |
| `web/frontend/src/components/artdeco/base/ArtDecoCollapsible.vue` | shared collapsible primitive |
| `web/frontend/src/components/artdeco/charts/ArtDecoChart.vue` | shared chart primitive |
| `web/frontend/src/components/artdeco/core/ArtDecoHeader.vue` | shared page header primitive |

## Route-Truth Position

This review did not identify a new stable `myweb-audit` route-truth family.

The dashboard route has already been covered in prior batches for:

- `numeric-truth`
- `request-provenance-truth`
- `partial-slice-truth`
- `selector-scoped-snapshot-truth`
- `enrichment-and-auxiliary-slice-truth`

Current findings are mostly:

- responsive/accessibility implementation gaps
- functional interaction semantics
- shared ArtDeco primitive risks
- local action truth for the one-click stress-test surface

No update to the main `myweb-audit` skill is recommended from this review.

## Agent Findings

### route-inventory

- `/dashboard` is a canonical route owner, not a secondary inventory candidate.
- Its ArtDeco location is an explicit current exception, not an archive or migration mistake.
- The dashboard support files are route-local canonical support and should move only as a dashboard-family batch if `/dashboard` is relocated later.

### functional-audit

- Flow and pool tabs are operable by click and ArrowLeft/ArrowRight, but their ARIA tab relationship is incomplete.
- The one-click stress-test action is executable, but the result surface does not clearly distinguish a local estimate from verified backend risk analysis.
- Quick navigation links are real route links, but the `<nav>` landmark lacks a descriptive label.

### data-state-audit

- Existing dashboard route-truth protections are substantially present: `DATA/SYNC/REQ/TIME`, primary-slice partial state, capital-flow tab retention, trend slice messages, indicator and monitoring unavailable/stale copy.
- The previous report's broad "zero values render on first load" finding is not accepted as a current High defect for the main dashboard cards after code review, because `DashboardMarketPanorama.vue` guards core panels with loading/error branches.
- `ArtDecoHeader` receives `statusType` from the dashboard but does not declare or render it, so market status semantics are flattened to one visual status style.
- `REQ: N/A` is acceptable under the current v2.1 route-provenance rule for unresolved first load; it should not be reclassified as a defect by itself.

### visual-artdeco-audit

- The page is broadly aligned with the current ArtDeco direction: framed panels, mono numeric treatment, A-share red/green semantics, route-level provenance strip, and dense workbench layout.
- Several non-clickable cards inherit hover lift/glow through shared `ArtDecoCard` defaults or dashboard `hoverable` usage, which can imply false interactivity.
- `transition: all` remains in route-local style rules and shared primitives, which is acceptable as a low-priority maintenance finding but not a release blocker.

### responsive-a11y-audit

- The most significant current defects are accessibility relationship gaps: tab/panel association, collapsible region labelling, chart accessible summaries, and pressure-test result announcements.
- The previous report's `prefers-reduced-motion` finding is superseded for route-local dashboard styles: `ArtDecoDashboard.scss` already includes a reduced-motion block near the end of the file.
- Mobile-width media queries below the supported `1280` desktop baseline remain a maintenance observation, not a supported-breakpoint defect.

## Consolidated Issues

### DA-01 [High] Dashboard tabs do not expose complete ARIA tab relationships

- **Source roles**: functional-audit, responsive-a11y-audit
- **Affected route**: `/dashboard`
- **Location**: `ArtDecoDashboard.vue`, flow tabs around `role="tablist"` and pool tabs around `role="tablist"`
- **Issue type**: accessibility / functional semantics
- **Expected**: each `role="tab"` has a stable `id`, `aria-controls`, selected-state-aware `tabindex`, and each `role="tabpanel"` has a matching `id` and `aria-labelledby`.
- **Actual**: tabs expose `role="tab"` and `aria-selected`, but panel association is incomplete.
- **Primary owner**: `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- **Shared impact**: page-local
- **Fix bucket**: `fix-now`
- **Verification surface**: DOM/a11y inspection plus keyboard tab and ArrowLeft/ArrowRight smoke.

### DA-02 [High] ArtDecoCollapsible content region references an unbound header id

- **Source roles**: responsive-a11y-audit
- **Affected route**: `/dashboard`; potentially all `ArtDecoCollapsible` consumers
- **Location**: `web/frontend/src/components/artdeco/base/ArtDecoCollapsible.vue`
- **Issue type**: accessibility / shared primitive
- **Expected**: the header element that controls the content owns the same `id` referenced by `aria-labelledby`.
- **Actual**: content uses `:aria-labelledby="headerId"`, but the header does not bind `:id="headerId"`.
- **Primary owner**: `web/frontend/src/components/artdeco/base/ArtDecoCollapsible.vue`
- **Shared impact**: shared component change
- **Fix bucket**: `fix-with-shared-impact-review`
- **Verification surface**: component DOM assertion plus dashboard collapsible keyboard smoke.

### DA-03 [High] Chart primitive has no accessible chart name or summary contract

- **Source roles**: responsive-a11y-audit, visual-artdeco-audit
- **Affected route**: `/dashboard`; potentially all `ArtDecoChart` consumers
- **Location**: `web/frontend/src/components/artdeco/charts/ArtDecoChart.vue`
- **Issue type**: accessibility / shared chart primitive
- **Expected**: each chart exposes an accessible name and a short text summary, or a route-owned adjacent summary that screen readers can reach.
- **Actual**: chart canvas container, loading overlay, and empty state exist, but successful charts do not expose an accessible chart name or summary.
- **Primary owner**: `web/frontend/src/components/artdeco/charts/ArtDecoChart.vue`
- **Shared impact**: shared component change
- **Fix bucket**: `fix-with-shared-impact-review`
- **Verification surface**: component DOM/a11y assertion and targeted dashboard chart smoke.

### DA-04 [Medium] Dashboard passes market status type, but ArtDecoHeader ignores it

- **Source roles**: data-state-audit, visual-artdeco-audit
- **Affected route**: `/dashboard`; potentially other `ArtDecoHeader` consumers already passing `status-type`
- **Location**: `web/frontend/src/components/artdeco/core/ArtDecoHeader.vue`
- **Issue type**: status semantics / shared primitive
- **Expected**: `statusType` affects status indicator class, color, or label semantics.
- **Actual**: dashboard passes `:status-type="marketStatusType"`, but the header props only declare `title`, `subtitle`, `showStatus`, and `statusText`.
- **Primary owner**: `web/frontend/src/components/artdeco/core/ArtDecoHeader.vue`
- **Shared impact**: shared component change
- **Fix bucket**: `fix-with-shared-impact-review`
- **Verification surface**: component prop test plus dashboard status class assertion.

### DA-05 [Medium] Non-clickable dashboard cards imply false interactivity

- **Source roles**: functional-audit, visual-artdeco-audit
- **Affected route**: `/dashboard`
- **Location**: dashboard `ArtDecoCard` usage and shared `ArtDecoCard` default `hoverable: true`
- **Issue type**: interaction affordance / visual semantics
- **Expected**: hover lift/glow should be reserved for clickable cards or controls, unless the page family explicitly uses hover only as row inspection feedback.
- **Actual**: several informational cards use `hoverable` without click behavior.
- **Primary owner**: `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- **Shared impact**: page-local if fixed by passing `:hoverable="false"` on non-clickable dashboard cards; shared if changing `ArtDecoCard` default.
- **Fix bucket**: `fix-now` for page-local cleanup; avoid shared default change without a separate review.
- **Verification surface**: visual smoke and no-click affordance review.

### DA-06 [Medium] One-click stress test needs explicit local-estimate and result-update semantics

- **Source roles**: functional-audit, data-state-audit, responsive-a11y-audit
- **Affected route**: `/dashboard`
- **Location**: `ArtDecoDashboard.vue` stress-test card and `useArtDecoDashboard.fetchers.ts` `runOneClickStressTest`
- **Issue type**: local-action-and-execution-truth / accessibility
- **Expected**: result copy clearly states that the output is a local estimate from currently loaded page data, and screen readers are notified when the result changes.
- **Actual**: the helper copy mentions local estimation before execution, but the result metrics themselves can read as verified risk output and do not live-announce changes.
- **Primary owner**: `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- **Shared impact**: page-local
- **Fix bucket**: `fix-now`
- **Verification surface**: click smoke, DOM copy assertion, `aria-live` inspection.

### DA-07 [Low] Low-width media branches remain below the supported desktop baseline

- **Source roles**: responsive-a11y-audit
- **Affected route**: `/dashboard`
- **Location**: `ArtDecoDashboard.scss`
- **Issue type**: desktop redline maintenance observation
- **Expected**: required responsive checks focus on `1920`, `1440`, and `1280`; below-1280 rules should not drive product behavior unless explicitly retained as legacy defensive layout.
- **Actual**: route-local SCSS still includes sub-1280/mobile-like branches.
- **Primary owner**: `web/frontend/src/views/artdeco-pages/styles/ArtDecoDashboard.scss`
- **Shared impact**: page-local
- **Fix bucket**: `defer`
- **Verification surface**: 1280/1440/1920 screenshot pass before any cleanup.

### DA-08 [Low] Route-local styles still use broad `transition: all`

- **Source roles**: visual-artdeco-audit, responsive-a11y-audit
- **Affected route**: `/dashboard`
- **Location**: `ArtDecoDashboard.scss`
- **Issue type**: performance / maintainability
- **Expected**: transitions list concrete properties such as `border-color`, `box-shadow`, `transform`, `color`, and `opacity`.
- **Actual**: several route-local rules still use `transition: all`.
- **Primary owner**: `web/frontend/src/views/artdeco-pages/styles/ArtDecoDashboard.scss`
- **Shared impact**: page-local for route styles
- **Fix bucket**: `defer`
- **Verification surface**: visual regression smoke after style cleanup.

## Superseded Or Downgraded Items From Earlier Draft

| Prior id | Prior finding | Current disposition |
| --- | --- | --- |
| D-01 | zero-initialized dashboard data renders before first load | Superseded as a High route-truth finding. Core `DashboardMarketPanorama` panels are guarded by loading/error branches. Re-check only through live-audit if a specific first-load path shows zero cards. |
| D-03 | `REQ: N/A` looks like real data | Downgraded. Under v2.1 request-provenance truth, unresolved first load may degrade to `N/A`; this is acceptable unless live copy proves user confusion or optimistic success. |
| R-01 | missing `prefers-reduced-motion` | Superseded. `ArtDecoDashboard.scss` includes a reduced-motion block for key dashboard hover transitions. |
| V-02 | decorative SCSS comments are a visual issue | Dropped from current issue list. This is maintainability noise, not a page audit defect. |
| V-03 | `QUANTIX` repeated | Dropped pending live visual proof. Static code review only confirmed title usage, not harmful duplication in the rendered route. |
| V-04 | alert/note shared style block duplication | Dropped. The selectors intentionally share one scoped declaration block; no user-facing defect. |
| F-02 | stock-pool tabs have no real API | Kept as background dependency only. Current copy explicitly says the real interface is not connected, so this is not a false live-truth defect. |
| D-02 | market sentiment uses industry breadth | Background product/data decision. Not promoted without route contract proof that the label promises full-market stock breadth. |

## Summary

| Severity | Count | Issues |
| --- | ---: | --- |
| Blocking | 0 | - |
| High | 3 | DA-01, DA-02, DA-03 |
| Medium | 3 | DA-04, DA-05, DA-06 |
| Low | 2 | DA-07, DA-08 |

## Shared Impact Candidates

| Issue | Primary owner | Impact basis | Decision timing |
| --- | --- | --- | --- |
| DA-02 | `ArtDecoCollapsible.vue` | shared component | pre-repair shared-impact review |
| DA-03 | `ArtDecoChart.vue` | shared chart primitive | pre-repair shared-impact review |
| DA-04 | `ArtDecoHeader.vue` | shared header primitive | pre-repair shared-impact review |

## Recommended Repair Order

1. Fix page-local tab ARIA relationships in `ArtDecoDashboard.vue`.
2. Add shared-impact approval package for `ArtDecoCollapsible`, `ArtDecoChart`, and `ArtDecoHeader` before editing shared primitives.
3. Clean up dashboard-local false hover affordances without changing `ArtDecoCard` defaults.
4. Clarify one-click stress-test result semantics and add `aria-live`.
5. Defer low-width media cleanup and `transition: all` tightening until a visual regression pass is scheduled.

## Verification Notes

This report is code-review-only. Before closing any repair batch, run focused checks for the approved repair scope:

- component/unit assertions for changed shared primitives
- dashboard logic regression where route state is touched
- browser smoke for `/dashboard` at required desktop widths: `1920`, `1440`, `1280`
- keyboard/a11y smoke for tabs, collapsibles, charts, and stress-test result updates
- artifact validation only if a formal `myweb-audit` manifest/findings/approval package is created

## Residual Risk

- No live browser audit was performed in this merge pass.
- No network interception or `success:false` route-state transition was re-tested.
- The worktree contains broad unrelated dirty state, so this report should not be used as a repository-wide quality verdict.

*Dashboard MyWeb Audit Report v2.1 Quick Mode | 2026-05-11 | merged code-review-only*

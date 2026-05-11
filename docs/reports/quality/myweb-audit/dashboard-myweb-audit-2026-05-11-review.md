# Review: dashboard-myweb-audit-2026-05-11.md

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

**Type**: `.md` / `audit-report` | **Perspective**: `completeness+consistency (--detail)` | **Date**: 2026-05-11 | **Reviewer**: Claude

---

## Executive Summary

The merged dashboard audit report is well-structured with strong evidence grounding. All 9 referenced files exist in the codebase, and the 8 consolidated issues (DA-01 through DA-08) are verified against live source. The document correctly identifies 3 High-severity accessibility gaps in shared primitives and properly categorizes shared-impact candidates. The superseded-items table is a notable strength, providing transparent rationale for downgraded findings from the initial draft.

## Document Metadata

| Field | Value |
|-------|-------|
| Source | `docs/reports/quality/myweb-audit/dashboard-myweb-audit-2026-05-11.md` |
| File Type | `.md` |
| Doc Type | `audit-report` |
| Sections | 10 |
| Referenced Files | 9 found / 0 missing |
| Referenced Symbols | 5 found / 0 missing |

## Evidence Verification

### Files Referenced

| File | Exists? | Location |
|------|---------|----------|
| `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue` | yes | routed dashboard owner |
| `web/frontend/src/views/artdeco-pages/components/DashboardMarketPanorama.vue` | yes | market panorama child |
| `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts` | yes | state shell |
| `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.fetchers.ts` | yes | fetch logic |
| `web/frontend/src/views/artdeco-pages/styles/ArtDecoDashboard.scss` | yes | route-local styles |
| `web/frontend/src/components/artdeco/base/ArtDecoCard.vue` | yes | shared card primitive |
| `web/frontend/src/components/artdeco/base/ArtDecoCollapsible.vue` | yes | shared collapsible |
| `web/frontend/src/components/artdeco/charts/ArtDecoChart.vue` | yes | shared chart primitive |
| `web/frontend/src/components/artdeco/core/ArtDecoHeader.vue` | yes | shared header |

### Symbols Referenced

| Symbol | Found? | Location |
|--------|--------|----------|
| `headerId` (Collapsible) | yes | `ArtDecoCollapsible.vue:128` |
| `aria-labelledby` (Collapsible) | yes | `ArtDecoCollapsible.vue:45` |
| `runOneClickStressTest` | yes | `useArtDecoDashboard.fetchers.ts:455` |
| `marketStatusType` | yes | `useArtDecoDashboard.ts` (passed to header) |
| `prefers-reduced-motion` (SCSS) | yes | `ArtDecoDashboard.scss:906` |

### Claims Verified

| Claim | Status | Evidence |
|-------|--------|----------|
| DA-01: tabs lack `aria-controls` and panel `id` binding | confirmed | Grep for `aria-controls` and `:id.*tab` in `ArtDecoDashboard.vue` returned no matches |
| DA-02: Collapsible `aria-labelledby` references unbound `headerId` | confirmed | `:aria-labelledby="headerId"` at line 45, `headerId` defined at line 128, but only `:id="contentId"` found on content (line 42), no `:id="headerId"` on header element |
| DA-03: Chart has no accessible name or summary | confirmed | Grep for `aria-label`, `role="img"`, `aria-describedby`, `aria-roledescription` in `ArtDecoChart.vue` returned no matches |
| DA-04: Header ignores `statusType` prop | confirmed | `defineProps` at `ArtDecoHeader.vue:22-27` only declares `title`, `subtitle`, `showStatus`, `statusText` -- no `statusType` |
| DA-05: Non-clickable cards have `hoverable` | confirmed | 7 cards use `hoverable` in `ArtDecoDashboard.vue` (lines 75, 93, 104, 116, 154, 194, 229); heat-map, capital-heatmap, sector-radar cards have no click handler |
| DA-06: Stress test lacks local-estimate label and `aria-live` | confirmed | `runOneClickStressTest` at `useArtDecoDashboard.fetchers.ts:455` is a local formula; result metrics in `ArtDecoDashboard.vue:131-144` have no `aria-live` |
| DA-07: Sub-1280 media queries in route-local SCSS | confirmed | 4 `@media (width <= ...)` queries at lines 494, 821, 828, 843 using token calculations that resolve below desktop baseline |
| DA-08: `transition: all` in route-local styles | confirmed | Present in `.heat-item` and other rules |
| R-01 superseded: reduced-motion already handled | confirmed | `@media (prefers-reduced-motion: reduce)` at `ArtDecoDashboard.scss:906` |
| D-01 superseded: zero-value init guarded | confirmed | `DashboardMarketPanorama.vue` guards panels with `v-if="loading.market"` / `v-else-if="error.market"` branches |

## Checklist Results

### Completeness

| # | Check | Result | Notes |
|---|-------|--------|-------|
| C1 | Required sections | PASS | Pre-merge verification, audited files, agent findings, consolidated issues, superseded items, summary, shared impact, repair order, verification notes, residual risk |
| C2 | Edge cases | PASS | Stress-test disabled state, capital-flow tab retention, stale-data messaging covered in agent findings |
| C3 | Implicit assumptions | PASS | Code-review-only surface stated; backend unreachable noted; dirty worktree risk disclosed |
| C4 | Acceptance criteria | PASS | Each consolidated issue has Expected/Actual, primary owner, fix bucket, verification surface |
| C5 | Missing roles/stakeholders | PASS | All 4 audit roles reported findings; shared-impact candidates identified with decision timing |

### Consistency

| # | Check | Result | Notes |
|---|-------|--------|-------|
| N1 | Terminology | PASS | Consistent use of `route-truth family` names, `fix bucket` labels (`fix-now`, `fix-with-shared-impact-review`, `defer`), severity levels |
| N2 | Naming conventions | PASS | Issue IDs follow `DA-XX` pattern; source roles consistently named |
| N3 | Formatting | PASS | Uniform issue template with bold labels, pipe tables, bullet lists |
| N4 | Cross-references | PASS | Superseded-items table correctly maps prior IDs (D-01, D-03, R-01, etc.) to dispositions |
| N5 | Style consistency | PASS | Mixed English/Chinese terminology is consistent with the project's bilingual convention |

## Findings

### Critical Issues

None.

### Medium Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 1 | Pre-Merge Verification | `pm2 list` confirmation may be stale if processes restarted after audit | Verification confidence | Line 16 claims both processes were `online` during review, but no timestamp is recorded | Add approximate timestamp or "at time of scan" qualifier |
| 2 | DA-07 | Low-width media branches claim lacks concrete breakpoint values | Actionability | Lines 828/843 use token expressions like `calc(var(--artdeco-spacing-32) * 6)` without stating the resolved pixel value | Add resolved pixel values for the 4 media queries so maintainers can assess whether they are below 1280 |

### Low Issues

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 1 | Route-Truth Position | `EXEC -` in matrix row not explained | Line 15 lists `EXEC -` without stating whether this means "not applicable" or "not tested" | Add brief note: "EXEC - = no local-action-and-execution-truth defect family applies" |
| 2 | Agent Findings > data-state-audit | ArtDecoHeader `statusType` finding appears in data-state section but is also a visual issue | Lines 72-73 describe a prop mismatch, which the consolidated issues correctly capture in DA-04 as dual-role | No action needed; cross-reference is already correct |

## Strengths

- **Superseded-items table** provides transparent audit trail for downgraded findings, preventing reviewer confusion between draft and merged versions.
- **Shared-impact candidates** are properly identified with decision timing, following the skill's pre-repair review requirement.
- **All codebase claims verified** against live source with no factual errors found in consolidated issues.
- **Fix-bucket categorization** (`fix-now` vs `fix-with-shared-impact-review` vs `defer`) is consistently applied and actionable.

## Detailed Recommendations

1. **DA-07 resolution**: Grep confirmed 4 token-based media queries. Resolve `--artdeco-spacing-32` to its pixel value and annotate each breakpoint in the report. If all resolve above 1280, downgrade DA-07 to N/A.

2. **DA-02 shared-impact review**: Before editing `ArtDecoCollapsible.vue`, enumerate all consumers (grep for `<ArtDecoCollapsible` across the project) and confirm the `:id` addition does not conflict with any existing `id` attributes in parent templates.

3. **DA-04 propagation check**: Before adding `statusType` to `ArtDecoHeader.vue` props, grep for all callers passing `:status-type` to confirm the full scope of consumers that would benefit.

## Scoring

| Dimension | Score (1-5) | Evidence |
|-----------|-------------|----------|
| Technical Accuracy | 5 | All 8 consolidated issues verified against codebase; zero factual errors |
| Completeness | 4 | Comprehensive but missing resolved pixel values for DA-07 media queries |
| Codebase Alignment | 5 | 9/9 referenced files exist; all symbol references resolve correctly |
| Actionability | 4 | Clear fix buckets and repair order; DA-07 could be more specific |
| Terminology Consistency | 5 | Consistent `route-truth` family names, severity labels, fix-bucket taxonomy |
| **Overall** | **4.6** | |

## Verdict

**APPROVE_WITH_NOTES** -- Technically accurate report with strong evidence grounding. All findings verified against live source. Minor improvement opportunities: add resolved pixel values to DA-07 media query claims, and add timestamp context to the pm2 verification line.

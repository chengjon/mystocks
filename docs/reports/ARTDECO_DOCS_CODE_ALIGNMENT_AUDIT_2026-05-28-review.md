# Review: ARTDECO_DOCS_CODE_ALIGNMENT_AUDIT_2026-05-28.md

**Type**: `.md` / `proposal` (audit) | **Perspective**: completeness, consistency, feasibility, architecture | **Date**: 2026-05-28 | **Reviewer**: Claude

---

## Executive Summary

The audit's core findings (component count off-by-one, missing 5th route exception, empty directories) are accurate and well-supported by the live codebase. However, the audit itself contains a filename error (`tokens.scss` vs actual `artdeco-tokens.scss`), an internal numeric inconsistency in its header summary, and paraphrased evidence blocks. None of these undermine the audit's correction recommendations, but they reduce confidence in the audit's self-consistency.

## Document Metadata

| Field | Value |
|-------|-------|
| Source | `docs/reports/ARTDECO_DOCS_CODE_ALIGNMENT_AUDIT_2026-05-28.md` |
| File Type | `.md` |
| Doc Type | `proposal` (audit) |
| Sections | 6 |
| Referenced Files | 15 found / 0 missing |
| Referenced Symbols | 12 found / 0 missing |

## Evidence Verification

### Files Referenced

| File | Exists? | Location |
|------|---------|----------|
| `docs/guides/web/ARTDECO_MASTER_INDEX.md` | yes | as stated |
| `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md` | yes | as stated |
| `web/frontend/ARTDECO_COMPONENTS_CATALOG.md` | yes | as stated |
| `docs/api/ArtDeco_System_Architecture_Summary.md` | yes | as stated |
| `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md` | yes | as stated |
| `docs/reports/ARTDECO_V3_COMPLETE_SUMMARY.md` | yes | as stated |
| `docs/guides/ARTDECO_FINTECH_UNIFIED_SPEC.md` | yes | as stated |
| `docs/api/ARTDECO_SYSTEM_ARCHITECTURE_SUMMARY.md` | yes | as stated |
| `web/frontend/src/router/index.ts` | yes | as stated |
| `web/frontend/src/styles/tokens.scss` | **no** | actual file: `web/frontend/src/styles/artdeco-tokens.scss` |
| `web/frontend/src/components/artdeco/base/ArtDecoBadge.vue` | yes | as stated (audit doesn't specify layer, but file is in `base/`) |
| `web/frontend/src/components/artdeco/core/ArtDecoHeader.vue` | yes | as stated |
| `web/frontend/src/components/artdeco/trading/ArtDecoCollapsibleSidebar.vue` | yes | as stated |
| `web/frontend/src/views/artdeco-pages/components/DashboardMarketPanorama.vue` | yes | as stated |
| `web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue` | yes | as stated |

Uncovered docs (Section 6): all 7 exist and are readable. Confirmed.

### Functions/Classes Referenced

| Symbol | Found? | Location |
|--------|--------|----------|
| `useHeaderSummary` | yes | `web/frontend/src/composables/useHeaderSummary.ts` |
| `useArtDecoDashboard` | yes | `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts` |
| `ArtDecoLayoutEnhanced` | yes | `web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue` |
| `pageConfig.ts` | yes | `web/frontend/src/config/pageConfig.ts` + `web/frontend/src/types/pageConfig.ts` |

### Claims Verified

| Claim | Status | Evidence |
|-------|--------|----------|
| 8 ArtDeco documents listed | confirmed | all 8 files exist via `test -f` |
| `artdeco/` components total = 73 | confirmed | `find web/frontend/src/components/artdeco -name '*.vue' \| wc -l` = 73 |
| Per-layer counts: base=14, core=14, business=11, charts=9, trading=13, advanced=10, specialized=2 | confirmed | each verified individually with `find` |
| `views/artdeco-pages/` total = 90 (audit corrects 89) | confirmed | `find web/frontend/src/views/artdeco-pages -name '*.vue' \| wc -l` = 90 |
| `components/` under artdeco-pages = 24 (audit corrects 23) | confirmed | `find .../components -name '*.vue' \| wc -l` = 24 |
| Route exceptions = 5 (audit corrects 4) | confirmed | 5 `artdeco-pages` imports in `router/index.ts` at lines 35, 147, 171, 277, 348 |
| 4 empty directories (ml-tabs, market, risk, trade) | confirmed | all contain 0 `.vue` files |
| ArtDecoBadge 9 variants | confirmed | `default/active/neutral/gold/profit/loss/holding/pending/warning` in `base/ArtDecoBadge.vue:13-21` |
| Fonts Cinzel + Barlow + JetBrains Mono at lines 29-31, 108-110 | confirmed | in `artdeco-tokens.scss` (not `tokens.scss`) |
| Spacing 13 levels at lines 344-358 | confirmed | 13 numbered scale entries in `artdeco-tokens.scss` (lines 346-358) |
| `--artdeco-transition-quick = 200ms` / `base = 400ms` | confirmed | `artdeco-tokens.scss:427-428` |
| `--artdeco-glow-profit` / `--artdeco-glow-loss` | confirmed | `artdeco-tokens.scss:417-418` |
| ArtDecoHeader has 0 "MyStocks ArtDeco" text | confirmed | `grep 'MyStocks ArtDeco' ArtDecoHeader.vue` = 0 |
| `--ad-*` token count = 85 | confirmed (scoped) | 85 in `artdeco-tokens.scss`; 195 across all `.vue/.scss/.css` |
| Summary "2 directory omissions" | **contradicted** | Section 4.3 lists 4 empty directories |

## Checklist Results

14 items PASS. FAIL and N/A rows shown below.

### Architecture

| # | Check | Result | Notes |
|---|-------|--------|-------|
| A6 | Terminology consistency | FAIL | Audit uses `tokens.scss` (3 occurrences) but the actual file is `artdeco-tokens.scss`. All line numbers are correct. |
| A8 | Implementation surface precision | FAIL | Evidence blocks in Section 3.1 show paraphrased grep output with fabricated inline comments (`# /dashboard`, `# /strategy/signals`) that do not appear in the actual `router/index.ts`. Line numbers are correct. |
| A9 | Named entities verified | PASS | All referenced .vue files, .md files, composables, and config files exist. |

### Completeness

| # | Check | Result | Notes |
|---|-------|--------|-------|
| C1 | Required sections | PASS | All expected audit sections present: file list, overall assessment, per-doc analysis, cross-doc issues, recommendations, uncovered docs. |
| C2 | Edge cases | FAIL | Header summary claims "2 directory omissions" but Section 4.3 documents 4 empty directories. Internal numeric inconsistency. |
| C3 | Implicit assumptions | PASS | Audit methodology and truth source (`web/frontend/`) stated explicitly. |
| C4 | Acceptance criteria | PASS | P0/P1/P2/P3 priority classification is clear and actionable. |
| C5 | Missing roles/stakeholders | N/A | Audit document, not a system design. |

### Consistency

| # | Check | Result | Notes |
|---|-------|--------|-------|
| N1 | Terminology | FAIL | `tokens.scss` vs `artdeco-tokens.scss` filename inconsistency. |
| N3 | Formatting | PASS | Uniform table/list/code-block usage across all sections. |
| N4 | Cross-references | PASS | All section references (e.g., "Section 4.1", "Section 6.3") resolve correctly. |
| N5 | Style consistency | PASS | Formal Chinese technical writing throughout. |

### Feasibility

| # | Check | Result | Notes |
|---|-------|--------|-------|
| F1 | Technical risk | PASS | Identified root cause (`DashboardMarketPanorama.vue` omission) is specific and verifiable. |
| F2 | Dependency availability | PASS | All referenced files and functions confirmed in codebase. |
| F3 | Timeline realism | N/A | No timeline estimates in audit. |
| F5 | Rollback plan | PASS | All recommendations are additive corrections (add entry, update count); no destructive changes. |

## Findings

### Critical Issues

None.

### Medium Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 1 | Sections 3.1, 3.2, 3.4 | Filename error: `tokens.scss` referenced 3 times but actual file is `artdeco-tokens.scss` | Misleading; readers may search for a non-existent file | Verified via `find web/frontend -name 'tokens.scss'` = 0 results; `find web/frontend -name 'artdeco-tokens.scss'` = 1 result. Document checked: lines 68, 69, 131 all say `tokens.scss`. No other section corrects the filename. | Replace all 3 occurrences of `tokens.scss` with `artdeco-tokens.scss` |
| 2 | Header (line 6) vs Section 4.3 | Summary says "2 directory omissions" but Section 4.3 lists 4 empty directories (ml-tabs, market, risk, trade) | Internal inconsistency undermines audit credibility | Header line 6: `3 处数量偏差 + 1 处路由例外遗漏 + 2 处目录遗漏`. Section 4.3 table has 4 rows. Both checked in source document. | Update header to `4 处目录遗漏` or clarify that "2" refers to categories rather than individual directories |

### Low Issues

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 1 | Section 3.1 (evidence block) | Grep output shows fabricated inline comments (`# /dashboard` etc.) not present in actual file | Actual line 35: `component: () => import('@/views/artdeco-pages/ArtDecoDashboard.vue'),`. Audit shows: `ArtDecoDashboard.vue          # /dashboard`. No section explains this is paraphrased. | Use verbatim grep output, or add a note that evidence is abbreviated |
| 2 | Section 3.2 (line 72) | `--ad-*` "85 references" scope is ambiguous | 85 matches in `artdeco-tokens.scss` alone; 195 across all `.vue/.scss/.css`. Audit doesn't state the scope. Checked document: no scope qualification exists. | Clarify scope: "85 definitions in `artdeco-tokens.scss`" |
| 3 | Section 5 (P2/P3 table) | E2E baseline (2026-04-19) flagged as stale but no deadline or trigger for re-verification | Document line 80: `E2E 验证基线 (10/10 stable) | ⚠ 2026-04-19 快照，需重验证`. P2 recommendation says "标注" (annotate) but not when to re-run. | Add a concrete trigger (e.g., "re-verify before next ArtDeco doc update") |

## Strengths

- Root cause analysis is precise: the `DashboardMarketPanorama.vue` omission is traced to specific count discrepancies across multiple documents, with a clear causal chain.
- Cross-document impact analysis (Section 4) correctly maps each finding to all affected documents, preventing partial fixes.
- Priority classification (P0 through P3) is well-calibrated — factual count errors are P0, route exceptions are P1, cosmetic fixes are P2/P3.
- Per-layer component counts (73 reusable assets) are fully verified against the live codebase with zero discrepancies.

## Recommendations

1. **Fix the filename first**: The `tokens.scss` → `artdeco-tokens.scss` correction affects 3 lines and undermines the audit's credibility as a "codebase truth" document. This should be treated as a self-audit P0 fix before applying the audit's recommendations to other documents.
2. **Reconcile the summary count**: Decide whether "2 处目录遗漏" was meant as 2 categories (undocumented empty dirs + undocumented ml-tabs/) or a simple counting error, and update accordingly.
3. **Use verbatim evidence**: Paraphrased grep output with added comments could confuse readers who try to reproduce the verification. Either use exact output or clearly mark it as "abbreviated for readability."
4. **Scope token counts explicitly**: The `--ad-*` count of 85 is correct for `artdeco-tokens.scss` definitions, but without scope it reads as a codebase-wide count. Adding "in `artdeco-tokens.scss`" would prevent misinterpretation.

## Scoring

| Dimension | Score (1-5) | Evidence |
|-----------|-------------|----------|
| Technical Accuracy | 4 | Core findings verified correct; `tokens.scss` filename error is the only factual mistake |
| Completeness | 4 | All 8 documents audited; 7 uncovered docs listed; summary count inconsistency is minor gap |
| Codebase Alignment | 5 | All component counts, file paths, route references, and symbol names verified against live code |
| Actionability | 5 | P0-P3 table with specific files, sections, and exact corrections needed |
| Terminology Consistency | 3 | `tokens.scss` vs `artdeco-tokens.scss`; "2" vs "4" directory count; paraphrased evidence |
| **Overall** | **4.0** | |

## Verdict

**APPROVE_WITH_NOTES** — The audit's recommendations are correct and actionable. Its own self-consistency issues (filename error, summary count mismatch, paraphrased evidence) should be fixed before distributing, as they could mislead consumers who trust the audit's evidence trails.

# Phase 5: Composables Disposition - Research

**Date:** 2026-04-08
**Phase:** 05-composables-disposition

## Research Questions

### Q1: Where in STANDARDS.md should the composable convention be added?

**Finding:** Section 二.1 (前端开发红线 / Frontend Development Red Lines), lines 69-73.
- Format: `* **Rule name**: Description` — bold-name bullet points
- Current rules (4): 路由纯净度, 路径语义化, 禁止硬编码样式, TRACE_ID显化
- No existing composable convention — this is a new addition
- Insert after line 73 (TRACE_ID rule), before section 二.2 (后端开发红线)

### Q2: What does COMPOSABLES-AUDIT.md currently have?

**Finding:** `web/frontend/COMPOSABLES-AUDIT.md` contains:
- 17-file inventory table with columns: #, File, Consumers, Consumer Paths, Classification
- 15/17 classified "Keep view-local", 2 classified "Extraction candidate"
- Summary section stating "Do NOT bulk-move"
- **Missing:** No "Final Disposition" section — needs to be added with per-file decisions and the audited-exception flag for tradingDashboardActions.ts

### Q3: What is the traceability state of COMP-01/02/03?

**Finding:** `.planning/REQUIREMENTS.md`:
- COMP-01/02/03 all marked `- [ ]` (unchecked/Pending)
- All mapped to Phase 5 in traceability table
- STRU-04 in PROJECT.md is under "Active" (not yet Validated)
- After phase execution: check boxes → `[x]`, traceability Status → "Complete", PROJECT.md Active → Validated

### Q4: Are there existing composable patterns to be consistent with?

**Finding:** No composable conventions documented anywhere in the project. The `src/composables/` directory has ~35 shared composables using `@/composables/xxx` alias imports, while view-local composables use `./composables/xxx` relative imports. The convention documentation will be the first formal rule of its kind.

## Key Findings

1. **STANDARDS.md insertion point:** Line 73, section 二.1, after existing 4 frontend rules. Use same `* **Rule name**: Description` format.
2. **COMPOSABLES-AUDIT.md needs:** A "Final Disposition" section added at the end with per-file decisions and exception flagging.
3. **Traceability updates:** 3 checkboxes in REQUIREMENTS.md, 1 traceability table update, 1 PROJECT.md move (Active → Validated).
4. **No file moves:** Both extraction candidates stay in place. Zero import changes needed. Build verification is a confirmation step, not a modification step.

## Recommendations

**Plan structure:** Single wave with 3 tasks:
1. Add composable convention to STANDARDS.md (二.1 section)
2. Update COMPOSABLES-AUDIT.md with final dispositions + exception flag
3. Update traceability (REQUIREMENTS.md + PROJECT.md) + verify build

All 3 tasks are independent and could run in parallel, but Task 3 logically comes last as it "closes" the phase.

## RESEARCH COMPLETE

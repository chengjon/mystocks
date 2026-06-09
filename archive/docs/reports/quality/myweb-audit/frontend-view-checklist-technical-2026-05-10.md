# Frontend View Redundant Page Review Checklist: `views/technical`

Date: 2026-05-10

Scope:
- `web/frontend/src/views/technical/TechnicalAnalysis.vue`

Related non-view assets observed in this batch:
- `web/frontend/src/views/technical/styles/TechnicalAnalysis.scss`
- `web/frontend/src/views/technical/composables/useTechnicalAnalysis.ts`

Purpose:
- Apply the frontend view governance redundant-page checklist to the nested legacy technical-analysis page.
- Distinguish the static-shell view decision from adjacent legacy style/composable assets.
- Prevent archive approval while direct specs and function-tree references still describe this page as a legacy technical-analysis / troubleshooting surface.

## Current Truth Inputs

Runtime truth:
- `web/frontend/src/router/index.ts` does not dynamically import `views/technical/TechnicalAnalysis.vue`.
- Current verified technical-analysis surfaces are `/detail/graphics/:symbol`, `/market/technical`, and `/data/indicator`.

Historical governance evidence:
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/technical-analysis-module-legacy-static-shell-truth-audit.md`
- `docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-18-audit.md`
- `docs/reports/quality/myweb-audit/audit-20260426-02/secondary-line-progress-summary.md`

Guard and reference evidence:
- `web/frontend/src/views/technical/__tests__/TechnicalAnalysis.spec.ts`
- `web/frontend/tests/unit/config/technical-web3-style-support.spec.ts`
- `web/frontend/tests/unit/config/console-log-cleanup-batch-23.spec.ts`
- `docs/FUNCTION_TREE.md`

## Page-Level Classification

| Page | Current implementation | Route status | Guard status | Reusable assets | Successor / owner | Lifecycle status | Archive decision |
|---|---|---:|---:|---|---|---|---|
| `views/technical/TechnicalAnalysis.vue` | Honest static shell | `dead` | `spec-guarded` | No dynamic business asset remains in the view | No one-to-one owner; handoff to `/detail/graphics/600519`, `/market/technical`, `/data/indicator` | `candidate-review` | Not archive-approved |

## Redundant-Page Checklist

### `TechnicalAnalysis.vue`

- Not menu referenced: pass.
- Not router dynamic import referenced: pass.
- Not active runtime owner: pass.
- Hidden reference check: incomplete; `TechnicalAnalysis.spec.ts`, `technical-web3-style-support.spec.ts`, historical audit docs, and `docs/FUNCTION_TREE.md` still reference the page.
- Function-tree status: legacy technical-analysis and troubleshooting surface, not yet formally retired.
- Reusable asset review: the view no longer contains reusable chart, indicator, signal, batch-calculation, selector, or verified technical-analysis logic after static-shell conversion.
- Successor proof: partial only; the shell points to multiple verified surfaces because no one-to-one canonical owner exists.
- Archive eligibility: blocked by direct specs, function-tree references, and lack of direct successor.

Decision: keep as `candidate-review`; do not mark as `archive-candidate`.

## Related Asset Notes

- `views/technical/styles/TechnicalAnalysis.scss` is intentionally still covered by `technical-web3-style-support.spec.ts`; it is not approved for cleanup by this view checklist.
- `views/technical/composables/useTechnicalAnalysis.ts` is covered by `console-log-cleanup-batch-23.spec.ts`; it requires a separate composable/function-tree review before any move or archive decision.
- The root-level `web/frontend/src/views/TechnicalAnalysis.vue`, advanced-analysis technical child pages, and ArtDeco technical pages are separate legacy surfaces and are not covered by this checklist.

## Batch Conclusion

`views/technical/TechnicalAnalysis.vue` is a retired static shell, but it is not archive-approved. Before archive eligibility, the project must either retire the legacy technical-analysis function-tree node or migrate it to a clearly named canonical successor, then migrate or remove the direct specs that intentionally guard the static-shell state.

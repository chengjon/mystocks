# Example Audit Run

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

Use this reference when you want a concrete execution pattern instead of only abstract rules.

## Quick Mode Example

Request shape:

`Check /market/overview for obvious interaction and layout issues. Do not write files.`

Recommended execution:

1. Resolve canonical entry from router truth.
2. Use `live-audit` if the frontend is reachable and browser tooling is available.
3. Run the audit dimensions inline:
   - functional
   - data/state
   - visual/ArtDeco
   - responsive/a11y
4. Consolidate findings inline.
5. Ask the user which findings to repair before editing.
6. If the user only wants a check, stop after reporting.

Expected output shape:

```md
# Quick Audit: /market/overview

## Canonical Entry
- web/frontend/src/views/market/MarketOverview.vue

## Findings
- [High] Filter reset leaves stale rows visible after controls clear.
- [Medium] Table toolbar spacing collapses at 1280 width.
- [Low] Empty state copy is technically correct but visually weak.

## Shared Impact
- Candidate: yes
- Basis: shared filter composable
- Related pages to spot-check: /market/watchlist

## Recommendation
- Fix now: stale reset behavior
- Defer: visual empty-state polish

## Verification Surface
- live-audit
```

Quick Mode defaults:

- no manifest file
- no batch report
- no closeout checklist
- inline-only unless the user asks for files

## Full Mode Example

Request shape:

`Audit the market pages in batches and repair approved frontend issues. Write files.`

Sample batch:

- batch id: `market-batch-01`
- pages:
  - `/market/overview`
  - `/market/watchlist`
  - `/market/heatmap`

Recommended execution:

1. Create manifest:
   - `docs/reports/quality/myweb-audit/audit-20260425-01/manifests/market-batch-01-manifest.yaml`
2. Run `route-inventory`.
3. Run the 4 audit roles in parallel when capacity allows.
4. Write raw findings:
   - `findings/market-batch-01-raw-findings.yaml`
5. Merge and deduplicate:
   - `findings/market-batch-01-merged-findings.yaml`
6. Mark shared-impact candidates.
7. Present merged findings to the user for approval.
8. Update manifest `repair_approval`.
9. Apply only approved fixes.
10. Run focused verification.
11. Write per-page report(s), batch report, and closeout.

Recommended artifact set:

```text
docs/reports/quality/myweb-audit/audit-20260425-01/
├── manifests/
│   └── market-batch-01-manifest.yaml
├── findings/
│   ├── market-batch-01-raw-findings.yaml
│   └── market-batch-01-merged-findings.yaml
├── pages/
│   ├── market-market-overview-audit.md
│   ├── market-market-watchlist-audit.md
│   └── market-market-heatmap-audit.md
├── batches/
│   └── market-batch-01-audit.md
└── closeout/
    └── audit-20260425-01-closeout.md
```

## Full Mode Approval Example

Example approval summary to record in the manifest:

```yaml
repair_approval:
  status: partial
  approved_findings:
    - market-overview-functional-001
    - market-watchlist-data-state-002
  deferred_findings:
    - market-heatmap-visual-001
```

## Code-Review-Only Example

Use this fallback when the app or browser surface is unavailable.

Expected differences:

- set manifest `execution_surface: code-review-only`
- set `verification_strategy: code-review-only`
- mark each finding `verification_surface: code-review-only`
- keep verification notes explicit about the missing live surface

Example finding note:

```yaml
verification_surface: code-review-only
verification:
  required: true
  complete: false
  notes: Browser automation unavailable; interaction behavior inferred from component code only.
```

## Practical Guidance

- Quick Mode is for fast inspection and decision support.
- Full Mode is for resumable, repair-oriented audit work.
- Do not create file artifacts unless the user asked for files or the audit needs resumable structure.

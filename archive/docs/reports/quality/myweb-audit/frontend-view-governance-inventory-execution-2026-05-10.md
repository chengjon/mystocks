# Frontend View Governance Inventory Execution - 2026-05-10

## Scope

This batch executes only the read-only inventory stage for `update-frontend-view-governance`.

No frontend code was modified. No view files were moved, archived, or deleted.

## Commands

```bash
node scripts/dev/tools/generate-myweb-audit-secondary-inventory.mjs \
  --json-output docs/reports/quality/myweb-audit/frontend-view-governance-inventory-2026-05-10.json \
  --markdown-output docs/reports/quality/myweb-audit/frontend-view-governance-inventory-2026-05-10.md
```

## Generated Artifacts

| Artifact | Purpose |
|---|---|
| `docs/reports/quality/myweb-audit/frontend-view-governance-inventory-2026-05-10.json` | Machine-readable non-routed view inventory |
| `docs/reports/quality/myweb-audit/frontend-view-governance-inventory-2026-05-10.md` | Human-readable inventory with heuristic shortlist |

## Measured Results

| Metric | Value | Source |
|---|---:|---|
| Total Vue view files | 272 | `web/frontend/src/views/**/*.vue` |
| Routed view imports | 42 | `web/frontend/src/router/index.ts` dynamic view imports |
| Non-routed view files | 230 | generated inventory |
| Current ArtDeco menu paths | 43 | `web/frontend/src/layouts/MenuConfig.ts`, including parent paths and `/dashboard` |

The earlier report observed 271 view files. This batch records the current measured value as 272. Governance reports should use the command-scoped measured value instead of treating older counts as current truth.

## Initial Three-Class Inventory

The current generator still uses the historical myweb-audit three-class vocabulary. These labels are first-pass triage labels only, not final archive decisions.

| Class | Count | Interpretation |
|---|---:|---|
| `候选待审` | 70 | Requires functional asset review before any mutation |
| `内嵌壳层` | 104 | Likely wrapper, tab, nested component, or compatibility surface |
| `Demo废弃` | 56 | Demo/example/test-like surface, still requires hidden-reference check |

## Priority Summary

| Priority | Count | Meaning |
|---|---:|---|
| H | 1 | High-priority review candidate based on selector/fallback/shared-composable hits |
| M | 123 | Medium-priority candidate or embedded surface |
| L | 106 | Low-priority/demo/static surface candidate |

High-priority shortlist:

| Page | Class | Hits |
|---|---|---|
| `web/frontend/src/views/ai/BatchAnalysis.vue` | `候选待审` | selector, fallback-literal, shared-composable |

## Zero-Router-Reference Sweep

These directories were explicitly checked because the design review identified them as high-risk legacy groups outside the canonical routing shape.

| Directory | Count | Initial classes | Priority split |
|---|---:|---|---|
| `stocks/` | 6 | `内嵌壳层=6` | `M=1 / L=5` |
| `trading/` | 4 | `候选待审=4` | `M=4` |
| `trading-decision/` | 4 | `候选待审=4` | `M=4` |
| `trade-management/` | 5 | `内嵌壳层=5` | `L=5` |
| `technical/` | 1 | `候选待审=1` | `M=1` |
| `settings/` | 4 | `候选待审=4` | `M=4` |

Total zero-router-reference focus set: 24 files.

## Interpretation

This inventory is sufficient to start lifecycle classification, but it is not sufficient to archive files. Before any mutation, each non-canonical page still needs:

- Hidden-reference checks across imports, tests, page config, layout tabs, docs, and string-based links.
- Functional asset review across the five approved asset classes.
- Lifecycle status assignment using the new governance vocabulary: `candidate-review`, `absorb-assets`, `compat-retained`, `experimental`, `archive-candidate`, or `archived`.

## Next Batch

The next safe batch is `2. Asset Classification` for the 24-file zero-router-reference focus set. It should remain read-only unless an explicit mutation approval is given.


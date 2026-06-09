# Frontend View Guard Map Execution - 2026-05-10

## Scope

This batch executes `update-frontend-view-governance` Step 0: guard-map discovery.

No frontend runtime code was modified. No view files were moved, archived, or deleted.

## Generated Artifacts

| Artifact | Purpose |
|---|---|
| `docs/reports/quality/myweb-audit/frontend-view-guard-map-2026-05-10.json` | Machine-readable guard/reference map |
| `docs/reports/quality/myweb-audit/frontend-view-guard-map-2026-05-10.md` | Human-readable summary |

## Scan Scope

The scan covered:

- `web/frontend/tests`
- `web/frontend/src`
- `docs/reports/quality/myweb-audit`
- `docs/superpowers/specs`

The scan looked for `@/views/*`, `src/views/*`, `--target-dir`, `--target-file`, and `/detail/*` string references.

The current router includes a `detail` route group for `/detail/graphics/:symbol` and `/detail/news/:symbol`; `/detail/*` matches are therefore not stale by default and must be interpreted from each record's `sourceFile` and `sourceType`.

## Summary

| Metric | Value |
|---|---:|
| Scanned files | 1833 |
| Mainline-gate specs | 22 |
| Total view-related references | 4452 |
| Spec references | 348 |
| Mainline-gate references | 121 |
| Runtime source references | 157 |
| Documentation references | 3826 |

Documentation references are discovery evidence, not automatic runtime blockers. Each page review must still decide whether the documented link or historical audit reference is expected to remain valid.

## Zero-Router-Reference Focus Directories

| Directory | Hit count | Key guard/reference signal |
|---|---:|---|
| `stocks/` | 49 | Runtime source and tests reference `views/stocks`; requires compatibility review |
| `trading/` | 91 | `trading-mainline-gate.spec.ts` and style/cleanup specs still reference it |
| `trading-decision/` | 49 | `trading-decision-mainline-gate.spec.ts` still references it |
| `trade-management/` | 26 | `trade-management-mainline-gate.spec.ts` and component normalization specs still reference it |
| `technical/` | 14 | Technical support specs and historical audits reference it |
| `settings/` | 18 | `settings-mainline-gate.spec.ts` and style normalization specs still reference it |

## Interpretation

The guard map confirms that zero-router-reference status is insufficient for cleanup. These directories must go through the redundant-page checklist before any archive decision:

- Guarded pages cannot become `archive-candidate` until the guard is migrated or explicitly retired.
- Runtime source references require successor or compatibility-retained decisions.
- Documentation references require per-page judgment: preserve link, update link, or mark historical-only.
- `route-detail-link` references require the same source-aware review because the current router still exposes canonical detail routes.

## Next Step

The next safe step is read-only lifecycle classification for the 24-file focus set, using:

- `frontend-view-governance-inventory-2026-05-10.json`
- `frontend-view-guard-map-2026-05-10.json`
- `frontend-view-redundant-page-review-checklist-2026-05-10.md`

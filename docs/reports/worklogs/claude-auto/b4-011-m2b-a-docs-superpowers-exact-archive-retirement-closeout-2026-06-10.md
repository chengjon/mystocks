# B4.011-M2b-A docs/superpowers exact archive-retirement closeout

Date: 2026-06-10

## Scope

This package accepts only the five exact `docs/superpowers/**`
archive-retirement candidates identified by the M2b-pre no-source audit.

The non-exact trade reconciliation design file is excluded from deletion and
restored/preserved for a separate HOLD decision.

## Retired Active Paths

- `docs/superpowers/plans/2026-05-09-miniqmt-evidence-execution-tracking.md`
- `docs/superpowers/plans/2026-05-19-codebase-map-openspec-execution-plan.md`
- `docs/superpowers/specs/2026-05-03-akshare-official-rename-mapping-design.md`
- `docs/superpowers/specs/2026-05-08-attribution-analysis-design.md`
- `docs/superpowers/specs/2026-05-08-ml-training-prediction-runtime-design.md`

## Added Archive Evidence

- `archive/docs/superpowers/plans/2026-05-09-miniqmt-evidence-execution-tracking.md`
- `archive/docs/superpowers/plans/2026-05-19-codebase-map-openspec-execution-plan.md`
- `archive/docs/superpowers/specs/2026-05-03-akshare-official-rename-mapping-design.md`
- `archive/docs/superpowers/specs/2026-05-08-attribution-analysis-design.md`
- `archive/docs/superpowers/specs/2026-05-08-ml-training-prediction-runtime-design.md`

## HOLD Preservation

`docs/superpowers/specs/2026-05-06-trade-reconciliation-statement-design.md`
was restored from HEAD and is not staged as a deletion. Its same-name archive
copy differs in two line positions and remains outside this package.

## Boundary

No source, test, runtime, route, UI, `docs/guides`, `docs/reports` outside this
closeout worklog, ST-HOLD, or `marketKlineData` files are modified by this
package.

## Verification Evidence

- Exact archive hash check: passed for all five retired files.
- HOLD file status after restore: clean.
- Staged set: five `R100` archive moves, governance metadata, and this
  closeout worklog only.
- `git diff --cached --check`: passed.
- `node .gitnexus/run.cjs verify-staged -r mystocks --cwd /opt/claude/mystocks_spec --json`: passed, risk `low`, affected processes `0`, index fresh for staged diff.
- `node .gitnexus/run.cjs detect-changes --scope staged -r mystocks --cwd /opt/claude/mystocks_spec`: passed, index `up-to-date`, risk `low`, affected processes `0`.
- OPENDOG verification: fresh, no failing runs or cleanup blockers.

## Closeout Decision

The five exact `docs/superpowers/**` files are formally retired from the active
documentation tree and preserved under `archive/docs/superpowers/**`.

The non-exact trade reconciliation design file remains active pending separate
HOLD drift decision.

# B4.011-M2b-pre docs/superpowers archive truth no-source audit

Date: 2026-06-10

## Scope

This no-source audit covers only the deleted tracked files under
`docs/superpowers/**` and their ignored archive evidence under
`archive/docs/superpowers/**`.

No source, test, runtime, route, UI, `docs/reports`, `docs/guides`, or
`archive/docs/reports` files are authorized by this audit.

## Summary

The original M1 conclusion expected six exact archive-retirement candidates.
Current HEAD/worktree evidence changes that disposition:

- Deleted tracked files under `docs/superpowers/**`: 6
- Files under ignored `archive/docs/superpowers/**`: 27
- Exact archive matches by content hash: 5
- Non-exact same-name archive drift: 1
- Tracked references outside `docs/superpowers/**` and `archive/**`: 0 for all six exact paths and basenames

Therefore M2b must split:

- `B4.011-M2b-A`: accept only the five exact archive-retirement files.
- `B4.011-M2b-HOLD`: preserve and separately decide the non-exact trade reconciliation design file.

## Exact Archive-Retirement Candidates

| Active deleted path | Archive evidence | Title | Notes |
| --- | --- | --- | --- |
| `docs/superpowers/plans/2026-05-09-miniqmt-evidence-execution-tracking.md` | `archive/docs/superpowers/plans/2026-05-09-miniqmt-evidence-execution-tracking.md` | `miniQMT Evidence Execution Tracking Implementation Plan` | Exact content hash match; no tracked path/name refs. |
| `docs/superpowers/plans/2026-05-19-codebase-map-openspec-execution-plan.md` | `archive/docs/superpowers/plans/2026-05-19-codebase-map-openspec-execution-plan.md` | `CODEBASE-MAP OpenSpec Execution Plan` | Exact content hash match; no tracked path/name refs. |
| `docs/superpowers/specs/2026-05-03-akshare-official-rename-mapping-design.md` | `archive/docs/superpowers/specs/2026-05-03-akshare-official-rename-mapping-design.md` | `AkShare Official Rename Candidate Evaluation Design` | Exact content hash match; no tracked path/name refs. |
| `docs/superpowers/specs/2026-05-08-attribution-analysis-design.md` | `archive/docs/superpowers/specs/2026-05-08-attribution-analysis-design.md` | `Attribution Analysis Design` | Exact content hash match; no tracked path/name refs. |
| `docs/superpowers/specs/2026-05-08-ml-training-prediction-runtime-design.md` | `archive/docs/superpowers/specs/2026-05-08-ml-training-prediction-runtime-design.md` | `ML Training and Prediction Runtime Design` | Exact content hash match; no tracked path/name refs. |

## HOLD Candidate

`docs/superpowers/specs/2026-05-06-trade-reconciliation-statement-design.md`
must not be accepted as an exact archive-retirement item in M2b-A.

Evidence:

- Same-name archive file exists at
  `archive/docs/superpowers/specs/2026-05-06-trade-reconciliation-statement-design.md`.
- Active HEAD copy size: 16435 bytes, 471 lines.
- Archive copy size: 16684 bytes, 471 lines.
- Content hashes differ.
- Only two line positions differ:
  - line 16: archive narrows multi-account switching to the first-batch account-descriptor contract.
  - line 43: archive narrows multi-account switching to the same first-batch account-descriptor contract.
- No tracked references outside `docs/superpowers/**` and `archive/**` were found for the path or basename.

Disposition: preserve active deletion for a separate HOLD decision. Do not stage
its deletion in M2b-A.

## Recommended Next Package

Proceed with `B4.011-M2b-A` as a five-file exact archive-retirement package:

- Stage the five active deletions.
- `git add -f` the five exact archive evidence files because `archive/` is ignored.
- Restore the HOLD active file from HEAD so the non-exact deletion is not silently accepted.
- Commit only the five exact retirements, archive evidence, governance metadata, and closeout worklog.

The HOLD candidate should receive its own decision after comparing whether the
archive drift is intentional updated guidance or an unsafe divergence from the
active design truth.

# G2.385 OpenSpec content-drift deletion-retirement reconciliation / no-source

## Boundary

Mode: `no-source`.

This node reconciles only the 6 OpenSpec content-drift deletion candidates left after `G2.384`. It does not authorize deletion, restore files, delete files, stage files, or commit files.

Explicit exclusions:
- The 13 strong-archive candidates were already accepted in commit `da07ca32f chore(openspec): retire archived strong-match changes`.
- Frontend, backend, script, root, docs, and test deletion candidates remain out of scope.
- Current `openspec/specs/**` modifications and untracked specs are not part of this node.

## Evidence Summary

- Remaining OpenSpec deleted files in scope: 26.
- Remaining content-drift change directories: 6.
- Active change overlap with these 6 directories: 0.
- `openspec validate --changes --strict`: passed, exit code 0.
- `openspec validate --specs --strict`: passed, exit code 0.
- Staged files during reconciliation: 0.

The 6 candidates are not archive-missing. All have complete archive copies. The observed drift is content drift between the current tracked unarchived change file at `HEAD` and its corresponding archived copy.

## Reconciliation Table

| Decision | Change | Files | Drift files | Drift cause | Active spec absorption | Next disposition |
|---|---|---:|---|---|---|---|
| Admit to formal deletion package with caveat | `add-broker-acknowledgement-reconciliation-contract` | 6 | `specs/trading-execution-safety/spec.md` | Archived spec is more complete than the unarchived tracked copy; it adds later broker readiness / transport / live bridge scenarios. | All archived Requirement/Scenario titles are present in active `openspec/specs/trading-execution-safety/spec.md`. | Can enter a deletion-retirement package if scoped alone with the other absorbed drift candidates. |
| Admit to formal deletion package with caveat | `add-miniqmt-live-bridge-runtime-contract` | 5 | `specs/trading-execution-safety/spec.md` | Archived spec is more complete; it includes additional Windows agent and Phase A identity scenarios. | All archived Requirement/Scenario titles are present in active `openspec/specs/trading-execution-safety/spec.md`. | Can enter a deletion-retirement package if scoped alone with the other absorbed drift candidates. |
| Admit to formal deletion package with caveat | `add-miniqmt-primary-broker-adapter-runtime` | 5 | `specs/trading-execution-safety/spec.md` | Archived spec is more complete; it includes later live bridge / Windows agent / audit scenarios. | All archived Requirement/Scenario titles are present in active `openspec/specs/trading-execution-safety/spec.md`. | Can enter a deletion-retirement package if scoped alone with the other absorbed drift candidates. |
| Admit to formal deletion package with caveat | `add-windows-qmt-agent-runtime-contract` | 5 | `specs/trading-execution-safety/spec.md` | Archived spec is more complete; it includes formal readiness and Phase A live bridge identity scenarios. | All archived Requirement/Scenario titles are present in active `openspec/specs/trading-execution-safety/spec.md`. | Can enter a deletion-retirement package if scoped alone with the other absorbed drift candidates. |
| Admit to formal deletion package with caveat | `implement-pinia-api-standardization` | 4 | `proposal.md`, `specs/api-integration/spec.md`, `tasks.md` | Archived files remove apparent tool-residue text and restructure the data-adapter requirement into a modified requirement. | All archived Requirement/Scenario titles are present in active `openspec/specs/api-integration/spec.md`. | Can enter a deletion-retirement package; preserve active `api-integration` spec and related governance reports. |
| Admit to formal deletion package with caveat | `update-frontend-view-governance` | 1 | `tasks.md` | Archived task file is more complete and records read-only evidence closures that the unarchived tracked copy lacks. | No spec delta in this change. The task drift is historical governance progress, not an active spec gap. | Can enter a deletion-retirement package; preserve frontend-view governance reports. |

## Reference Scan Notes

The second-pass reference scan found many historical report and plan references, especially for `update-frontend-view-governance` and broker reconciliation changes. These references are not active OpenSpec change dependencies and should be preserved as documentation history.

Important distinction:
- Old path references such as `openspec/changes/<change-id>` in historical reports are evidence links, not blockers by themselves.
- Active spec absorption was checked by comparing archived Requirement/Scenario headings against current active specs.
- No current active OpenSpec change directory depends on the unarchived dirty paths for these 6 candidates.

## Decision

G2.385 admits all 6 content-drift candidates to a future formal deletion-retirement authorization package, with the caveat that the next node must explicitly acknowledge archive-vs-HEAD content drift and active-spec absorption.

This node does not authorize deletion.

## Required Gates For Next Node

Recommended next node:

`G2.386 openspec content-drift deletion-retirement acceptance / deletion-retirement authorized`

Suggested scope: only the 26 tracked deletion paths under these 6 change directories.

Required gates:
- Stage only the 26 named OpenSpec deletion paths.
- Do not stage current `openspec/specs/**` modifications or untracked specs.
- Do not stage frontend, backend, script, root, docs, or test deletion candidates.
- Re-run `openspec validate --changes --strict`.
- Re-run `openspec validate --specs --strict`.
- Run `git diff --cached --check`.
- Run a staged path allowlist check before commit.
- Run GitNexus staged detection after direct `gitnexus analyze` if the index is stale.

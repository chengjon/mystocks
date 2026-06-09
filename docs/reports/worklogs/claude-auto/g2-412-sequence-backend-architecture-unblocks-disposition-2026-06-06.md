# G2.412 sequence-backend-architecture-unblocks Disposition

Date: 2026-06-06
Mode: `no-source`

## Scope

This disposition covers the remaining dirty OpenSpec active-change artifacts under:

- `openspec/changes/sequence-backend-architecture-unblocks/proposal.md`
- `openspec/changes/sequence-backend-architecture-unblocks/proposal-review.md`
- `openspec/changes/sequence-backend-architecture-unblocks/specs/architecture-governance/spec.md`

The tracked `tasks.md` file is part of the active change but is not dirty in this node.

## Current Evidence

- HEAD at disposition: `6d52bd23f`
- `git status --short -- openspec/changes/sequence-backend-architecture-unblocks`:
  - `?? openspec/changes/sequence-backend-architecture-unblocks/proposal-review.md`
  - `?? openspec/changes/sequence-backend-architecture-unblocks/proposal.md`
  - `?? openspec/changes/sequence-backend-architecture-unblocks/specs/`
- `openspec validate sequence-backend-architecture-unblocks --strict`: valid
- `tasks.md`: `33/33` tasks complete
- `openspec list`: active change still present
- Archive path for this change id: none found

## Delta Evidence

The untracked `architecture-governance` delta defines four requirements:

| Delta requirement | Present in current `openspec/specs/architecture-governance/spec.md` |
|---|---:|
| `Runtime Unblock Must Precede Broad Architecture Evidence` | No |
| `Schema Compatibility Must Be Proved Before Directory Retirement` | No |
| `Singleton Lifecycle Work Must Start From Classification` | No |
| `Codebase Map Evidence Shall Distinguish Historical And Current-Head Truth` | No |

This means the delta is not already absorbed into the current active spec and should not be silently ignored as a duplicate.

## Review Evidence

The untracked `proposal-review.md` is not an approval artifact. It explicitly marks the proposal as needing revision:

- HIGH: root cause of the runtime blocker is misidentified.
- HIGH: task 2.1 prescribes the wrong fix.
- MED: the stated health-route collection failure chain does not currently reproduce as described.
- MED: the proposal impact section omits `_data_lineage_responses.py`, the actual file implicated by the review.
- LOW: the proposal does not name the actual failing file.

The review conclusion states that the sequencing logic is sound, but the proposal cannot be executed as written.

## Disposition

Do not accept `sequence-backend-architecture-unblocks` as an ordinary active-change residual package in its current state.

Do not delete the artifacts in this node. The delta requirements are not present in the current active spec, and the active change has no archive path, so deletion would require a separate retirement/deletion authorization.

Treat the change as a blocked backfill package pending one of two explicit follow-up decisions:

1. **Revision path**: create a source-authorized package that updates the proposal/tasks/delta to correct the factual root-cause and affected-file claims before acceptance.
2. **Retirement path**: create a deletion/retirement package for the untracked backfill artifacts, with explicit rationale for why the completed active change should remain without these proposal/delta files.

## Non-Goals

- No backend source/test changes.
- No OpenSpec archive operation.
- No deletion or retirement.
- No mutation of the tracked `tasks.md`.
- No acceptance commit for the untracked proposal/delta files as-is.

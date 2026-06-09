# G2.391 OpenSpec backend-core split change package preflight / no-source

## Boundary

Mode: `no-source`.

Scope is limited to:

`openspec/changes/split-backend-core-modules-with-compatibility-wrappers/`

This node does not edit, restore, delete, stage, or commit any file.

## Evidence Summary

- Active change: `split-backend-core-modules-with-compatibility-wrappers`
- Active status: `12/24 tasks`, `15d ago`
- Dirty shape: `??=4`, `M=0`
- Files:
  - `design.md`
  - `proposal.md`
  - `specs/architecture-governance/spec.md`
  - `specs/directory-governance/spec.md`
- `openspec validate split-backend-core-modules-with-compatibility-wrappers --strict`: exit code 0.
- Staged files during preflight: 0.
- PostHog flush network noise appears in stderr, but OpenSpec validation exits 0.

## Package Structure

| File | Role | Status |
|---|---|---|
| `proposal.md` | Change proposal | Present, untracked |
| `design.md` | Design notes | Present, untracked |
| `specs/architecture-governance/spec.md` | Delta spec | Present, untracked |
| `specs/directory-governance/spec.md` | Delta spec | Present, untracked |

No `tasks.md` is dirty in this package. The existing active change task state remains `12/24`.

## Delta Spec Check

| Delta spec | Requirement/Scenario count | Active spec overlap | Decision |
|---|---:|---|---|
| `architecture-governance` | 5 | All 5 headings are missing from current active `architecture-governance` spec. | Additive governance delta, not duplicate. |
| `directory-governance` | 7 | All 7 headings are missing from current active `directory-governance` spec. | Additive directory-governance delta, not duplicate. |

Key requirements introduced:

- `Backend Core Import Compatibility Governance`
- `Backend Core Split Batch Governance`
- `Compatibility-Aware Core Directory Migration`
- `Core Wrapper Retirement Gate`
- `Core Import Matrix Artifact`

## Duplicate / Stale / Validity Check

| Question | Result | Evidence |
|---|---|---|
| Is this change active? | Yes | `openspec list` shows `12/24 tasks`. |
| Does it validate? | Yes | `openspec validate <change-id> --strict` exits 0. |
| Is it a tracked modification? | No | All 4 files are untracked. |
| Is it already archived? | No hard evidence | No archive match was observed in the active-change inventory. |
| Are the delta requirements already in active specs? | No | Both active specs exist, but all delta Requirement/Scenario headings are missing. |
| Is it stale? | No | The active change is half complete, not closed. |
| Is it duplicate? | No confirmed duplicate | There are related backend OpenSpec reports and references, but no exact duplicate package was confirmed. |

## External Reference Notes

The change id is referenced by many backend OpenSpec reports and plans. One active change design also references it:

`openspec/changes/migrate-backend-singletons-to-lifecycle-di/design.md`

This does not block accepting the OpenSpec package, but it means implementation work must coordinate with backend lifecycle / singleton migration lines. The package should not be mixed with `sequence-backend-architecture-unblocks` or lifecycle implementation changes.

## Decision

Classification: `有效`.

Disposition: eligible for a formal OpenSpec package acceptance node, with strict scope limited to the 4 untracked files under `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/`.

It should not be bundled with:

- `sequence-backend-architecture-unblocks`
- `migrate-backend-singletons-to-lifecycle-di`
- modified active specs
- untracked spec directories
- backend source/test changes
- deletion-retirement residue

## Recommended Next Node

`G2.392 openspec backend-core split change package acceptance / spec-authorized`

Suggested scope:

- `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/design.md`
- `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/proposal.md`
- `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/specs/architecture-governance/spec.md`
- `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/specs/directory-governance/spec.md`

Required gates:

- Stage only the 4 files above.
- Do not stage `openspec/specs/**`.
- Do not stage other active change groups.
- Run `openspec validate split-backend-core-modules-with-compatibility-wrappers --strict`.
- Run `openspec validate --changes --strict`.
- Run `git diff --cached --check`.
- Run staged path allowlist before commit.
- Run GitNexus staged detection; if stale, refresh with direct `gitnexus analyze`, not `npx`.

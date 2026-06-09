# G2.393 OpenSpec frontend active-change package split / no-source

## Boundary

Mode: `no-source`.

Scope is limited to the two frontend active OpenSpec change groups identified by `G2.388`:

- `openspec/changes/implement-html5-migration-experience-optimization/`
- `openspec/changes/restructure-frontend-directory/`

This node does not edit, restore, delete, stage, or commit any frontend change file. It only records evidence and package disposition.

Explicitly out of scope:

- `openspec/specs/**` modified active specs.
- Untracked active spec directories under `openspec/specs/**`.
- Backend active-change packages.
- Completed-change backfill artifacts.
- Frontend/backend/source/test/runtime files.

## Evidence Summary

- Current HEAD: `cc3b72f3b docs(openspec): add backend core split change`.
- Staged files during this inventory: 0.
- `openspec validate implement-html5-migration-experience-optimization --strict`: exit code 0.
- `openspec validate restructure-frontend-directory --strict`: exit code 0.
- `openspec validate --changes --strict`: 16 passed, 0 failed.
- `openspec validate --specs --strict`: 47 passed, 0 failed.
- PostHog flush network noise appears in OpenSpec stderr, but validation exit status is 0.

## Decision Table

| Decision | Change | Dirty shape | Validation | Evidence | Next disposition |
|---|---|---:|---|---|---|
| Valid but high-risk; keep isolated | `implement-html5-migration-experience-optimization` | `M=4`, `??=1`, tracked diff `+550/-88` | Pass | Large active change with modified `design.md`, `proposal.md`, delta spec, `tasks.md`, and untracked `tasks-review.md`. Current task ledger is `71` done / `48` open. Delta spec contains `8` requirements and `20` scenarios. | Do not accept in the same package as any other frontend change. Requires a dedicated review node before source/spec acceptance. |
| Valid narrow package candidate | `restructure-frontend-directory` | `M=2`, tracked diff `+3/-3` | Pass | Only `design.md` and `tasks.md` are modified. Current task ledger is `193` done / `16` open. No dirty delta spec files under this change. | Eligible for a strict two-file acceptance node after staged allowlist, OpenSpec validation, and GitNexus staged detection. |

## Split Decision

The two frontend active changes must not be committed together.

`restructure-frontend-directory` is a narrow active-change update and can be accepted first as a small OpenSpec package.

`implement-html5-migration-experience-optimization` is a broad frontend architecture / runtime experience package. Its tracked diff is large, it has an additional untracked review artifact, and its delta spec is substantial. It should remain isolated until a dedicated no-source review decides whether the full dirty set is internally consistent and whether `tasks-review.md` belongs in the package.

## Recommended Next Nodes

1. `G2.394 openspec restructure-frontend-directory active-change acceptance / spec-authorized`
   - Scope:
     - `openspec/changes/restructure-frontend-directory/design.md`
     - `openspec/changes/restructure-frontend-directory/tasks.md`
   - Do not stage `implement-html5-migration-experience-optimization`.
   - Do not stage `openspec/specs/**`.
   - Required gates:
     - `openspec validate restructure-frontend-directory --strict`
     - `openspec validate --changes --strict`
     - staged path allowlist
     - `git diff --cached --check`
     - GitNexus staged detection

2. `G2.395 openspec html5 migration experience active-change review / no-source`
   - Scope:
     - `openspec/changes/implement-html5-migration-experience-optimization/design.md`
     - `openspec/changes/implement-html5-migration-experience-optimization/proposal.md`
     - `openspec/changes/implement-html5-migration-experience-optimization/specs/html5-web-platform-optimization/spec.md`
     - `openspec/changes/implement-html5-migration-experience-optimization/tasks.md`
     - `openspec/changes/implement-html5-migration-experience-optimization/tasks-review.md`
   - Goal: decide whether all five dirty files form one coherent active-change package, whether `tasks-review.md` should be accepted, and whether the large task-ledger rewrite needs further split.

## Residual Notes

The modified active specs and untracked active spec directories remain excluded. They should follow the active-spec residual inventory line described by `G2.387`, not this frontend active-change package split.

# B4.011 Governance Card Residual No-Source Review

Date: 2026-06-12

Mode: no-source review, source edits unauthorized

## Scope

This review covers only the three historical untracked FUNCTION_TREE task-card files under:

- `.governance/programs/artdeco-web-design-governance/cards/`

Explicitly out of scope:

- source, tests, runtime, routes, API paths, OpenSpec, ST-HOLD, `marketKlineData`
- `docs/guides/**`
- `docs/superpowers/**`
- `docs/reports/**` content except this worklog
- already closed B4.011 docs report archive/preservation artifacts
- external dirty files

Current HEAD:

- `982061007 B4.011-M2a-Residual: archive docs reports dirty review`

## Residual Files

| File | Lines | SHA-256 | Matching node | Node status | Decision |
| --- | ---: | --- | --- | --- | --- |
| `.governance/programs/artdeco-web-design-governance/cards/ai-batch-shape-readiness.yaml` | 27 | `c71b0fddb247fe2918b312a4a05d01861c32d6e23eb1d42adaf27d6ab1a418a1` | `ai-batch-shape-readiness` | `closed` | stale generated task card; deletion-retirement candidate after explicit authorization |
| `.governance/programs/artdeco-web-design-governance/cards/b4-docs-reports-archive-retirement.yaml` | 33 | `d3ec12b945267b4fe134af8bd22362d5d6acf6de98806c1fc75b1272b9665859` | `b4-docs-reports-archive-retirement` | `closed` | stale generated task card; deletion-retirement candidate after explicit authorization |
| `.governance/programs/artdeco-web-design-governance/cards/b4-docs-reports-hold-a-low-delta-retirement.yaml` | 40 | `2d1d6108165ee3b5fe5dc5253a4acae2dfc2a9a683403928fdeb68aa88f2f86f` | `b4-docs-reports-hold-a-low-delta-retirement` | `closed` | stale generated task card; deletion-retirement candidate after explicit authorization |

## Findings

- All three card files are untracked worktree artifacts.
- Each card maps to an existing FUNCTION_TREE node.
- Each matching node is already closed and `source_edits_authorized: false`.
- No active FUNCTION_TREE gate currently depends on these cards.
- The files are generated authorization/task-card artifacts, not source, test, route, runtime, API, OpenSpec, or report truth content.
- They should not be blindly committed because doing so would reintroduce stale authorization records for closed nodes.

## Decision

The safest disposition is a narrow deletion-retirement package for these three untracked card files only. This should be executed only after explicit authorization because it removes files from the worktree.

No source, test, runtime, route, API, OpenSpec, `docs/guides`, `docs/superpowers`, ST-HOLD, `marketKlineData`, or report content edits are needed.

## Proposed Authorization

Node:

- `b4-governance-card-residual-review`

Allowed deletion-retirement targets:

- `.governance/programs/artdeco-web-design-governance/cards/ai-batch-shape-readiness.yaml`
- `.governance/programs/artdeco-web-design-governance/cards/b4-docs-reports-archive-retirement.yaml`
- `.governance/programs/artdeco-web-design-governance/cards/b4-docs-reports-hold-a-low-delta-retirement.yaml`

Required gates:

- exact staged allowlist contains only the three card removals plus approved governance state and closeout evidence files
- `git diff --cached --check`
- GitNexus `verify-staged`
- GitNexus staged change detection reports low risk and zero affected processes
- OPENDOG verification returns blockers: `[]`
- post-commit GitNexus index refresh

## Recommendation

Prepare the authorization card now, then wait for explicit deletion-retirement approval before removing any of the three card files.

## Implementation Record

Deletion-retirement approval:

- User approved implementation after the authorization-prepared package.

Local recovery snapshot:

- `/tmp/b4-011-governance-card-residual-backup-20260612/`

Removed files:

| File | Backup SHA-256 | Result |
| --- | --- | --- |
| `.governance/programs/artdeco-web-design-governance/cards/ai-batch-shape-readiness.yaml` | `c71b0fddb247fe2918b312a4a05d01861c32d6e23eb1d42adaf27d6ab1a418a1` | removed from worktree |
| `.governance/programs/artdeco-web-design-governance/cards/b4-docs-reports-archive-retirement.yaml` | `d3ec12b945267b4fe134af8bd22362d5d6acf6de98806c1fc75b1272b9665859` | removed from worktree |
| `.governance/programs/artdeco-web-design-governance/cards/b4-docs-reports-hold-a-low-delta-retirement.yaml` | `2d1d6108165ee3b5fe5dc5253a4acae2dfc2a9a683403928fdeb68aa88f2f86f` | removed from worktree |

Implementation boundary:

- No source, test, runtime, route, API, OpenSpec, ST-HOLD, `marketKlineData`, `docs/guides`, `docs/superpowers`, or report content changes were made.
- The removal targets were untracked generated governance card artifacts, so the implementation commit records the governance state and this evidence note rather than tracked file deletions.

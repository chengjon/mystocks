# G2.387 OpenSpec residual M/?? inventory / no-source

## Boundary

Mode: `no-source`.

This node inventories the residual OpenSpec dirty state after the deletion-retirement line was closed by:

- `da07ca32f chore(openspec): retire archived strong-match changes`
- `99cfce98a chore(openspec): retire archived drift changes`

This node does not edit, restore, delete, stage, or commit any OpenSpec file.

## Evidence Summary

- Current HEAD: `99cfce98a chore(openspec): retire archived drift changes`.
- OpenSpec tracked deletion candidates: 0.
- `git status --short -- openspec`: `M=11`, `??=22`.
- `git status --porcelain=v1 -uall -- openspec`: `M=11`, `??=26`.
- Residual groups after expansion: 24.
- `openspec list`: 16 active changes.
- `openspec list --specs`: 47 specs.
- `openspec validate --changes --strict`: passed, `16 passed, 0 failed`.
- `openspec validate --specs --strict`: passed, `47 passed, 0 failed`.
- Staged files during inventory: 0.

Count note: the `??=22` short-status count is directory-collapsed. The actionable file-level count is `??=26`.

## Classification Summary

| Class | Groups | Files | Disposition |
|---|---:|---:|---|
| Active change residuals | 5 | 16 | Review and commit only in change-scoped packages. |
| Modified active specs | 5 | 5 | Require spec-authorized review; do not bundle with active change drafts. |
| New active spec directories | 14 | 14 | Require spec-addition package or per-domain acceptance review. |

## Active Change Residuals

| Change | Active status | M | ?? files | Evidence | Decision |
|---|---|---:|---:|---|---|
| `implement-dirty-worktree-cleanup-governance` | `0/67 tasks` | 0 | 4 | New design, proposal, `directory-governance` delta spec, and tasks. | Candidate for a dedicated OpenSpec governance-change package. |
| `implement-html5-migration-experience-optimization` | `63/111 tasks` | 4 | 1 | Modified design/proposal/spec/tasks plus `tasks-review.md`; tracked diff is large (`+550/-88`). | Needs dedicated active-change reconciliation before any commit. |
| `restructure-frontend-directory` | `76/92 tasks` | 2 | 0 | Modified design/tasks with small tracked diff (`+3/-3`). | Candidate for narrow active-change update after review. |
| `sequence-backend-architecture-unblocks` | `Complete` | 0 | 3 | New proposal review, proposal, and `architecture-governance` delta spec under a completed change. | High caution: completed-change residual; verify whether stale, duplicate, or intentionally resurrected. |
| `split-backend-core-modules-with-compatibility-wrappers` | `12/24 tasks` | 0 | 4 | New design, proposal, `architecture-governance` delta spec, and `directory-governance` delta spec. | Candidate for dedicated backend-core OpenSpec package. |

## Modified Active Specs

| Spec | M files | Diff size | Listed by OpenSpec | Decision |
|---|---:|---|---|---|
| `agent-memory-workflow` | 1 | `+39/-0` | Yes | Candidate for spec-authorized commit after checking linked change/source of truth. |
| `api-integration` | 1 | `+63/-1` | Yes | Candidate for spec-authorized commit; likely related to Pinia/API standardization line. |
| `architecture-governance` | 1 | `+15/-0` | Yes | Candidate for spec-authorized commit; may overlap backend/core governance changes. |
| `code-quality` | 1 | `+48/-0` | Yes | Candidate for spec-authorized commit; likely governance/process spec drift. |
| `trading-execution-safety` | 1 | `+110/-2` | Yes | Candidate for spec-authorized commit; overlaps broker/QMT safety line. |

## New Active Spec Directories

| Spec | ?? files | Listed by OpenSpec | Decision |
|---|---:|---|---|
| `broker-acknowledgement-reconciliation` | 1 | Yes | Candidate for broker/QMT spec-add package. |
| `broker-truth-channel-topology` | 1 | Yes | Candidate for broker/QMT spec-add package. |
| `codex-task-looping` | 1 | Yes | Candidate for governance/process spec package. |
| `containerized-runtime-deployment` | 1 | Yes | Candidate for runtime/deployment spec package. |
| `frontend-audit-orchestration` | 1 | Yes | Candidate for frontend-audit spec package. |
| `kronos-integration-contract` | 1 | Yes | Candidate for Kronos spec package. |
| `miniqmt-live-bridge-runtime` | 1 | Yes | Candidate for broker/QMT spec-add package. |
| `miniqmt-primary-broker-adapter-runtime` | 1 | Yes | Candidate for broker/QMT spec-add package. |
| `portfolio-attribution-analysis` | 1 | Yes | Candidate for portfolio analytics spec package. |
| `windows-qmt-agent-contract-acceptance` | 1 | Yes | Candidate for broker/QMT spec-add package. |
| `windows-qmt-agent-live-contract` | 1 | Yes | Candidate for broker/QMT spec-add package. |
| `windows-qmt-agent-reference-service` | 1 | Yes | Candidate for broker/QMT spec-add package. |
| `windows-qmt-contract-formal-sequence` | 1 | Yes | Candidate for broker/QMT spec-add package. |
| `windows-qmt-service-readiness-probe` | 1 | Yes | Candidate for broker/QMT spec-add package. |

## Decision

The OpenSpec deletion-retirement line is closed: there are no remaining tracked deletion candidates under `openspec/`.

The residual OpenSpec dirty state should not be handled as deletion cleanup. It is now a spec/change reconciliation line with three separate authorities:

1. Active change packages for dirty `openspec/changes/<change-id>/...`.
2. Spec-authorized packages for modified tracked `openspec/specs/**`.
3. Spec-addition packages for untracked `openspec/specs/<spec>/spec.md`.

## Recommended Next Nodes

Recommended order:

1. `G2.388 openspec active-change residual inventory / no-source`
   - Scope: the 5 dirty active change groups.
   - Goal: decide which active change packages are valid, stale, duplicate, or need OpenSpec archive/approval handling.

2. `G2.389 openspec active-spec residual inventory / no-source`
   - Scope: 5 modified active specs plus 14 untracked active spec directories.
   - Goal: split spec-authorized packages by domain.

Do not stage OpenSpec residuals until the relevant package receives explicit authorization.

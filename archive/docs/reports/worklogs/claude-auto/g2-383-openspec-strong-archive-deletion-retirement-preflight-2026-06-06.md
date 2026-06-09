# G2.383 OpenSpec strong-archive deletion-retirement authorization preflight / no-source

## Boundary

Mode: `no-source`.

This node only preflights the 13 OpenSpec deletion candidates that already have complete, byte-identical archive copies. It does not authorize deletion, restore files, delete files, stage files, or commit files.

Explicit exclusions:
- 6 content-drift OpenSpec changes remain isolated.
- Frontend, backend, script, root, docs, and test deletion candidates remain out of scope.
- This report is a decision preflight, not a deletion-retirement acceptance package.

## Evidence Summary

- OpenSpec tracked deletion candidates still observed: 76 files.
- Deleted OpenSpec change directories: 19.
- Strong archive candidates in this node: 13 changes / 50 files.
- Isolated non-strong candidates: 6 changes / 26 files.
- `openspec list`: 16 active changes.
- Active change overlap with the 13 strong candidates: 0.
- `openspec list --specs`: 47 specs.
- `openspec validate --changes --strict`: passed, exit code 0.
- `openspec validate --specs --strict`: passed, exit code 0.
- Staged files during preflight: 0.

Current OpenSpec dirty status stayed outside this node's authority:
- `D`: 76
- `M`: 11
- `??`: 22

## Isolated Content-Drift Changes

These remain excluded from G2.383 and must not be accepted in the same deletion-retirement package:

| Change | Files | Reason |
|---|---:|---|
| `add-broker-acknowledgement-reconciliation-contract` | 6 | Archive complete but content drift exists. |
| `add-miniqmt-live-bridge-runtime-contract` | 5 | Archive complete but content drift exists. |
| `add-miniqmt-primary-broker-adapter-runtime` | 5 | Archive complete but content drift exists. |
| `add-windows-qmt-agent-runtime-contract` | 5 | Archive complete but content drift exists. |
| `implement-pinia-api-standardization` | 4 | Archive complete but proposal/task/spec drift exists. |
| `update-frontend-view-governance` | 1 | Archive complete but task drift exists. |

## Preflight Decision Table

| Decision | Change | Files | Delta specs | Archive link | Reference scan result | Formal deletion package admission |
|---|---|---:|---|---|---|---|
| Admit to formal package | `add-broker-channel-topology-for-miniqmt-and-tdx` | 4 | `broker-truth-channel-topology` | `openspec/changes/archive/2026-05-12-add-broker-channel-topology-for-miniqmt-and-tdx` | Old path/id references only in historical report/cleanup docs; no active change dependency found. | Yes |
| Admit to formal package | `add-containerized-runtime-deployment-capability` | 1 | None | `openspec/changes/archive/2026-05-12-add-containerized-runtime-deployment-capability` | Governance report references only. | Yes |
| Admit to formal package | `add-kronos-integration-contract` | 4 | `kronos-integration-contract` | `openspec/changes/archive/2026-05-12-add-kronos-integration-contract` | Governance report references only. | Yes |
| Admit to formal package | `add-page-audit-orchestration-governance` | 4 | `frontend-audit-orchestration` | `openspec/changes/archive/2026-05-12-add-page-audit-orchestration-governance` | Historical quality report and active spec mention the change id; old path reference is historical report only. | Yes, with note to preserve active spec. |
| Admit to formal package | `add-portfolio-attribution-analysis` | 4 | `portfolio-attribution-analysis` | `openspec/changes/archive/2026-05-12-add-portfolio-attribution-analysis` | Historical superpowers plan/design references; no active change dependency found. | Yes |
| Admit to formal package | `add-stop-hook-graphiti-task-closeout` | 4 | `agent-memory-workflow` | `openspec/changes/archive/2026-05-12-add-stop-hook-graphiti-task-closeout` | Governance report references only. | Yes |
| Admit to formal package | `add-windows-qmt-agent-reference-service` | 5 | `trading-execution-safety`, `windows-qmt-agent-reference-service` | `openspec/changes/archive/2026-05-12-add-windows-qmt-agent-reference-service` | Quant-trading guide mentions the change id; no old path dependency found outside governance reports. | Yes, with note to preserve guide. |
| Admit to formal package | `add-windows-qmt-contract-acceptance-harness` | 4 | `windows-qmt-agent-contract-acceptance` | `openspec/changes/archive/2026-05-12-add-windows-qmt-contract-acceptance-harness` | Governance report references only. | Yes |
| Admit to formal package | `add-windows-qmt-contract-formal-sequence` | 4 | `trading-execution-safety`, `windows-qmt-contract-formal-sequence` | `openspec/changes/archive/2026-05-12-add-windows-qmt-contract-formal-sequence` | Governance report references only. | Yes |
| Admit to formal package | `add-windows-qmt-service-readiness-probe` | 4 | `trading-execution-safety`, `windows-qmt-service-readiness-probe` | `openspec/changes/archive/2026-05-12-add-windows-qmt-service-readiness-probe` | Governance report references only. | Yes |
| Admit to formal package | `align-artdeco-stateful-primitives-with-design` | 4 | `artdeco-design-governance` | `openspec/changes/archive/2026-05-12-align-artdeco-stateful-primitives-with-design` | ArtDeco reports mention the change id; old path reference is governance report only. | Yes, with note to preserve ArtDeco reports/specs. |
| Admit to formal package | `align-business-route-status-and-tooltip-surfaces` | 4 | `artdeco-design-governance` | `openspec/changes/archive/2026-05-12-align-business-route-status-and-tooltip-surfaces` | ArtDeco reports mention the change id; old path reference is governance report only. | Yes, with note to preserve ArtDeco reports/specs. |
| Admit to formal package | `update-miniqmt-phase-a-contract-hardening` | 4 | `trading-execution-safety` | `openspec/changes/archive/2026-05-12-update-miniqmt-phase-a-contract-hardening` | Governance report references only. | Yes |

## Admission Conditions For The Next Node

The next formal deletion-retirement node may accept only the 50 tracked deletion paths belonging to the 13 rows above, if it receives explicit deletion-retirement authorization.

Required gates for that next node:
- Stage only the 50 named OpenSpec deletion paths.
- Do not stage the 6 content-drift change directories.
- Do not stage current `openspec/specs/**` modifications or untracked specs.
- Re-run `openspec validate --changes --strict`.
- Re-run `openspec validate --specs --strict`.
- Run `git diff --cached --check`.
- Run a staged path allowlist check before commit.
- Commit only if staged paths match the 13 strong archive changes exactly.

## Decision

G2.383 admits the 13 strong archive change directories to a future formal deletion-retirement authorization package.

G2.383 does not itself authorize deletion. It only establishes that these candidates have complete archive copies, no active change overlap, passing OpenSpec validation, and no observed active change dependency on the unarchived dirty paths.

Recommended next node:

`G2.384 openspec strong-archive deletion-retirement acceptance / deletion-retirement authorized`

Suggested scope for G2.384: only the 50 tracked deletion paths under the 13 admitted change directories.

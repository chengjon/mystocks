# G2.398 OpenSpec active-spec residual inventory / no-source

## Boundary

Mode: `no-source`.

Scope is limited to dirty `openspec/specs/**` residuals:

- 5 tracked modified active spec files.
- 14 untracked active spec directories.

This node only inventories, classifies, and recommends package boundaries. It does not edit, restore, delete, stage, or commit any spec file.

Explicitly out of scope:

- `openspec/changes/**` active-change packages.
- Frontend/backend/source/test/runtime files.
- Previously accepted OpenSpec deletion-retirement packages.
- Untracked G2 worklog reports.

## Evidence Summary

- Current HEAD: `b2050b2fd docs(openspec): update html5 migration evidence ledger`.
- Staged files during inventory: 0.
- Modified active specs: 5.
- Untracked active spec directories: 14.
- `openspec list --specs`: 47 specs listed.
- `openspec validate --specs --strict`: 47 passed, 0 failed.
- `openspec validate --changes --strict`: 16 passed, 0 failed.
- PostHog flush network noise appears in OpenSpec stderr, but validation exit status is 0.

## Modified Active Specs

| Spec | Diff size | New/changed theme | Risk | Disposition |
|---|---:|---|---|---|
| `agent-memory-workflow` | `+39/-0` | Stop-hook Graphiti closeout reporting, auditable payload, non-blocking behavior. | Low / governance-local | Eligible for a one-file spec-authorized acceptance package. |
| `api-integration` | `+63/-1` | Data adapter safety, standardized Pinia store factory, unified API client integration, API/store performance monitoring. | Medium / frontend data contract | Eligible for a dedicated API integration spec package after checking it is not mixed with `openspec/changes/implement-html5-migration-experience-optimization`. |
| `architecture-governance` | `+15/-0` | Broker execution truth registry. | Medium / broker-governance cross-link | Should be reviewed together with broker/trading safety specs, not committed as generic architecture cleanup. |
| `code-quality` | `+48/-0` | Static analysis remeasure governance, freshness, two-step approval boundary. | Low / quality-governance-local | Eligible for a one-file spec-authorized acceptance package. |
| `trading-execution-safety` | `+110/-2` | External broker-facing readiness, broker acknowledgement boundary, live bridge result contract, remote Windows agent contract, replay suppression, audit evidence. | High / broker execution safety | Requires dedicated broker/QMT safety preflight before acceptance. |

## Untracked Active Spec Directories

All 14 untracked spec directories are visible to `openspec list --specs` and pass strict spec validation as part of the 47-spec set.

| Cluster | Spec directories | Count | Disposition |
|---|---|---:|---|
| Broker / QMT execution safety | `broker-acknowledgement-reconciliation`, `broker-truth-channel-topology`, `miniqmt-live-bridge-runtime`, `miniqmt-primary-broker-adapter-runtime`, `windows-qmt-agent-contract-acceptance`, `windows-qmt-agent-live-contract`, `windows-qmt-agent-reference-service`, `windows-qmt-contract-formal-sequence`, `windows-qmt-service-readiness-probe` | 9 | Must be reviewed with `architecture-governance` and `trading-execution-safety`; do not accept as scattered spec additions. |
| Independent tooling / runtime / analysis specs | `codex-task-looping`, `containerized-runtime-deployment`, `frontend-audit-orchestration`, `kronos-integration-contract`, `portfolio-attribution-analysis` | 5 | Candidate for independent spec-addition preflight packages; do not mix with broker/QMT safety. |

## Decision

The active-spec residuals are valid OpenSpec content, but they should not be accepted as one bulk spec commit.

Package split:

1. Small governance-local spec updates can be accepted in narrow one-file packages.
2. API integration should be accepted as its own frontend data-contract package.
3. Broker/QMT execution safety must get a dedicated no-source preflight before any acceptance because it spans modified specs plus 9 untracked spec directories.
4. Independent untracked spec additions should be preflighted separately from the broker/QMT line.

## Recommended Next Nodes

1. `G2.399 openspec agent-memory stop-hook spec acceptance / spec-authorized`
   - Scope: `openspec/specs/agent-memory-workflow/spec.md`
   - Required gates: staged allowlist, `openspec validate --specs --strict`, `openspec validate --changes --strict`, `git diff --cached --check`, GitNexus staged detection.

2. `G2.400 openspec static-analysis code-quality spec acceptance / spec-authorized`
   - Scope: `openspec/specs/code-quality/spec.md`
   - Keep separate from broker/QMT and API integration specs.

3. `G2.401 openspec api-integration pinia store spec acceptance / spec-authorized`
   - Scope: `openspec/specs/api-integration/spec.md`
   - Confirm it remains an active spec update, not an active-change package continuation.

4. `G2.402 openspec broker-qmt active-spec safety preflight / no-source`
   - Scope:
     - `openspec/specs/architecture-governance/spec.md`
     - `openspec/specs/trading-execution-safety/spec.md`
     - the 9 broker/QMT untracked spec directories listed above
   - Goal: decide whether to accept as one broker execution safety package or split into broker truth / miniQMT / Windows qmt subpackages.

5. `G2.403 openspec independent untracked spec-addition preflight / no-source`
   - Scope:
     - `codex-task-looping`
     - `containerized-runtime-deployment`
     - `frontend-audit-orchestration`
     - `kronos-integration-contract`
     - `portfolio-attribution-analysis`

## Residual Notes

The untracked G2 reports remain worklog artifacts and are not part of this spec residual inventory.

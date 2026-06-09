# G2.402 OpenSpec broker-QMT active-spec safety preflight / no-source

## Boundary

Mode: `no-source`.

Scope is limited to the broker/QMT spec residual cluster:

- `openspec/specs/architecture-governance/spec.md`
- `openspec/specs/trading-execution-safety/spec.md`
- `openspec/specs/broker-acknowledgement-reconciliation/spec.md`
- `openspec/specs/broker-truth-channel-topology/spec.md`
- `openspec/specs/miniqmt-live-bridge-runtime/spec.md`
- `openspec/specs/miniqmt-primary-broker-adapter-runtime/spec.md`
- `openspec/specs/windows-qmt-agent-contract-acceptance/spec.md`
- `openspec/specs/windows-qmt-agent-live-contract/spec.md`
- `openspec/specs/windows-qmt-agent-reference-service/spec.md`
- `openspec/specs/windows-qmt-contract-formal-sequence/spec.md`
- `openspec/specs/windows-qmt-service-readiness-probe/spec.md`

This node only reviews package boundaries. It does not edit, restore, delete, stage, or commit any file.

Explicitly out of scope:

- Non-broker untracked specs.
- Frontend/backend/source/test/runtime files.
- Worklog report commits.

## Evidence Summary

- Current HEAD: `4e5641bf3 docs(openspec): add pinia api integration contract`.
- Staged files during preflight: 0.
- Scope status:
  - 2 tracked modified specs: `architecture-governance`, `trading-execution-safety`.
  - 9 untracked broker/QMT specs.
- `openspec validate --specs --strict`: 47 passed, 0 failed.
- `openspec validate --changes --strict`: 16 passed, 0 failed.
- PostHog flush network noise appears in OpenSpec stderr, but validation exit status is 0.

## Scope Metrics

| File | Status | Requirements | Scenarios | Primary theme |
|---|---|---:|---:|---|
| `architecture-governance/spec.md` | `M` | 14 | 17 | Broker execution truth registry. |
| `trading-execution-safety/spec.md` | `M` | 10 | 24 | Broker-facing readiness, live bridge, remote Windows qmt, audit and acknowledgement boundaries. |
| `broker-acknowledgement-reconciliation/spec.md` | `??` | 4 | 8 | Local-to-external identity, lifecycle event identity, reconciliation divergence. |
| `broker-truth-channel-topology/spec.md` | `??` | 3 | 6 | Primary/supplemental broker roles and channel-scoped correlation. |
| `miniqmt-live-bridge-runtime/spec.md` | `??` | 4 | 8 | miniQMT live bridge submission, result retrieval, identity echo, escalation. |
| `miniqmt-primary-broker-adapter-runtime/spec.md` | `??` | 4 | 8 | miniQMT primary submission, outcome classification, deferred lifecycle re-entry. |
| `windows-qmt-agent-contract-acceptance/spec.md` | `??` | 3 | 3 | Local Windows qmt contract acceptance harness. |
| `windows-qmt-agent-live-contract/spec.md` | `??` | 4 | 8 | Authenticated Windows qmt execute/result contract and failure boundary. |
| `windows-qmt-agent-reference-service/spec.md` | `??` | 5 | 9 | Dedicated reference service, auth/versioning, task registry, provider modes. |
| `windows-qmt-contract-formal-sequence/spec.md` | `??` | 4 | 5 | Formal acceptance sequence and manifest artifacts. |
| `windows-qmt-service-readiness-probe/spec.md` | `??` | 3 | 4 | Read-only readiness probe and L1/L2/L3 verdict semantics. |

## Coupling Assessment

The cluster is one domain, but it has three natural subpackages:

1. Broker truth foundation
   - Defines the shared language for broker acknowledgement, broker truth, identity binding, channel topology, and reconciliation.
   - `architecture-governance` and `trading-execution-safety` both rely on this vocabulary.

2. miniQMT runtime contracts
   - Defines miniQMT primary adapter and live bridge runtime boundaries.
   - Depends conceptually on broker truth foundation but can be accepted as a separate runtime subpackage.

3. Windows qmt contracts
   - Defines Windows qmt acceptance, live contract, reference service, formal sequence, and readiness probe.
   - Depends conceptually on broker truth foundation and overlaps with the readiness/fail-closed scenarios added to `trading-execution-safety`.

## Decision

Do not accept all 11 files as one bulk spec commit.

Although the files are semantically related and all validate together, a single 11-file acceptance would combine foundation governance, miniQMT runtime semantics, and Windows qmt readiness/acceptance semantics. That is too dense for a source-authorized package.

Recommended split:

- First accept the broker truth foundation package.
- Then accept miniQMT runtime contracts.
- Then accept Windows qmt contracts.

This keeps the same domain together while preserving reviewable commit boundaries.

## Recommended Next Nodes

1. `G2.403 openspec broker truth foundation spec acceptance / spec-authorized`
   - Scope:
     - `openspec/specs/architecture-governance/spec.md`
     - `openspec/specs/trading-execution-safety/spec.md`
     - `openspec/specs/broker-acknowledgement-reconciliation/spec.md`
     - `openspec/specs/broker-truth-channel-topology/spec.md`
   - Required gates:
     - staged path allowlist
     - `openspec validate --specs --strict`
     - `openspec validate --changes --strict`
     - `git diff --cached --check`
     - GitNexus staged detection

2. `G2.404 openspec miniqmt runtime contract spec acceptance / spec-authorized`
   - Scope:
     - `openspec/specs/miniqmt-live-bridge-runtime/spec.md`
     - `openspec/specs/miniqmt-primary-broker-adapter-runtime/spec.md`

3. `G2.405 openspec windows qmt contract spec acceptance / spec-authorized`
   - Scope:
     - `openspec/specs/windows-qmt-agent-contract-acceptance/spec.md`
     - `openspec/specs/windows-qmt-agent-live-contract/spec.md`
     - `openspec/specs/windows-qmt-agent-reference-service/spec.md`
     - `openspec/specs/windows-qmt-contract-formal-sequence/spec.md`
     - `openspec/specs/windows-qmt-service-readiness-probe/spec.md`

## Residual Notes

The non-broker untracked specs remain outside this preflight and should continue through the independent spec-addition line from `G2.398`.

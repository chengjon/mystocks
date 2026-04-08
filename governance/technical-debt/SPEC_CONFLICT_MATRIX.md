# Spec Conflict Matrix

## Legend

- Status: `open` | `triage` | `in_review` | `accepted` | `closed`
- Impact: `low` | `medium` | `high`

| ID | Area | Conflict Summary | Impact | Owner | Status | Next Action | Target Date |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SC-001 | Entry Docs | Repository entry docs historically repeated governance rules instead of pointing at `architecture/STANDARDS.md` | high | main | accepted | Keep entry docs reference-only and bridge to `STANDARDS.md` | 2026-04-08 |
| SC-002 | Task Boards | Root `TASK.md` / `TASK-REPORT.md` and `docs/reports/tasks/*` can be mistaken for the same truth source | high | main | accepted | Mark `docs/reports/tasks/*` as historical and bridge to canonical governance directory | 2026-04-08 |
| SC-003 | Governance Location | Governance artifacts existed in sidecar and archive paths but not in one live canonical directory | high | main | accepted | Publish `governance/technical-debt/` as the single live location | 2026-04-08 |
| SC-004 | Metrics | Historical governance reports mixed current observations with frozen baselines | high | main | closed | Weekly cadence, rollups, and current retirement-readiness audits now separate `measured`, `inferred`, `historical_baseline`, and optional `target` facts | 2026-04-08 |
| SC-005 | Migration Closure | Migration exit criteria were enforced in standards but not linked from governance execution artifacts | high | main | closed | Governance SoT, cadence, and migration-oriented governance records now cite explicit migration-closeout fields and `architecture/STANDARDS.md` | 2026-04-08 |
| SC-006 | Compatibility Layers | Shim and compatibility retirement rules were not surfaced in governance artifacts | high | main | closed | Governance cadence and records now cite compatibility-surface and shim-retirement requirements explicitly | 2026-04-08 |
| SC-007 | Cleanup Authorization | Some cleanup planning docs relied on narrative context without explicit code-path and function-tree sources | high | main | closed | Current retirement-readiness audits and the governance cadence now require and demonstrate both verdict layers before any deletion recommendation | 2026-04-08 |
| SC-008 | Deletion Evidence | Deletion gate behavior is canonical in OpenSpec, but many cleanup readers start from runbooks or reports | medium | main | closed | Deletion runbook and governance-record guidance now explicitly subordinate themselves to `openspec/specs/directory-governance/spec.md` and the machine-truth registries | 2026-04-09 |
| SC-009 | Historical Task Reports | `docs/reports/tasks/TASK-T01..T10` remain discoverable without a canonical replacement pointer | medium | main | accepted | Add canonical pointer to `governance/technical-debt/INDEX.md` | 2026-04-08 |
| SC-010 | Archived Sidecars | `archive/legacy-root-archived/governance/technical-debt/*` contains draft truth that is no longer live | medium | main | accepted | Preserve for audit only and point readers to the new live directory | 2026-04-08 |
| SC-011 | Baseline Usage | `reports/analysis/tech-debt-baseline.json` is authoritative but not always cited in governance docs | medium | main | closed | SoT, weekly rollup, and governance audits now label the baseline as `historical_baseline` rather than current measured truth | 2026-04-08 |
| SC-012 | Governance Board Semantics | Historical governance board used task IDs that drifted from the active OpenSpec execution line | medium | main | accepted | Seed a new canonical board aligned with `tech-debt-governance-2026q1` | 2026-04-08 |
| SC-013 | OpenSpec State | `tech-debt-governance-2026q1` had partial sidecar implementation without canonical artifact convergence | high | main | accepted | Complete live artifacts and update change tasks | 2026-04-08 |
| SC-014 | Index Discoverability | `docs/INDEX.md` and technical-debt indexes did not surface the canonical governance baseline | medium | main | accepted | Add quick links to the governance directory | 2026-04-08 |
| SC-015 | Measurement Evidence | Weekly reports sometimes inferred status from file presence instead of real measurements | medium | main | closed | Canonical cadence and governance records now require explicit evidence sources, and historical no-evidence drafts are marked as unverified context only | 2026-04-08 |
| SC-016 | Temporary Artifacts | Mechanical splits, temporary entrypoints, and backup files lacked one governance inventory path | medium | main | closed | `governance/technical-debt/TEMPORARY_ARTIFACT_INVENTORY.md` now serves as the canonical class-level review inventory | 2026-04-08 |
| SC-017 | Root Coordination vs Governance | Mainline Mongo coordination snapshots and governance execution tracking served different audiences but shared similar filenames | high | main | accepted | Bridge instead of replace; keep operational and governance concerns separate | 2026-04-08 |
| SC-018 | Cleanup Readiness | Deletion readiness often appears in reports without linking exact registry paths for approval evidence | medium | main | in_review | Keep exact registry paths in governance references and task templates | 2026-04-17 |
| SC-019 | Live Capability Promotion | `architecture-governance` was previously represented only in the active change and is now promoted into the live spec set | medium | main | closed | Keep the live capability in `openspec/specs/architecture-governance/spec.md` and treat the archived change as historical traceability only | 2026-04-08 |
| SC-020 | Ownership Freshness | Older governance drafts used `TBD` owners, weakening auditability | medium | main | accepted | Seed owner and DDL fields across the canonical board and register | 2026-04-08 |

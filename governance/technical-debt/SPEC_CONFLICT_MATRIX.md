# Spec Conflict Matrix

## Legend

- Status: `open` | `triage` | `in_review` | `accepted` | `closed`
- Impact: `low` | `medium` | `high`

| ID | Area | Conflict Summary | Impact | Owner | Status | Next Action | Target Date |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SC-001 | Entry Docs | Repository entry docs historically repeated governance rules instead of pointing at `architecture/STANDARDS.md` | high | main | accepted | Keep entry docs reference-only and bridge to `STANDARDS.md` | 2026-04-08 |
| SC-002 | Task Boards | Root `TASK.md` / `TASK-REPORT.md` and `docs/reports/tasks/*` can be mistaken for the same truth source | high | main | accepted | Mark `docs/reports/tasks/*` as historical and bridge to canonical governance directory | 2026-04-08 |
| SC-003 | Governance Location | Governance artifacts existed in sidecar and archive paths but not in one live canonical directory | high | main | accepted | Publish `governance/technical-debt/` as the single live location | 2026-04-08 |
| SC-004 | Metrics | Historical governance reports mixed current observations with frozen baselines | high | main | in_review | Enforce `measured` vs `inferred` vs `historical_baseline` labels in weekly cadence docs | 2026-04-15 |
| SC-005 | Migration Closure | Migration exit criteria were enforced in standards but not linked from governance execution artifacts | high | main | in_review | Bridge governance board to migration closure rules in `architecture/STANDARDS.md` | 2026-04-16 |
| SC-006 | Compatibility Layers | Shim and compatibility retirement rules were not surfaced in governance artifacts | high | main | in_review | Add retirement-rule references to cadence and debt register | 2026-04-16 |
| SC-007 | Cleanup Authorization | Some cleanup planning docs relied on narrative context without explicit code-path and function-tree sources | high | main | in_review | Require both verdict sources in governance debt items and cleanup tasks | 2026-04-17 |
| SC-008 | Deletion Evidence | Deletion gate behavior is canonical in OpenSpec, but many cleanup readers start from runbooks or reports | medium | main | triage | Keep runbooks linked but subordinate to `openspec/specs/directory-governance/spec.md` | 2026-04-18 |
| SC-009 | Historical Task Reports | `docs/reports/tasks/TASK-T01..T10` remain discoverable without a canonical replacement pointer | medium | main | accepted | Add canonical pointer to `governance/technical-debt/INDEX.md` | 2026-04-08 |
| SC-010 | Archived Sidecars | `archive/legacy-root-archived/governance/technical-debt/*` contains draft truth that is no longer live | medium | main | accepted | Preserve for audit only and point readers to the new live directory | 2026-04-08 |
| SC-011 | Baseline Usage | `reports/analysis/tech-debt-baseline.json` is authoritative but not always cited in governance docs | medium | main | in_review | Make it explicit in SoT and weekly cadence docs | 2026-04-15 |
| SC-012 | Governance Board Semantics | Historical governance board used task IDs that drifted from the active OpenSpec execution line | medium | main | accepted | Seed a new canonical board aligned with `tech-debt-governance-2026q1` | 2026-04-08 |
| SC-013 | OpenSpec State | `tech-debt-governance-2026q1` had partial sidecar implementation without canonical artifact convergence | high | main | accepted | Complete live artifacts and update change tasks | 2026-04-08 |
| SC-014 | Index Discoverability | `docs/INDEX.md` and technical-debt indexes did not surface the canonical governance baseline | medium | main | accepted | Add quick links to the governance directory | 2026-04-08 |
| SC-015 | Measurement Evidence | Weekly reports sometimes inferred status from file presence instead of real measurements | medium | main | open | Require evidence paths and explicit evidence class for each metric | 2026-04-19 |
| SC-016 | Temporary Artifacts | Mechanical splits, temporary entrypoints, and backup files lacked one governance inventory path | medium | main | open | Add these classes to the debt register for explicit review | 2026-04-20 |
| SC-017 | Root Coordination vs Governance | Mainline Mongo coordination snapshots and governance execution tracking served different audiences but shared similar filenames | high | main | accepted | Bridge instead of replace; keep operational and governance concerns separate | 2026-04-08 |
| SC-018 | Cleanup Readiness | Deletion readiness often appears in reports without linking exact registry paths for approval evidence | medium | main | in_review | Keep exact registry paths in governance references and task templates | 2026-04-17 |
| SC-019 | Live Capability Promotion | `architecture-governance` is represented in the active change but not yet promoted to a live spec | medium | main | open | Archive the change after adoption review and publish live capability spec | 2026-04-22 |
| SC-020 | Ownership Freshness | Older governance drafts used `TBD` owners, weakening auditability | medium | main | accepted | Seed owner and DDL fields across the canonical board and register | 2026-04-08 |

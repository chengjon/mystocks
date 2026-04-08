# Debt Register

## Legend

- Severity: `low` | `medium` | `high` | `critical`
- Status: `open` | `in_progress` | `blocked` | `done`

| ID | Area | Description | Severity | Owner | DDL | Status | Next Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TD-001 | Governance | Canonical `technical_debt/governance/` directory was missing | high | main | 2026-04-08 | done | Keep future governance artifacts in this directory only |
| TD-002 | Discoverability | Historical `docs/reports/tasks/*` artifacts could be mistaken for live governance truth | high | main | 2026-04-08 | done | Keep historical note and canonical bridge in indexes |
| TD-003 | Metrics | Governance reporting lacked hard separation between measured, inferred, and historical-baseline metrics | high | main | 2026-04-15 | in_progress | Apply the taxonomy in the next weekly rollup |
| TD-004 | Compatibility Retirement | Compatibility layer and shim retirement rules were not linked from governance artifacts | high | main | 2026-04-16 | in_progress | Add explicit references in cadence and task templates |
| TD-005 | Migration Exit | Migration completion and exit criteria were not surfaced in governance execution artifacts | high | main | 2026-04-16 | in_progress | Tie governance review steps back to `architecture/STANDARDS.md` |
| TD-006 | Cleanup Evidence | Cleanup readiness decisions were not consistently tied to both code-path and function-tree verdicts | high | main | 2026-04-17 | in_progress | Require both sources in deletion-related task work |
| TD-007 | Ownership | Previous governance task drafts used `TBD` owner and DDL fields | medium | main | 2026-04-08 | done | Keep owner and DDL fields mandatory on the canonical board |
| TD-008 | Indexing | Technical debt indexes did not expose a canonical governance baseline path | medium | main | 2026-04-08 | done | Maintain links from `docs/INDEX.md` and debt indexes |
| TD-009 | Capability Promotion | `architecture-governance` is still an active change, not a live archived capability | medium | main | 2026-04-22 | open | Archive the change after adoption review |
| TD-010 | Weekly Cadence | Weekly governance cadence had templates but no canonical kickoff location | medium | main | 2026-04-11 | in_progress | Publish the first rollup in `technical_debt/governance/TASK-REPORT.md` |
| TD-011 | Historical Sidecars | Archived sidecar governance docs remain available and can cause reader drift | low | main | 2026-04-20 | open | Add retirement notes when those paths are indexed or cited |
| TD-012 | Mainline Semantics | Root `TASK.md` and governance task boards share names but not semantics | medium | main | 2026-04-08 | done | Keep bridge text in root task docs |
| TD-013 | Baseline Context | The baseline JSON exists, but not all governance reports cite it as frozen historical context | medium | main | 2026-04-15 | in_progress | Require baseline citation in weekly reports |
| TD-014 | Temporary Artifacts | Mechanical splits, temporary entrypoints, and backup files are governed by standards but not tracked as a debt class | medium | main | 2026-04-19 | open | Add review inventory for temporary artifacts in a future wave |
| TD-015 | Narrative-Only Status | Some older governance reports inferred progress from narrative text instead of explicit evidence links | medium | main | 2026-04-19 | open | Keep evidence-path fields mandatory on board and report templates |

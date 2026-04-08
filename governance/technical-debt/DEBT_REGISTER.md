# Debt Register

## Legend

- Severity: `low` | `medium` | `high` | `critical`
- Status: `open` | `in_progress` | `blocked` | `done`

| ID | Area | Description | Severity | Owner | DDL | Status | Next Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TD-001 | Governance | Canonical `governance/technical-debt/` directory was missing | high | main | 2026-04-08 | done | Keep future governance artifacts in this directory only |
| TD-002 | Discoverability | Historical `docs/reports/tasks/*` artifacts could be mistaken for live governance truth | high | main | 2026-04-08 | done | Keep historical note and canonical bridge in indexes |
| TD-003 | Metrics | Governance reporting lacked hard separation between measured, inferred, and historical-baseline metrics | high | main | 2026-04-15 | done | Keep future governance rollups using the evidence-labeled metric blocks from the canonical cadence |
| TD-004 | Compatibility Retirement | Compatibility layer and shim retirement rules were not linked from governance artifacts | high | main | 2026-04-16 | done | Keep future governance reviews citing the canonical migration checklist and `architecture/STANDARDS.md` |
| TD-005 | Migration Exit | Migration completion and exit criteria were not surfaced in governance execution artifacts | high | main | 2026-04-16 | done | Keep migration-closeout fields explicit in governance records and audits |
| TD-006 | Cleanup Evidence | Cleanup readiness decisions were not consistently tied to both code-path and function-tree verdicts | high | main | 2026-04-17 | done | Keep future deletion-readiness reviews citing both verdict layers before approval |
| TD-007 | Ownership | Previous governance task drafts used `TBD` owner and DDL fields | medium | main | 2026-04-08 | done | Keep owner and DDL fields mandatory on the canonical board |
| TD-008 | Indexing | Technical debt indexes did not expose a canonical governance baseline path | medium | main | 2026-04-08 | done | Maintain links from `docs/INDEX.md` and debt indexes |
| TD-009 | Capability Promotion | `architecture-governance` promotion was pending until the governance baseline change was archived and promoted into live spec truth | medium | main | 2026-04-22 | done | Keep future governance changes updating `openspec/specs/architecture-governance/spec.md` directly |
| TD-010 | Weekly Cadence | Weekly governance cadence had templates but no canonical kickoff location | medium | main | 2026-04-11 | done | Keep Friday rollups landing in `governance/technical-debt/TASK-REPORT.md` |
| TD-011 | Historical Sidecars | Archived sidecar governance docs remain available and can cause reader drift | low | main | 2026-04-20 | done | Keep historical indexes and cited sidecar reports carrying explicit retirement notes and canonical redirect paths |
| TD-012 | Mainline Semantics | Root `TASK.md` and governance task boards share names but not semantics | medium | main | 2026-04-08 | done | Keep bridge text in root task docs |
| TD-013 | Baseline Context | The baseline JSON exists, but not all governance reports cite it as frozen historical context | medium | main | 2026-04-15 | done | Keep baseline references explicitly labeled as `historical_baseline` in future rollups and audits |
| TD-014 | Temporary Artifacts | Mechanical splits, temporary entrypoints, and backup files are governed by standards but not tracked as a debt class | medium | main | 2026-04-19 | done | Keep `governance/technical-debt/TEMPORARY_ARTIFACT_INVENTORY.md` as the canonical class-level review inventory |
| TD-015 | Narrative-Only Status | Some older governance reports inferred progress from narrative text instead of explicit evidence links | medium | main | 2026-04-19 | done | Keep canonical governance records requiring explicit evidence sources, and mark historical no-evidence drafts as unverified context only |

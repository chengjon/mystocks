## 1. Implementation

- [x] 1.1 Extend the collaboration specification and runtime docs to define the dedicated transcript ledger boundary, including `work_item_id`-required ingest.
- [x] 1.2 Add transcript session, event, hot-body, and legacy-index records to the collaboration store model and Mongo backend.
- [x] 1.3 Add CLI / service entrypoints for transcript session start, block append, session close, and transcript query/export flows.
- [x] 1.4 Add archive backend abstraction plus a filesystem-backed default implementation for immutable transcript body sealing.
- [x] 1.5 Add explicit failure-state events and compensation-event support so transcript correction never mutates prior audit records.
- [x] 1.6 Add hot-retention expiration handling so full transcript body export degrades after 90 days while audit metadata remains queryable.
- [x] 1.7 Add migration tooling that scans historical `AUTO` / `MANUAL` markdown blocks and creates only legacy audit indexes plus archive references.
- [x] 1.8 Add focused unit / integration coverage for ingest gates, append-only behavior, export degradation after 90 days, archive failure semantics, and legacy index migration.
- [x] 1.9 Update operator guidance so `TASK-REPORT.md` remains summary-first while explicit session export becomes the controlled path for full-body access.

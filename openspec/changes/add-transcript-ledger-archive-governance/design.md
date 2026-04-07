## Context

> **设计方案说明**:
> 本文件用于记录某项变更的设计思路、结构拆分、实现取舍或技术路径，属于方案设计层材料。
> 它不是共享规则正文，也不直接代表当前仓库已落地状态；落地判断应结合 `architecture/STANDARDS.md`、对应 proposal/tasks、审批结果与实际代码验证。


MyStocks now treats Mongo as the source of truth for active work items, updates, requests, and
status views. However, `AUTO` / `MANUAL` session transcripts remain outside that model:

- historical transcript blocks live in archived markdown
- new transcript behavior is not specified
- there is no contract for retention, export, archive sealing, or correction

The design must preserve the existing control-plane boundary:

- Mongo control plane remains authoritative for work lifecycle
- transcript handling must not overload existing `work_events`
- audit integrity must outrank convenience exports

## Goals

- Introduce a dedicated transcript ledger for new `AUTO` / `MANUAL` session transcripts.
- Require every transcript to resolve to a concrete `work_item_id`.
- Preserve an append-only audit chain in Mongo indefinitely.
- Allow full transcript body export only during a 90-day hot window.
- Seal transcript bodies into immutable cold archives through a pluggable archive backend.
- Keep legacy transcript history readable and auditable without large-scale body migration.

## Non-Goals

- Do not redesign the existing work-item/update/request/status control plane.
- Do not move transcript truth into `TASK-REPORT.md`.
- Do not backfill historical transcript bodies into new Mongo transcript events.
- Do not bind the archive design to a single long-term storage vendor.
- Do not introduce a web UI in this change.

## Decisions

### 1. Add a dedicated transcript ledger instead of extending `work_events`

Transcript data is materially different from control-plane automation events:

- it is larger
- it has hot/cold body retention rules
- it is queried by session and time ranges
- it requires compensation semantics rather than mutable correction

The design therefore adds a dedicated transcript subsystem alongside, but separate from, the
existing control plane.

### 2. Every transcript must belong to a work item

New transcript ingestion is valid only when the system can resolve a concrete `work_item_id`.

If no work item exists, the system rejects ingest rather than creating a free-floating session log.
This keeps transcript auditability anchored to task accountability.

### 3. Use three transcript-facing persistence surfaces

#### 3.1 Authoritative ledger in Mongo

Permanent Mongo truth covers:

- `transcript_session`
- `transcript_event`
- immutable archive references / manifests
- compensation records

This layer is append-only and permanently retained.

#### 3.2 Hot body access tier

Recent transcript bodies are stored for online access during a 90-day hot window:

- full body blocks are available for explicit session export
- this layer exists for operational convenience, not long-term truth

#### 3.3 Cold archive backend

Archived transcript bodies are sealed into an abstract archive backend.

The interface is pluggable, but the first implementation uses a filesystem archive directory
because it is simple, reliable, and easy to migrate later.

### 4. Model transcript data with dedicated collections / records

The minimal design introduces:

- `transcript_session`
  - `session_id`
  - `work_item_id`
  - `actor_cli`
  - `branch`
  - `transcript_kind`
  - `started_at`
  - `closed_at`
  - `archive_policy_version`
- `transcript_event`
  - `event_id`
  - `session_id`
  - `work_item_id`
  - `event_type`
  - `sequence_no`
  - `occurred_at`
  - `payload`
- `transcript_body_hot`
  - `body_id`
  - `session_id`
  - `event_id`
  - `content`
  - `checksum`
  - `available_until`
- `transcript_legacy_index`
  - `legacy_index_id`
  - `work_item_id`
  - `source_artifact`
  - `legacy_block_kind`
  - `legacy_session_label`
  - `captured_at`
  - `source_anchor`
  - `archive_locator`
  - `checksum`
  - `migration_batch_id`
  - `migration_recorded_at`

If archive metadata later grows large, the system may add a separate archive manifest read model,
but the audit truth remains in `transcript_event`.

### 5. Fix the event taxonomy up front

The base event set is:

- `transcript.session_started`
- `transcript.block_appended`
- `transcript.session_closed`
- `transcript.body_archived`
- `transcript.hot_body_expired`
- `transcript.compensation_recorded`

Operational failure / control events are also first-class:

- `transcript.hot_body_write_failed`
- `transcript.archive_pending`
- `transcript.archive_write_failed`
- `transcript.archive_write_retried`
- `transcript.archive_write_succeeded`
- `transcript.ingest_rejected`

This ensures the system never hides degraded states behind implicit behavior.

### 6. Enforce append-only semantics

The authoritative ledger never updates or deletes prior transcript records.

Corrections, redactions, or operator clarifications must append a compensation event referencing the
affected prior event. Views may honor compensation rules, but the underlying audit chain remains
unchanged.

### 7. Separate permanent audit truth from temporary body access

The lifecycle is:

1. append transcript events to the authoritative ledger
2. write recent body content into the hot tier
3. seal immutable archive body / manifest
4. record the archive reference in the ledger
5. after 90 days, drop default online body access while retaining the ledger and archive reference

The design does not treat hot-body expiry as deletion of truth. It is a downgrade of online access
scope, recorded through an appended event.

### 8. Default exports are audit-first, not body-first

By default:

- `TASK-REPORT.md` does not inline complete transcript bodies
- task-level exports show transcript metadata, event summaries, archive state, and compensation state
- explicit session export may return full body only inside the 90-day hot window
- after 90 days, exports show the permanent audit chain and archive reference, not the complete body

This preserves the priority order:

- audit completeness
- debugging usability
- knowledge retention

### 9. Legacy transcript migration is index-only

Historical `AUTO` / `MANUAL` blocks are not backfilled as synthetic new ledger events.

Instead, migration creates:

- a legacy transcript audit index
- a stable archive reference back to the read-only historical artifact

This preserves historical fidelity and avoids the risk of fabricating event order or body ownership
after the fact.

## Archive Backend Contract

The design standardizes an archive backend interface without binding the implementation to one
storage target.

Minimum operations:

- `seal_session(session_id, chunks, metadata) -> archive_result`
- `stat(locator) -> archive_status`
- `retrieve_metadata(locator) -> archive_metadata`

The first implementation binds this interface to a filesystem archive directory configured by the
runtime profile.

## Query and Export Model

The system exposes three first-class retrieval modes:

- work-item audit view
  - returns transcript session summaries, event summaries, hot/cold availability, compensation state
- session view
  - returns full session metadata and, when still hot, the complete transcript body
- actor/time-window operational view
  - returns session indexes and event summaries without default full-body expansion

Export modes are similarly separated:

- audit export
  - audit chain only
- session export
  - full body only during hot retention
- work report export
  - transcript summary only by default

## Failure Semantics

The design distinguishes:

- ledger write failure
  - transcript ingest is rejected; no body-only success is allowed
- hot body write failure
  - ledger may succeed, but the failure is itself recorded as an event
- archive write failure
  - session remains in an `archive_pending` / failed state until sealed successfully

This preserves an auditable record of degraded states.

## Risks / Trade-offs

- Additional collections and query surfaces increase implementation scope relative to simply
  extending `work_events`.
  - Mitigation: keep the first cut small and CLI-first.
- Dual persistence of hot bodies and cold archives can drift if sealing semantics are underspecified.
  - Mitigation: require checksum-based sealing records and archive success events.
- Operators may expect full transcript content in `TASK-REPORT.md`.
  - Mitigation: codify that report exports are summary-first and require explicit session export for
    full body access.

## Migration Plan

1. Approve the transcript ledger boundary and archive policy.
2. Add transcript ledger schema and CLI surfaces for new transcript ingest / query / export.
3. Add archive backend interface and filesystem default implementation.
4. Add explicit hot-window expiry handling.
5. Scan historical markdown transcript blocks and build legacy indexes plus archive references only.
6. Update documentation so new transcripts must use the ledger-managed path.

## Open Questions

- None for this design pass. The approved policy decisions are:
  - append-only ledger
  - compensation-only correction model
  - 90-day hot body retention
  - pluggable archive backend with filesystem default
  - no historical body backfill

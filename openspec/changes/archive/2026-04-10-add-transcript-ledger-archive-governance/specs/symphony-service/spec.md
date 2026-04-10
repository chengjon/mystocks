## ADDED Requirements

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


### Requirement: Work-Scoped Transcript Ledger

The system SHALL record new `AUTO` / `MANUAL` session transcripts in a dedicated transcript ledger
that is scoped to a single `work_item_id`, rather than storing transcript truth in exported markdown
artifacts or in the generic control-plane event stream.

#### Scenario: Reject transcript ingest without a work item

- **WHEN** an operator or automation attempts to record a new transcript without a valid
  `work_item_id`
- **THEN** the system rejects the ingest attempt
- **AND** it does not create transcript ledger records

#### Scenario: Keep transcript data separate from generic control-plane events

- **WHEN** the system records transcript activity for a work item
- **THEN** it writes transcript audit data to dedicated transcript ledger records
- **AND** existing generic `work_events` remain reserved for control-plane and automation events

### Requirement: Append-Only Transcript Audit Chain

The system SHALL preserve transcript audit truth as an append-only event chain in Mongo and SHALL
use compensation events instead of in-place update or deletion for transcript correction, redaction,
or clarification.

#### Scenario: Append transcript activity without mutation

- **WHEN** transcript session activity is recorded
- **THEN** the system appends new transcript events with ordered sequence numbers
- **AND** it does not modify or delete prior authoritative transcript events

#### Scenario: Correct transcript view with compensation events

- **WHEN** an operator needs to correct, redact, or clarify previously recorded transcript content
- **THEN** the system appends a compensation event referencing the earlier transcript event
- **AND** the authoritative prior event remains preserved in the audit chain

### Requirement: Transcript Body Retention and Archive Sealing

The system SHALL retain full transcript body content for online access during a 90-day hot window,
and SHALL preserve long-term transcript recoverability through immutable archive references after
that window expires.

#### Scenario: Export complete transcript body inside the hot window

- **WHEN** a transcript session is queried or explicitly exported within 90 days of capture
- **THEN** the system can return the complete transcript body from the hot access tier
- **AND** the permanent audit chain remains stored in Mongo

#### Scenario: Degrade body access after the hot window

- **WHEN** a transcript session ages beyond the 90-day hot retention window
- **THEN** the system retains transcript audit metadata and append-only events in Mongo
- **AND** it returns an immutable archive reference for the full body
- **AND** it no longer returns the complete transcript body by default

#### Scenario: Use a pluggable archive backend with a filesystem default

- **WHEN** the system seals transcript bodies for cold retention
- **THEN** it uses a pluggable archive backend interface
- **AND** the first implementation uses a filesystem-backed archive directory as the default backend

### Requirement: Transcript Query and Export Boundaries

The system SHALL keep transcript queries and exports audit-first by default, while allowing explicit
session-level full-body export only when the transcript body is still within the hot retention
window.

#### Scenario: Keep task reports summary-first

- **WHEN** an operator exports or reads a task-level report such as `TASK-REPORT.md`
- **THEN** the report shows transcript session summaries, event summaries, compensation state, and
  archive references by default
- **AND** it does not inline complete transcript bodies by default

#### Scenario: Allow explicit session export during hot retention

- **WHEN** an operator explicitly requests session-level transcript export for a still-hot session
- **THEN** the system may return the complete transcript body
- **AND** the export remains bound to the session and work item that own the transcript

### Requirement: Legacy Transcript Indexing Without Body Backfill

The system SHALL preserve historical `AUTO` / `MANUAL` transcript blocks through audit indexing and
archive references without backfilling their full bodies into the new transcript ledger event model.

#### Scenario: Index historical transcript blocks without synthesizing new events

- **WHEN** the system migrates historical transcript markdown artifacts created before transcript
  ledger cutover
- **THEN** it creates legacy transcript audit indexes and archive references for those historical
  blocks
- **AND** it does not fabricate new append-only transcript body events from the historical text

#### Scenario: Distinguish legacy and ledger-managed transcript views

- **WHEN** an operator queries transcript history for a work item that spans both historical and
  ledger-managed transcript eras
- **THEN** the system distinguishes legacy indexed transcript records from ledger-managed transcript
  sessions
- **AND** both remain traceable back to the owning `work_item_id`

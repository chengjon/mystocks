# Transcript Ledger And Archive Governance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a dedicated work-scoped transcript ledger for new `AUTO` / `MANUAL` sessions, keep the audit chain append-only in Mongo, support 90-day hot body access plus immutable cold archive references, and preserve historical transcript blocks through index-only migration.

**Architecture:** Keep the existing Mongo control plane (`work_item`, `work_update`, `work_request`, `work_event`, `worker_status_view`) intact and add transcript-specific records, services, and CLI surfaces beside it. New transcript truth lives in dedicated transcript collections and services; `TASK-REPORT.md` remains a summary/export surface, while full transcript bodies are available only through explicit session export during the hot retention window.

**Tech Stack:** Python 3.12, Pydantic models, MongoDB collections/indexes, argparse CLI, filesystem-backed archive adapter, pytest unit tests, OpenSpec validation.

---

## Inputs

- Approved OpenSpec change: `openspec/changes/add-transcript-ledger-archive-governance/`
- Design constraints already fixed:
  - every transcript requires `work_item_id`
  - append-only authoritative audit chain in Mongo
  - correction/redaction only through compensation events
  - full transcript body hot retention for 90 days
  - immutable cold archive references
  - pluggable archive backend with filesystem default
  - historical transcript blocks are index-only migrations, not body backfills

## Task 1: Extend the Store Schema for Transcript Records

**Files:**
- Modify: `src/services/maestro/collab/store/models.py`
- Modify: `src/services/maestro/collab/store/base.py`
- Modify: `src/services/maestro/collab/backends/mongo/indexes.py`
- Modify: `src/services/maestro/collab/backends/mongo/store.py`
- Modify: `tests/unit/maestro_collab/test_mongo_store.py`
- Modify: `tests/unit/maestro_collab/test_coordination_service.py`

- [ ] **Step 1: Write failing store tests for transcript persistence primitives**

Add failing cases in `tests/unit/maestro_collab/test_mongo_store.py` that expect the store to persist and sort:

```python
TranscriptSessionRecord(...)
TranscriptEventRecord(..., sequence_no=1, ...)
TranscriptHotBodyRecord(..., available_until=...)
TranscriptLegacyIndexRecord(...)
```

Cover uniqueness and ordering expectations:
- session lookup by `session_id`
- transcript event ordering by `sequence_no` and `occurred_at`
- hot-body lookup by `session_id`
- legacy index lookup by `work_item_id`

- [ ] **Step 2: Extend the in-memory fake store used by service tests**

Update `tests/unit/maestro_collab/test_coordination_service.py` so `_InMemoryCollaborationStore` can hold the new transcript collections without falling back to `dict[str, Any]` shortcuts.

- [ ] **Step 3: Add transcript record models**

Extend `src/services/maestro/collab/store/models.py` with explicit frozen models:

```python
class TranscriptSessionRecord(_FrozenModel): ...
class TranscriptEventRecord(_FrozenModel): ...
class TranscriptHotBodyRecord(_FrozenModel): ...
class TranscriptLegacyIndexRecord(_FrozenModel): ...
```

Use exact datetime fields for retention and ordering:
- `started_at`
- `closed_at`
- `occurred_at`
- `available_until`
- `migration_recorded_at`

- [ ] **Step 4: Extend the store protocol and Mongo backend**

Add transcript-specific methods to `CollaborationStore` and implement them in `MongoCollaborationStore`, for example:

```python
def upsert_transcript_session(...)
def get_transcript_session(...)
def append_transcript_event(...)
def list_transcript_events(...)
def upsert_transcript_hot_body(...)
def get_transcript_hot_body(...)
def append_transcript_legacy_index(...)
def list_transcript_legacy_indexes(...)
```

Also add new Mongo collections and index definitions in `indexes.py`.

- [ ] **Step 5: Run store-layer verification**

Run:

```bash
PYTHONPATH=. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/unit/maestro_collab/test_mongo_store.py tests/unit/maestro_collab/test_coordination_service.py -q -o addopts=''
```

Expected:
- new transcript persistence assertions pass
- no regression in existing work-item/update/request/event tests

- [ ] **Step 6: Commit**

```bash
git add src/services/maestro/collab/store/models.py src/services/maestro/collab/store/base.py src/services/maestro/collab/backends/mongo/indexes.py src/services/maestro/collab/backends/mongo/store.py tests/unit/maestro_collab/test_mongo_store.py tests/unit/maestro_collab/test_coordination_service.py
git commit -m "feat[maestro-collab]: add transcript store records"
```

## Task 2: Add the Transcript Ledger Service and Authorization Gates

**Files:**
- Create: `src/services/maestro/collab/services/transcript_ledger.py`
- Modify: `src/services/maestro/collab/services/__init__.py`
- Modify: `src/services/maestro/collab/authz/policy.py`
- Modify: `tests/unit/maestro_collab/test_coordination_service.py`
- Create: `tests/unit/services/maestro/test_transcript_ledger_service.py`

- [ ] **Step 1: Write failing service tests for transcript lifecycle rules**

Create `tests/unit/services/maestro/test_transcript_ledger_service.py` with failing tests for:
- reject ingest when `work_item_id` does not exist
- allow `session_started` only once per `session_id`
- append block with increasing `sequence_no`
- reject block append after `session_closed`
- append compensation event without mutating earlier events

- [ ] **Step 2: Extend authorization checks**

In `src/services/maestro/collab/authz/policy.py`, add explicit transcript permissions that reuse work-item visibility rules instead of creating a second ACL system:

```python
def require_can_append_transcript(...)
def require_can_export_transcript(...)
```

- [ ] **Step 3: Implement the transcript service**

Create `TranscriptLedgerService` in `src/services/maestro/collab/services/transcript_ledger.py` with focused methods:

```python
start_session(...)
append_block(...)
close_session(...)
record_compensation(...)
get_session(...)
list_session_events(...)
```

The service should:
- validate `work_item_id`
- append audit events only
- write hot-body records separately
- never mutate prior authoritative transcript events

- [ ] **Step 4: Export the service cleanly**

Update `src/services/maestro/collab/services/__init__.py` so downstream callers can import:

```python
from src.services.maestro.collab.services import TranscriptLedgerService
```

- [ ] **Step 5: Run service-layer verification**

Run:

```bash
PYTHONPATH=. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/unit/services/maestro/test_transcript_ledger_service.py tests/unit/maestro_collab/test_coordination_service.py -q -o addopts=''
```

Expected:
- transcript lifecycle and permission tests pass
- existing coordination audit tests remain green

- [ ] **Step 6: Commit**

```bash
git add src/services/maestro/collab/services/transcript_ledger.py src/services/maestro/collab/services/__init__.py src/services/maestro/collab/authz/policy.py tests/unit/services/maestro/test_transcript_ledger_service.py tests/unit/maestro_collab/test_coordination_service.py
git commit -m "feat[maestro-collab]: add transcript ledger service"
```

## Task 3: Add CLI Surfaces for Transcript Ingest, Query, and Export

**Files:**
- Modify: `scripts/runtime/maestro_collab.py`
- Modify: `scripts/runtime/coordctl.py`
- Modify: `tests/unit/runtime/test_maestro_coordination_cli.py`

- [ ] **Step 1: Write failing CLI tests**

Extend `tests/unit/runtime/test_maestro_coordination_cli.py` with cases for a new `transcript` command group:

```text
transcript start
transcript append
transcript close
transcript show-session
transcript export-session
transcript index-legacy
```

Verify JSON output shape and required-argument enforcement.

- [ ] **Step 2: Extend the CLI facade**

Add transcript-facing methods to `_MongoCoordinationFacade` so parser handlers can call a stable interface instead of embedding business logic inside argparse branches.

- [ ] **Step 3: Add parser and handler branches**

Update `scripts/runtime/maestro_collab.py` to:
- register the `transcript` subparser family
- parse transcript metadata and body payloads
- delegate to `TranscriptLedgerService`
- enforce explicit output modes (`json` / `text`)

`scripts/runtime/coordctl.py` should continue delegating without adding extra behavior.

- [ ] **Step 4: Run CLI verification**

Run:

```bash
PYTHONPATH=. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/unit/runtime/test_maestro_coordination_cli.py tests/unit/services/maestro/test_transcript_ledger_service.py -q -o addopts=''
```

Expected:
- transcript CLI flows pass
- existing work/update/export CLI tests still pass

- [ ] **Step 5: Commit**

```bash
git add scripts/runtime/maestro_collab.py scripts/runtime/coordctl.py tests/unit/runtime/test_maestro_coordination_cli.py
git commit -m "feat[maestro-collab]: add transcript CLI commands"
```

## Task 4: Implement Archive Backends and Hot/Cold Retention Lifecycle

**Files:**
- Create: `src/services/maestro/collab/transcript_archive.py`
- Modify: `src/services/maestro/profiles/mystocks.py`
- Modify: `src/services/maestro/collab/services/transcript_ledger.py`
- Create: `tests/unit/services/maestro/test_transcript_archive.py`
- Modify: `tests/unit/services/maestro/test_transcript_ledger_service.py`

- [ ] **Step 1: Write failing archive and retention tests**

Create `tests/unit/services/maestro/test_transcript_archive.py` for:
- filesystem archive sealing success
- archive manifest / checksum capture
- retryable archive failure

Add service tests that expect:
- `transcript.body_archived`
- `transcript.archive_pending`
- `transcript.archive_write_failed`
- `transcript.hot_body_expired`

- [ ] **Step 2: Add a pluggable archive backend interface**

Create `src/services/maestro/collab/transcript_archive.py` with a small abstraction:

```python
class TranscriptArchiveBackend(Protocol): ...
class FilesystemTranscriptArchiveBackend: ...
```

The filesystem implementation should seal session output into a deterministic archive directory and return immutable locators plus checksums.

- [ ] **Step 3: Add runtime defaults for archive location / policy version**

Extend `src/services/maestro/profiles/mystocks.py` with transcript archive defaults, such as:
- archive backend kind
- filesystem archive root
- hot retention days
- archive policy version

- [ ] **Step 4: Wire archive sealing and expiry into the service**

Update `TranscriptLedgerService` so:
- session close can trigger archive sealing
- archive success appends `transcript.body_archived`
- archive failure appends explicit failure events
- expiry is expressed by appending `transcript.hot_body_expired`, not by mutating audit truth

- [ ] **Step 5: Run archive / retention verification**

Run:

```bash
PYTHONPATH=. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/unit/services/maestro/test_transcript_archive.py tests/unit/services/maestro/test_transcript_ledger_service.py -q -o addopts=''
```

Expected:
- archive adapter and failure semantics pass
- hot-retention downgrade remains append-only

- [ ] **Step 6: Commit**

```bash
git add src/services/maestro/collab/transcript_archive.py src/services/maestro/profiles/mystocks.py src/services/maestro/collab/services/transcript_ledger.py tests/unit/services/maestro/test_transcript_archive.py tests/unit/services/maestro/test_transcript_ledger_service.py
git commit -m "feat[maestro-collab]: add transcript archive lifecycle"
```

## Task 5: Add Summary-First Query and Export Behavior

**Files:**
- Modify: `scripts/runtime/export_collab_snapshots.py`
- Modify: `scripts/runtime/maestro_collab.py`
- Modify: `tests/unit/runtime/test_collab_migration_scripts.py`
- Modify: `tests/unit/runtime/test_maestro_coordination_cli.py`
- Modify: `tests/unit/services/maestro/test_task_report_graphiti_projection.py`

- [ ] **Step 1: Write failing export tests**

Add cases that expect:
- `TASK-REPORT.md` shows transcript summary metadata, not full body by default
- explicit session export can return full body within the 90-day window
- expired sessions show audit chain and archive reference only

- [ ] **Step 2: Extend snapshot rendering**

Update `render_task_report_markdown()` in `scripts/runtime/export_collab_snapshots.py` to render a compact transcript summary section, for example:

```markdown
## Transcripts
- session_id / actor_cli / kind / started_at / hot_body=yes|no / archive_ref
```

Do not inline complete transcript body in default task-level exports.

- [ ] **Step 3: Add explicit session export behavior**

Update CLI handlers so `transcript export-session` can:
- emit complete body while `available_until` has not expired
- emit summary plus archive locator after expiration

- [ ] **Step 4: Run export verification**

Run:

```bash
PYTHONPATH=. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/unit/runtime/test_collab_migration_scripts.py tests/unit/runtime/test_maestro_coordination_cli.py tests/unit/services/maestro/test_task_report_graphiti_projection.py -q --no-cov -o addopts=''
```

Expected:
- default task report export remains summary-first
- transcript-specific export respects hot/cold boundaries

- [ ] **Step 5: Commit**

```bash
git add scripts/runtime/export_collab_snapshots.py scripts/runtime/maestro_collab.py tests/unit/runtime/test_collab_migration_scripts.py tests/unit/runtime/test_maestro_coordination_cli.py tests/unit/services/maestro/test_task_report_graphiti_projection.py
git commit -m "feat[maestro-collab]: add transcript export boundaries"
```

## Task 6: Add Legacy Transcript Index Migration and Operator Guidance

**Files:**
- Create: `scripts/runtime/migrate_transcript_legacy_indexes.py`
- Create: `tests/unit/runtime/test_transcript_legacy_migration.py`
- Modify: `docs/guides/multi-cli-tasks/MULTI_CLI_WORKTREE_MANAGEMENT.md`
- Modify: `docs/guides/governance/FEATURE_MANAGEMENT_WORKFLOW.md`
- Modify: `openspec/changes/add-transcript-ledger-archive-governance/tasks.md`

- [ ] **Step 1: Write failing migration tests**

Create `tests/unit/runtime/test_transcript_legacy_migration.py` that parses historical `AUTO` / `MANUAL` blocks from archived markdown and asserts:
- body text is not inserted into new transcript event collections
- legacy index records are created with archive references
- historical records remain distinguishable from ledger-managed sessions

- [ ] **Step 2: Implement index-only migration tooling**

Create `scripts/runtime/migrate_transcript_legacy_indexes.py` to:
- scan archived markdown artifacts
- resolve owning `work_item_id`
- create `TranscriptLegacyIndexRecord`
- create stable archive locators / checksums
- never synthesize `transcript.block_appended` events from historical body text

- [ ] **Step 3: Update operator documentation**

Update the guides so operators know:
- new transcripts must be ledger-managed and work-scoped
- `TASK-REPORT.md` remains summary-first
- full body retrieval is an explicit session export during the 90-day hot window
- historical transcript blocks are legacy indexed, not replayed into the new ledger

- [ ] **Step 4: Reflect implementation completion in the OpenSpec task list**

When the work is actually complete, update `openspec/changes/add-transcript-ledger-archive-governance/tasks.md` from unchecked to checked items. Do not mark tasks complete early.

- [ ] **Step 5: Run migration and documentation verification**

Run:

```bash
PYTHONPATH=. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/unit/runtime/test_transcript_legacy_migration.py tests/unit/runtime/test_collab_migration_scripts.py -q --no-cov -o addopts=''

openspec validate add-transcript-ledger-archive-governance --strict
```

Expected:
- legacy transcript migration stays index-only
- OpenSpec change remains valid after doc updates

- [ ] **Step 6: Commit**

```bash
git add scripts/runtime/migrate_transcript_legacy_indexes.py tests/unit/runtime/test_transcript_legacy_migration.py docs/guides/multi-cli-tasks/MULTI_CLI_WORKTREE_MANAGEMENT.md docs/guides/governance/FEATURE_MANAGEMENT_WORKFLOW.md openspec/changes/add-transcript-ledger-archive-governance/tasks.md
git commit -m "feat[maestro-collab]: add legacy transcript indexing"
```

## Final Verification

- [ ] **Step 1: Run the focused end-to-end transcript verification batch**

```bash
PYTHONPATH=. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/unit/maestro_collab/test_mongo_store.py tests/unit/maestro_collab/test_coordination_service.py tests/unit/runtime/test_maestro_coordination_cli.py tests/unit/runtime/test_collab_migration_scripts.py tests/unit/runtime/test_transcript_legacy_migration.py tests/unit/services/maestro/test_transcript_ledger_service.py tests/unit/services/maestro/test_transcript_archive.py tests/unit/services/maestro/test_task_report_graphiti_projection.py -q --no-cov -o addopts=''
```

Expected:
- transcript ledger, archive, export, and legacy-index behaviors all pass together

- [ ] **Step 2: Re-run strict spec validation**

```bash
openspec validate add-transcript-ledger-archive-governance --strict
```

Expected:
- change remains valid after implementation and doc updates

- [ ] **Step 3: Export and inspect a sample task report**

Run:

```bash
python scripts/runtime/coordctl.py work export-task-report 2026-04-03-root-task-artifact-mongo-cutover-main --output-path /tmp/transcript-ledger-task-report.md --output json
sed -n '1,220p' /tmp/transcript-ledger-task-report.md
```

Expected:
- task report remains summary-first
- transcript summaries appear without dumping full body by default

- [ ] **Step 4: Prepare completion note**

Summarize:
- collections / services / CLI commands added
- hot/cold retention behavior
- archive backend default
- legacy index migration scope
- any deferred follow-up work

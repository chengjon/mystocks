# Change: Sequence backend architecture unblocks behind explicit OpenSpec gates

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why

The current codebase map execution work established a governance baseline, but the next practical architecture moves are not all at the same readiness level.

One line item is a runtime unblock: the `web/backend/app/api/data_lineage.py` import chain initially reached `web/backend/app/api/_data_lineage_responses.py`, where `@asynccontextmanager` was used without importing it. That missing transitive import prevented `app.main` import from succeeding in the current checkout. Implementation then exposed the same split-helper import-time pattern in additional route/helper modules, so the approved runtime unblock batch is scoped to low-risk import, export, and route-composition repairs that directly block `app.main` import or `test_health_route_conflicts.py` collection.

Other items are not immediate code edits:

- schema dual-directory consolidation needs compatibility verification before any directory removal
- singleton lifecycle work needs a better pilot strategy than searching for a "clean" low-risk service
- codebase-map facts still need consistency updates so old live-count language does not look current
- runtime route/OpenAPI refresh must wait until the import chain is healthy

This change creates a sequenced OpenSpec path so the team can execute the work in the right order without losing the original architecture goals.

## What Changes

- Add a governance requirement that runtime unblock evidence must be restored before broad route/OpenAPI or architecture-batch claims are made
- Add a governance requirement that schema dual-directory cleanup must preserve compatibility until canonical exports and consumer migration are verified
- Add a governance requirement that singleton lifecycle work starts from interface/test-double classification rather than a presumed low-risk pilot
- Add a governance requirement that codebase-map evidence must distinguish historical counts from current-head truth
- Add a sequencing plan for:
  - minimal runtime unblock
  - schema shim closure
  - runtime evidence refresh
  - later service-seam / lifecycle proposals

## Impact

- Affected specs:
  - `architecture-governance`
- Affected code, when implementation is approved:
  - `web/backend/app/api/_data_lineage_responses.py`
  - route/helper modules recorded in `docs/reports/quality/backend-sequence-runtime-unblock-implementation-2026-05-20.md`
  - `web/backend/app/api/data_lineage.py`
  - `web/backend/app/schema/`
  - `web/backend/app/schemas/`
  - `web/backend/app/services/`
  - `docs/reports/quality/` evidence artifacts and codebase-map references
- Affected workflows:
  - runtime smoke collection
  - route/OpenAPI evidence capture
  - singleton lifecycle batching
  - codebase-map freshness and evidence indexing

## Scope Boundaries

- This change does not approve backend implementation on its own.
- This change does not authorize Core Batch 2.
- This change does not authorize issue15 publication.
- This change does not authorize deleting `app/schema/` until compatibility is proved.

## Success Criteria

- The runtime unblock step is isolated from the schema cleanup step
- The runtime unblock step may repair direct import-time split-helper blockers discovered by `app.main` smoke, but it must not become a broad route refactor or business behavior migration
- The schema cleanup step is isolated from the singleton lifecycle proposal step
- The codebase map accurately labels historical evidence, current-head evidence, and stale snapshots
- The OpenSpec tasks provide an implementation order that preserves the original architecture goals

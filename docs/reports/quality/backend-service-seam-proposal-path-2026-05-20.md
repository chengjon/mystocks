# Backend Service Seam Proposal Path - 2026-05-20

> **历史文档说明**:
> 本文件是 `sequence-backend-architecture-unblocks` Task 6.x 的治理记录。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: proposal path defined; no service lifecycle implementation authorized
- Change lane: `sequence-backend-architecture-unblocks`
- OpenSpec directory: `openspec/changes/sequence-backend-architecture-unblocks/`
- Related future candidate: `define-backend-service-seams-and-singleton-pilots`
- HEAD: `7b097fffd`
- Branch: `wip/root-dirty-20260403`
- Code changes in this task: none

## Current Inventory Evidence

Current heuristic inventory artifact:

- `.planning/codebase/generated/service-singleton-inventory-2026-05-20.json`

Summary:

| Field | Value |
|-------|-------|
| service Python files scanned | `152` |
| candidate files with singleton-like or lifecycle-relevant patterns | `140` |
| no singleton pattern detected | `12` |
| external-client wrapper bucket | `69` |
| DB/session-backed bucket | `24` |
| cache/task-running bucket | `17` |
| interface/test-double candidate needing review | `28` |
| separate design gate bucket | `2` |

Pattern totals in the heuristic scan:

| Pattern | Count |
|---------|-------|
| `get_*` functions | `281` |
| async `get_*` functions | `96` |
| module-level instance / service / client / manager / cache / adapter assignments | `71` |
| private module-level assignments | `111` |
| `lru_cache` / cache decorators | `4` |

The inventory is intentionally heuristic. It is useful for routing and candidate discovery, not for deleting
code or selecting an implementation pilot without follow-up review.

Comparability note: this report's `candidate_files=140` is not a direct regression from the 2026-05-19
singleton lifecycle routing matrix count of `111`. The 2026-05-20 inventory uses a broader
lifecycle-relevant heuristic over `web/backend/app/services/**/*.py`, including additional getter, module
instance, private instance, and cache patterns. Treat the two numbers as different scan methods unless a
future normalized scanner is introduced.

Current `separate_design_gate` bucket contents from the JSON artifact:

| File | Class |
|------|-------|
| `web/backend/app/services/stock_search_service/stock_search_service.py` | `StockSearchService` |
| `web/backend/app/services/technical_pattern_detection_service.py` | `TechnicalPatternDetectionService` |

## Dirty Worktree Guard

The service directory is not clean. The current path-limited service status contains `18` entries, including
modified service files and deleted backup files. This report therefore does not select a concrete migration
pilot.

The next service-seam action must either run in a clean worktree or explicitly account for those service
changes before treating the inventory as implementation-ready.

## Routing Decision

The 2026-05-19 singleton lifecycle routing matrix found no clean low-risk stateless pilot. The current
heuristic scan does not overturn that conclusion. It only refines the next strategy:

1. Do not search for a "clean pilot" by filename alone.
2. First extract a service seam inventory into interface/test-double candidates versus stateful services.
3. Exclude external-client wrappers, DB/session-backed services, cache/task-running services, and separate
   design-gate modules from generic lifecycle batches.
4. Only after a clean candidate is selected and approved should a separate implementation plan modify service
   code.

## Bucket Policy

| Bucket | Policy |
|--------|--------|
| External-client wrapper | Keep in a wrapper/external-client lane; do not mix with ordinary stateless service DI batches |
| DB/session-backed service | Treat as stateful; requires explicit transaction/session lifetime design before migration |
| Cache/task-running service | Treat as stateful; requires cache/task ownership and shutdown semantics before migration |
| Interface/test-double candidate needing review | Candidate discovery only; must be manually reviewed for side effects, imports, route consumers, and tests |
| Separate design gate | Keep out of generic batches; current artifact members are `StockSearchService` and `TechnicalPatternDetectionService` |

Prior cross-line exclusions such as `realtime_mtm` and `adapter_loader` remain outside ordinary service
lifecycle batches, but they are not members of the current `separate_design_gate` bucket because this
artifact scans `web/backend/app/services/**/*.py`.

## Proposal Path

If this line proceeds, create a separate OpenSpec proposal only after human approval:

- Change ID candidate: `define-backend-service-seams-and-singleton-pilots`
- Proposal scope:
  - define service seam taxonomy
  - select one clean interface/test-double candidate
  - specify test double / dependency injection boundary
  - define rollback criteria
  - preserve #78 adapter lifecycle and #79 service lifecycle separation
- Non-goals:
  - no generic singleton replacement batch
  - no migration of current `separate_design_gate` members, separately excluded `realtime_mtm` / `adapter_loader`
    concerns, DB/session-backed services, cache/task-running services, or external-client wrappers
  - no source edits under the evidence-package lane

## Review Absorption

The paired review file `docs/reports/quality/backend-service-seam-proposal-path-2026-05-20-review.md`
was evaluated after this report was created.

| Review item | Disposition |
|-------------|-------------|
| OpenSpec change lane reported missing | Current worktree check shows `openspec/changes/sequence-backend-architecture-unblocks/` exists; this report now names the directory explicitly |
| `separate_design_gate` examples were wrong | Corrected to the artifact's actual members: `StockSearchService` and `TechnicalPatternDetectionService` |
| `111` versus `140` candidate count needed explanation | Added the scan-method comparability note above |

## Next Gate

Task 6.x is complete when the plan records that service lifecycle work remains proposal-only and that no
new service implementation batch is scheduled from this evidence alone. A concrete service migration requires
a future approved proposal plus a clean, reviewed candidate packet.

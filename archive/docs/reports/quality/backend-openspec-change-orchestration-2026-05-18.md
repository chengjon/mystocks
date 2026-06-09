# Backend OpenSpec Change Orchestration

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> Historical planning artifact. Use current code, `architecture/STANDARDS.md`,
> root `AGENTS.md`, and the latest actual validation results as the execution
> source of truth before implementation.

## Purpose

This document coordinates the four backend OpenSpec drafts created from the
May 2026 backend audit review:

| Change | Scope | Approval status |
|---|---|---|
| `consolidate-backend-api-domain-routers` | Announcement, strategy, risk router governance; trading/backup deferred as follow-up domain ownership decisions | Human approval required |
| `consolidate-backend-health-endpoints` | Health/status endpoint taxonomy and probe compatibility | Human approval required |
| `split-backend-core-modules-with-compatibility-wrappers` | Core import compatibility matrix and wrapper-safe module moves | Human approval required |
| `migrate-backend-singletons-to-lifecycle-di` | Singleton/getter lifecycle classification and pilot DI migration | Human approval required |

The purpose is to prevent independently valid proposals from colliding on
shared router, OpenAPI, Core import, lifecycle, and rollback surfaces.

## Source Evidence

- `docs/reports/quality/backend-openspec-drafts-mattpocock-review-2026-05-18.md`
- `docs/reports/quality/backend-route-table-openapi-baseline-2026-05-18.md`
- `docs/reports/quality/backend-route-table-duplicate-routes-mattpocock-review-2026-05-18.md`
- `docs/reports/quality/generated/backend-fullpath-route-table.md`
- `docs/reports/quality/backend-audit-documents-review-2026-05-15.md`

## Shared Prerequisites

| Prerequisite | Artifact / command | Blocks |
|---|---|---|
| Local decorator route baseline | `docs/reports/quality/backend-route-table-openapi-baseline-2026-05-18.md` | C, G |
| Prefix-expanded full-path route table | `cd web/backend && python ../../scripts/dev/backend_audit_fullpath_routes.py ../../docs/reports/quality/generated` | C, G |
| Full-path route artifact | `docs/reports/quality/generated/backend-fullpath-route-table.md` and `.json` | C, G |
| OpenAPI baseline | `python scripts/generate_openapi.py --output docs/reports/quality/generated/openapi-before.json` | C, G |
| Core import compatibility inventory | F `tasks.md` section 1 | F implementation, E shared-Core implementation |
| Singleton/getter lifecycle inventory | E `tasks.md` section 1 | E implementation, F moves of lifecycle-owned modules |

## Execution Order

| Order | Work | Reason | May run in parallel |
|---|---|---|---|
| 0 | Approve this orchestration layer and the four OpenSpec drafts | Establishes `Blocked by` relationships before issues are marked `ready-for-agent` | None |
| 1 | Regenerate or confirm route/OpenAPI baselines | C and G both depend on route exposure evidence and OpenAPI contract drift | E inventory, F inventory |
| 2 | Decide G health/status taxonomy | Probe paths affect PM2, monitoring, CI, and route/OpenAPI diff ownership | C domain evidence gathering |
| 3 | Decide C announcement/strategy/risk canonical router contracts and explicitly defer trading/backup implementation | Prevents route ownership ambiguity while keeping high-risk trading/backup duplicates visible | G taxonomy implementation only if route/OpenAPI owner is coordinated |
| 4 | Complete F import compatibility matrix and lifecycle-owned Core module list | E cannot safely migrate dependencies whose import surface may move | E singleton/getter inventory only |
| 5 | Run E first pilot on one low-risk representative candidate | Avoids parallel migration of many singleton classes before lifecycle evidence exists | F low-risk pure-helper move only if not lifecycle-owned |
| 6 | Expand implementation batches one domain/class at a time | Keeps rollback domain-local and evidence reviewable | Only unrelated files/contracts with explicit owner split |

## Shared Surfaces And Owners

| Surface | Primary owner | Secondary reviewer | Rule |
|---|---|---|---|
| `router_registry.py`, `VERSION_MAPPING.py`, registered API paths | C/G route owner | C/G counterpart | Only one route/OpenAPI-changing implementation batch may edit these at a time |
| OpenAPI schema and diff artifacts | C/G route owner | API documentation reviewer | Every route/prefix/response/status/tag/operation-id change needs before/after diff |
| Health/status probe paths | G owner | PM2/monitoring owner | Probe compatibility must be retained until consumer migration is proven |
| `web/backend/app/core/database*`, `cache*`, `security*`, `socketio*`, `logger*` | F owner | E lifecycle owner | F must classify lifecycle-owned modules before moving them |
| Dependency providers, `app.state`, lifespan/shutdown hooks | E owner | F import owner | E must use stable import paths or wrappers from F's matrix |
| Rollback notes | Per-change owner | Reviewer for shared surface | Rollback must be domain-local and cite exact files/routes/providers restored |

## Blocking Matrix

| Item | Blocked by | May become `ready-for-agent` when |
|---|---|---|
| C implementation issues | Route/OpenAPI baselines, C approval, trading/backup deferral decision | Domain-specific `Blocked by` chain is recorded |
| G implementation issues | Route/OpenAPI baselines, G approval, status taxonomy decision | Health/status taxonomy issue is approved |
| E inventory issue | E approval and this orchestration note | Inventory is evidence-only and does not mutate lifecycle |
| E implementation batches | E inventory, lifecycle classification, F import matrix for shared Core modules | One low-risk pilot is selected |
| F import matrix issue | F approval and this orchestration note | Inventory scope and output path are named |
| F move batches | F import matrix, lifecycle-owned module list, rollback notes | Batch touches one Core domain and has import smoke |
| Trading router implementation | New OpenSpec follow-up | C records it as deferred, not hidden in current scope |
| Backup router implementation | New OpenSpec follow-up | C records it as deferred, not hidden in current scope |

## Allowed Parallel Batches

- Evidence-only route/OpenAPI regeneration can run in parallel with E and F
  inventories.
- E singleton/getter inventory can run in parallel with F import inventory.
- C announcement/strategy/risk consumer matrices can run in parallel with G
  health/status consumer matrix if they do not edit code.
- Implementation batches may run in parallel only when they do not touch the
  same route registry, OpenAPI contract, Core module, dependency provider,
  lifespan hook, or smoke/rollback artifact.

## Not Ready For Implementation

The four OpenSpec drafts are valid for approval review, but implementation is
not unlocked until:

- This orchestration document is accepted.
- C explicitly includes or defers trading and backup route ownership.
- G explicitly includes `GET /status` taxonomy.
- C/G use prefix-expanded final full-path route evidence, not only local
  decorator duplicates.
- E and F share lifecycle/import ownership rules for Core modules.
- Each implementation issue has a concrete verification command or named script.

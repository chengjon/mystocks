# Backend EnhancedDataService Getter Retirement Authorization - 2026-05-25

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.98 EnhancedDataService getter-retirement authorization
Status: ready for review

## Purpose

Authorize only a future, source-capable G2.99 branch to retire the public
compatibility getter `get_enhanced_data_service` from
`web/backend/app/services/data_service_enhanced.py`.

This packet does not modify source code, tests, routes, OpenAPI exposure, PM2
state, OpenSpec changes, frontend assets, or GitHub issue labels. It exists to
separate the getter-retirement decision from implementation.

## Input State

G2.97 was accepted through PR `#250`, merged at
`dfb1dce27c0501b7eb855e478e68b82db4959d9d`.

G2.97 selected `get_enhanced_data_service` only as a future authorization
candidate because:

- route/API references are `0`;
- focused test references are `0`;
- package export references are `0`;
- GitNexus impact is LOW with impacted count `3` and affected processes `0`.

## Current Evidence

Current HEAD for this packet:
`dfb1dce27c0501b7eb855e478e68b82db4959d9d`.

| Check | Result |
|---|---|
| GitNexus index | `gitnexus analyze --with-gitignore`; `62,748` nodes, `145,908` edges, `3,283` clusters, `300` flows |
| GitNexus impact | `get_enhanced_data_service`: LOW, impacted count `3`, direct `1`, affected processes `0` |
| GitNexus context | getter has module-local incoming reference only; no outgoing refs; no process participation |
| `get_enhanced_data_service` scan | `1` app file, `2` refs total: definition at line `580` and module-local `__main__` smoke call at line `592` |
| Route/API refs | `0` |
| Focused test refs | `0` |
| Package export refs | `0` |
| `EnhancedDataService` scan | `2` files, `9` refs total; class remains active through `web/backend/app/api/v1/system/health.py` |
| `_enhanced_data_service` scan | `1` file, `5` refs total; private state is tied to the public getter |

The active runtime path must not be confused with the compatibility getter:

- `web/backend/app/api/v1/system/health.py` imports `EnhancedDataService`
  directly.
- `web/backend/app/api/v1/system/health.py` constructs
  `EnhancedDataService(auto_fetch=False, use_cache=False)` through its own
  `_get_data_service()` helper.
- No route/API path imports or calls `get_enhanced_data_service`.

## Authorized Future Scope

If this G2.98 packet is reviewed and accepted, G2.99 may be created as a
source-capable implementation branch with this maximum scope:

| Path | Future allowed action |
|---|---|
| `web/backend/app/services/data_service_enhanced.py` | Remove only `get_enhanced_data_service`; remove `_enhanced_data_service` only if it becomes unused; replace the module-local `__main__` smoke call with direct `EnhancedDataService` construction or remove only that obsolete smoke dependency |
| `web/backend/tests/test_enhanced_data_service_getter_retirement.py` | Add a focused static/import regression test proving the public getter is absent while `EnhancedDataService` remains importable |
| `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md` | Record implementation status after the branch runs |
| `.planning/codebase/generated/enhanced-data-service-getter-retirement-implementation-2026-05-25.json` | Record generated implementation evidence |
| `docs/reports/quality/backend-enhanced-data-service-getter-retirement-implementation-2026-05-25.md` | Record implementation evidence |
| `governance/mainline/task-cards/pr-252.yaml` | Record implementation task-card gate if PR numbering remains sequential |

Future G2.99 must remain a getter-retirement branch. It must not delete
`EnhancedDataService`, migrate the system health route, alter response models,
change OpenAPI exposure, edit frontend code, touch PM2 state, or change issue
labels.

## Required Future G2.99 Verification

Before any source edit:

1. Read `architecture/STANDARDS.md`.
2. Run GitNexus impact/context for `get_enhanced_data_service`.
3. Add the focused regression test first and verify red state.

After the minimal source edit:

1. Verify the focused test is green.
2. Run `ruff check` and `black --check` on touched backend files.
3. Run the route/OpenAPI smoke if the import path changes or if `app.main`
   import could be affected.
4. Stage only authorized paths and run GitNexus `detect_changes` with
   `scope=staged`.
5. Run the mainline scope gate and markdown governance gate for updated
   governance artifacts.

## Boundary

This packet makes no source or test changes and does not authorize any immediate
implementation.

Explicitly out of scope:

- deleting `EnhancedDataService`;
- editing `web/backend/app/api/v1/system/health.py` in this authorization
  packet;
- changing routes, response models, response shapes, or OpenAPI exposure;
- changing frontend, PM2, OpenSpec changes/specs, GitHub issue labels, or
  readiness state;
- broadening future G2.99 beyond the getter-retirement seam without a separate
  authorization packet.

## Next Gate

Human review / PR merge decision for this G2.98 authorization packet.

If accepted, create G2.99 as a source-capable implementation branch and apply
TDD red/green before retiring `get_enhanced_data_service`.

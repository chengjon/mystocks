# Backend Wencai Compatibility Getter Retirement Authorization - 2026-05-25

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.94 Wencai getter-retirement authorization
Status: ready for review

## Purpose

Authorize the exact scope for a future G2.95 implementation branch to remove the
unused public compatibility getter `get_wencai_service`.

This packet is authorization-only. It does not change backend source, tests,
routes, OpenAPI exposure, PM2 state, OpenSpec content, frontend files, or issue
labels.

## Input State

| Field | Value |
|---|---|
| Worktree | `.worktrees/g2-94-wencai-getter-retirement-authorization` |
| Branch | `g2-94-wencai-getter-retirement-authorization` |
| Current HEAD | `d8e1d14440d4db21a43b8dd50586f0deef383081` |
| HEAD subject | `docs(governance): refresh service lifecycle candidates (#246)` |
| Parent PR | `#246`, `MERGED`, merge commit `d8e1d14440d4db21a43b8dd50586f0deef383081` |
| Parent evidence | `backend-service-lifecycle-candidate-refresh-after-advanced-analysis-2026-05-25.md` |
| GitNexus refresh | `gitnexus analyze --with-gitignore` completed in this worktree |

## Current Evidence

| Signal | Value |
|---|---:|
| `get_wencai_service` definition line | `web/backend/app/services/wencai_service.py:419` |
| `get_wencai_service` app refs | `1` |
| `get_wencai_service` route/API refs | `0` |
| `get_wencai_service` test refs | `0` |
| `get_wencai_service` package export refs | `0` |
| `WencaiService` app refs | `20` |
| `WencaiService` route/API refs | `9` |
| `WencaiService` test refs | `0` |
| GitNexus impact | LOW / impacted count `0` |

GitNexus context for `get_wencai_service` reports no incoming references, no
outgoing references, and no participating processes. The function body only
returns `WencaiService(db=db)`.

## Authorized Future Scope

If this G2.94 packet is reviewed and accepted, G2.95 may be created as a
source-capable implementation branch with this maximum scope:

| Path | Future allowed action |
|---|---|
| `web/backend/app/services/wencai_service.py` | Remove only `get_wencai_service`; keep `WencaiService` and existing direct class usage intact |
| `web/backend/tests/test_wencai_service_getter_retirement.py` | Add a focused static/import regression test proving the public getter is absent while `WencaiService` remains importable |
| `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md` | Record implementation status after the branch runs |
| `.planning/codebase/generated/wencai-compat-getter-retirement-implementation-2026-05-25.json` | Record generated implementation evidence |
| `docs/reports/quality/backend-wencai-compat-getter-retirement-implementation-2026-05-25.md` | Record implementation evidence |
| `governance/mainline/task-cards/pr-248.yaml` | Record implementation task-card gate |

## Required Future G2.95 Verification

G2.95 must not rely on this packet's checks alone. It must rerun:

- GitNexus impact for `get_wencai_service` before source edits.
- TDD red/green:
  - red: focused test fails while `get_wencai_service` is still present;
  - green: focused test passes after removing the public getter.
- `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_wencai_service_getter_retirement.py -q --no-cov --tb=short`.
- `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short`.
- `ruff check` on touched backend source/test paths.
- `git diff --cached --check`.
- staged GitNexus change detection before commit.
- post-commit mainline scope gate.

## Boundary

Out of scope here and in the authorized future G2.95 scope:

- deleting or renaming `WencaiService`;
- changing `web/backend/app/api/wencai.py`;
- changing `web/backend/app/tasks/wencai_tasks.py`;
- changing `src/database/services/database_service.py`;
- changing routes, response models, response shapes, or OpenAPI exposure;
- changing frontend files, generated clients, PM2 state, OpenSpec files, or
  GitHub issue labels.

## Next Gate

Human review / PR merge decision for this authorization packet.

If accepted, create G2.95 as the Wencai getter-retirement implementation branch
before any source edit.

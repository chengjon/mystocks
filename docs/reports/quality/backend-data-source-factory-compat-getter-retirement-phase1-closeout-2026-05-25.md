# Backend DataSourceFactory Compatibility Getter Retirement Phase 1 Closeout - 2026-05-25

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.82 closeout/current-head refresh

Status: ready for review

Branch: `g2-82-data-source-factory-compat-getter-phase1-closeout`

Current HEAD: `c176b9e71dd0fe4fb9df65c1f2c82631a45cfc3d`

Prepared at: `2026-05-25T13:10:00+08:00`

## Purpose

Close out the merged G2.81 implementation and update the steward tree so the
G2.81 function is recorded as accepted against current HEAD.

This packet is governance-only. It does not edit backend source, tests, routes,
OpenAPI exposure, frontend code, runtime/PM2 scripts, OpenSpec changes, package
exports, or GitHub issue labels.

## Merge Evidence

| Item | Value |
|---|---|
| G2.81 PR | `#234` |
| PR state | `MERGED` |
| Merge timestamp | `2026-05-25T05:06:06Z` |
| Merge commit | `c176b9e71dd0fe4fb9df65c1f2c82631a45cfc3d` |
| Implementation commit | `3e2888c4ff89788d512d2dbde64f1e605ae66225` |
| Base branch | `wip/root-dirty-20260403` |

## Current-Head Evidence

| Check | Result |
|---|---|
| `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short` | 5 passed in 1.77s |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | 120 passed in 69.72s |
| OpenAPI smoke with root `.env` loaded | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0` |

Current-head reference scan:

| Metric | Result |
|---|---:|
| Route/API direct `get_data_source_factory()` calls | 0 |
| Service-module exact refs | 1 |
| Service helper public getter calls | 0 |
| Package export mentions | 4 |
| Service private initializer refs | 7 |

The single service-module exact ref is the public compatibility getter
definition itself. Package exports remain intentionally present.

## Steward Decision

G2.81 is accepted as Phase 1 service-internal decoupling.

The current state is:

- private `_get_or_create_data_source_factory()` exists;
- public `get_data_source_factory()` remains a compatibility wrapper;
- service-internal helper fallback calls no longer depend on the public getter;
- route/API direct public getter calls remain `0`;
- package exports remain unchanged.

## Boundary Confirmation

This closeout does not authorize:

- public `get_data_source_factory()` deletion;
- package export removal from
  `web/backend/app/services/data_source_factory/__init__.py`;
- route/API edits;
- route path, response model, response shape, or OpenAPI exposure changes;
- frontend edits;
- runtime or PM2 changes;
- OpenSpec changes;
- GitHub issue-label changes.

## Next Gate

Human review / PR merge decision for this G2.82 closeout.

After this closeout is accepted, any further public getter or package export
retirement still requires a separate source-capable authorization packet with
fresh current-head reference scans and GitNexus impact analysis.

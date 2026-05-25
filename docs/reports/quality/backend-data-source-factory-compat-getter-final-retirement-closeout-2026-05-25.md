# Backend DataSourceFactory Compatibility Getter Final Retirement Closeout - 2026-05-25

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.85 closeout/current-head refresh

Status: ready for review

Branch: `g2-85-data-source-factory-compat-getter-final-retirement-closeout`

Current HEAD: `f31720ec3a891607eec3ce29b27ad1bc80be0a43`

Prepared at: `2026-05-25T15:41:45+08:00`

## Purpose

Close out the merged G2.84 implementation and update the steward tree so the
DataSourceFactory public compatibility getter retirement is recorded as accepted
against current HEAD.

This packet is governance-only. It does not edit backend source, tests, routes,
OpenAPI exposure, frontend code, runtime/PM2 scripts, OpenSpec changes,
dependency providers, private initializers, or GitHub issue labels.

## Merge Evidence

| Item | Value |
|---|---|
| G2.84 PR | `#237` |
| PR URL | `https://github.com/chengjon/mystocks/pull/237` |
| PR state | `MERGED` |
| Merge timestamp | `2026-05-25T05:55:18Z` |
| Merge commit | `f31720ec3a891607eec3ce29b27ad1bc80be0a43` |
| Implementation commit | `cf3085e54` |
| Base branch | `wip/root-dirty-20260403` |

## Current-Head Evidence

| Check | Result |
|---|---|
| `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short` | 5 passed in 2.07s |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | 120 passed in 83.93s |
| touched-path `ruff check` | passed |
| OpenAPI smoke with root `.env` loaded | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0` |
| GitNexus `detect_changes(scope=staged)` | LOW, changed files=`4`, changed symbols=`0`, affected processes=`0` |

Current-head reference scan:

| Metric | Result |
|---|---:|
| Exact public `get_data_source_factory` symbol hits | 3 |
| Production exact public symbol hits | 0 |
| Package export lines | 0 |
| Route/API public symbol hits | 0 |
| `get_data_source_factory_dependency` token count | 51 |
| `_get_or_create_data_source_factory` token count | 13 |

The remaining exact public symbol hits are negative assertions in
`web/backend/tests/test_data_source_factory_lifecycle_di.py`.

## Steward Decision

G2.84 is accepted as the final public compatibility getter retirement.

The current state is:

- public `get_data_source_factory()` no longer exists in the service module;
- the package no longer exports `get_data_source_factory`;
- production exact public getter hits are `0`;
- route/API public getter hits are `0`;
- `get_data_source_factory_dependency()` remains the canonical FastAPI DI
  provider;
- `_get_or_create_data_source_factory()` remains the service-internal
  initializer.

## Known Baseline

`tests/backend/test_data_api_regression.py` still contains existing
historical-route 404 debt for `/api/v1/data/...`. G2.84 did not change that
baseline, and this G2.85 closeout does not reopen it.

## Boundary Confirmation

This closeout does not authorize:

- route/API edits;
- route path, response model, response shape, or OpenAPI exposure changes;
- frontend edits;
- runtime or PM2 changes;
- OpenSpec changes;
- GitHub issue-label changes;
- removing `get_data_source_factory_dependency()`;
- removing `_get_or_create_data_source_factory()`;
- unrelated historical-route test-debt fixes.

## Next Gate

Human review / PR merge decision for this G2.85 closeout.

After this closeout is accepted, the DataSourceFactory public compatibility
getter retirement lane is closed. Any next service lifecycle lane must start
from a separate authorization packet with fresh current-head evidence and a
clear source/test boundary.

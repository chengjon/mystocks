# Backend MarketDataServiceV2 Dashboard Helper Provider Migration Authorization - 2026-05-23

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Workline: G2.31 `MarketDataServiceV2` dashboard helper provider migration authorization
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `f87cb60afd399e16db0142c3eaaa7ab24c3a1ab1`
- Captured at: `2026-05-23T17:43:37+08:00`
- GitHub issue: `#79` remains open with `needs-triage`
- Parent decision: PR `#170` merged at `f87cb60afd399e16db0142c3eaaa7ab24c3a1ab1`
- Scope: authorization and evidence only

Boundary note: this packet authorizes only a future, separate dashboard helper
provider migration implementation branch. It does not authorize backend source
edits, test edits, route edits, OpenAPI changes, OpenSpec changes, issue label
movement, `ready-for-agent` movement, PM2/runtime work, frontend work,
compatibility getter deletion, or implementation inside this PR.

This packet authorizes a future, separate implementation branch to migrate the
remaining dashboard helper `MarketDataServiceV2` consumers from direct
compatibility getter calls to an explicit provider-fed service path. It does
not perform the implementation.

## Boundary

This PR does not edit backend source, tests, runtime behavior, OpenAPI output,
OpenSpec specs, issue labels, PM2 state, frontend files, docs/API examples, or
generated clients.

This packet does not authorize deleting, renaming, privatizing, or changing the
fallback semantics of `get_market_data_service_v2()`. The compatibility getter
remains active after the future dashboard migration because
`install_market_data_service_v2(app, service=None)` still uses it as the default
fallback.

## Parent Evidence

G2.30 classified the current consumers after route-provider DI:

- `market_v2.py` route-local direct getter calls: `0`
- `market_v2.py` provider references: `14`
- `dashboard_data_source.py` direct getter calls: `2`
- `dashboard_data_source.py` compatibility getter import: `1`
- `get_market_data_service_v2()` decision: active dashboard-helper
  compatibility surface
- Next lane selected by G2.30: G2.31 dashboard helper provider migration
  authorization before any source edits

G2.30 was merged by PR `#170` at
`f87cb60afd399e16db0142c3eaaa7ab24c3a1ab1`.

## Current Consumer Snapshot

| File | Current state | Migration relevance |
|---|---|---|
| `web/backend/app/api/market_v2.py` | 13 route handlers receive `MarketDataServiceV2` via `Depends(get_market_data_service_v2_dependency)`; no route-local direct getter calls remain | Already complete for the route surface; do not include in the dashboard helper implementation batch |
| `web/backend/app/api/dashboard_data_source.py` | Imports `get_market_data_service_v2`; `_get_market_overview_data()` calls it once; `prewarm_dashboard_market_overview_cache()` calls it once | Primary future implementation target |
| `web/backend/app/api/dashboard.py` | `/market-overview` and `/health` already use `Depends(get_data_source)`; `/summary` still calls `get_data_source()` inside the route body | Secondary future implementation target so the dashboard source can be provider-fed consistently |
| `web/backend/app/main.py` | Schedules `prewarm_dashboard_market_overview_cache` without passing a service instance | Secondary future implementation target if the prewarm helper receives an injected service |
| `web/backend/app/services/market_data_service_v2.py` | Defines compatibility getter, app-state installer, provider dependency, and state key | Keep current public symbols; future implementation may import existing installer/provider but must not delete fallback behavior |
| `web/backend/tests/test_dashboard_data_source.py` | Existing dashboard source regression coverage exists but does not cover service injection | Focused future test target |
| `web/backend/tests/test_market_data_service_v2_lifecycle_di.py` | Covers provider/installer behavior and fallback semantics | Keep; extend only if implementation changes provider expectations |

## GitNexus Evidence

| Target | Result | Interpretation |
|---|---:|---|
| `get_market_data_service_v2` | CRITICAL; direct impact `15`; processes affected `6`; modules affected `2` | Future implementation must not remove or rename the getter; graph still sees route callers and active dashboard helper callers, so text guards are required before and after implementation |
| `prewarm_dashboard_market_overview_cache` | LOW; direct impact `0` | The prewarm helper itself is narrow, but it is scheduled from `main.py`, so startup smoke remains required |
| `RealBusinessDataSource` | Found in `dashboard_data_source.py`; no graph incoming/outgoing processes reported | Text and route-level tests are more useful than graph impact for this class |

Known GitNexus/text divergence remains: text guards show `market_v2.py` route
direct getter calls are `0`, while graph impact still lists historical route
callers. Future implementation must use both graph impact and exact text guards.

## Authorized Future Implementation Shape

After this authorization packet is reviewed and approved, a separate
implementation branch may:

1. Add an explicit provider-fed construction path for `RealBusinessDataSource`,
   such as constructor injection of `MarketDataServiceV2` or a narrowly scoped
   service-provider callable.
2. Update `get_data_source` so FastAPI dependency resolution can provide
   `MarketDataServiceV2` through `get_market_data_service_v2_dependency`.
3. Update `get_dashboard_summary` to receive the dashboard data source through a
   dependency instead of calling `get_data_source()` inside the route body.
4. Update `prewarm_dashboard_market_overview_cache` so it can receive a service
   instance from the caller.
5. Update `main.py` startup prewarm scheduling only as needed to pass the app
   state installed service or an explicitly installed service to the prewarm
   helper.
6. Add focused tests proving the dashboard source can use an injected
   `MarketDataServiceV2` and that provider/fallback behavior remains intact.

The future implementation must keep `get_market_data_service_v2()` public and
working as the compatibility fallback.

## Future Implementation Allowed Paths

Only the future implementation branch, not this PR, may edit:

- `web/backend/app/api/dashboard_data_source.py`
- `web/backend/app/api/dashboard.py`
- `web/backend/app/main.py`
- `web/backend/tests/test_dashboard_data_source.py`
- `web/backend/tests/test_market_data_service_v2_lifecycle_di.py`
- `docs/reports/quality/backend-market-data-service-v2-dashboard-helper-provider-migration-implementation-*.md`
- `governance/mainline/task-cards/pr-*.yaml`

Any broader source file, route module, OpenAPI schema helper, service package
export, frontend file, PM2 script, or docs/API file requires a new decision
packet.

## Future Implementation Non-Goals

- Do not delete, rename, privatize, or change the return semantics of
  `get_market_data_service_v2()`.
- Do not modify `market_v2.py`; route-provider DI is already complete for this
  lane.
- Do not merge `MarketDataService` and `MarketDataServiceV2`.
- Do not change route paths, operation IDs, response models, OpenAPI examples,
  or API response payload shape.
- Do not migrate unrelated dashboard dependencies.
- Do not add a new OpenSpec change from this packet.
- Do not move issue `#79` or issue `#92` labels from this packet.

## Future Implementation Verification Gate

Before any source edit in the implementation branch:

1. Run GitNexus impact for:
   - `get_market_data_service_v2`
   - `RealBusinessDataSource`
   - `get_data_source`
   - `get_dashboard_summary`
   - `prewarm_dashboard_market_overview_cache`
2. If any new or unexpected HIGH/CRITICAL impact appears outside the known
   getter graph divergence, stop and return to review.

After source edits in the implementation branch:

1. Text guard:
   - `web/backend/app/api/market_v2.py` direct `get_market_data_service_v2()`
     calls remain `0`
   - `web/backend/app/api/dashboard_data_source.py` direct
     `get_market_data_service_v2()` calls become `0`
   - `get_market_data_service_v2()` remains defined in
     `market_data_service_v2.py`
2. Focused tests:
   - `pytest -o addopts= web/backend/tests/test_dashboard_data_source.py web/backend/tests/test_market_data_service_v2_lifecycle_di.py -q --no-cov`
3. Startup smoke:
   - placeholder-env `app.main` import smoke
4. OpenAPI smoke:
   - path count remains explainable
   - duplicate operation IDs remain `0`
5. Lint:
   - `ruff check` on touched backend files
6. Pre-commit:
   - stage exact paths
   - run `gitnexus_detect_changes(scope="staged")`

## Decision

G2.31 authorizes only a future, separate implementation branch for the dashboard
helper provider migration described above.

It does not authorize implementation inside this PR.

The next steward-tree gate is human review of this authorization packet. If
accepted, create G2.32 as the implementation branch with the exact allowed
source/test scope and verification gate above.

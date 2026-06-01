# Backend Data Source Registry Provider Closeout / Residual Refresh

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Gate: G2.292
- Status: for review in future PR `#445`
- Prepared at: `2026-06-01T11:52:20+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `3d161e90547720f4ce95111ea511d3f8dc3174dc`
- Parent gate: G2.291 provider implementation, PR `#444`, merged at `3d161e90547720f4ce95111ea511d3f8dc3174dc`
- OpenSpec change: `migrate-backend-singletons-to-lifecycle-di`

Boundary note: G2.292 is a no-source closeout / residual refresh package. It
does not authorize backend source edits, test edits, route/OpenAPI contract
changes, docs/api artifact edits, frontend/config/script changes, OpenSpec
proposal/spec edits, PM2 commands, runtime state changes, source retirement, or
implementation authorization for the next candidate.

## Closeout Result

G2.291 is accepted/merged and the `data_source_registry.get_manager` provider
lane is closed.

Current scan of `web/backend/app/api/data_source_registry.py` records:

- route-local provider `get_data_source_registry_manager` exists
- direct route-body `get_manager()` calls: `0`
- provider backing `get_manager()` calls: `1`
- `Depends(get_data_source_registry_manager)` bindings: `7`
- data-source registry runtime routes: `16`

Closed target handlers:

| Handler | Direct route-body calls | Provider binding |
|---|---:|---:|
| `search_data_sources` | 0 | 1 |
| `get_category_stats` | 0 | 1 |
| `get_data_source` | 0 | 1 |
| `update_data_source` | 0 | 1 |
| `test_data_source` | 0 | 1 |
| `health_check_data_source` | 0 | 1 |
| `health_check_all_data_sources` | 0 | 1 |

## Verification

Parent PR state:

- PR `#444`: `MERGED`
- merged at: `2026-06-01T03:40:06Z`
- merge commit: `3d161e90547720f4ce95111ea511d3f8dc3174dc`

Focused regression:

```text
PYTHONPATH=web/backend pytest -q web/backend/tests/test_data_source_registry_manager_provider.py --tb=short --no-cov
3 passed in 6.74s
```

Route/OpenAPI smoke with placeholder import-time environment values records:

- FastAPI routes: `548`
- OpenAPI paths: `500`
- duplicate operation IDs: `0`
- data-source registry runtime routes: `16`

The smoke emitted expected import-time service logs and the historical GPU
NumPy fallback warning; these did not affect route/OpenAPI counts.

## Residual Refresh

The post-closeout route/helper residual scan covered:

- `web/backend/app/api`
- `web/backend/app/services`

The scan excluded known closed G2 provider surfaces, the historical
`data_source_config.old.py` compatibility file, the just-closed
`data_source_registry.get_manager` surface, and the already closed
`data_source_config.get_config_manager` provider backing surface.

The filtered scan found `58` active interesting residual names. The highest
remaining non-closed candidate is:

- gate: G2.293
- target family: `get_postgresql_session`
- files:
  - `web/backend/app/api/auth.py`
  - `web/backend/app/api/market/market_data_request.py`
  - `web/backend/app/api/v1/admin/audit.py`
  - `web/backend/app/api/v1/admin/optimization.py`
- active route-body calls: `9`
- classification: cross-domain PostgreSQL session route helper family requiring
  ownership decision before implementation

The next candidate is not selected for implementation. It spans auth, admin,
and market route modules and resolves to two underlying database helper
definitions:

- `Function:web/backend/app/core/database.py:get_postgresql_session`
- `Function:web/backend/app/core/database_factory.py:get_postgresql_session`

GitNexus evidence for the selected next target:

- MCP `context`: `Transport closed`
- MCP `impact`: `Transport closed`
- CLI query found both core/database and core/database_factory definitions
- CLI impact on `Function:web/backend/app/core/database.py:get_postgresql_session`:
  - risk: `CRITICAL`
  - impacted symbols: `67`
  - direct callers: `15`
  - affected processes: `54`
  - affected modules: `12`
  - index status: stale warning
- CLI impact on `Function:web/backend/app/core/database_factory.py:get_postgresql_session`:
  - risk: `LOW`
  - impacted symbols: `4`
  - direct callers: `2`
  - affected processes: `1`
  - affected modules: `1`
  - index status: stale warning

Because the selected next target includes a CRITICAL-impact database helper and
cross-domain route consumers, G2.292 must stop for human review and must not
auto-merge under the limited autopilot rule.

## Deferred / Excluded Residuals

`web/backend/app/api/data_source_config.old.py:get_config_manager` appears in
raw scans but is historical compatibility surface and is not selected from the
active route/helper residual queue.

`web/backend/app/api/data_source_config.py:get_config_manager` currently appears
only as active provider backing after the prior data-source config manager lane
closed. It is not reopened by G2.292.

`get_cache_manager` remains an ambiguous dashboard/cache helper and should stay
deferred until cache ownership is disambiguated.

`get_postgresql_engine` spans industry/concept business routes and pool
monitoring control-plane routes. It should not be batched with
`get_postgresql_session`.

## Decision

G2.292 closes the `data_source_registry.get_manager` provider lane and selects
only the next no-source decision target:

G2.293 no-source `get_postgresql_session` ownership / route-provider decision.

G2.292 does not authorize G2.293 implementation. G2.293 must classify route
ownership, database helper ownership, security/auth boundaries, test scope,
OpenAPI behavior, and GitNexus blast radius before any future authorization
package.

## Evidence

- `.planning/codebase/generated/data-source-registry-provider-closeout-refresh-2026-06-01.json`
- `docs/reports/quality/backend-data-source-registry-provider-closeout-refresh-2026-06-01.md`
- `governance/mainline/task-cards/pr-445.yaml`

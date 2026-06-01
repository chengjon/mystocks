# Backend Governance Dashboard Postgres Provider Implementation

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Gate: G2.287
- Status: for review in future PR `#440`
- Prepared at: `2026-06-01T08:12:57+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `e7c78892e1928d86fabecbe4135e7ce68fd0f01e`
- Parent gate: G2.286 provider authorization, PR `#439`, merged at `e7c78892e1928d86fabecbe4135e7ce68fd0f01e`
- OpenSpec change: `migrate-backend-singletons-to-lifecycle-di`

Boundary note: G2.287 is a path-limited source implementation package. It
must stop at PR review and must not auto-merge under the limited-autopilot
rule because it edits backend source and the target GitNexus impact is MEDIUM.

## Implemented Scope

G2.287 implements the source lane authorized by G2.286:

- `web/backend/app/api/governance_dashboard.py`
- `tests/api/file_tests/test_governance_dashboard_api.py`
- `web/backend/tests/test_governance_dashboard_postgres_provider.py`

It also updates steward evidence, this quality report, and the PR task card.

The implementation adds route-local provider
`get_governance_dashboard_postgres_connection()`, moves the five governance
dashboard handlers to `Depends(provider)`, and moves connection cleanup into the
provider finalizer.

## Contract Boundary

This package does not change:

- route registration
- route paths or HTTP methods
- `response_model` declarations
- `responses` metadata
- generated OpenAPI artifacts
- docs/api artifacts
- frontend, config, scripts, OpenSpec, PM2, or runtime state
- shared PostgreSQL/session infrastructure
- source retirement or archive state

The existing `get_postgres_connection()` helper remains as the provider backing
call. This preserves the current route-local ownership model while removing
direct route-body connection lifecycle management.

## Target Surface

Before implementation, the five target handlers each performed a direct
`await get_postgres_connection()` call, and the module had nine route-body
manual cleanup lines.

After implementation:

| Handler | Direct route-body calls | Manual `conn.close()` calls | Provider binding |
|---|---:|---:|---:|
| `get_quality_overview` | 0 | 0 | 1 |
| `get_lineage_stats` | 0 | 0 | 1 |
| `get_assets_catalog` | 0 | 0 | 1 |
| `get_compliance_metrics` | 0 | 0 | 1 |
| `get_dashboard_summary` | 0 | 0 | 1 |

Aggregate post-change counts:

- direct route-body `await get_postgres_connection()` calls: `0`
- provider backing `await get_postgres_connection()` calls: `1`
- route-body manual `conn.close()` calls: `0`
- `Depends(get_governance_dashboard_postgres_connection)` bindings: `5`

## GitNexus

GitNexus MCP remained unavailable for this target:

- `context`: `Transport closed`
- `impact`: `Transport closed`

CLI fallback before source edit:

- target: `Function:web/backend/app/api/governance_dashboard.py:get_postgres_connection`
- risk: `MEDIUM`
- impacted symbols: `6`
- direct callers: `5`
- affected processes: `0`
- affected modules: `1`
- index status: stale warning

Staged verification:

- MCP `detect_changes`: `Transport closed`
- CLI `verify-staged`: low risk
- changed files: `12`
- changed symbols: `7`
- affected processes: `0`
- index status: stale warning

The stale index still names one incoming caller as `fetch_all_data`; current
code truth maps that surface to `get_dashboard_summary`.

## TDD Evidence

RED:

```text
pytest -q web/backend/tests/test_governance_dashboard_postgres_provider.py -n 0 --tb=short --no-cov
2 failed
```

Both failures were expected: `get_governance_dashboard_postgres_connection`
did not exist before implementation.

GREEN:

```text
pytest -q web/backend/tests/test_governance_dashboard_postgres_provider.py -n 0 --tb=short --no-cov
2 passed in 0.92s
```

Focused existing + new tests:

```text
pytest -q tests/api/file_tests/test_governance_dashboard_api.py web/backend/tests/test_governance_dashboard_postgres_provider.py -n 0 --tb=short --no-cov
14 passed in 0.69s
```

Health / route conflict regression:

```text
pytest -q web/backend/tests/test_health_route_conflicts.py -n 0 --tb=short --no-cov
121 passed in 223.41s
```

Lint:

```text
ruff check web/backend/app/api/governance_dashboard.py web/backend/tests/test_governance_dashboard_postgres_provider.py tests/api/file_tests/test_governance_dashboard_api.py
All checks passed
```

Note: the first ruff run removed two unused imports from the touched route
module and one unused import from the focused existing governance dashboard
file test. No additional source files were modified.

## Route / OpenAPI Smoke

Import-time route/OpenAPI smoke with placeholder environment values records:

- FastAPI routes: `548`
- OpenAPI paths: `500`
- duplicate operation IDs: `0`
- provider dependency parameter leaks: `0`

Governance dashboard paths remain present:

- `/api/v1/governance/assets/catalog`
- `/api/v1/governance/compliance/metrics`
- `/api/v1/governance/dashboard/summary`
- `/api/v1/governance/lineage/stats`
- `/api/v1/governance/quality/overview`

The smoke produced expected import-time service logs and `119` captured Python
warnings; none changed the route/OpenAPI counts or the target path inventory.

## Review Stop

PR `#440` must stop for human review. If accepted and merged, the next
recommended gate is G2.288 no-source `governance_dashboard.get_postgres_connection`
provider closeout / residual refresh.

The limited-autopilot rule must not merge G2.287 automatically because this
package edits backend source and the GitNexus sampled target risk is MEDIUM.

## Evidence

- `.planning/codebase/generated/governance-dashboard-postgres-provider-implementation-2026-06-01.json`
- `docs/reports/quality/backend-governance-dashboard-postgres-provider-implementation-2026-06-01.md`
- `governance/mainline/task-cards/pr-440.yaml`

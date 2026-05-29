# Backend Monitoring Calculator Factory Provider Closeout Refresh

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2: `G2.239`
- Status: closeout / residual refresh for review
- Prepared at: `2026-05-29T21:17:11+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `fd9efeefc31cdbe5aa702b47f736b5bc8b9d4bea`
- Parent: G2.238, PR `#391`, merge commit `fd9efeefc31cdbe5aa702b47f736b5bc8b9d4bea`
- Source edit authority: No

## Closeout Result

G2.238 is closed as implemented for the monitoring calculator factory route
provider seam.

| Check | Result |
|---|---:|
| Route-local providers | 2 |
| Target route handlers | 8 |
| Direct route-body `get_calculator_factory()` calls | 0 |
| `Depends(get_monitoring_calculator_factory)` parameters | 8 |
| app/OpenAPI smoke | `routes=548`, `paths=500` |

The remaining `get_calculator_factory` accessor in
`src/monitoring/domain/calculator_factory.py` is the retained domain owner and
is not a route-provider residual.

## Verification

| Check | Result |
|---|---|
| Focused monitoring API tests | `17 passed` |
| Health route conflicts collect-only | `121 tests collected` |
| Ruff on authorized G2.238 files | `All checks passed` |
| app/OpenAPI smoke | `routes=548`, `paths=500` |
| Static scan | 2 providers, 8 target handlers, 0 route-body direct calls, 8 dependency parameters |

## Preserved Boundaries

This closeout confirms G2.238 did not change:

- `src/monitoring/domain/calculator_factory.py`
- calculator construction behavior
- GPU/CPU/risk calculator selection semantics
- route paths
- OpenAPI path count
- response models
- `UnifiedResponse` contracts
- `get_mock_data_manager`
- `get_monitoring_db`
- `get_postgres_async`

## Residual Refresh

Monitoring calculator factory route-provider work is closed for the 8 active
route handlers covered by G2.236 through G2.238.

No further source lane should be opened from this closeout without a new
current-HEAD contradiction. The next appropriate step is a no-source broader
service lifecycle residual candidate refresh.

Recommended next gate:

- `G2.240` no-source service lifecycle residual candidate refresh
- Source authority: No

## Rollback

If later evidence contradicts this closeout, revert PR `#391`. G2.239 itself is
governance-only and can be reverted independently without runtime impact.

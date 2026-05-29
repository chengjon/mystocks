# Backend Mock Data Manager Provider Closeout Refresh

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2: `G2.244`
- Status: closeout / residual refresh for review
- Prepared at: `2026-05-30T00:45:20+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `a0eec8bea7077e59e25a6f4491d4c695b1e25ed9`
- Parent: G2.243, PR `#396`, merge commit `a0eec8bea7077e59e25a6f4491d4c695b1e25ed9`

## Closeout Result

G2.243 is closed as implemented and verified.

The mock data manager factory now has the explicit provider/reset seam
authorized by G2.242:

- `set_mock_data_manager_provider(provider)`
- `reset_mock_data_manager_provider()`

The following behavior is preserved:

- `get_mock_data_manager` remains the compatibility accessor.
- package-level cached `mock_data_manager` lookup remains.
- `UnifiedMockDataManager` creation path remains.
- fallback manager behavior remains.
- mock response shapes remain.

No consumer migration was performed.

## Verification

| Check | Result |
|---|---|
| Provider/reset static guard | provider and reset functions present |
| Focused mock manager + runtime tests | `14 passed` |
| Ruff on G2.243 touched runtime/test files | `All checks passed` |
| app/OpenAPI smoke | `routes=548`, `paths=500`, `duplicate_operation_id_warnings=0` |

## Residual Candidate Refresh

| Candidate | Classification | Current evidence | Recommendation |
|---|---|---|---|
| `get_postgres_async` | single-definition infrastructure data-access singleton | 1 definition, 28 import lines, 30 call expressions, 22 API route-body calls; GitNexus CLI impact `LOW`, 4 impacted, 3 direct, 0 processes, 2 modules | Select G2.245 no-source ownership / provider decision |
| `get_monitoring_db` | multi-definition monitoring/risk/strategy logging seam | 3 definitions, 2 import lines, 12 call expressions, 12 API route-body calls; GitNexus impact ambiguous with 3 candidates | Defer until disambiguation and ownership classification |

## Decision

G2.244 does not authorize implementation.

The next gate is G2.245: no-source `get_postgres_async` ownership / provider
decision. This should classify the singleton owner, route-body consumers,
infrastructure constraints, and whether a future source lane is safe.

`get_monitoring_db` remains deferred because the graph currently reports three
same-name definitions across risk, utilities, and strategy management.

## Forbidden Scope

G2.244 does not authorize:

- source edits
- test edits
- route or OpenAPI changes
- frontend changes
- config or script changes
- OpenSpec proposal/spec changes
- direct implementation of `get_postgres_async`
- direct implementation of `get_monitoring_db`

## Next Gate

If accepted, start G2.245 as a no-source `get_postgres_async` ownership /
provider decision packet. Do not start source implementation from G2.244.

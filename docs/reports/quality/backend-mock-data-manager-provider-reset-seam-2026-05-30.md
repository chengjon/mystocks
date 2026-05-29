# Backend Mock Data Manager Provider Reset Seam

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2: `G2.243`
- Status: implementation for review
- Prepared at: `2026-05-30T00:30:17+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `e7506af885ed635580f2ab765ec9e4fe279cc98b`
- Parent: G2.242, PR `#395`, merge commit `e7506af885ed635580f2ab765ec9e4fe279cc98b`

## Scope

G2.243 implements the path-limited provider/reset/test-double seam authorized by
G2.242:

- `web/backend/app/mock/mock_data/factory.py`
- `web/backend/tests/test_mock_data_manager_configuration.py`
- `web/backend/tests/test_runtime_regressions_p0.py`

No API/helper fallback consumer, service adapter, route, OpenAPI, frontend,
config, script, or OpenSpec file is in scope.

## Implementation

`factory.py` now exposes:

- `set_mock_data_manager_provider(provider)`
- `reset_mock_data_manager_provider()`

`get_mock_data_manager()` first checks the explicit provider. If no provider is
installed, it keeps the existing package-level cached manager lookup,
`UnifiedMockDataManager` creation path, invalid-manager fallback path, and
exception fallback path.

The provider is intentionally narrow. It is a test-double and app-wiring seam,
not a migration of existing API/helper or adapter consumers.

## TDD Evidence

RED:

```text
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_mock_data_manager_configuration.py::test_mock_data_manager_provider_can_be_overridden_and_reset -q --no-cov --tb=short
```

Result before implementation:

```text
AttributeError: module 'app.mock.mock_data.factory' has no attribute 'set_mock_data_manager_provider'
```

GREEN:

```text
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_mock_data_manager_configuration.py::test_mock_data_manager_provider_can_be_overridden_and_reset -q --no-cov --tb=short
```

Result after implementation:

```text
1 passed
```

## Verification

| Check | Result |
|---|---|
| GitNexus impact before edit | `CRITICAL`, 63 impacted, 27 direct, 4 affected processes, 8 modules; MCP transport closed, CLI fallback used |
| Focused mock manager test | `1 passed` |
| Focused mock manager + runtime regression tests | `14 passed` |
| Ruff on authorized files | `All checks passed` |
| app/OpenAPI smoke | `routes=548`, `paths=500`, `duplicate_operation_id_warnings=0` |

## Preserved Boundaries

G2.243 does not change:

- API/helper fallback consumers
- service adapters
- legacy/facade adapters
- route paths
- OpenAPI exposure or path count
- frontend code
- config or scripts
- OpenSpec proposals or specs

G2.243 also keeps `get_mock_data_manager` as the compatibility accessor.

## Rollback

Revert the G2.243 PR. The explicit provider/reset seam and focused test are
removed, and `get_mock_data_manager()` returns to the previous default-only
lookup path.

## Next Gate

If accepted, start G2.244 as a no-source closeout / residual refresh for the
mock data manager provider/reset seam. Do not use G2.243 to migrate any
additional consumers.

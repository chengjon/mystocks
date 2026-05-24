# Backend Data Source Factory Provider Seam Closeout - 2026-05-24

> **历史总结说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: ready for review

Workline: G2.61a closeout / current-head refresh

Base branch: `wip/root-dirty-20260403`

Current HEAD: `0aadb27801c86e97e65ffdb4426276e1bd14c352`

## Scope Boundary

This closeout records the merged G2.61a result. It does not change backend
source code, tests, route paths, response contracts, OpenAPI exposure, generated
clients, OpenSpec files, issue labels, runtime process state, or PM2 state.

## Merge Evidence

PR `#202` was merged at
`0aadb27801c86e97e65ffdb4426276e1bd14c352`.

Merged implementation summary:

- Added `DATA_SOURCE_FACTORY_STATE_KEY`.
- Added `install_data_source_factory(app, factory=None)`.
- Added `get_data_source_factory_dependency(request)`.
- Preserved `get_data_source_factory()` and `_global_factory`.
- Added focused lifecycle DI tests.
- Did not migrate any API route consumers.

## Current-Head Provider Surface

Current HEAD contains the provider seam in:

```text
web/backend/app/services/data_source_factory/data_source_factory.py
```

The focused lifecycle DI test remains in:

```text
web/backend/tests/test_data_source_factory_lifecycle_di.py
```

## Route Guard

Post-merge static scan reports:

- API files scanned: `219`
- Direct `get_data_source_factory()` API calls: `17`
- `get_data_source_factory_dependency` API refs: `0`

This confirms G2.61a did not perform route migration. The `17` direct route/API
calls remain intentionally locked for later route-specific packets.

## GitNexus Refresh

GitNexus was refreshed from a temporary non-linked checkout:

- Checkout: `.worktrees/g2-61a-closeout-gitnexus-index-checkout`
- `.git` kind: `directory`
- HEAD: `0aadb27801c8`
- `gitnexus analyze` exit: `0`
- Nodes: `62642`
- Edges: `145826`
- Clusters: `3288`
- Flows: `300`

Refreshed graph results:

| Symbol | Location | Incoming callers | Upstream risk |
|---|---|---:|---|
| `get_data_source_factory_dependency` | `data_source_factory.py:314-318` | 0 | LOW |
| `install_data_source_factory` | `data_source_factory.py:308-311` | 0 | LOW |

This closes the stale-graph risk for the new provider symbols.

## Verification

Focused lifecycle DI test:

```text
pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short
4 passed
```

Existing factory regression:

```text
pytest -o addopts= web/backend/tests/test_data_source_factory.py -q --no-cov --tb=short
38 passed
```

Route-adjacent runtime fallback:

```text
pytest -o addopts= web/backend/tests/test_data_stocks_runtime_fallback.py -q --no-cov --tb=short
1 passed
```

Lint and formatting:

```text
ruff check ...data_source_factory.py ...test_data_source_factory_lifecycle_di.py
All checks passed
```

```text
black --check ...data_source_factory.py ...test_data_source_factory_lifecycle_di.py
2 files would be left unchanged
```

App/OpenAPI smoke with non-secret test env values:

```text
app_import=passed
routes=548
openapi_paths=500
operation_ids=536
duplicate_operation_ids=0
```

## Residuals

- `web/backend/app/services/data_source_factory/__init__.py` does not re-export
  the new provider symbols. This remains outside G2.61a and should be decided by
  the first route migration authorization packet if route code wants package
  imports.
- `17` direct API route calls remain unchanged.
- `tests/backend/test_data_api_regression.py` still has baseline 404
  expectations, already reproduced in an unmodified checkout during G2.61a.

## Next Gate

G2.61a closeout supports opening a separate first route migration planning
packet.

Recommended next packet:

- G2.61b: `data_quality.py` route migration authorization / consumer matrix.

G2.61b should remain decision/authorization-first and must not migrate routes
until reviewed. It should decide whether to import
`get_data_source_factory_dependency` from the implementation module directly or
authorize a package `__init__.py` export update before route edits.

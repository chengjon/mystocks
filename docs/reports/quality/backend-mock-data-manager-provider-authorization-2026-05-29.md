# G2.242 Mock Data Manager Provider / Reset Seam Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: provider authorization for review
- Prepared at: `2026-05-29T22:42:25+08:00`
- Base HEAD checked: `cb0e7cd605e2828c495e3f31433ad1b8b6a3d64c`
- Parent: G2.241, PR `#394`
- Source edit authority in this PR: none

Boundary note: this report authorizes only a future bounded source lane if
accepted. It does not itself modify source, tests, routes, OpenAPI, config,
scripts, OpenSpec, issue labels, PM2 state, or PR merge state.

## Authorization Decision

If G2.242 is accepted, create G2.243 as a path-limited source implementation
lane for the mock data manager provider/reset seam.

G2.242 itself remains no-source.

## Future G2.243 Allowed Scope

| Scope | Paths |
|---|---|
| Source | `web/backend/app/mock/mock_data/factory.py` |
| Focused tests | `web/backend/tests/test_mock_data_manager_configuration.py` |
| Focused regressions | `web/backend/tests/test_runtime_regressions_p0.py` |

Required behavior for G2.243:

- Preserve `get_mock_data_manager` as the public compatibility accessor.
- Preserve current `app.main.mock_data_manager` runtime cache compatibility.
- Preserve fallback manager behavior and mock response shapes.
- Add an explicit provider/reset/test-double seam with deterministic cleanup for
  tests.
- Keep compatibility helper functions delegating through the public accessor.

## Explicit Non-Goals

G2.243 must not:

- migrate all API/helper consumers
- rewrite service adapters or legacy/facade adapters
- remove `get_mock_data_manager`
- change route paths, route registration, OpenAPI paths, response models, or
  frontend behavior
- touch config, scripts, docs/api, `FUNCTION_TREE`, OpenSpec changes, or
  OpenSpec specs

## Evidence Snapshot

| Item | Result |
|---|---:|
| Factory file lines | 156 |
| Definition count | 1 |
| Import lines | 16 |
| Call expressions | 27 |
| Active route-body calls | 0 |
| GitNexus impact sample | `CRITICAL`, 63 impacted, 27 direct, 4 processes, 8 modules |

Consumer buckets:

| Bucket | Calls | Files | Future handling |
|---|---:|---:|---|
| API/helper fallback consumers | 8 | 6 | Forbidden in G2.243 |
| Mock factory / fixture helpers | 9 | 2 | Owner surface |
| Active service adapters | 3 | 3 | Forbidden in G2.243 |
| Legacy/facade adapters | 3 | 3 | Forbidden in G2.243 |
| Tests | 4 | 3 | Focused verification only |

Focused test inventory:

- `web/backend/tests/test_mock_data_manager_configuration.py`
  covers settings-backed mock manager behavior, explicit flag override behavior,
  and fallback enabled / disabled behavior.
- `web/backend/tests/test_runtime_regressions_p0.py` covers watchlist mock data
  success response shape and `added_at` schema preservation.

## G2.243 Prerequisites

Before editing source in G2.243:

- Run GitNexus impact on `get_mock_data_manager`.
- Use TDD: add failing tests for provider/reset cleanup behavior first.
- Keep source edits inside `web/backend/app/mock/mock_data/factory.py`.
- Keep test edits inside the two focused test files listed above.
- Run app/OpenAPI smoke and confirm `routes=548`, `paths=500`.
- Run GitNexus staged detect before commit.

## Next Gate

If G2.242 is accepted:

- start G2.243 path-limited implementation
- do not expand scope beyond the authorized source and focused test files
- preserve route, OpenAPI, response shape, frontend, config, scripts, and
  OpenSpec boundaries

## Verification Targets

- generated JSON parses
- `steward-index.json` parses
- Markdown governance gate has 0 errors
- app/OpenAPI smoke remains `routes=548`, `paths=500`
- `openspec validate migrate-backend-singletons-to-lifecycle-di --strict` passes
- mainline scope gate reports only governance/documentation files
- GitNexus detect changes reports docs-only low risk

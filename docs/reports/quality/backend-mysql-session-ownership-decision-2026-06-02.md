# Backend get_mysql_session Ownership Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: this report is a no-source ownership / route-provider decision
package. It does not edit backend source, tests, route contracts, docs/api
artifacts, frontend, config, scripts, OpenSpec changes/specs, PM2, or runtime
state.

Status: for review in future PR `#463`.

## Summary

G2.310 follows PR `#462`, which merged G2.309 at
`5d24bed2e77bcb142a81e1b1bcc68a1cdca27d18`.

G2.309 selected `get_mysql_session` as the next no-source decision target
because the call sites are bounded to one module. G2.310 narrows that further:
the five calls live in `web/backend/app/api/indicators/create_indicator_config.py`,
but that module's router is not currently registered in the FastAPI app or
OpenAPI schema.

Decision: do not authorize a provider implementation lane from this package.
The next gate must first decide the route ownership truth for the indicator
configuration CRUD module.

## Target Surface

| Item | Value |
|---|---|
| Helper | `app.core.database.get_mysql_session` |
| Route module | `web/backend/app/api/indicators/create_indicator_config.py` |
| Module size | `363` lines |
| Bare route-body calls | `5` |
| Handler functions | `create_indicator_config`, `list_indicator_configs`, `get_indicator_config`, `update_indicator_config`, `delete_indicator_config` |
| GitNexus CLI impact | `MEDIUM`, direct `5`, affected processes `0`, affected modules `0`, stale index with commits behind `0` |

Call sites:

| Line | Call |
|---:|---|
| `60` | `session = get_mysql_session()` |
| `129` | `session = get_mysql_session()` |
| `189` | `session = get_mysql_session()` |
| `251` | `session = get_mysql_session()` |
| `331` | `session = get_mysql_session()` |

The current implementation also preserves explicit cleanup through
`session.close()` in `finally` blocks at lines `107`, `165`, `223`, `309`, and
`355`.

## Route Registration Truth

`create_indicator_config.py` defines its own `router = APIRouter()`, but the
current package export `web/backend/app/api/indicators/__init__.py` exports
`router` from `indicator_cache.py`. `router_registry.py` registers
`indicators.router`, which therefore points to the indicator cache router rather
than the configuration CRUD router.

Fresh app route-table smoke with non-secret test environment values recorded:

| Metric | Result |
|---|---:|
| Total FastAPI routes | `548` |
| OpenAPI paths | `500` |
| Duplicate operation IDs | `0` |
| Registered `create_indicator_config.py` handlers | `0` |
| OpenAPI indicator config CRUD paths from this module | `0` |

Observed current indicator paths are cache/registry/calculate routes, not
`/configs` CRUD routes from `create_indicator_config.py`.

## Test Inventory

The scanner found related tests and references, but none prove the dormant
router is currently registered:

| Path | Relevance |
|---|---|
| `tests/api/file_tests/test_indicators_api.py` | File-level endpoint expectations and model validation references |
| `tests/ddd/test_architecture_validation.py` | Domain `IndicatorConfig` value-object checks |
| `web/backend/tests/unit/services/indicators/test_indicator_registry.py` | Indicator registry and metadata unit tests |

## GitNexus Evidence

GitNexus MCP impact returned `Transport closed`. CLI fallback succeeded:

| Target | Risk | Direct | Affected processes | Affected modules | Index |
|---|---:|---:|---:|---:|---|
| `Function:web/backend/app/core/database.py:get_mysql_session` | `MEDIUM` | `5` | `0` | `0` | stale, commits behind `0`, embeddings unavailable |

Because this PR is no-source, the impact result is decision evidence only. It
does not authorize edits to the shared helper or the route module.

## Decision

Classify `get_mysql_session` in `create_indicator_config.py` as an unregistered
indicator-config router session helper.

Do not create a provider implementation lane yet. The real next question is
whether the indicator configuration CRUD router should be:

- registered and then governed as an active route surface,
- retired through a separate route/source retirement lane, or
- retained as dormant compatibility code with explicit evidence.

Recommended next gate: G2.311 no-source indicator config router ownership /
registration-retirement decision.

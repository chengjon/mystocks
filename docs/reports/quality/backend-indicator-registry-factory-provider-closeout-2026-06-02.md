# Backend Indicator Registry Factory Provider Closeout - G2.316

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: for review
- Prepared at: `2026-06-02T08:24:18+08:00`
- Base HEAD checked: `8b09c714784ce90a1a8b1fe938e5904a81110094`
- Parent gate: G2.315 accepted / merged by PR `#468`
- Source edit authority: none

Boundary note: this G2.316 package is no-source closeout / residual refresh only. It does not authorize backend source edits, tests, route registration changes, route/OpenAPI contract edits, docs/api artifacts, frontend/config/script changes, PM2 commands, OpenSpec spec edits, or source retirement.

## Closeout Result

The `indicator_registry.get_factory` provider lane is closed.

| Check | Result |
|---|---|
| Route-body direct `get_factory()` calls | `0` |
| Provider backing `get_factory()` calls | `1` |
| `Depends(get_indicator_factory)` bindings | `3` |
| Focused test | `tests/api/file_tests/test_indicator_registry_api.py`: `11 passed, 1 warning` |
| Ruff | target source/test files pass |
| Route/OpenAPI | `548` FastAPI routes, `500` OpenAPI paths, duplicate operation IDs `0` |

All three indicator-registry routes now expose `get_indicator_factory` as their route dependency, while `get_factory()` remains as the backing singleton compatibility seam.

## Residual Refresh

The broad residual scan covered `364` active API/service Python files after excluding old/backup/archive-style paths. It saw `658` getter-like names and `827` broad residual groups. This broad count is a triage index only, not a direct replacement for earlier curated candidate counts.

The next selected candidate is:

| Field | Value |
|---|---|
| Next node | G2.317 |
| Candidate | `get_config_manager` |
| Main route file | `web/backend/app/api/data_source_config.py` |
| Backing implementation file | `web/backend/app/api/_data_source_config_responses.py` |
| Current route dependency | `get_config_manager_dependency` |
| Registered route count | `9` |
| Sample backing line | `data_source_config.py:103 return get_config_manager()` |

GitNexus MCP impact failed with `Transport closed`; CLI fallback resolved the backing symbol as `Function:web/backend/app/api/_data_source_config_responses.py:get_config_manager` and reported `HIGH` risk, `9` direct callers, and `3` affected processes. Because of that, G2.317 must be ownership / provider seam decision only. It must not authorize source implementation directly.

## Next Gate

Start G2.317 as a no-source `data_source_config.get_config_manager` ownership / provider seam decision after PR `#469` is accepted / merged.

G2.317 should decide whether the current provider/backing split is already acceptable, needs closeout documentation only, or needs a later high-risk authorization package. It must not edit source.

# Backend Technical Analysis DataSourceFactory Provider Authorization Preflight

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Summary

- Node: `G2.326 technical_analysis DataSourceFactory provider authorization preflight`
- Type: no-source provider authorization preflight
- Prepared at: `2026-06-03T17:48:01+08:00`
- Current workspace HEAD checked: `33e8af754c815a1c1c3e1e49a7d5453881534cca`
- Accepted PR anchor: PR `#474` merged at `2026-06-02T16:23:25Z`, merge commit `2ebff6d7ded33403c691a60fc43f87dabf90a975`

G2.326 completes a no-source authorization preflight for the technical analysis
DataSourceFactory provider candidate. It prepares only a bounded future G2.327
source lane; no source execution starts in this node.

## Parent Decision

G2.325 classified `web/backend/app/api/technical_analysis.py` as an active
route-local DataSourceFactory seam candidate selected by G2.324:

- `8` route handlers with route-body DataSourceFactory residuals.
- `8` `DataSourceFactory()` calls.
- `8` `.get_data_source(...)` calls.
- Source authority remains false for G2.325.

## Future Source Boundary

G2.326 prepares a future G2.327 source implementation lane limited to:

- `web/backend/app/api/technical_analysis.py`
- `tests/api/file_tests/test_technical_analysis_api.py`

Forbidden surfaces:

- `web/backend/app/services/data_source_factory/**`
- `web/backend/app/api/watchlist.py`
- `web/backend/app/api/strategy_management/**`
- `web/backend/app/api/_technical_analysis_models.py`
- `web/backend/app/api/_technical_analysis_responses.py`
- `docs/api/**`
- `web/frontend/**`
- `src/**`
- `config/**`
- `scripts/**`
- `openspec/**`
- PM2 or runtime state

## Required Future Shape For G2.327

- Run pre-edit GitNexus impact/context for `technical_analysis.py` and affected
  route symbols.
- Stop if risk becomes HIGH or CRITICAL without human approval.
- Add route-local provider wiring for the technical analysis DataSourceFactory
  seam.
- Move only the eight affected `technical_analysis.py` handlers away from
  route-body `DataSourceFactory()` and `.get_data_source(...)` acquisition.
- Preserve route paths, methods, request models, response models, and OpenAPI
  contract shape.
- Retain shared DataSourceFactory implementation unchanged as backing
  infrastructure.

## Stop Rule

G2.326 is no-source. Future G2.327 is a source node, but source execution has
not started and still requires explicit source-lane approval. Any future source
PR must stop for human review before merge.

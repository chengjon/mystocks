# Backend Data-Quality Market Data Adapter Provider Implementation

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: review candidate
- Prepared at: `2026-05-28T17:58:00+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `b4b34375eef0186b81be9a24491328dab72c2e21`
- Worktree branch: `g2-208-data-quality-market-data-adapter-provider-implementation`
- Scope: path-limited source implementation
- Source edit authority: yes, limited by G2.207

## Parent State

PR `#360` merged G2.207 at
`b4b34375eef0186b81be9a24491328dab72c2e21`.

G2.207 authorized only a narrow provider seam implementation for
`web/backend/app/services/market_data_adapter.py`, plus focused tests.

## Implementation Result

| Item | Result |
|---|---|
| Constructor contract | `MarketDataSourceAdapter` keeps positional `config` and adds keyword-only optional `quality_monitor` |
| Default behavior | Without injection, `_trigger_quality_monitoring` still falls back to `get_data_quality_monitor()` |
| Injected behavior | With injection, `_trigger_quality_monitoring` uses the supplied monitor and bypasses the module-level getter |
| Factory compatibility | `MarketDataSourceAdapter(config.__dict__)` remains valid because the new parameter is keyword-only optional |
| Function-tree mapping | `domain-01-node-03` now records the market data adapter facade and focused test |

Changed source path:

- `web/backend/app/services/market_data_adapter.py`

Changed test path:

- `web/backend/tests/test_market_data_adapter_quality_monitor_provider.py`

## TDD Evidence

| Phase | Result |
|---|---|
| RED | New focused test failed with `TypeError: MarketDataSourceAdapter.__init__() got an unexpected keyword argument 'quality_monitor'` |
| GREEN | New focused test passed with `2 passed` |
| Regression | Authorized regression package passed with `18 passed` |
| Ruff | Authorized source/test files passed |

## GitNexus Evidence

Pre-edit impact checks were run before source edits:

| Target | Risk | Impact |
|---|---|---|
| `web/backend/app/services/market_data_adapter.py` | LOW | `impacted_count=3`, `direct=1`, `processes_affected=0` |
| `MarketDataSourceAdapter` | LOW | `impacted_count=0`, `direct=0`, `processes_affected=0` |

## Preserved Boundaries

This implementation did not edit:

- `web/backend/app/services/data_source_factory/**`
- `web/backend/app/services/_data_quality_monitor_singleton.py`
- `web/backend/app/services/data_quality_monitor.py`
- `web/backend/app/services/adapters/**`
- `web/backend/app/services/adapters_split/**`
- `web/backend/app/services/data_adapters/**`
- `web/backend/app/api/**`
- frontend, `src`, config, scripts, docs/api, or OpenSpec files

## Recommended Next Gate

Start G2.209 as a governance-only closeout / residual refresh package.

G2.209 should confirm the market data adapter provider seam is closed and
classify the remaining data-quality monitor residuals before any singleton
wrapper or backing API retirement is considered.

## Evidence Artifacts

| Artifact | Role |
|---|---|
| `.planning/codebase/generated/data-quality-market-data-adapter-provider-authorization-2026-05-28.json` | G2.207 authorization package |
| `docs/reports/quality/backend-data-quality-market-data-adapter-provider-authorization-2026-05-28.md` | G2.207 human-readable authorization package |
| `.planning/codebase/generated/data-quality-market-data-adapter-provider-implementation-2026-05-28.json` | G2.208 machine-readable implementation evidence |
| `docs/reports/quality/backend-data-quality-market-data-adapter-provider-implementation-2026-05-28.md` | G2.208 human-readable implementation report |
| `governance/mainline/task-cards/pr-361.yaml` | G2.208 source implementation scope card |

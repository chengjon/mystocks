# Backend Service Lifecycle Residual Refresh After Indicator Config Exclusion

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: this report is a no-source candidate refresh package. It does
not edit backend source, tests, route contracts, docs/api artifacts, frontend,
config, scripts, OpenSpec changes/specs, PM2, or runtime state.

Status: for review in future PR `#465`.

## Summary

G2.312 follows PR `#464`, which merged G2.311 at
`0f5382cea875d2983ada5d9c63548b0530861002`.

G2.311 classified `create_indicator_config.py` as retained dormant route code.
G2.312 therefore excludes `get_mysql_session` in that dormant module from the
active service lifecycle provider candidate queue and refreshes the remaining
candidate list.

## Refresh Result

| Item | Result |
|---|---:|
| Python files scanned | `371` |
| Getter-like names seen | `663` |
| Active interesting candidates after exclusions | `53` |
| Newly excluded dormant helper | `get_mysql_session` in `create_indicator_config.py` |

## Top Candidate Snapshot

| Candidate | Bare API calls | Handling |
|---|---:|---|
| `get_config_manager` | `9` | Defer; data-source-config legacy/compat surface |
| `get_cache_data` | `7` | Defer; data/cache helper family |
| `get_cache_manager` | `7` | Defer; dashboard/cache cross-route helper |
| `get_postgresql_engine` | `6` | Defer; control-plane / DB engine helper |
| `get_risk_management_core` | `6` | Defer; risk core helper |
| `get_mtm_engine` | `5` | Defer; realtime MTM / streaming-adjacent surface |
| `get_factory` | `3` | Select for next no-source ownership / route-provider decision |

## Selected Next Gate

Select G2.313 no-source `indicator_registry.get_factory` ownership /
route-provider decision.

Rationale:

- `get_factory` is concentrated in one API module:
  `web/backend/app/api/indicator_registry.py`.
- The scan records three bare route-body calls:
  - line `159`: `factory = get_factory()`
  - line `186`: `factory = get_factory()`
  - line `201`: `factory = get_factory()`
- It is lower ambiguity than data-source-config, dashboard/cache, risk core,
  realtime MTM, and control-plane DB surfaces.

G2.313 must remain decision-only until it is reviewed. It must not edit source,
tests, route contracts, OpenAPI artifacts, frontend, config, scripts, OpenSpec,
PM2, or runtime state.

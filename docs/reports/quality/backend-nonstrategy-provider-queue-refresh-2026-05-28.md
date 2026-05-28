# Backend Non-Strategy Provider Queue Refresh - 2026-05-28

> **历史文档说明**: 本文件是 G2.214 执行证据快照，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Lane: G2.214 non-Strategy provider governance queue refresh / next-candidate selection
- Parent closeout: G2.213, PR `#366`
- Parent merge commit: `3d3f8285f3a83cb4dda60d9b7eb8cf36fdf77117`
- OpenSpec change: `migrate-backend-singletons-to-lifecycle-di`
- Source authority: none
- Result: ready for review

## Purpose

G2.214 returns from the closed data-quality monitor conveyor to the broader
non-Strategy provider/getter queue. It refreshes current HEAD evidence and
selects the next governance target without authorizing source edits.

## Queue Scan

Scope:

- `web/backend/app/**/*.py`

Summary:

| Metric | Count |
|---|---:|
| Python files scanned | 575 |
| Files with provider/getter items | 201 |
| Provider/getter items | 408 |

Bucket summary:

| Bucket | Items | Disposition |
|---|---:|---|
| Closed data-quality monitor | 14 | Closed by G2.213 unless fresh current-HEAD evidence contradicts |
| Excluded Strategy | 44 | Strategy residuals closed by G2.183 with retained residuals |
| Route provider surface | 131 | Active route/provider governance surface; not a direct source lane from G2.214 |
| Realtime streaming/socket | 36 | Prior realtime/socket evidence exists; do not reopen from token count alone |
| Dashboard/TDX | 11 | Direct helper debt remains closed; retain until contradictory evidence |
| Indicator/Data | 45 | Requires current-HEAD contradiction review because `get_data_service` now reports CRITICAL impact |
| Adapter/factory | 26 | Factory/adapter ownership surface; defer behind higher-risk current-head contradiction |
| Risk/alert | 23 | Stop-loss pair already closed; broader alert surfaces deferred |
| Other service/provider | 78 | Mixed infra/control-plane/root facade queue; candidate-level decisions required |

## Candidate Impact Refresh

| Candidate | Current risk | Direct | Processes | Disposition |
|---|---:|---:|---:|---|
| `get_data_service` | CRITICAL | 3 | 7 | Select for G2.215 no-source contradiction / ownership decision |
| `get_execution_tracking_evidence_service` | HIGH | 2 | 3 | Defer behind `get_data_service`; trade evidence route is a separate high-risk track |
| `get_prewarming_strategy` | LOW | 3 | 0 | Defer; current risk is lower and bounded to cache prewarming routes |
| `get_unified_data_service` | MEDIUM | 5 | 0 | Retain as root facade / service self-wrapper pending a root-facade ownership decision |

`get_data_service` direct callers at current HEAD:

- `web/backend/app/api/indicators/indicator_cache.py::calculate_indicators`
- `web/backend/app/api/indicators/indicator_cache.py::_calculate_single_indicator`
- `web/backend/app/api/v1/strategy/indicators.py::get_technical_indicators`

This is a current-HEAD contradiction against the older G2.184/G2.186 wording
that treated the candidate as LOW or retained route-local provider fallback.
It does not mean source implementation is authorized. It means the next package
must decide the ownership and route/provider classification first.

## Decision

Select the next governance target:

`G2.215 indicator/data get_data_service current-HEAD contradiction / ownership decision package`

G2.215 must remain no-source. It should classify whether the current
`get_data_service` route callers are:

- retained provider surfaces
- route-body direct singleton debt
- route-local compatibility fallbacks
- or a future path-limited authorization candidate

G2.215 must not batch:

- trade execution evidence providers
- cache prewarming control-plane providers
- data-quality monitor residuals
- Strategy residual reopenings
- realtime/socket ownership

## Verification Results

Governance checks:

- JSON/YAML parse: passed
- Markdown governance: `errors: 0`
- OpenSpec strict validate: valid; PostHog connection refusal is telemetry noise only
- `git diff --check`: passed
- Mainline scope gate: pending after commit

## Next Gate

If PR `#367` is accepted, start G2.215 as a no-source indicator/data
`get_data_service` current-HEAD contradiction / ownership decision package.

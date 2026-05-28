# Backend Data-Quality Legacy Adapter Compatibility Closure Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Node: G2.203 data-quality legacy adapter compatibility closure authorization
- Status: authorization-only package
- Prepared at: `2026-05-28T12:37:20+08:00`
- Base HEAD checked: `bf5d5ffba6bfc837c009a3d937cf0a9e6549883f`
- Parent decision: G2.202, PR `#355`, merge commit `bf5d5ffba6bfc837c009a3d937cf0a9e6549883f`
- Source edit authority in this PR: no

Boundary note: this authorization package defines what a future implementation
lane may do after human acceptance. It does not edit source files, delete legacy
modules, change routes, change OpenAPI contracts, change frontend behavior,
change config/scripts, create OpenSpec proposals, or change GitHub issue labels.

## Authorization Decision

If accepted, G2.203 authorizes a future G2.204 source lane with this exact
implementation shape:

Convert the two legacy `data_adapters` modules into thin compatibility wrappers
that re-export the canonical `app.services.adapters` classes.

Deletion is not authorized.

| Future lane | Authorized source paths | Authorized test path | Authorized shape |
|---|---|---|---|
| G2.204 data-quality legacy adapter compatibility wrapper implementation | `web/backend/app/services/data_adapters/dashboard.py`, `web/backend/app/services/data_adapters/data_source.py` | `web/backend/tests/test_data_quality_legacy_data_adapter_compat.py` | Thin wrappers preserving old module import paths |

## Evidence

At HEAD `bf5d5ffba6bfc837c009a3d937cf0a9e6549883f`:

| Check | Result |
|---|---|
| Exact external imports of `app.services.data_adapters.dashboard` / `data_source` | `0` |
| `web/backend/app/services/data_adapters/dashboard.py` | 299 lines, class `DashboardDataSourceAdapter`, one `get_data_quality_monitor()` call at line 249 |
| `web/backend/app/services/data_adapters/data_source.py` | 688 lines, class `DataDataSourceAdapter`, one `get_data_quality_monitor()` call at line 608 |
| GitNexus impact for `dashboard.py` | LOW, `impacted_count=0`, `processes_affected=0` |
| GitNexus impact for `data_source.py` | LOW, `impacted_count=0`, `processes_affected=0` |

Why not delete:

- exact module-path consumer count is useful evidence, not deletion authority
- hidden consumers may still rely on the old module import paths
- thin wrappers remove duplicated legacy implementation and getter calls while
  preserving compatibility

## Future G2.204 Required Checks

G2.204 must be a separate source implementation lane after G2.203 is accepted.
It must include:

- GitNexus impact for both legacy files before editing
- a red test proving legacy module import compatibility
- conversion of only the two legacy modules into thin wrappers
- no file deletion
- focused tests for legacy module imports and canonical class identity or
  equivalent wrapper behavior
- import smoke for `app.services.data_adapter` and `data_source_factory`
- targeted ruff for changed source and test files
- `rg` verification that `get_data_quality_monitor()` no longer appears in the
  two legacy modules
- GitNexus staged `detect_changes`
- mainline scope gate with a G2.204 task card

## Forbidden Future Scope

G2.204 must not batch any of these:

- `web/backend/app/services/market_data_adapter.py`
- `web/backend/app/services/_data_quality_monitor_singleton.py`
- `web/backend/app/services/data_quality_monitor.py`
- `web/backend/app/services/adapters/**`
- `web/backend/app/services/adapters_split/**`
- `web/backend/app/api/**`
- `web/frontend/**`
- `src/**`
- `docs/api/**`
- `config/**`
- `scripts/**`
- `openspec/changes/**`
- `openspec/specs/**`

## Verification

| Check | Result |
|---|---|
| JSON/YAML parse | Passed for generated authorization JSON, `steward-index.json`, and `pr-356.yaml` |
| Markdown governance | Passed, `checked_files=6`, `errors=0` |
| OpenSpec validation | `openspec validate migrate-backend-singletons-to-lifecycle-di --strict` passed; PostHog network flush warning is telemetry noise |
| Diff whitespace | `git diff --check` and `git diff --cached --check` passed |
| GitNexus staged scope | Low risk, `changed_files=9`, `changed_symbols=0`, `affected_processes=0` |
| Mainline scope gate | Passed, `changed_files=9`, `violations=0`, report `/tmp/pr356-mainline-governance-report.json` |

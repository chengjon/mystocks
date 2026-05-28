# Backend Data-Quality Legacy Adapter Compatibility Wrapper Implementation

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Node: G2.204 data-quality legacy adapter compatibility wrapper implementation
- Status: source implementation package
- Prepared at: `2026-05-28T13:15:46+08:00`
- Base HEAD checked: `142a2bf1c0c5f979cf9c32415d2f25832e7e62cd`
- Parent authorization: G2.203, PR `#356`, merge commit `142a2bf1c0c5f979cf9c32415d2f25832e7e62cd`
- Source edit authority: yes, limited to the two legacy modules and one focused test

Boundary note: this implementation uses only the G2.203-authorized thin-wrapper
shape. It does not delete legacy modules, edit `market_data_adapter.py`, alter
singleton wrapper/backing APIs, edit canonical adapters, change routes, change
OpenAPI contracts, change frontend behavior, change config/scripts, create
OpenSpec proposals, or change GitHub issue labels.

## Implementation Result

| Path | Result |
|---|---|
| `web/backend/app/services/data_adapters/dashboard.py` | Thin wrapper re-exporting `app.services.adapters.dashboard_adapter.DashboardDataSourceAdapter` |
| `web/backend/app/services/data_adapters/data_source.py` | Thin wrapper re-exporting `app.services.adapters.data_adapter.DataDataSourceAdapter` |
| `web/backend/tests/test_data_quality_legacy_data_adapter_compat.py` | Focused compatibility test proving old module paths import canonical classes and no legacy getter calls remain |

No legacy module was deleted.

## TDD Evidence

RED:

```bash
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_quality_legacy_data_adapter_compat.py -q --no-cov
```

Result before implementation: `2 failed`.

The failures proved:

- legacy adapter classes were not the canonical `app.services.adapters` classes
- legacy modules still contained `get_data_quality_monitor`

GREEN:

```bash
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_quality_legacy_data_adapter_compat.py -q --no-cov
```

Result after implementation: `2 passed`.

## Verification

| Check | Result |
|---|---|
| GitNexus pre-edit impact | LOW/0 for both legacy target files |
| Focused compatibility pytest | `2 passed` |
| Broader focused pytest | `23 passed` across the new compatibility test, canonical service adapter provider test, data adapter regression test, and logging-noise regression test |
| Ruff targeted | Passed |
| Import smoke | Passed for legacy module imports, canonical adapter imports, root `app.services.data_adapter` facade, and `data_source_factory` |
| Legacy getter scan | `0` `get_data_quality_monitor()` calls in the two legacy modules |
| JSON/YAML parse | Passed for generated implementation JSON, `steward-index.json`, and `pr-357.yaml` |
| Markdown governance | Passed, `checked_files=6`, `errors=0` |
| OpenSpec validation | `openspec validate migrate-backend-singletons-to-lifecycle-di --strict` passed; PostHog network flush warning is telemetry noise |
| Diff whitespace | `git diff --check` and `git diff --cached --check` passed |
| GitNexus staged scope | Low risk, `changed_files=14`, `changed_symbols=30`, `affected_processes=0` |
| GitNexus compare scope | Low risk, `changed_files=14`, `changed_symbols=30`, `affected_processes=0` |
| Mainline scope gate | Passed, `changed_files=14`, `violations=0`, report `/tmp/pr357-mainline-governance-report.json` |

## Next Gate

If accepted, start G2.205 as a closeout / residual refresh package with no new
source authority. G2.205 should verify the remaining data-quality monitor
surfaces after this wrapper implementation and decide the next narrow target.

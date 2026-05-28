# Backend Data-Quality Legacy Adapter Ownership Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Node: G2.202 data-quality legacy adapter compatibility ownership decision
- Status: decision-only package
- Prepared at: `2026-05-28T11:53:30+08:00`
- Base HEAD checked: `e672f1523c30037202310278daf71488681d9a1f`
- Parent closeout: G2.201, PR `#354`, merge commit `e672f1523c30037202310278daf71488681d9a1f`
- Source edit authority: no

Boundary note: this package classifies legacy adapter ownership. It does not
authorize source edits, compatibility wrapper deletion, route changes, OpenAPI
contract changes, frontend changes, config/script changes, OpenSpec changes, or
GitHub issue label changes.

## Decision

G2.202 classifies these files as legacy compatibility ownership surfaces, not as
an immediate implementation lane:

| Target | Current fact | Decision |
|---|---|---|
| `web/backend/app/services/data_adapters/dashboard.py` | Contains `DashboardDataSourceAdapter`, one `get_data_quality_monitor()` call, GitNexus upstream impact `LOW/0` | Candidate for future compatibility closure authorization; no source edits here |
| `web/backend/app/services/data_adapters/data_source.py` | Contains `DataDataSourceAdapter`, one `get_data_quality_monitor()` call, GitNexus upstream impact `LOW/0` | Candidate for future compatibility closure authorization; no source edits here |

Module-path consumer scan found no external Python imports of
`app.services.data_adapters.dashboard` or
`app.services.data_adapters.data_source` outside the legacy package. This is
useful evidence, but it is not deletion authority. Static non-use remains
insufficient to remove compatibility surfaces without a separate authorization
and rollback plan.

## Consumer Evidence

| Evidence | Result |
|---|---|
| Exact legacy module import scan | `external_python_legacy_module_imports=0` |
| Class-name text scan | Ambiguous because canonical `app.services.adapters.*` classes use the same names |
| Root facade truth | `web/backend/app/services/data_adapter.py` imports from canonical `app.services.adapters` |
| Factory truth | `web/backend/app/services/data_source_factory/data_source_factory.py` imports through the root facade, not the legacy module path |
| OpenAPI/docs/planning hits | Historical or generated references only; not runtime consumers |

## Scope Classification

| Surface | Classification | Source authority |
|---|---|---|
| Legacy `data_adapters/dashboard.py` and `data_adapters/data_source.py` | G2.202 decision target | No |
| `market_data_adapter.py` root facade | Deferred owner-specific compatibility facade surface | No |
| Singleton wrapper/backing API | Retained backing API; not a deletion lane | No |
| Canonical service adapters | Closed by G2.200/G2.201 | No |
| Route/OpenAPI/frontend/config/scripts/OpenSpec | Out of scope | No |

## Next Gate

Start G2.203 as an authorization-only package:

| Future gate | Scope | Source authority |
|---|---|---|
| G2.203 data-quality legacy adapter compatibility closure authorization | Decide the exact approved implementation shape for the two legacy files: thin compatibility wrapper, retirement, or retained legacy surface | No |

G2.203 must include, at minimum:

- current-HEAD module-path consumer scan
- GitNexus impact for both target files before authorizing any source edit lane
- exact implementation shape and rollback plan
- import smoke for `app.services.data_adapter` and `data_source_factory`
- focused regression plan if a later source implementation is approved
- explicit exclusion of `market_data_adapter.py`, singleton wrapper/backing API,
  canonical adapters, routes, OpenAPI, frontend, config, scripts, and OpenSpec
  files

## Verification

| Check | Result |
|---|---|
| JSON/YAML parse | Passed for generated decision JSON, `steward-index.json`, and `pr-355.yaml` |
| Markdown governance | Passed, `checked_files=6`, `errors=0` |
| OpenSpec validation | `openspec validate migrate-backend-singletons-to-lifecycle-di --strict` passed; PostHog network flush warning is telemetry noise |
| Diff whitespace | `git diff --check` and `git diff --cached --check` passed |
| GitNexus staged scope | Low risk, `changed_files=9`, `changed_symbols=0`, `affected_processes=0` |
| Mainline scope gate | Passed, `changed_files=9`, `violations=0`, report `/tmp/pr355-mainline-governance-report.json` |

## Non-Goals

- Do not edit `web/backend/app/services/data_adapters/dashboard.py`.
- Do not edit `web/backend/app/services/data_adapters/data_source.py`.
- Do not delete or convert the legacy files in G2.202.
- Do not touch `market_data_adapter.py`, singleton wrapper/backing API,
  canonical adapters, routes, OpenAPI, frontend, config, scripts, or OpenSpec
  files.

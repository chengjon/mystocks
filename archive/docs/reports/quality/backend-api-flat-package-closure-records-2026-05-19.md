# API Flat-Package Closure Records

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: static closure classification complete; runtime route/OpenAPI evidence attached on
`2026-05-21` after the `data_lineage` import blocker was fixed.

## Freshness

| Field | Value |
|---|---|
| `generated_at` | `2026-05-21` runtime refresh |
| `git_head` | `f97f2eb57 fix(api): repair data lineage companion imports` |
| `current_head_checked_at_review` | `f97f2eb57` |
| `stale_if_head_mismatch` | Yes |
| `worktree_state` | dirty-worktree evidence |
| `runtime_diff_artifact` | `.planning/codebase/generated/backend-route-openapi-diff-2026-05-21.json` |
| `runtime_diff_report` | `docs/reports/quality/backend-route-openapi-diff-2026-05-19.md` |

## Summary

| Domain | Flat file present | Package present | Router registry signal | Static `app.api` refs | Classification | Note |
|---|---|---|---|---:|---|---|
| `algorithms` | Yes | Yes | No direct router-registry hit in this static scan | 16 | `unknown pending runtime diff` | Keep runtime diff pending before claiming closure |
| `backup_recovery_secure` | Yes | Yes | Yes | 10 | `active and documented` | Package and flat path both still participate in the live surface |
| `indicators` | Yes | Yes | Yes | 4 | `active and documented` | Companion file `_indicator_cache_responses.py` is part of the current implementation pattern |
| `signal_monitoring` | Yes | Yes | Yes | 12 | `active and documented` | Companion file `_signal_history_responses.py` is part of the current implementation pattern |
| `stock_search` | Yes | Yes | Yes | 9 | `active and documented` | Flat/package coexistence is still visible in current consumers |
| `system` | Yes | Yes | Yes | 7 | `active and documented` | Companion file `_system_health_responses.py` is part of the current implementation pattern |

## Runtime Route / OpenAPI Evidence

Current Task 6 runtime evidence at `f97f2eb57`:

| Metric | Result |
|---|---:|
| Runtime routes | `548` |
| Runtime unique paths | `511` |
| Schema-visible routes | `536` |
| Hidden runtime routes | `12` |
| Endpoint modules | `98` |
| OpenAPI paths | `500` |
| OpenAPI operations | `536` |
| Duplicate operationIds | `0` |
| OpenAPI warning count | `0` |
| Runtime route path diff vs `2026-05-20` artifact | `+0 / -0` |
| OpenAPI path diff vs `2026-05-20` artifact | `+0 / -0` |

Per-domain closure attachment:

| Domain | Runtime evidence attached | Closure impact |
|---|---|---|
| `algorithms` | No route/OpenAPI path additions or removals in current refresh | Classification remains `unknown pending domain-specific consumer parity`; runtime diff is no longer blocked |
| `backup_recovery_secure` | No route/OpenAPI path additions or removals in current refresh | Classification remains `active and documented` |
| `indicators` | No route/OpenAPI path additions or removals in current refresh | Classification remains `active and documented` |
| `signal_monitoring` | No route/OpenAPI path additions or removals in current refresh | Classification remains `active and documented` |
| `stock_search` | No route/OpenAPI path additions or removals in current refresh | Classification remains `active and documented` |
| `system` | No route/OpenAPI path additions or removals in current refresh | Classification remains `active and documented` |

Runtime-only compatibility and control-plane routes are intentionally kept separate from the flat-package closure decision. In particular, `/api/strategy-mgmt/{path:path}` remains hidden from OpenAPI, and `/metrics` still has one hidden runtime entry plus one schema-visible exporter entry. Neither finding authorizes endpoint deletion from this report.

## Notes

- The current checkout no longer fails on the `data_lineage` import chain.
- Static closure classification is now paired with a current runtime route/OpenAPI diff, but this still does not replace per-domain consumer contract parity checks.
- No runtime-only hidden-from-schema or retired state is newly claimed by this report.

## Verification

- `git diff --check -- docs/reports/quality/backend-api-flat-package-closure-records-2026-05-19.md`
- `python scripts/compliance/markdown_governance_gate.py --root-dir . --format json docs/reports/quality/backend-api-flat-package-closure-records-2026-05-19.md`
- `env PYTHONPATH=web/backend python -c "from app.main import app; print(len(app.routes))"`
- `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py --collect-only -q --no-cov`

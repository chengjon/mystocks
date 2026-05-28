# Backend Data-Quality Market Data Adapter Provider Closeout Refresh - 2026-05-28

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Lane: G2.209 data-quality `market_data_adapter.py` provider seam closeout / residual refresh
- Prepared at: `2026-05-28T19:32:39+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `90d8f12cc01f9fb360abc531673e3ed9535706e7`
- Parent PR: `#361`
- Parent merge commit: `90d8f12cc01f9fb360abc531673e3ed9535706e7`
- Source edit authority: none

Boundary note: this report records closeout and residual classification only. It
does not authorize source edits, singleton wrapper deletion, route/OpenAPI
changes, frontend changes, OpenSpec edits, issue label changes, PM2 commands, or
PR merges.

## Closeout Result

G2.208 is merged by PR `#361`. The target provider seam is closed for
`web/backend/app/services/market_data_adapter.py`.

| Checkpoint | Current result |
|---|---|
| Constructor compatibility | `def __init__(self, config: Dict[str, Any], *, quality_monitor: Any = None):` |
| Positional `config` compatibility | Preserved |
| Optional injection shape | Keyword-only `quality_monitor` |
| Default behavior | Singleton fallback through `get_data_quality_monitor()` preserved |
| Injected behavior | Injected monitor bypasses the module-level getter |
| `data_source_factory` compatibility | `MarketDataSourceAdapter(config.__dict__)` remains the active factory call |

G2.209 does not reopen `market_data_adapter.py`. The retained fallback is
intentional compatibility behavior, not an unclosed implementation defect.

## Residual Scan

Residual scan at HEAD `90d8f12cc01f9fb360abc531673e3ed9535706e7`:

| Metric | Count |
|---|---:|
| `get_data_quality_monitor` hits under `web/backend/app/services` | 15 |
| `get_data_quality_monitor` hits under `web/backend/tests` | 12 |

Residual classification:

| Path | Classification | Handling |
|---|---|---|
| `web/backend/app/services/market_data_adapter.py` | Closed market-data adapter fallback | Closed by G2.208/G2.209; retained fallback is intentional |
| `web/backend/app/services/adapters/dashboard_adapter.py` | Closed canonical service adapter fallback | Covered by G2.200/G2.201; do not reopen without contradictory current evidence |
| `web/backend/app/services/adapters/data_adapter.py` | Closed canonical service adapter fallback | Covered by G2.200/G2.201; do not reopen without contradictory current evidence |
| `web/backend/app/services/adapters_split/base_adapter.py` | Closed adapter-split base fallback | Covered by G2.196/G2.197; do not reopen without contradictory current evidence |
| `web/backend/app/services/_data_quality_monitor_singleton.py` | Singleton backing API | Retained; requires separate ownership decision before source edits |
| `web/backend/app/services/data_quality_monitor.py` | Public singleton facade | Retained; requires separate ownership decision before source edits |
| `web/backend/app/services/data_adapter.py.backup.20260130` | Historical backup file | Not a G2.209 source target; cleanup needs separate repository hygiene authority |

Test-only residuals are expected in:

- `web/backend/tests/test_adapter_split_data_quality_monitor_provider.py`
- `web/backend/tests/test_data_quality_canonical_service_adapter_provider.py`
- `web/backend/tests/test_data_quality_legacy_data_adapter_compat.py`
- `web/backend/tests/test_data_quality_route_provider_regressions.py`
- `web/backend/tests/test_market_data_adapter_quality_monitor_provider.py`

## Verification Plan

The G2.209 PR must rerun the same post-merge evidence checks before it can be
accepted:

```bash
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_market_data_adapter_quality_monitor_provider.py -q --no-cov --tb=short
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_market_data_adapter_quality_monitor_provider.py web/backend/tests/test_market_data_service_getter_retirement.py web/backend/tests/_test_data_source_factory_management.py -q --no-cov --tb=short
python -m json.tool .planning/codebase/steward-tree/steward-index.json >/dev/null
python -m json.tool .planning/codebase/generated/data-quality-market-data-adapter-provider-closeout-refresh-2026-05-28.json >/dev/null
python scripts/compliance/markdown_governance_gate.py --root-dir . --format json docs/reports/quality/backend-data-quality-market-data-adapter-provider-closeout-refresh-2026-05-28.md .planning/codebase/steward-tree/current-next-gates.md .planning/codebase/steward-tree/branch-register.md .planning/codebase/steward-tree/evidence-index.md .planning/codebase/steward-tree/completed-ledger.md .planning/codebase/steward-tree/tracks/service-lifecycle-di.md
openspec validate migrate-backend-singletons-to-lifecycle-di --strict
python governance/mainline/scripts/mainline_scope_gate.py --task-card governance/mainline/task-cards/pr-362.yaml --schema governance/mainline/schemas/ai-task-card.schema.json --base-sha 90d8f12cc01f9fb360abc531673e3ed9535706e7 --head-sha HEAD --report /tmp/pr362-mainline-governance-report.json
```

## Next Gate

If G2.209 is accepted, start G2.210 as a decision package only:

- decide whether singleton/backing API residuals need a dedicated ownership
  package
- keep closed fallback surfaces closed unless current evidence contradicts their
  closeout reports
- keep historical backup cleanup separate from service lifecycle DI source
  implementation
- do not open a new source implementation lane directly from G2.209

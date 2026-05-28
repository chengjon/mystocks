# Backend Data-Quality Legacy Adapter Compatibility Wrapper Closeout Refresh

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: review candidate
- Prepared at: `2026-05-28T16:50:15+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `a621ba4ae66f581074a3b66539e296cbf0ced1b5`
- Worktree branch: `g2-205-data-quality-legacy-adapter-closeout-refresh`
- Scope: governance closeout and residual refresh only
- Source edit authority: none

## Parent State

PR `#357` merged G2.204 at
`a621ba4ae66f581074a3b66539e296cbf0ced1b5`.

G2.204 converted the two legacy data-quality adapter modules into thin
compatibility wrappers while preserving old import paths:

| Target | Post-merge state |
|---|---|
| `web/backend/app/services/data_adapters/dashboard.py` | Thin wrapper re-exporting canonical `DashboardDataSourceAdapter` |
| `web/backend/app/services/data_adapters/data_source.py` | Thin wrapper re-exporting canonical `DataDataSourceAdapter` |
| `web/backend/tests/test_data_quality_legacy_data_adapter_compat.py` | Focused compatibility test for old import paths and getter removal |

Deletion remains unauthorized. The wrappers are compatibility surfaces, not dead
files.

## Closed Capability

| Item | State | Evidence |
|---|---|---|
| Legacy wrapper target getter calls | Closed | `0` `get_data_quality_monitor` calls remain in the two legacy wrapper modules |
| Old module import paths | Preserved | Old module paths import canonical adapter classes |
| Legacy module deletion | Not authorized | G2.203 allowed only thin wrappers, not removal |
| Focused compatibility regression | Present | `web/backend/tests/test_data_quality_legacy_data_adapter_compat.py` |

## Post-Merge Residual Refresh

Post-merge text scan for `get_data_quality_monitor` under `web/backend/app` and
`web/backend/tests` produced `42` total hits. Active app hits excluding backup
files are `29`.

| Bucket | Files | Active hits | Current decision |
|---|---:|---:|---|
| Route provider backing | 1 | 17 | Retain as FastAPI dependency/provider surface; route-body direct-call migration is already closed by G2.192/G2.193 |
| `adapter_split` base fallback | 1 | 2 | Retain default singleton fallback after G2.196 constructor injection |
| Canonical service adapter fallbacks | 2 | 4 | Retain default fallback after G2.200 optional monitor injection |
| Legacy data adapter wrappers | 2 | 0 | Closed by G2.204; no remaining getter calls in target wrappers |
| `market_data_adapter.py` facade | 1 | 2 | Remaining compatibility facade; needs owner-specific decision before source work |
| Singleton wrapper / backing API | 2 | 4 | Retain public backing API; not a deletion lane |
| Backup artifact | 1 | 3 | Excluded from active source residual count; route through cleanup governance only |
| Tests | 4 | 10 | Expected regression evidence, not implementation backlog |

## Recommended Next Gate

Start G2.206 as a governance decision package:

| Next gate | Type | Source authority | Reason |
|---|---|---|---|
| G2.206 data-quality `market_data_adapter.py` compatibility facade ownership decision | Decision package | None | The legacy wrapper target is closed. `market_data_adapter.py` is now the next owner-specific compatibility facade that must be classified before singleton wrapper retirement can be considered |

G2.206 should not edit source. It should decide whether the
`market_data_adapter.py` facade is retained, wrapped, migrated, or scheduled for
a later authorized implementation lane.

## Explicit Non-Goals

This closeout does not authorize:

- backend source edits
- legacy wrapper deletion
- `market_data_adapter.py` edits
- singleton wrapper deletion or privatization
- `DataQualityMonitor` internals
- route or OpenAPI changes
- frontend changes
- OpenSpec proposal creation
- GitHub issue label changes

## Evidence Artifacts

| Artifact | Role |
|---|---|
| `.planning/codebase/generated/data-quality-legacy-adapter-compatibility-wrapper-implementation-2026-05-28.json` | G2.204 implementation evidence |
| `docs/reports/quality/backend-data-quality-legacy-adapter-compatibility-wrapper-implementation-2026-05-28.md` | G2.204 implementation report |
| `governance/mainline/task-cards/pr-357.yaml` | G2.204 source implementation scope card |
| `.planning/codebase/generated/data-quality-legacy-adapter-compatibility-wrapper-closeout-refresh-2026-05-28.json` | G2.205 machine-readable closeout / residual refresh |
| `docs/reports/quality/backend-data-quality-legacy-adapter-compatibility-wrapper-closeout-refresh-2026-05-28.md` | G2.205 human-readable closeout / residual refresh |
| `governance/mainline/task-cards/pr-358.yaml` | G2.205 governance-only PR scope card |

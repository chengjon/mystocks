# Frontend View Governance A3 Alert Rules Coverage Review

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: next-batch selection evidence for `openspec/changes/update-frontend-view-governance` after the A3 watchlist absorption batch.

This review does not move files, edit runtime code, update tests, or change routes.

## Decision

Select the next narrow batch as:

```text
A3-alert-rules-coverage-review
```

Do not approve `A3-alert-rules-archive` yet.

Reason: `web/frontend/src/views/monitoring/AlertRulesManagement.vue` is not an active route owner, but it still contains alert-rule CRUD capability that is not currently covered by the canonical `/risk/alerts` route. The safe next step is a CRUD absorption decision package, not an archive move.

## Function Tree Position

Primary function-tree domain:

- `06-监控与告警` -> `6.3 告警管理` -> `告警规则`.

Current active frontend successor:

- `/risk/alerts` -> `web/frontend/src/views/risk/Alerts.vue`.

Current function-tree wording says `/risk/alerts` can view rule status and read alert-rule interfaces. It does not prove create, update, or delete coverage.

Legacy source family:

- `web/frontend/src/views/monitoring/AlertRulesManagement.vue`
- `web/frontend/src/views/monitoring/composables/useAlertRulesManagement.ts`
- `web/frontend/src/views/monitoring/styles/AlertRulesManagement.scss`

## Coverage Matrix

| Legacy capability in `monitoring/AlertRulesManagement.vue` | Current canonical coverage in `/risk/alerts` | Decision |
| --- | --- | --- |
| List alert rules | Covered through `monitoringApi.getAlertRules()` with verified snapshot gating | Covered |
| Display rule status | Covered with active/inactive tags and rule stats | Covered |
| Display alert records | Covered through `monitoringApi.getAlerts()` with verified snapshot gating | Covered by canonical route, not legacy page |
| Create alert rule | Legacy has dialog form and calls `monitoringApi.createAlertRule()` | Gap |
| Update alert rule | Legacy has edit flow and calls `monitoringApi.updateAlertRule()` | Gap |
| Delete alert rule | Legacy has confirmation flow and calls `monitoringApi.deleteAlertRule()` | Gap |
| Rule fields: name, symbol, stock name, type | Legacy form covers these fields | Gap if CRUD is approved |
| Rule parameters: `include_st`, `change_percent_threshold`, `volume_ratio_threshold` | Legacy form covers these fields | Gap if CRUD is approved |
| Notification config: level and channels | Legacy form covers these fields | Gap if CRUD is approved |
| Priority and active flag | Legacy form covers these fields | Gap if CRUD is approved |
| Verified snapshot/provenance semantics | Canonical `/risk/alerts` has verified snapshot and stale-state handling | Keep canonical behavior; do not replace with legacy state model |
| Route/menu ownership | No active route/menu owner found for legacy page; `/risk/alerts` is current active entry | Legacy is not route truth |

## Current Active Blockers

Active code/test references still include:

- `web/frontend/src/views/monitoring/AlertRulesManagement.vue`
- `web/frontend/src/views/monitoring/composables/useAlertRulesManagement.ts`
- `web/frontend/src/views/monitoring/styles/AlertRulesManagement.scss`
- `web/frontend/tests/unit/config/monitoring-style-sources.spec.ts`
- `web/frontend/tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts`

The backend and frontend API surface already expose alert-rule CRUD:

- `monitoringApi.getAlertRules()`
- `monitoringApi.createAlertRule(data)`
- `monitoringApi.updateAlertRule(id, data)`
- `monitoringApi.deleteAlertRule(id)`

## Recommended Next Profile

Prepare an approval-only runtime absorption package:

```text
A3-alert-rules-crud-absorb-decision
```

Proposed scope:

- Decide whether `/risk/alerts` should become a read-write rule-management page or remain a read-only alert review page.
- If read-write is approved, absorb CRUD from `useAlertRulesManagement.ts` into the canonical `/risk/alerts` chain while preserving verified snapshot, stale-state, request-id, and partial-sync semantics.
- Do not create a new `/monitoring/alert-rules` route.
- Do not add a parallel store or route-local live snapshot.
- Do not archive the legacy monitoring page until CRUD coverage is either absorbed or formally rejected as out of scope.

## Required Pre-Mutation Checks For Any Later Runtime Absorption

```bash
rg -n "AlertRulesManagement|useAlertRulesManagement|AlertRulesManagement.scss|monitoring/AlertRulesManagement|src/views/monitoring/AlertRulesManagement" web/frontend/src web/frontend/tests web/frontend/package.json docs openspec --glob '!**/.claude/**'
rg -n "createAlertRule|updateAlertRule|deleteAlertRule|getAlertRules|/risk/alerts|alert-rules" web/frontend/src/views/risk web/frontend/src/api web/frontend/tests --glob '!**/.claude/**'
```

## Approval Needed

Recommended approval wording:

```text
批准执行 A3-alert-rules-crud-absorb-decision，只做 /risk/alerts canonical 链路的 CRUD 是否吸收判断和方案化；不归档 monitoring/AlertRulesManagement，除非后续单独审批 archive batch。
```

Without explicit approval, no runtime code or archive move should occur.

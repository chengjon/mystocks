# Frontend View Governance A3 Alert Rules Archive Approval Package

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: archive-decision package for the legacy monitoring alert-rule page after canonical `/risk/alerts` absorbed minimal alert-rule CRUD.

This package does not move files or edit tests. It prepares the exact archive candidate set and required guard retirements for a later mutation batch.

## Decision

Select the next narrow batch as:

```text
A3-alert-rules-archive-prep
```

Do not move files in this preparation batch.

Reason: the previous runtime batch added create, update, and delete rule coverage to `/risk/alerts` while preserving canonical verified snapshot refresh semantics. The old monitoring page is now a route-orphan duplicate for alert-rule management, but it still has direct config guard references that must be retired in the same archive mutation batch.

## Candidate Files

Proposed later archive target:

```text
archive/web/frontend/src/views/monitoring/alert-rules/
```

Candidate files:

- `web/frontend/src/views/monitoring/AlertRulesManagement.vue`
- `web/frontend/src/views/monitoring/composables/useAlertRulesManagement.ts`
- `web/frontend/src/views/monitoring/styles/AlertRulesManagement.scss`

## Function Tree Status

Function-tree node:

- `06-监控与告警 -> 6.3 告警管理 -> 告警规则`

Canonical successor:

- `/risk/alerts` -> `web/frontend/src/views/risk/Alerts.vue`
- Local canonical support component: `web/frontend/src/views/risk/AlertRuleManagementPanel.vue`

Lifecycle status after CRUD absorption:

- `AlertRulesManagement.vue`: `duplicate-redundant/archive-candidate`
- `useAlertRulesManagement.ts`: `page-local support/archive-with-owner`
- `AlertRulesManagement.scss`: `page-local style/archive-with-owner`

## Coverage Closure

| Legacy capability | Canonical successor coverage after absorption | Archive implication |
| --- | --- | --- |
| List alert rules | `/risk/alerts` uses `monitoringApi.getAlertRules()` with verified snapshot gating | Covered |
| Create alert rule | `AlertRuleManagementPanel.vue` emits create payload; `Alerts.vue` calls `monitoringApi.createAlertRule()` and refreshes canonical snapshot | Covered |
| Update alert rule | `AlertRuleManagementPanel.vue` emits update payload; `Alerts.vue` calls `monitoringApi.updateAlertRule()` and preserves verified rows on failure | Covered |
| Delete alert rule | `AlertRuleManagementPanel.vue` confirms deletion; `Alerts.vue` calls `monitoringApi.deleteAlertRule()` and refreshes canonical snapshot | Covered |
| Rule fields | Canonical panel covers name, symbol, stock name, type, thresholds, notification level/channels, priority, active flag | Covered |
| Legacy local state model | Replaced by canonical `/risk/alerts` verified snapshot refresh semantics | Do not preserve as runtime truth |
| Legacy style | Page-local only | Archive with owner |

## Active Reference Findings

Current active code/test references found by exact search:

- `web/frontend/tests/unit/config/monitoring-style-sources.spec.ts` directly reads `src/views/monitoring/styles/AlertRulesManagement.scss`.
- `web/frontend/tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts` directly reads `src/views/monitoring/AlertRulesManagement.vue`.
- `web/frontend/src/views/monitoring/AlertRulesManagement.vue` imports `./composables/useAlertRulesManagement` and `./styles/AlertRulesManagement.scss`.

No current `router/index.ts` or `MenuConfig.ts` route ownership was found for `AlertRulesManagement.vue` in this A3 review line. Historical docs and inventory reports still mention the file, but those are not active runtime references.

## Required Guard Retirement In Later Archive Batch

The later archive mutation batch must update these direct guards in the same commit:

- Remove `src/views/monitoring/styles/AlertRulesManagement.scss` from `web/frontend/tests/unit/config/monitoring-style-sources.spec.ts`.
- Remove `src/views/monitoring/AlertRulesManagement.vue` from `web/frontend/tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts`.

Do not remove guards for:

- `RiskDashboard.vue`
- `WatchlistManagement.vue`
- their styles or composables

Those pages remain separate A3 candidates and require their own successor coverage decisions.

## Required Pre-Move Checks

Run before any file move:

```bash
rg -n "AlertRulesManagement|useAlertRulesManagement|AlertRulesManagement.scss|monitoring/AlertRulesManagement|src/views/monitoring/AlertRulesManagement" web/frontend/src web/frontend/tests web/frontend/package.json docs openspec --glob '!**/.claude/**'
rg -n "AlertRuleManagementPanel|createAlertRule|updateAlertRule|deleteAlertRule|getAlertRules|/risk/alerts" web/frontend/src/views/risk web/frontend/src/api web/frontend/tests --glob '!**/.claude/**'
```

Expected active references after the move:

- No active source/test references to `web/frontend/src/views/monitoring/AlertRulesManagement.vue`.
- No active source/test references to `web/frontend/src/views/monitoring/composables/useAlertRulesManagement.ts`.
- No active source/test references to `web/frontend/src/views/monitoring/styles/AlertRulesManagement.scss`.
- Historical docs may continue to mention the old path as historical record.

## Required Validation In Later Archive Batch

Targeted validation:

```bash
cd web/frontend && npx vitest run tests/unit/config/monitoring-style-sources.spec.ts tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts src/views/risk/__tests__/Alerts.spec.ts
openspec validate update-frontend-view-governance --strict
python scripts/compliance/markdown_governance_gate.py --root-dir /opt/claude/mystocks_spec --format text --path openspec/changes/update-frontend-view-governance/tasks.md
```

If staged files include frontend `.vue` or test files, the commit hook file-size guard must pass.

Before committing, stage only the intended archive files, guard edits, and task update, then run `gitnexus_detect_changes(scope="staged")`.

## Approval Needed

Recommended approval wording:

```text
批准执行 A3-alert-rules-archive，只移动 AlertRulesManagement.vue、useAlertRulesManagement.ts、AlertRulesManagement.scss 到 archive/web/frontend/src/views/monitoring/alert-rules/，并只退休这三个文件的直接 config guard；不触碰 RiskDashboard/WatchlistManagement。
```

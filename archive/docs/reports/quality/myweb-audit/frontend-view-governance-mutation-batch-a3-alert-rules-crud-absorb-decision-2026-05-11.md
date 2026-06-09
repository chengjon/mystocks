# Frontend View Governance A3 Alert Rules CRUD Absorb Decision Package

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: approval package for deciding whether canonical `/risk/alerts` should absorb alert-rule CRUD capability from `web/frontend/src/views/monitoring/AlertRulesManagement.vue`.

This package does not approve runtime edits by itself. It records the proposed scope, guardrails, tests, and explicit non-scope before any code mutation.

## Current Truth

Canonical route truth:

- `/risk/alerts` is implemented by `web/frontend/src/views/risk/Alerts.vue`.
- `MenuConfig.ts` points the risk alert entry to `/risk/alerts`.
- `FUNCTION_TREE.md` positions alert-rule management under `06-监控与告警 -> 6.3 告警管理`.

Canonical behavior today:

- Reads alert rules through `monitoringApi.getAlertRules()`.
- Reads alert records through `monitoringApi.getAlerts({ page: 1, page_size: 50 })`.
- Preserves verified snapshot, stale-state, request-id, partial-sync, and first-load failure semantics.
- Does not expose create, update, or delete rule UI.

Legacy capability source:

- `web/frontend/src/views/monitoring/AlertRulesManagement.vue`
- `web/frontend/src/views/monitoring/composables/useAlertRulesManagement.ts`

Reusable API surface already exists:

- `monitoringApi.createAlertRule(data)`
- `monitoringApi.updateAlertRule(id, data)`
- `monitoringApi.deleteAlertRule(id)`

## Recommended Decision

Approve a small absorption batch only if `/risk/alerts` is intended to be the read-write alert-rule management surface.

Recommended profile:

```text
A3-alert-rules-crud-absorb-minimal
```

This should add canonical CRUD coverage to `/risk/alerts` without restoring legacy `/monitoring/*` routing and without creating a second alert-rule state truth.

## Proposed Scope If Approved

Runtime files likely in scope:

- `web/frontend/src/views/risk/Alerts.vue`
- `web/frontend/src/views/risk/__tests__/Alerts.spec.ts`

Permitted behavior changes:

- Add a rule-management action area to the existing `规则列表` panel.
- Add create/edit dialog fields for rule name, symbol, stock name, rule type, parameters, notification level/channels, priority, and active flag.
- Add delete confirmation for selected rule.
- Reuse `fetchRiskAlerts()` after successful create/update/delete so canonical verified snapshot semantics remain centralized.
- Keep `monitoringApi` as the only transport surface; do not introduce a new store or route-local live snapshot.

## Hard Guardrails

- Do not restore `/monitoring/alert-rules` or any `/monitoring/*` page route.
- Do not move or archive `AlertRulesManagement.vue` in the same CRUD absorption batch.
- Do not copy legacy composable state wholesale if it bypasses `/risk/alerts` verified snapshot semantics.
- Do not display request IDs, counts, or rule totals from unverified mutation responses as route truth.
- Do not add fake defaults, demo rows, random metrics, or snapshot fallbacks.
- Do not broaden the batch to `RiskDashboard.vue` or `WatchlistManagement.vue`.

## TDD Plan If Approved

Add or extend tests in `web/frontend/src/views/risk/__tests__/Alerts.spec.ts` before implementation:

1. RED: create-rule action posts through `monitoringApi.createAlertRule()` and refreshes rules through `getAlertRules()` only after success.
2. RED: edit-rule action posts through `monitoringApi.updateAlertRule(id, payload)` and keeps stale verified rows visible when update fails.
3. RED: delete-rule action calls `monitoringApi.deleteAlertRule(id)` only after confirmation and refreshes canonical rules after success.
4. RED: first-load and partial-sync tests continue to prove no unverified request id, counts, or empty states leak into the page.

Expected GREEN scope:

- Minimal UI and handlers in `Alerts.vue`.
- Mock additions for `createAlertRule`, `updateAlertRule`, and `deleteAlertRule`.
- No router, menu, package, global store, or legacy monitoring file mutation.

## Required Verification If Approved

Targeted checks:

```bash
cd web/frontend && npx vitest run src/views/risk/__tests__/Alerts.spec.ts
openspec validate update-frontend-view-governance --strict
python scripts/compliance/markdown_governance_gate.py --root-dir /opt/claude/mystocks_spec --format text --path openspec/changes/update-frontend-view-governance/tasks.md
```

Pre-commit scope check:

```text
Stage only the approved runtime/test/doc files, then run gitnexus_detect_changes(scope="staged").
```

## Archive Decision After Absorption

Even if CRUD absorption is approved and completed, archive still requires a separate batch.

Later archive candidates would be:

- `web/frontend/src/views/monitoring/AlertRulesManagement.vue`
- `web/frontend/src/views/monitoring/composables/useAlertRulesManagement.ts`
- `web/frontend/src/views/monitoring/styles/AlertRulesManagement.scss`

Archive remains blocked until:

- CRUD coverage is proven or explicitly rejected.
- Direct style and normalization guards are retired or migrated.
- Active-reference checks are clear.
- A separate archive approval names the exact files to move.

## Approval Options

Recommended approval wording:

```text
批准执行 A3-alert-rules-crud-absorb-minimal，只在 /risk/alerts canonical 页面吸收最小规则 CRUD，并保留现有 verified snapshot / provenance 语义；不归档 monitoring/AlertRulesManagement。
```

Alternative rejection wording:

```text
拒绝 A3-alert-rules CRUD 吸收，/risk/alerts 保持只读告警审查页；将 legacy AlertRulesManagement 标记为保留待产品决策，不进入 archive。
```

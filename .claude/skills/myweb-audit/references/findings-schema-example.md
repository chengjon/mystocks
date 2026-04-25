# Findings Schema Example

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

Normalize each role output into this structure before merge and deduplication.

For machine validation, use `findings-schema.json`. This file remains the human-readable reference and example payload source.

## Minimal Schema

```yaml
finding_id: market-overview-functional-001
batch_id: market-batch-01
page:
  route: /market/overview
  page_key: market-overview
  route_class: canonical-page
  canonical_entry: web/frontend/src/views/market/MarketOverview.vue
source_role: functional-audit
severity: High
issue_type: interaction
title: Filter reset button does not restore default table query
trigger:
  steps:
    - Open /market/overview
    - Apply a symbol filter
    - Click reset
expected: Default query params and visible table rows return to the initial state.
actual: UI controls clear, but the table stays filtered until a manual refresh.
evidence:
  kind: code-path-review
  note: Reset handler clears control state but the filtering path remains disconnected from rendered rows.
repair_target:
  files:
    - web/frontend/src/views/market/MarketOverview.vue
    - web/frontend/src/composables/useMarketFilters.ts
can_fix_frontend: true
shared_impact_candidate: false
cross_page_impact: []
status: open
dependency: null
dedupe_key: /market/overview:interaction:useMarketFilters
verification_surface: live-audit
verification:
  required: true
  complete: false
  notes: Re-check reset flow and data refresh after fix.
```

## Merge Example

Use this shape after main-skill deduplication:

```yaml
consolidated_issue_id: market-overview-issue-01
severity: High
title: Filter reset leaves stale filtered results on market overview
pages:
  - /market/overview
source_roles:
  - functional-audit
  - data-state-audit
why_consolidated: Both roles describe the same broken reset and stale-render behavior.
repair_decision: fix-now
deferred_reason: null
verification_scope:
  routes:
    - /market/overview
  states:
    - default
    - loading
  breakpoints:
    - 1920
    - 1440
    - 1280
```

## Normalization Rules

- Keep one finding per discrete issue, not one finding per sentence.
- `source_role` must stay singular in raw findings.
- `severity` must use only `Blocking`, `High`, `Medium`, or `Low`.
- `issue_type` should stay practical: `route`, `interaction`, `data-state`, `visual`, `responsive`, `a11y`, or `dependency`.
- `route_class` should stay practical: `canonical-page`, `detail-page`, or `compatibility-redirect`.
- `expected` and `actual` are required for anything above `Low`.
- `dependency` must be explicit when a fix is out of scope.
- `can_fix_frontend` must state whether the issue is fixable inside the approved frontend batch without backend/API redesign.
- `dedupe_key` must be constructed as `{route}:{issue_type}:{primary_repair_target_component_or_file}` with file extension omitted when a file name is used.
- Findings from different roles with the same `dedupe_key` describe the same underlying issue and must be consolidated.
- `verification_surface` should be `live-audit` or `code-review-only`.
- `evidence.kind` should describe the strongest available proof surface, for example `live-observation`, `network-observation`, or `code-path-review`.
- Use the same finding fields across all audit roles except `route-inventory`, which is a scope-setting role rather than a finding-producing role.

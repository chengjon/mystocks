# HTML5 Migration Accessibility ARIA Coverage Audit

Date: 2026-05-12
Change: `implement-html5-migration-experience-optimization`
Task focus: `2.8.2 Add comprehensive ARIA attributes`
Scope: Desktop-only, repo-local audit only

## Decision

`2.8.2` remains open.

This batch records the current ARIA coverage evidence for the Desktop-only frontend surface. The repo already has useful ARIA implementation points in navigation, status regions, tabs, tables, dialogs, forms, and ArtDeco primitives, but the evidence is still partial. It does not prove comprehensive coverage across the seven canonical domains, all chart surfaces, all filter/trading forms, and all table/data-value patterns.

## Evidence Checked

Commands:

```bash
rg -n "role=\"(table|grid|img|tablist|tab|dialog|status|alert|search|navigation|tree|treeitem|button|switch)\"|aria-label|aria-labelledby|aria-describedby|aria-live|aria-busy|aria-selected|aria-expanded|aria-controls|aria-current|aria-modal" web/frontend/src/views web/frontend/src/components/artdeco web/frontend/src/components/menu web/frontend/src/components/market
sed -n '1,180p' web/frontend/src/components/artdeco/charts/ArtDecoChart.vue
sed -n '210,330p' web/frontend/src/views/trade/Center.vue
sed -n '190,270p' web/frontend/src/views/trade/History.vue
sed -n '1,120p' web/frontend/src/views/risk/Center.vue
sed -n '1,120p' web/frontend/src/views/data/Advanced.vue
```

Observed repo facts:

- `web/frontend/src/components/menu/TreeMenu.vue` provides the strongest current menu surface: `aria-label="Main Navigation"`, `role="navigation"`, `role="search"`, `role="tree"`, `role="treeitem"`, `aria-expanded`, `aria-selected`, and `aria-current`.
- `web/frontend/src/components/artdeco/navigation/ArtDecoCollapsibleSidebar.vue` exposes collapse state with `aria-expanded`, `aria-controls`, and button labels; `ArtDecoBreadcrumb.vue` exposes breadcrumb navigation labels.
- Status and feedback regions exist in several ArtDeco primitives and routed views, including `ArtDecoSkeleton.vue`, `ArtDecoToast.vue`, `ArtDecoStatCard.vue`, and business views using `role="status"`, `role="alert"`, or `aria-live="polite"`.
- Tab-like interaction surfaces exist in `web/frontend/src/views/data/Advanced.vue`, `web/frontend/src/views/risk/Center.vue`, and ArtDeco dashboard/template surfaces with `role="tablist"`, `role="tab"`, `aria-selected`, and `aria-controls`.
- Trading tables in `web/frontend/src/views/trade/Center.vue` and `web/frontend/src/views/trade/History.vue` use `role="table"`, `aria-label`, `aria-busy`, row groups, rows, column headers, and cells.
- `web/frontend/src/components/artdeco/charts/ArtDecoChart.vue` exposes chart containers as `role="img"` with a configurable accessible label.
- Form/control primitives include examples such as `ArtDecoSelect.vue` labels and `ArtDecoMechanicalSwitch.vue` with `role="switch"`, `aria-checked`, and labels.
- `web/frontend/src/views/risk/AlertRuleManagementPanel.vue` exposes a dialog surface with `role="dialog"` and `aria-modal="true"`.

## Gap Summary

The current codebase has meaningful ARIA surfaces, but there is no complete Desktop-only ARIA coverage matrix for the seven canonical business domains. Menu/navigation coverage is comparatively strong; chart, table, filter form, trading form, market value, and dialog coverage still needs explicit inventory and acceptance evidence.

Chart coverage is not yet comprehensive. `ArtDecoChart.vue` has `role="img"` and an accessible label, but this audit did not find a consistent data-summary, axis/trend narration, or `aria-describedby` pattern for chart interpretation.

Table coverage is partial. Some trading tables have ARIA table roles and labels, but this audit does not prove that all data tables are covered or that keyboard/table navigation semantics are complete.

Form coverage is partial. Select/switch primitives and some local labels exist, but there is no complete required/error/help association matrix covering `aria-describedby`, invalid state, validation messages, and filter/trading form fields.

Dialog coverage is partial. At least one risk dialog exposes `role="dialog"` and `aria-modal`, but this audit did not verify all dialogs for accessible naming, focus trap, focus return, and escape behavior.

## Task Disposition

Keep `2.8.2` unchecked until a later approved batch produces a comprehensive Desktop-only ARIA inventory and closes the identified gaps with verification evidence.

Minimum future evidence should include:

- A seven-domain ARIA coverage matrix for navigation, charts, tables, filters, forms, dialogs, status/error regions, and market/trading values.
- Remediation evidence for chart summaries or approved chart accessibility alternatives.
- Form field label/help/error associations for key filters and trading forms.
- Dialog accessible-name, focus-trap, and focus-return verification.
- Targeted automated or manual accessibility verification for the covered route/component set.

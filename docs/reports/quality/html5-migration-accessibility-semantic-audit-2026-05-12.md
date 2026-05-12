# HTML5 Migration Accessibility Semantic Audit

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。

Date: 2026-05-12
Change: `implement-html5-migration-experience-optimization`
Task focus: `2.8.1 Audit and optimize HTML5 semantic elements`
Scope: Desktop-only, repo-local audit only

## Decision

`2.8.1` is closed for the repo-local Desktop active shell semantic audit plus skip-link/main-target optimization scope.

This batch adds a concrete semantic-audit record for the current Desktop-only frontend shell and closes the active-shell skip-link gap. It does not claim WCAG closure, screen-reader acceptance, or comprehensive semantic coverage across every data table, form, and chart.

## Evidence Checked

Commands:

```bash
rg -n "<main|<nav|<header|<section|<article|role=|aria-|tabindex|ArtDecoSkipLink|id=\"main-content\"" web/frontend/src/layouts web/frontend/src/components/menu web/frontend/src/views/{market,data,watchlist,strategy,trade,risk,system} web/frontend/src/components/artdeco
sed -n '1,220p' web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue
sed -n '1,220p' web/frontend/src/layouts/BaseLayout.vue
sed -n '1,220p' web/frontend/src/components/menu/TreeMenu.vue
```

Observed repo facts:

- `web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue` uses `<main id="main-content" class="artdeco-main" tabindex="-1">` for the active ArtDeco shell.
- `web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue` now renders the existing `ArtDecoSkipLink` before the sidebar, so keyboard users can skip directly to the active main landmark.
- `web/frontend/src/components/menu/TreeMenu.vue` uses `<nav aria-label="Main Navigation" role="navigation">`, `role="search"`, `role="tree"`, `role="treeitem"`, `aria-expanded`, `aria-selected`, and `aria-current`.
- `web/frontend/src/layouts/BaseLayout.vue` still has the stronger skip-link pattern: `<ArtDecoSkipLink />` plus `<main id="main-content" tabindex="-1">`.
- Many current business views use semantic sections and live/status/error roles, including `market/Realtime.vue`, `data/Advanced.vue`, `risk/Center.vue`, `trade/Center.vue`, `trade/History.vue`, and `system/Health.vue`.
- ArtDeco base/core components already expose several semantic affordances, including `ArtDecoBreadcrumb.vue` with breadcrumb navigation, `ArtDecoSkeleton.vue` with `role="status"`, `ArtDecoToast.vue` with alert/live regions, `ArtDecoStatCard.vue` with status/live labels, and `ArtDecoChart.vue` with `role="img"`.

## Gap Summary

The active ArtDeco shell now exposes the same skip-link target contract as the legacy layout: `ArtDecoSkipLink` plus `id="main-content"` and `tabindex="-1"` on the active main landmark.

The route/component surface has many local semantic elements, but this audit is not yet a complete seven-domain semantic matrix with remediation evidence. It should not be used to claim WCAG closure, full semantic optimization, or screen-reader acceptance.

## Task Disposition

Mark `2.8.1` checked for this repo-local scope.

Verification:

```bash
cd web/frontend && npm run test -- tests/unit/layout/ArtDecoLayoutEnhanced.accessibility.spec.ts
```

Result: `1 passed`.

Remaining accessibility work should continue under `2.8.2-2.8.5`: comprehensive ARIA inventory, keyboard-only route matrix, screen-reader copy rules for financial data, WAVE / broader axe coverage, and WCAG acceptance evidence.

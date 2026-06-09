# HTML5 Migration Accessibility Keyboard Navigation Audit

Date: 2026-05-12
Change: `implement-html5-migration-experience-optimization`
Task focus: `2.8.3 Implement keyboard navigation improvements`
Scope: Desktop-only, repo-local audit only

## Decision

`2.8.3` remains open.

This batch records current keyboard-navigation evidence for the Desktop-only frontend surface. The repo already has meaningful local keyboard support in the menu tree, command palette, selected tab surfaces, collapsible panels, inputs, and a few specialized widgets. It does not yet provide a complete keyboard-only acceptance matrix for all seven canonical domains, routed shells, dialogs, forms, tables, and chart/data surfaces.

## Evidence Checked

Commands:

```bash
rg -n "keydown|keyup|KeyboardEvent|tabindex|focus\\(|blur\\(|ArrowUp|ArrowDown|ArrowLeft|ArrowRight|Enter|Escape|Space|Home|End|focus-trap|focusTrap|trapFocus|skip" web/frontend/src/layouts web/frontend/src/components web/frontend/src/views/{market,data,watchlist,strategy,trade,risk,system}
sed -n '1,260p' web/frontend/src/components/menu/TreeMenu.vue
rg -n "keyboard|focus|tab|shortcut|accessibility|axe|skip" web/frontend/tests docs/reports/quality openspec/changes/implement-html5-migration-experience-optimization -g '*.ts' -g '*.md' -g '*.vue'
```

Observed repo facts:

- `web/frontend/src/components/menu/TreeMenu.vue` implements a virtual keyboard cursor for menu navigation and handles `Ctrl/Cmd+K`, `ArrowUp`, `ArrowDown`, `ArrowLeft`, `ArrowRight`, `Enter`, and `Space`.
- `web/frontend/src/components/menu/CommandPalette.vue` and `web/frontend/src/components/shared/command-palette/CommandPalette.vue` handle search focus and command selection with arrow keys, `Enter`, and `Escape`.
- `web/frontend/src/views/risk/Center.vue` provides a tablist with roving `tabindex`, keyboard handlers for arrow keys, `Home`, and `End`, and moves focus to the active tab.
- `web/frontend/src/views/data/Advanced.vue` exposes tablist/tab roles and roving `tabindex` for its active tab surface.
- `web/frontend/src/components/artdeco/base/ArtDecoCollapsible.vue` supports `Enter` and `Space` toggling with `tabindex="0"`.
- `web/frontend/src/components/artdeco/base/ArtDecoSkipLink.vue` exists and can focus `#main-content`, while `web/frontend/src/layouts/BaseLayout.vue` still provides `id="main-content"` and `tabindex="-1"`.
- The active ArtDeco shell `web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue` was not found to expose the same `ArtDecoSkipLink` plus `#main-content` focus target contract.
- `web/frontend/tests/e2e/accessibility-smoke.spec.ts` and `npm run test:e2e:axe` provide limited accessibility smoke coverage, but they are not a keyboard-only route matrix.

## Gap Summary

The strongest local keyboard surface is the menu tree and command palette. Several individual widgets and tab surfaces also support keyboard interaction. However, this does not yet prove global keyboard navigation quality.

There is no complete Desktop-only keyboard-only E2E matrix for the seven canonical domains. This audit did not find route-level evidence for logical Tab order, visible focus continuity, skip-link behavior in the active ArtDeco shell, table navigation expectations, chart interaction expectations, or form submission/error recovery using keyboard only.

Dialog coverage remains incomplete. At least one dialog has ARIA dialog markers from the ARIA audit, but this keyboard audit did not verify focus trap, focus return, `Escape` behavior, or first-focus placement for the full dialog inventory.

The active shell still differs from the legacy `BaseLayout.vue` skip-link target contract. Until the active layout either adopts that contract or documents an approved alternative, keyboard navigation cannot be considered fully closed.

## Task Disposition

Keep `2.8.3` unchecked until a later approved batch adds or verifies a Desktop-only keyboard-navigation acceptance matrix.

Minimum future evidence should include:

- Keyboard-only route traversal for the seven canonical domains.
- Active shell skip-link/main-target verification or an approved equivalent landmark/focus strategy.
- Focus-visible and logical Tab order verification for key menu, header, table, chart, form, and status surfaces.
- Dialog focus-trap, focus-return, first-focus, and `Escape` behavior verification.
- Keyboard-only interaction checks for the command palette, tablists, trading forms, and representative data tables.

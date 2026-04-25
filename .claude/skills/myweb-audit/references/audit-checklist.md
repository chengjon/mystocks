# Audit Checklist

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

Use this checklist for every audited page.

## 1. Structure

Check whether the page has the expected regions and hierarchy:

- title/header area
- filter/search/control area
- content area
- action area
- table, chart, card, or detail panel
- pagination or load-more behavior when applicable
- modal/drawer/popup entry and close path when applicable

Flag issues when regions are missing, merged confusingly, visually collapsed, or structurally inconsistent with similar pages.

Also check:

- whether the page is composed from the appropriate existing page family structure and shared ArtDeco components, rather than drifting into one-off local component patterns
- whether the page follows the existing container width, page padding, workbench margin, and module-wrapper conventions used by its page family

## 2. Functional Interaction

Check whether the page can complete user tasks:

- buttons are clickable and correctly labeled
- links navigate to the expected route
- tabs switch content correctly
- filters, sorting, and pagination work as intended
- forms accept input, validate, submit, reset, and cancel correctly
- dialogs open, close, and preserve or reset state correctly
- back/return flows are clear and usable

Flag issues when the user cannot complete the primary task or when interactions are misleading.

Also check interaction feedback:

- action buttons show appropriate loading or disabled feedback during async work
- success, warning, or failure feedback is visible when the action completes
- repeated clicks are not silently accepted when the action should be locked
- dialog submit and cancel actions provide clear result feedback

In `code-review-only` runs, also check:

- whether click handlers or row-click handlers are empty or no-op
- whether emitted events have a meaningful downstream consumer
- whether visible controls actually affect query params, filtered rows, tab content, or submitted payloads

## 3. Data / API / State

Check whether requests and rendered content are aligned:

- API URL and method are appropriate for the page action
- request trigger timing is correct
- request parameters match UI state
- visible content matches returned data
- loading state is visible and not misleading
- empty state is explicit and understandable
- error state is visible and actionable
- disabled/no-permission state is explicit
- extreme-data state does not break the layout or meaning

Flag issues when visible values disagree with API data, when states are missing, or when state transitions are unclear.

Also check refresh behavior:

- changing filters, sorting, tabs, or pagination triggers the correct data refresh path
- returning to the page does not leave obviously stale data without visual indication
- page-level refresh actions and auto-refresh indicators, if present, remain consistent with visible data

Also check display-format correctness:

- dates, times, percentages, prices, quantities, and precision-sensitive numbers are rendered in a format that matches the data meaning
- rounding, truncation, separators, and units do not distort the returned data

Also check state transitions:

- loading -> empty
- loading -> success
- loading -> error
- error -> retry -> success
- disabled/no-permission -> restored access when applicable

State changes should not leave stale content, broken placeholders, or misleading feedback behind.

In `code-review-only` runs, also check:

- whether one failed request incorrectly clears other successfully loaded data surfaces
- whether related pages normalize equivalent API payload shapes consistently
- whether route meta, generated page config, and actual service calls disagree on the page's API truth

## 4. Visual Quality

Check visual structure and proportion:

- heading hierarchy is clear
- card/table/chart proportions are appropriate
- font sizes fit the page density
- spacing inside modules is consistent
- spacing between modules reflects hierarchy
- alignment is stable across columns and blocks
- buttons and controls use consistent heights and padding
- borders, dividers, and shadows are restrained and intentional

Flag issues when the page feels crowded, weakly grouped, visually noisy, or inconsistent with related pages.

Also check token compliance:

- typography, color, spacing, border, glow, and transition choices should follow existing project tokens or shared ArtDeco styles
- avoid local hardcoded values when an established token or shared component already exists

Also check breakpoint-level visual consistency:

- the page should preserve the same visual family across breakpoints
- font treatment, spacing rhythm, control density, and module grouping should remain coherent when the layout compresses

## 5. Responsive

Check at `1920`, `1440`, and `1280`.

Optional informational-only observation may be recorded at `1024`, but it is not a defect baseline for this project.

At required desktop breakpoints, check:

- no horizontal overflow unless explicitly justified
- no clipped text or controls
- no overlapping sections
- stacked layouts remain readable
- dense tables/charts degrade gracefully
- control groups remain usable on narrow widths

Flag issues when layout breaks, key actions disappear, or the page becomes hard to use at supported desktop widths.

In `code-review-only` runs, also flag architecture-level responsive redlines:

- mobile-width media queries that contradict the desktop-only support policy
- layout branches primarily designed for widths below the supported baseline

## 6. Accessibility

Check practical accessibility basics:

- text contrast is sufficient for reading
- focus state is visible
- disabled state is distinguishable
- clickable areas are large enough
- labels or contextual text exist for form controls
- icon-only buttons remain understandable

Flag issues when users cannot confidently identify, focus, read, or activate controls.

Also check keyboard operability:

- interactive controls can be reached in a sensible tab order
- Enter or Space works where appropriate
- keyboard focus is not lost inside dialogs, drawers, or tab flows

## 7. Design Consistency

Check whether the page matches established project patterns:

- same page family uses similar header and control structure
- cards, tables, filters, and actions follow existing component patterns
- tokens and style choices do not drift locally
- no isolated one-off styling without clear reason

Flag issues when a page visually diverges from its page family or reimplements common patterns inconsistently.

Also check shared-component consistency:

- the same shared button, card, badge, dialog, table, or status pattern should not drift in style or interaction across pages without a clear approved reason

## 8. Required States

Each page must be checked for:

- default
- loading
- empty
- error
- disabled/no-permission
- extreme-data

Do not stop at the default success path.

Note:
This project is a desktop-first workbench. Responsive checks are for layout stability and usability, not for promising a separate mobile product experience.
Widths below `1280` should not be treated as required responsive targets unless the user explicitly requests exploratory observation.

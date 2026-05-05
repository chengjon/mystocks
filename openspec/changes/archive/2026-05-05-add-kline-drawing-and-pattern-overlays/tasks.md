## 1. Specification

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- [x] 1.1 Add a new `technical-chart-analysis` capability that defines manual K-line drawing tools and backend-driven pattern overlays.
- [x] 1.2 Freeze the MVP tool scope to `trendline`, `horizontal line`, and `rectangle`.
- [x] 1.3 Freeze the MVP pattern scope to `double_top`, `double_bottom`, `head_shoulders_top`, and `head_shoulders_bottom`.
- [x] 1.4 Define a reviewed pattern-result contract with chart-renderable anchor points and provenance boundaries.

## 2. Backend Implementation

- [x] 2.1 Implement the reviewed pattern endpoint contract on the existing dedicated route `web/backend/app/api/_technical_patterns_router.py`; this is net-new detection work on top of an existing placeholder entry point, not a drop-in replacement of a real detector.
- [x] 2.2 Add Pydantic request/response models for `GET /api/v1/technical/patterns/{symbol}`, including `PatternDetection` and `PatternAnchorPoint`.
- [x] 2.3 Implement backend detection flow for `double_top`, `double_bottom`, `head_shoulders_top`, and `head_shoulders_bottom`.
- [x] 2.4 Ensure the backend returns structured detections with `pattern_name`, `direction`, `confidence`, and ordered `anchor_points`.
- [x] 2.5 Ensure the backend returns an empty reviewed result when no pattern is detected, rather than fabricating inferred labels.
- [x] 2.6 Add backend tests for supported detections, empty-result behavior, anchor-point payload shape, and `422/503` contract behavior.

## 3. Frontend Implementation

- [x] 3.1 Add `web/frontend/src/components/technical/composables/useChartOverlays.ts` as the chart overlay orchestration layer for manual and automatic overlays.
- [x] 3.2 Implement manual drawing creation for `trendline` and `horizontal line` using KLineChart official overlay primitives.
- [x] 3.3 Implement manual `rectangle` drawing as a reviewed custom overlay built on the official KLineChart overlay/figure APIs.
- [x] 3.4 Implement manual overlay operations for `select`, `delete`, and `clear all`.
- [x] 3.5 Integrate the frontend overlay layer with the reviewed backend pattern contract from section `2.x`; automatic overlays depend on the backend payload being in place first.
- [x] 3.6 Render backend pattern detections as read-only overlays on the same chart surface.
- [x] 3.7 Distinguish manual overlays from automatic overlays in toolbar state and chart styling.
- [x] 3.8 Surface backend detection loading and user-facing error states without breaking manual drawing behavior.

## 4. Validation

- [x] 4.1 Run `openspec validate add-kline-drawing-and-pattern-overlays --strict`.
- [x] 4.2 Run targeted backend tests for pattern detection and API payload shape.
- [x] 4.3 Run targeted frontend tests for manual overlay behavior and automatic overlay rendering.
- [x] 4.4 Add a cross-boundary integration check that verifies: backend returns a reviewed pattern payload, frontend renders the automatic overlay, and manual drawing remains usable on the same chart.
- [x] 4.5 Re-run relevant FUNCTION_TREE governance checks before changing implementation status.

## 5. Follow-Up

- [x] 5.1 Update `docs/FUNCTION_TREE.md` only after the MVP is implemented and verified.
- [x] 5.2 Keep advanced tools and additional pattern families as follow-up changes rather than extending this MVP batch in place.
